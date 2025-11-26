"""
FastAPI Main Application
Defines all REST API endpoints
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.exc import DatabaseError, SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware

# Try relative imports first (when run as package), fall back to absolute (when run standalone)
try:
    from . import auth, crud, csrf, models, rate_limiter, schemas, team_crud
    from .config import settings
    from .database import SessionLocal, engine, get_db
    from .logging_config import logger
except ImportError:
    import auth
    import crud
    import csrf
    import models
    import rate_limiter
    import schemas
    import team_crud
    from config import settings
    from database import SessionLocal, engine, get_db
    from logging_config import logger


# ==================== Auth Context ====================


class AuthContext:
    """Authentication context with user and team information"""

    def __init__(self, user_id: str, team_id: Optional[str] = None, role: Optional[str] = None):
        self.user_id = user_id
        self.team_id = team_id
        self.role = role  # Role in current team


# Create database tables
models.Base.metadata.create_all(bind=engine)


class SessionActivityMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track user session activity
    Updates last_activity_at for authenticated requests
    """

    async def dispatch(self, request: Request, call_next):
        # Get session ID from header
        session_id = request.headers.get("X-Session-ID")

        if session_id:
            # Update last_activity_at timestamp
            db = SessionLocal()
            try:
                db.execute(
                    text(
                        """
                        UPDATE sessions
                        SET last_activity_at = :now
                        WHERE id = :session_id
                    """
                    ),
                    {"now": datetime.now().isoformat(), "session_id": session_id},
                )
                db.commit()
            except (SQLAlchemyError, DatabaseError) as e:
                # Database errors are expected for invalid/expired sessions
                logger.debug(f"Failed to update session activity: {e}")
                db.rollback()
            except Exception as e:
                # Log unexpected errors but don't block the request
                logger.error(f"Unexpected error in session activity middleware: {e}", exc_info=True)
                db.rollback()
            finally:
                db.close()

        # Continue processing request
        response = await call_next(request)
        return response


# Initialize FastAPI app
app = FastAPI(
    title="ProjectGoat API",
    description="Project management and team collaboration API",
    version="1.0.0",
)

# CORS middleware - supports local development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session activity tracking middleware (before CSRF check)
app.add_middleware(SessionActivityMiddleware)

# CSRF protection middleware (skip in test mode)
if not os.getenv("TEST_MODE"):
    app.add_middleware(csrf.CSRFMiddleware)


# Security headers middleware (production only)
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to responses in production mode
    - X-Content-Type-Options: Prevents MIME type sniffing
    - X-Frame-Options: Prevents clickjacking
    - X-XSS-Protection: Enables browser XSS protection
    - Strict-Transport-Security: Forces HTTPS (production only)
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # HSTS only in production (requires HTTPS)
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response


# Add security headers in all modes (HSTS only in production)
app.add_middleware(SecurityHeadersMiddleware)


# ==================== Global Exception Handler ====================


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions
    Logs the error and returns a generic error response
    """
    logger.error(
        f"Unhandled exception in {request.method} {request.url.path}: {exc}", exc_info=True
    )
    return JSONResponse(
        status_code=500, content={"detail": "Internal server error", "path": request.url.path}
    )


# ==================== Health Check ====================


@app.get("/api/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "ok", "message": "ProjectGoat API is running"}


# ==================== Authentication Dependency ====================


def require_auth(http_request: Request, db: Session = Depends(get_db)) -> str:
    """
    Dependency to require authentication for endpoints.
    Returns the authenticated user ID.
    Raises 401 if not authenticated.
    Supports both session-based auth and fallback auth from settings.
    """
    user_id = None

    # Try to get user from session ID header
    session_id = http_request.headers.get("X-Session-ID")
    if session_id:
        user_id = auth.get_session_user(db, session_id)

    # If no session, try to get current user from settings (skip in test mode)
    if not user_id and not os.getenv("TEST_MODE"):
        user_id = auth.get_current_user_setting(db)

    # If still no user, return 401
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return user_id


def require_auth_with_team(http_request: Request, db: Session = Depends(get_db)) -> AuthContext:
    """
    Dependency to require authentication with team context.
    Returns AuthContext with user_id, team_id, and role.
    Raises 401 if not authenticated, 400 if no team context.
    """
    session_id = http_request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session = auth.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    # Get team context
    team_id = session.current_team_id

    # If no team in session, try to get user's first team
    if not team_id:
        teams = team_crud.get_teams_for_user(db, session.user_id)
        if teams:
            team_id = teams[0].id
            # Update session with team
            auth.switch_team(db, session_id, team_id)

    if not team_id:
        raise HTTPException(
            status_code=400, detail="No team context. Please join or create a team."
        )

    # Get user's role in this team
    role = team_crud.get_user_role_in_team(db, team_id, session.user_id)
    if not role:
        raise HTTPException(status_code=403, detail="Not a member of this team")

    return AuthContext(user_id=session.user_id, team_id=team_id, role=role)


def require_admin(auth_ctx: AuthContext = Depends(require_auth_with_team)) -> AuthContext:
    """
    Dependency to require admin role in current team.
    """
    if auth_ctx.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return auth_ctx


def get_optional_team_context(
    http_request: Request, db: Session = Depends(get_db)
) -> Optional[AuthContext]:
    """
    Get team context if available, otherwise return None.
    Used for endpoints that should filter by team when authenticated but still work without.
    """
    session_id = http_request.headers.get("X-Session-ID")
    if not session_id:
        return None

    session = auth.get_session(db, session_id)
    if not session or not session.current_team_id:
        return None

    role = team_crud.get_user_role_in_team(db, session.current_team_id, session.user_id)
    if not role:
        return None

    return AuthContext(user_id=session.user_id, team_id=session.current_team_id, role=role)


# ==================== User Endpoints ====================


@app.get("/api/users", response_model=List[schemas.User])
def list_users(
    http_request: Request, db: Session = Depends(get_db), user_id: str = Depends(require_auth)
):
    """Get all users (filtered by team if team context available)"""
    team_ctx = get_optional_team_context(http_request, db)
    team_id = team_ctx.team_id if team_ctx else None
    return crud.get_users(db, team_id=team_id)


# Profile endpoints must come before {user_id} to avoid route conflicts
@app.get("/api/users/me", response_model=schemas.UserProfile)
def get_current_user_profile(http_request: Request, db: Session = Depends(get_db)):
    """Get current user's profile"""
    user_id = None

    # Try to get user from session ID header
    session_id = http_request.headers.get("X-Session-ID")
    if session_id:
        user_id = auth.get_session_user(db, session_id)

    # If no session, try to get current user from settings (skip in test mode)
    if not user_id and not os.getenv("TEST_MODE"):
        user_id = auth.get_current_user_setting(db)

    # If still no user, return 401
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Get user details
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get login history
    login_history = db.execute(
        text(
            """
            SELECT ip_address, user_agent, attempted_at, success
            FROM login_attempts
            WHERE email = :email
            ORDER BY attempted_at DESC
            LIMIT 10
        """
        ),
        {"email": user.email},
    ).fetchall()

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "createdAt": user.created_at.isoformat() if user.created_at else None,
        "lastLoginAt": user.last_login_at.isoformat() if user.last_login_at else None,
        "passwordChangedAt": (
            user.password_changed_at.isoformat() if user.password_changed_at else None
        ),
        "loginHistory": [
            {
                "ipAddress": row[0],
                "userAgent": row[1],
                "attemptedAt": row[2] if isinstance(row[2], str) else row[2].isoformat(),
                "success": bool(row[3]),
            }
            for row in login_history
        ],
    }


@app.put("/api/users/me", response_model=schemas.User)
def update_current_user_profile(
    profile_update: schemas.ProfileUpdate, http_request: Request, db: Session = Depends(get_db)
):
    """Update current user's profile"""
    # Get session ID from header
    session_id = http_request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Get user from session
    user_id = auth.get_session_user(db, session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    # Validate: users can't change their own role
    if profile_update.role is not None:
        raise HTTPException(status_code=403, detail="You cannot change your own role")

    # Update user
    updated_user = crud.update_user(db, user_id, profile_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")

    return updated_user


@app.get("/api/users/{user_id}", response_model=schemas.User)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get specific user"""
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id '{user_id}' not found")
    return user


@app.post("/api/users", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Create new user"""
    return crud.create_user(db, user)


@app.put("/api/users/{user_id}", response_model=schemas.User)
def update_user(user_id: str, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Update existing user"""
    updated_user = crud.update_user(db, user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail=f"User with id '{user_id}' not found")
    return updated_user


# ==================== Project Endpoints ====================


@app.get("/api/projects", response_model=List[schemas.Project])
def list_projects(
    http_request: Request, db: Session = Depends(get_db), user_id: str = Depends(require_auth)
):
    """Get all projects (filtered by team if team context available)"""
    team_ctx = get_optional_team_context(http_request, db)
    team_id = team_ctx.team_id if team_ctx else None
    return crud.get_projects(db, team_id=team_id)


@app.get("/api/projects/{project_id}", response_model=schemas.Project)
def get_project(project_id: str, http_request: Request, db: Session = Depends(get_db)):
    """Get specific project"""
    team_ctx = get_optional_team_context(http_request, db)
    team_id = team_ctx.team_id if team_ctx else None
    project = crud.get_project(db, project_id, team_id=team_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id '{project_id}' not found")
    return project


@app.post("/api/projects", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(
    project: schemas.ProjectCreate, http_request: Request, db: Session = Depends(get_db)
):
    """Create new project (associated with team if team context available)"""
    team_ctx = get_optional_team_context(http_request, db)
    team_id = team_ctx.team_id if team_ctx else None
    return crud.create_project(db, project, team_id=team_id)


@app.put("/api/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: str, project: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    """Update existing project"""
    updated_project = crud.update_project(db, project_id, project)
    if not updated_project:
        raise HTTPException(status_code=404, detail=f"Project with id '{project_id}' not found")
    return updated_project


@app.delete("/api/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    """Delete project"""
    success = crud.delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Project with id '{project_id}' not found")
    return None


# ==================== Task Endpoints ====================


def serialize_task(task: models.Task) -> dict:
    """Convert task model to dict with proper JSON field handling"""
    task_dict = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "assigneeId": task.assignee_id,
        "startDate": task.start_date,
        "dueDate": task.due_date,
        "progress": task.progress,
        "tags": json.loads(task.tags) if task.tags else [],
        "isBlocked": task.is_blocked,
        "isMilestone": task.is_milestone,
        "dependencies": json.loads(task.dependencies) if task.dependencies else [],
        "storyPoints": task.story_points,
        "parentId": task.parent_id,
        "projectId": task.project_id,
        "comments": [
            {
                "id": comment.id,
                "userId": comment.user_id,
                "text": comment.text,
                "timestamp": comment.timestamp.isoformat(),
            }
            for comment in task.comments
        ],
        "blocker": (
            {
                "id": task.blocker.id,
                "description": task.blocker.description,
                "createdAt": task.blocker.created_at.isoformat(),
                "resolvedAt": (
                    task.blocker.resolved_at.isoformat() if task.blocker.resolved_at else None
                ),
                "resolutionNotes": task.blocker.resolution_notes,
            }
            if task.blocker
            else None
        ),
    }
    return task_dict


@app.get("/api/tasks")
def list_tasks(
    http_request: Request,
    project_id: Optional[str] = None,
    assignee_id: Optional[str] = None,
    status: Optional[str] = None,
    is_blocked: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    user_id: str = Depends(require_auth),
):
    """Get all tasks with optional filtering (filtered by team if team context available)"""
    team_ctx = get_optional_team_context(http_request, db)
    team_id = team_ctx.team_id if team_ctx else None
    tasks = crud.get_tasks(
        db, project_id, assignee_id, status, is_blocked, limit, offset, team_id=team_id
    )
    return [serialize_task(task) for task in tasks]


@app.get("/api/tasks/{task_id}")
def get_task(task_id: str, db: Session = Depends(get_db)):
    """Get specific task with all details"""
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id '{task_id}' not found")
    return serialize_task(task)


@app.post("/api/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Create new task"""
    created_task = crud.create_task(db, task)
    return serialize_task(created_task)


@app.put("/api/tasks/{task_id}")
def update_task(task_id: str, task: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """Update existing task"""
    updated_task = crud.update_task(db, task_id, task)
    if not updated_task:
        raise HTTPException(status_code=404, detail=f"Task with id '{task_id}' not found")
    return serialize_task(updated_task)


@app.patch("/api/tasks/{task_id}/status")
def update_task_status(
    task_id: str, status_update: schemas.TaskStatusUpdate, db: Session = Depends(get_db)
):
    """Update task status only"""
    updated_task = crud.update_task_status(db, task_id, status_update.status)
    if not updated_task:
        raise HTTPException(status_code=404, detail=f"Task with id '{task_id}' not found")
    return serialize_task(updated_task)


@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    """Delete task"""
    success = crud.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Task with id '{task_id}' not found")
    return None


# ==================== Comment Endpoints ====================


@app.post(
    "/api/tasks/{task_id}/comments",
    response_model=schemas.Comment,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(task_id: str, comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    """Add comment to task"""
    # Verify task exists
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id '{task_id}' not found")
    return crud.create_comment(db, task_id, comment)


@app.delete("/api/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: str, db: Session = Depends(get_db)):
    """Delete comment"""
    success = crud.delete_comment(db, comment_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Comment with id '{comment_id}' not found")
    return None


# ==================== Blocker Endpoints ====================


@app.post(
    "/api/tasks/{task_id}/blocker",
    response_model=schemas.Blocker,
    status_code=status.HTTP_201_CREATED,
)
def create_blocker(task_id: str, blocker: schemas.BlockerCreate, db: Session = Depends(get_db)):
    """Add blocker to task"""
    # Verify task exists
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id '{task_id}' not found")
    return crud.create_blocker(db, task_id, blocker)


@app.put("/api/blockers/{blocker_id}/resolve", response_model=schemas.Blocker)
def resolve_blocker(
    blocker_id: str, resolution: schemas.BlockerResolve, db: Session = Depends(get_db)
):
    """Resolve blocker"""
    resolved_blocker = crud.resolve_blocker(db, blocker_id, resolution)
    if not resolved_blocker:
        raise HTTPException(status_code=404, detail=f"Blocker with id '{blocker_id}' not found")
    return resolved_blocker


@app.delete("/api/blockers/{blocker_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blocker(blocker_id: str, db: Session = Depends(get_db)):
    """Remove blocker"""
    success = crud.delete_blocker(db, blocker_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Blocker with id '{blocker_id}' not found")
    return None


# ==================== Sprint Endpoints ====================


def serialize_sprint(sprint: models.Sprint) -> dict:
    """Convert sprint model to dict with proper JSON field handling"""
    return {
        "id": sprint.id,
        "name": sprint.name,
        "startDate": sprint.start_date,
        "endDate": sprint.end_date,
        "goals": json.loads(sprint.goals) if sprint.goals else [],
        "taskIds": json.loads(sprint.task_ids) if sprint.task_ids else [],
        "velocity": sprint.velocity,
    }


@app.get("/api/sprints")
def list_sprints(http_request: Request, db: Session = Depends(get_db)):
    """Get all sprints (filtered by team if team context available)"""
    team_ctx = get_optional_team_context(http_request, db)
    team_id = team_ctx.team_id if team_ctx else None
    sprints = crud.get_sprints(db, team_id=team_id)
    return [serialize_sprint(sprint) for sprint in sprints]


@app.post("/api/sprints", status_code=status.HTTP_201_CREATED)
def create_sprint(
    sprint: schemas.SprintCreate, http_request: Request, db: Session = Depends(get_db)
):
    """Create new sprint (associated with team if team context available)"""
    team_ctx = get_optional_team_context(http_request, db)
    team_id = team_ctx.team_id if team_ctx else None
    created_sprint = crud.create_sprint(db, sprint, team_id=team_id)
    return serialize_sprint(created_sprint)


# ==================== Risk Endpoints ====================


@app.get("/api/risks", response_model=List[schemas.Risk])
def list_risks(
    http_request: Request, db: Session = Depends(get_db), user_id: str = Depends(require_auth)
):
    """Get all risks (filtered by team if team context available)"""
    team_ctx = get_optional_team_context(http_request, db)
    team_id = team_ctx.team_id if team_ctx else None
    return crud.get_risks(db, team_id=team_id)


@app.get("/api/risks/{risk_id}", response_model=schemas.Risk)
def get_risk(risk_id: str, http_request: Request, db: Session = Depends(get_db)):
    """Get specific risk"""
    team_ctx = get_optional_team_context(http_request, db)
    team_id = team_ctx.team_id if team_ctx else None
    risk = crud.get_risk(db, risk_id, team_id=team_id)
    if not risk:
        raise HTTPException(status_code=404, detail=f"Risk with id '{risk_id}' not found")
    return risk


@app.post("/api/risks", response_model=schemas.Risk, status_code=status.HTTP_201_CREATED)
def create_risk(risk: schemas.RiskCreate, http_request: Request, db: Session = Depends(get_db)):
    """Create new risk (associated with team if team context available)"""
    team_ctx = get_optional_team_context(http_request, db)
    team_id = team_ctx.team_id if team_ctx else None
    return crud.create_risk(db, risk, team_id=team_id)


@app.put("/api/risks/{risk_id}", response_model=schemas.Risk)
def update_risk(risk_id: str, risk: schemas.RiskUpdate, db: Session = Depends(get_db)):
    """Update existing risk"""
    updated_risk = crud.update_risk(db, risk_id, risk)
    if not updated_risk:
        raise HTTPException(status_code=404, detail=f"Risk with id '{risk_id}' not found")
    return updated_risk


@app.delete("/api/risks/{risk_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_risk(risk_id: str, db: Session = Depends(get_db)):
    """Delete risk"""
    success = crud.delete_risk(db, risk_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Risk with id '{risk_id}' not found")
    return None


# ==================== Issue Endpoints ====================


def serialize_issue(issue: models.Issue) -> dict:
    """Convert issue model to dict with proper JSON field handling"""
    return {
        "id": issue.id,
        "title": issue.title,
        "description": issue.description,
        "priority": issue.priority,
        "assigneeId": issue.assignee_id,
        "status": issue.status,
        "relatedTaskIds": json.loads(issue.related_task_ids) if issue.related_task_ids else [],
        "createdAt": issue.created_at.isoformat(),
        "resolvedAt": issue.resolved_at.isoformat() if issue.resolved_at else None,
    }


@app.get("/api/issues")
def list_issues(
    http_request: Request,
    status: Optional[str] = None,
    assignee_id: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(require_auth),
):
    """Get all issues with optional filtering (filtered by team if team context available)"""
    team_ctx = get_optional_team_context(http_request, db)
    team_id = team_ctx.team_id if team_ctx else None
    issues = crud.get_issues(db, status, assignee_id, team_id=team_id)
    return [serialize_issue(issue) for issue in issues]


@app.get("/api/issues/{issue_id}")
def get_issue(issue_id: str, http_request: Request, db: Session = Depends(get_db)):
    """Get specific issue"""
    team_ctx = get_optional_team_context(http_request, db)
    team_id = team_ctx.team_id if team_ctx else None
    issue = crud.get_issue(db, issue_id, team_id=team_id)
    if not issue:
        raise HTTPException(status_code=404, detail=f"Issue with id '{issue_id}' not found")
    return serialize_issue(issue)


@app.post("/api/issues", status_code=status.HTTP_201_CREATED)
def create_issue(issue: schemas.IssueCreate, http_request: Request, db: Session = Depends(get_db)):
    """Create new issue (associated with team if team context available)"""
    team_ctx = get_optional_team_context(http_request, db)
    team_id = team_ctx.team_id if team_ctx else None
    created_issue = crud.create_issue(db, issue, team_id=team_id)
    return serialize_issue(created_issue)


@app.put("/api/issues/{issue_id}")
def update_issue(issue_id: str, issue: schemas.IssueUpdate, db: Session = Depends(get_db)):
    """Update existing issue"""
    updated_issue = crud.update_issue(db, issue_id, issue)
    if not updated_issue:
        raise HTTPException(status_code=404, detail=f"Issue with id '{issue_id}' not found")
    return serialize_issue(updated_issue)


@app.patch("/api/issues/{issue_id}/resolve")
def resolve_issue(issue_id: str, db: Session = Depends(get_db)):
    """Resolve issue"""
    resolved_issue = crud.resolve_issue(db, issue_id)
    if not resolved_issue:
        raise HTTPException(status_code=404, detail=f"Issue with id '{issue_id}' not found")
    return serialize_issue(resolved_issue)


@app.delete("/api/issues/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(issue_id: str, db: Session = Depends(get_db)):
    """Delete issue"""
    success = crud.delete_issue(db, issue_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Issue with id '{issue_id}' not found")
    return None


# ==================== Authentication Endpoints ====================


@app.post("/api/auth/login", response_model=schemas.LoginResponse)
def login(request: schemas.LoginRequest, http_request: Request, db: Session = Depends(get_db)):
    """Authenticate user and create session with rate limiting"""
    # Get client IP and user agent
    client_ip = http_request.client.host if http_request.client else None
    user_agent = http_request.headers.get("user-agent")

    # Check rate limits
    is_allowed, attempts_remaining, locked_until = rate_limiter.check_rate_limit(
        db, request.email, client_ip
    )

    if not is_allowed:
        # Account is locked
        rate_limiter.record_login_attempt(
            db,
            request.email,
            False,
            client_ip,
            user_agent,
            "Account locked due to too many failed attempts",
        )
        raise HTTPException(
            status_code=429,
            detail=f"Too many failed login attempts. Account locked for 15 minutes.",
        )

    # Find user by email
    user = crud.get_user_by_email(db, request.email)
    if not user:
        rate_limiter.record_login_attempt(
            db, request.email, False, client_ip, user_agent, "Email not found"
        )
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Check if account is active
    if not user.is_active:
        rate_limiter.record_login_attempt(
            db, request.email, False, client_ip, user_agent, "Account disabled"
        )
        raise HTTPException(
            status_code=403, detail="Account has been disabled. Please contact an administrator."
        )

    # Verify password
    if not auth.verify_password(request.password, user.password_hash):
        rate_limiter.record_login_attempt(
            db, request.email, False, client_ip, user_agent, "Invalid credentials"
        )
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Successful login - record it
    rate_limiter.record_login_attempt(db, request.email, True, client_ip, user_agent)

    # Clear any previous failed attempts
    rate_limiter.clear_login_attempts(db, request.email)

    # Update last login timestamp
    from sqlalchemy import text

    db.execute(
        text("UPDATE users SET last_login_at = :now WHERE id = :user_id"),
        {"now": datetime.now().isoformat(), "user_id": user.id},
    )
    db.commit()

    # Get user's teams and set the first one as current
    teams = team_crud.get_teams_for_user(db, user.id)
    current_team = teams[0] if teams else None
    current_team_id = current_team.id if current_team else None

    # Get user's role in current team
    current_role = user.role  # Default to stored role
    if current_team_id:
        team_role = team_crud.get_user_role_in_team(db, current_team_id, user.id)
        if team_role:
            current_role = team_role

    # Create session with team context
    session_id = auth.create_session(db, user.id, current_team_id)

    # Set as current user
    auth.set_current_user_setting(db, user.id)

    # Generate and store CSRF token
    csrf_token = csrf.generate_csrf_token()
    csrf.store_csrf_token(session_id, csrf_token)

    # Convert to response - use new response type if team exists
    if current_team:
        return schemas.LoginResponseWithTeam(
            sessionId=session_id,
            csrfToken=csrf_token,
            user=schemas.User(
                id=user.id,
                name=user.name,
                email=user.email,
                role=current_role,
                avatar=user.avatar,
                availability=user.availability,
            ),
            team=schemas.Team(
                id=current_team.id,
                name=current_team.name,
                accountType=current_team.account_type,
                createdAt=current_team.created_at,
                isArchived=current_team.is_archived,
            ),
            teams=[
                schemas.Team(
                    id=t.id,
                    name=t.name,
                    accountType=t.account_type,
                    createdAt=t.created_at,
                    isArchived=t.is_archived,
                )
                for t in teams
            ],
        )
    else:
        # Legacy response for users without teams (backward compatibility)
        return schemas.LoginResponse(
            sessionId=session_id,
            csrfToken=csrf_token,
            user=schemas.User(
                id=user.id,
                name=user.name,
                email=user.email,
                role=user.role,
                avatar=user.avatar,
                availability=user.availability,
            ),
        )


@app.get("/api/auth/session", response_model=schemas.SessionResponse)
def check_session(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Check if there's a valid session"""
    user_id = None

    # Try to get user from session ID
    if session_id:
        user_id = auth.get_session_user(db, session_id)

    # If no session, try to get current user from settings (skip in test mode)
    if not user_id and not os.getenv("TEST_MODE"):
        user_id = auth.get_current_user_setting(db)

    if not user_id:
        return schemas.SessionResponse(user=None, authenticated=False)

    # Get user details
    user = crud.get_user(db, user_id)
    if not user:
        return schemas.SessionResponse(user=None, authenticated=False)

    return schemas.SessionResponse(
        user=schemas.User(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            avatar=user.avatar,
            availability=user.availability,
        ),
        authenticated=True,
    )


@app.post("/api/auth/logout")
def logout(request: schemas.LogoutRequest, db: Session = Depends(get_db)):
    """Logout user and delete session"""
    auth.delete_session(db, request.session_id)
    return {"message": "Logged out successfully"}


@app.post("/api/auth/change-password", response_model=schemas.ChangePasswordResponse)
def change_password(
    request: schemas.ChangePasswordRequest, http_request: Request, db: Session = Depends(get_db)
):
    """Change user password with validation"""
    # Get session ID from header
    session_id = http_request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=401, detail="Session ID required")

    # Get user from session
    user_id = auth.get_session_user(db, session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    # Get user
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify current password
    if not auth.verify_password(request.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    # Validate new password strength
    is_valid, error_message = auth.validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    # Check if new password is different from current
    if auth.verify_password(request.new_password, user.password_hash):
        raise HTTPException(
            status_code=400, detail="New password must be different from current password"
        )

    # Hash new password
    new_password_hash = auth.hash_password(request.new_password)

    # Update password in database
    db.execute(
        text(
            """
            UPDATE users
            SET password_hash = :password_hash,
                password_changed_at = :changed_at
            WHERE id = :user_id
        """
        ),
        {
            "password_hash": new_password_hash,
            "changed_at": datetime.now().isoformat(),
            "user_id": user_id,
        },
    )
    db.commit()

    # Invalidate ALL sessions including current one for security after password change
    auth.invalidate_user_sessions(db, user_id)

    # Generate and store new CSRF token for security after password change
    new_csrf_token = csrf.generate_csrf_token()
    csrf.store_csrf_token(session_id, new_csrf_token)

    return schemas.ChangePasswordResponse(
        success=True, message="Password changed successfully", csrf_token=new_csrf_token
    )


@app.post("/api/auth/register", response_model=schemas.RegisterResponse)
def register(request: schemas.RegisterRequest, db: Session = Depends(get_db)):
    """Register a new team with an admin user"""
    # Check if email already exists
    existing_user = crud.get_user_by_email(db, request.admin.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate password strength
    is_valid, error_message = auth.validate_password_strength(request.admin.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    # Create team and admin user
    team, user = team_crud.register_team_with_admin(
        db,
        team_name=request.team_name,
        account_type=request.account_type,
        admin_name=request.admin.name,
        admin_email=request.admin.email,
        admin_password=request.admin.password,
    )

    # Create session with team context
    session_id = auth.create_session(db, user.id, team.id)

    # Generate CSRF token
    csrf_token = csrf.generate_csrf_token()
    csrf.store_csrf_token(session_id, csrf_token)

    return schemas.RegisterResponse(
        sessionId=session_id,
        csrfToken=csrf_token,
        user=schemas.User(
            id=user.id,
            name=user.name,
            email=user.email,
            role="admin",
            avatar=user.avatar,
            availability=user.availability,
        ),
        team=schemas.Team(
            id=team.id,
            name=team.name,
            accountType=team.account_type,
            createdAt=team.created_at,
            isArchived=team.is_archived,
        ),
    )


# ==================== Team Endpoints ====================


@app.get("/api/teams", response_model=List[schemas.Team])
def list_user_teams(http_request: Request, db: Session = Depends(get_db)):
    """Get all teams the current user belongs to"""
    session_id = http_request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = auth.get_session_user(db, session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    teams = team_crud.get_teams_for_user(db, user_id)
    return [
        schemas.Team(
            id=t.id,
            name=t.name,
            accountType=t.account_type,
            createdAt=t.created_at,
            isArchived=t.is_archived,
        )
        for t in teams
    ]


@app.get("/api/teams/current", response_model=schemas.Team)
def get_current_team(
    auth_ctx: AuthContext = Depends(require_auth_with_team), db: Session = Depends(get_db)
):
    """Get the current team"""
    team = team_crud.get_team(db, auth_ctx.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return schemas.Team(
        id=team.id,
        name=team.name,
        accountType=team.account_type,
        createdAt=team.created_at,
        isArchived=team.is_archived,
    )


@app.put("/api/teams/current", response_model=schemas.Team)
def update_current_team(
    request: schemas.TeamUpdate,
    auth_ctx: AuthContext = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update the current team (admin only)"""
    if not request.name:
        raise HTTPException(status_code=400, detail="Team name is required")

    team = team_crud.update_team(db, auth_ctx.team_id, request.name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    return schemas.Team(
        id=team.id,
        name=team.name,
        accountType=team.account_type,
        createdAt=team.created_at,
        isArchived=team.is_archived,
    )


@app.post("/api/teams/switch")
def switch_team(
    request: schemas.TeamSwitchRequest, http_request: Request, db: Session = Depends(get_db)
):
    """Switch to a different team"""
    session_id = http_request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = auth.get_session_user(db, session_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    # Verify user is member of target team
    role = team_crud.get_user_role_in_team(db, request.team_id, user_id)
    if not role:
        raise HTTPException(status_code=403, detail="Not a member of this team")

    # Switch team
    auth.switch_team(db, session_id, request.team_id)

    # Get team details
    team = team_crud.get_team(db, request.team_id)

    return {
        "message": "Team switched successfully",
        "team": schemas.Team(
            id=team.id,
            name=team.name,
            accountType=team.account_type,
            createdAt=team.created_at,
            isArchived=team.is_archived,
        ),
    }


# ==================== Team Member Endpoints ====================


@app.get("/api/teams/current/members", response_model=List[schemas.TeamMember])
def list_team_members(
    auth_ctx: AuthContext = Depends(require_auth_with_team), db: Session = Depends(get_db)
):
    """Get all members of the current team"""
    members = team_crud.get_team_members(db, auth_ctx.team_id)
    return [
        schemas.TeamMember(
            id=user.id,
            name=user.name,
            email=user.email,
            role=membership.role,
            avatar=user.avatar,
            availability=user.availability,
            joinedAt=membership.joined_at,
        )
        for user, membership in members
    ]


@app.post(
    "/api/teams/current/members",
    response_model=schemas.TeamMember,
    status_code=status.HTTP_201_CREATED,
)
def create_team_member(
    request: schemas.CreateTeamMemberRequest,
    auth_ctx: AuthContext = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new user and add them to the team (admin only)"""
    # Check if email already exists
    existing_user = crud.get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate password strength
    is_valid, error_message = auth.validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    # Create user and add to team
    user = team_crud.create_team_member(
        db,
        team_id=auth_ctx.team_id,
        name=request.name,
        email=request.email,
        password=request.password,
        role=request.role,
    )

    # Get membership for joined_at
    membership = team_crud.get_team_membership(db, auth_ctx.team_id, user.id)

    return schemas.TeamMember(
        id=user.id,
        name=user.name,
        email=user.email,
        role=membership.role,
        avatar=user.avatar,
        availability=user.availability,
        joinedAt=membership.joined_at,
    )


@app.put("/api/teams/current/members/{user_id}/role", response_model=schemas.TeamMember)
def update_member_role(
    user_id: str,
    request: schemas.TeamMemberRoleUpdate,
    auth_ctx: AuthContext = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update a team member's role (admin only)"""
    # Can't change own role
    if user_id == auth_ctx.user_id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")

    # Check if this would remove the last admin
    if request.role != "admin":
        membership = team_crud.get_team_membership(db, auth_ctx.team_id, user_id)
        if membership and membership.role == "admin":
            admin_count = team_crud.count_team_admins(db, auth_ctx.team_id)
            if admin_count <= 1:
                raise HTTPException(status_code=400, detail="Cannot remove the last admin")

    membership = team_crud.update_member_role(db, auth_ctx.team_id, user_id, request.role)
    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")

    user = crud.get_user(db, user_id)
    return schemas.TeamMember(
        id=user.id,
        name=user.name,
        email=user.email,
        role=membership.role,
        avatar=user.avatar,
        availability=user.availability,
        joinedAt=membership.joined_at,
    )


@app.delete("/api/teams/current/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_team_member(
    user_id: str,
    request: schemas.RemoveMemberOptions = None,
    auth_ctx: AuthContext = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Remove a member from the team (admin only)"""
    # Can't remove yourself
    if user_id == auth_ctx.user_id:
        raise HTTPException(status_code=400, detail="Cannot remove yourself from the team")

    # Check if this would remove the last admin
    membership = team_crud.get_team_membership(db, auth_ctx.team_id, user_id)
    if membership and membership.role == "admin":
        admin_count = team_crud.count_team_admins(db, auth_ctx.team_id)
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="Cannot remove the last admin")

    task_action = request.task_action if request else "unassign"
    success = team_crud.remove_member_from_team(db, auth_ctx.team_id, user_id, task_action)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")


# ==================== Invitation Endpoints ====================


@app.post(
    "/api/invitations", response_model=schemas.Invitation, status_code=status.HTTP_201_CREATED
)
def create_invitation(
    request: schemas.InvitationCreate,
    auth_ctx: AuthContext = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create an invitation to join the team (admin only)"""
    # Check if user already exists in team
    existing_user = crud.get_user_by_email(db, request.email)
    if existing_user:
        existing_membership = team_crud.get_team_membership(db, auth_ctx.team_id, existing_user.id)
        if existing_membership:
            raise HTTPException(status_code=400, detail="User is already a member of this team")

    # Check if invitation already exists
    existing_invitation = team_crud.get_invitation_by_email(db, auth_ctx.team_id, request.email)
    if existing_invitation:
        raise HTTPException(status_code=400, detail="An invitation for this email already exists")

    invitation = team_crud.create_invitation(
        db,
        team_id=auth_ctx.team_id,
        email=request.email,
        role=request.role,
        invited_by_user_id=auth_ctx.user_id,
    )

    inviter = crud.get_user(db, auth_ctx.user_id)
    return schemas.Invitation(
        id=invitation.id,
        email=invitation.email,
        role=invitation.role,
        invitedByName=inviter.name,
        expiresAt=invitation.expires_at,
        createdAt=invitation.created_at,
    )


@app.get("/api/invitations", response_model=List[schemas.Invitation])
def list_invitations(auth_ctx: AuthContext = Depends(require_admin), db: Session = Depends(get_db)):
    """List pending invitations for the team (admin only)"""
    invitations = team_crud.get_pending_invitations(db, auth_ctx.team_id)
    result = []
    for inv in invitations:
        inviter = crud.get_user(db, inv.invited_by_user_id)
        result.append(
            schemas.Invitation(
                id=inv.id,
                email=inv.email,
                role=inv.role,
                invitedByName=inviter.name if inviter else "Unknown",
                expiresAt=inv.expires_at,
                createdAt=inv.created_at,
            )
        )
    return result


@app.delete("/api/invitations/{invitation_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_invitation(
    invitation_id: str,
    auth_ctx: AuthContext = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Revoke an invitation (admin only)"""
    success = team_crud.revoke_invitation(db, invitation_id, auth_ctx.team_id)
    if not success:
        raise HTTPException(status_code=404, detail="Invitation not found")


@app.get("/api/invitations/{token}/details", response_model=schemas.InvitationDetails)
def get_invitation_details(token: str, db: Session = Depends(get_db)):
    """Get invitation details by token (for accept page)"""
    invitation = team_crud.get_invitation_by_token(db, token)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found or expired")

    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invitation has expired")

    team = team_crud.get_team(db, invitation.team_id)
    inviter = crud.get_user(db, invitation.invited_by_user_id)

    return schemas.InvitationDetails(
        teamName=team.name,
        teamAccountType=team.account_type,
        invitedByName=inviter.name if inviter else "Unknown",
        email=invitation.email,
        role=invitation.role,
        expiresAt=invitation.expires_at,
    )


@app.post("/api/invitations/{token}/accept", response_model=schemas.RegisterResponse)
def accept_invitation(token: str, request: schemas.InvitationAccept, db: Session = Depends(get_db)):
    """Accept an invitation and create account"""
    invitation = team_crud.get_invitation_by_token(db, token)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found or expired")

    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invitation has expired")

    # Check if user already exists
    existing_user = crud.get_user_by_email(db, invitation.email)
    if existing_user:
        # User exists, just add to team
        existing_membership = team_crud.get_team_membership(
            db, invitation.team_id, existing_user.id
        )
        if existing_membership:
            raise HTTPException(status_code=400, detail="Already a member of this team")

        team_crud.accept_invitation(db, invitation, existing_user.id)
        user = existing_user
    else:
        # Validate password strength
        is_valid, error_message = auth.validate_password_strength(request.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)

        # Create new user
        user = team_crud.create_team_member(
            db,
            team_id=invitation.team_id,
            name=request.name,
            email=invitation.email,
            password=request.password,
            role=invitation.role,
        )

        # Mark invitation as accepted
        invitation.accepted_at = datetime.utcnow()
        db.commit()

    # Get team
    team = team_crud.get_team(db, invitation.team_id)

    # Create session
    session_id = auth.create_session(db, user.id, team.id)

    # Generate CSRF token
    csrf_token = csrf.generate_csrf_token()
    csrf.store_csrf_token(session_id, csrf_token)

    return schemas.RegisterResponse(
        sessionId=session_id,
        csrfToken=csrf_token,
        user=schemas.User(
            id=user.id,
            name=user.name,
            email=user.email,
            role=invitation.role,
            avatar=user.avatar,
            availability=user.availability,
        ),
        team=schemas.Team(
            id=team.id,
            name=team.name,
            accountType=team.account_type,
            createdAt=team.created_at,
            isArchived=team.is_archived,
        ),
    )


# ==================== Settings Endpoints ====================


@app.get("/api/settings/current-user")
def get_current_user(db: Session = Depends(get_db)):
    """Get the current user ID from settings"""
    user_id = auth.get_current_user_setting(db)
    if not user_id:
        raise HTTPException(status_code=404, detail="No current user set")
    return {"userId": user_id}


@app.put("/api/settings/current-user")
def set_current_user(user_id: str, db: Session = Depends(get_db)):
    """Set the current user ID in settings"""
    # Verify user exists
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id '{user_id}' not found")

    auth.set_current_user_setting(db, user_id)
    return {"message": "Current user updated", "userId": user_id}


# ==================== Serve Frontend (Production) ====================

# Check if build directory exists (production mode)
BUILD_PATH = Path(__file__).parent.parent / "build"
if BUILD_PATH.exists():
    from fastapi.responses import FileResponse

    # Mount static assets (JS, CSS, images, etc.)
    app.mount("/assets", StaticFiles(directory=str(BUILD_PATH / "assets")), name="assets")

    # Serve static files from build root (logo, etc.)
    @app.get("/project-goat-logo.svg")
    async def logo():
        logo_path = BUILD_PATH / "project-goat-logo.svg"
        if logo_path.exists():
            return FileResponse(logo_path)
        raise HTTPException(status_code=404, detail="Logo not found")

    # Catch-all route for SPA - must be last!
    # This serves index.html for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't intercept API routes
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")

        # Serve index.html for all other routes (SPA routing)
        return FileResponse(BUILD_PATH / "index.html")
