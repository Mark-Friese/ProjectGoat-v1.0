"""
FastAPI Main Application
Defines all REST API endpoints
"""
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pathlib import Path
from datetime import datetime
import json
import os

import crud
import models
import schemas
import auth
import rate_limiter
import csrf
from database import engine, get_db, SessionLocal
from config import settings

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
                    text("""
                        UPDATE sessions
                        SET last_activity_at = :now
                        WHERE id = :session_id
                    """),
                    {"now": datetime.now().isoformat(), "session_id": session_id}
                )
                db.commit()
            except Exception:
                # Silently fail - don't block request if activity update fails
                pass
            finally:
                db.close()

        # Continue processing request
        response = await call_next(request)
        return response


# Initialize FastAPI app
app = FastAPI(
    title="ProjectGoat API",
    description="Project management and team collaboration API",
    version="1.0.0"
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

# CSRF protection middleware
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


# ==================== Health Check ====================

@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "message": "ProjectGoat API is running"}


# ==================== User Endpoints ====================

@app.get("/api/users", response_model=List[schemas.User])
def list_users(db: Session = Depends(get_db)):
    """Get all users"""
    return crud.get_users(db)

# Profile endpoints must come before {user_id} to avoid route conflicts
@app.get("/api/users/me", response_model=schemas.UserProfile)
def get_current_user_profile(
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Get current user's profile"""
    # Get session ID from header
    session_id = http_request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    # Get user from session
    user_id = auth.get_session_user(db, session_id)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    # Get user details
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Get login history
    login_history = db.execute(
        text("""
            SELECT ip_address, user_agent, attempted_at, success
            FROM login_attempts
            WHERE email = :email
            ORDER BY attempted_at DESC
            LIMIT 10
        """),
        {"email": user.email}
    ).fetchall()

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "createdAt": user.created_at.isoformat() if user.created_at else None,
        "lastLoginAt": user.last_login_at.isoformat() if user.last_login_at else None,
        "passwordChangedAt": user.password_changed_at.isoformat() if user.password_changed_at else None,
        "loginHistory": [
            {
                "ipAddress": row[0],
                "userAgent": row[1],
                "attemptedAt": row[2],
                "success": bool(row[3])
            }
            for row in login_history
        ]
    }


@app.put("/api/users/me", response_model=schemas.User)
def update_current_user_profile(
    profile_update: schemas.ProfileUpdate,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    # Get session ID from header
    session_id = http_request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    # Get user from session
    user_id = auth.get_session_user(db, session_id)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    # Validate: users can't change their own role
    if profile_update.role is not None:
        raise HTTPException(
            status_code=403,
            detail="You cannot change your own role"
        )

    # Update user
    updated_user = crud.update_user(db, user_id, profile_update)
    if not updated_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

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
def list_projects(db: Session = Depends(get_db)):
    """Get all projects"""
    return crud.get_projects(db)

@app.get("/api/projects/{project_id}", response_model=schemas.Project)
def get_project(project_id: str, db: Session = Depends(get_db)):
    """Get specific project"""
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project with id '{project_id}' not found")
    return project

@app.post("/api/projects", response_model=schemas.Project, status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    """Create new project"""
    return crud.create_project(db, project)

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
                "timestamp": comment.timestamp.isoformat()
            } for comment in task.comments
        ],
        "blocker": {
            "id": task.blocker.id,
            "description": task.blocker.description,
            "createdAt": task.blocker.created_at.isoformat(),
            "resolvedAt": task.blocker.resolved_at.isoformat() if task.blocker.resolved_at else None,
            "resolutionNotes": task.blocker.resolution_notes
        } if task.blocker else None
    }
    return task_dict

@app.get("/api/tasks")
def list_tasks(
    project_id: Optional[str] = None,
    assignee_id: Optional[str] = None,
    status: Optional[str] = None,
    is_blocked: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get all tasks with optional filtering"""
    tasks = crud.get_tasks(db, project_id, assignee_id, status, is_blocked, limit, offset)
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
def update_task_status(task_id: str, status_update: schemas.TaskStatusUpdate, db: Session = Depends(get_db)):
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

@app.post("/api/tasks/{task_id}/comments", response_model=schemas.Comment, status_code=status.HTTP_201_CREATED)
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

@app.post("/api/tasks/{task_id}/blocker", response_model=schemas.Blocker, status_code=status.HTTP_201_CREATED)
def create_blocker(task_id: str, blocker: schemas.BlockerCreate, db: Session = Depends(get_db)):
    """Add blocker to task"""
    # Verify task exists
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task with id '{task_id}' not found")
    return crud.create_blocker(db, task_id, blocker)

@app.put("/api/blockers/{blocker_id}/resolve", response_model=schemas.Blocker)
def resolve_blocker(blocker_id: str, resolution: schemas.BlockerResolve, db: Session = Depends(get_db)):
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
        "velocity": sprint.velocity
    }

@app.get("/api/sprints")
def list_sprints(db: Session = Depends(get_db)):
    """Get all sprints"""
    sprints = crud.get_sprints(db)
    return [serialize_sprint(sprint) for sprint in sprints]

@app.post("/api/sprints", status_code=status.HTTP_201_CREATED)
def create_sprint(sprint: schemas.SprintCreate, db: Session = Depends(get_db)):
    """Create new sprint"""
    created_sprint = crud.create_sprint(db, sprint)
    return serialize_sprint(created_sprint)


# ==================== Risk Endpoints ====================

@app.get("/api/risks", response_model=List[schemas.Risk])
def list_risks(db: Session = Depends(get_db)):
    """Get all risks"""
    return crud.get_risks(db)

@app.get("/api/risks/{risk_id}", response_model=schemas.Risk)
def get_risk(risk_id: str, db: Session = Depends(get_db)):
    """Get specific risk"""
    risk = crud.get_risk(db, risk_id)
    if not risk:
        raise HTTPException(status_code=404, detail=f"Risk with id '{risk_id}' not found")
    return risk

@app.post("/api/risks", response_model=schemas.Risk, status_code=status.HTTP_201_CREATED)
def create_risk(risk: schemas.RiskCreate, db: Session = Depends(get_db)):
    """Create new risk"""
    return crud.create_risk(db, risk)

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
        "resolvedAt": issue.resolved_at.isoformat() if issue.resolved_at else None
    }

@app.get("/api/issues")
def list_issues(
    status: Optional[str] = None,
    assignee_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all issues with optional filtering"""
    issues = crud.get_issues(db, status, assignee_id)
    return [serialize_issue(issue) for issue in issues]

@app.get("/api/issues/{issue_id}")
def get_issue(issue_id: str, db: Session = Depends(get_db)):
    """Get specific issue"""
    issue = crud.get_issue(db, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail=f"Issue with id '{issue_id}' not found")
    return serialize_issue(issue)

@app.post("/api/issues", status_code=status.HTTP_201_CREATED)
def create_issue(issue: schemas.IssueCreate, db: Session = Depends(get_db)):
    """Create new issue"""
    created_issue = crud.create_issue(db, issue)
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
def login(
    request: schemas.LoginRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
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
        minutes_remaining = int(
            (locked_until - datetime.now()).total_seconds() / 60
        )
        rate_limiter.record_login_attempt(
            db, request.email, False, client_ip, user_agent,
            "Account locked due to too many failed attempts"
        )
        raise HTTPException(
            status_code=429,
            detail=f"Too many failed login attempts. Account locked for "
                   f"{minutes_remaining} more minutes."
        )

    # Find user by email
    user = crud.get_user_by_email(db, request.email)
    if not user:
        rate_limiter.record_login_attempt(
            db, request.email, False, client_ip, user_agent,
            "Email not found"
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Check if account is active
    if not user.is_active:
        rate_limiter.record_login_attempt(
            db, request.email, False, client_ip, user_agent,
            "Account disabled"
        )
        raise HTTPException(
            status_code=403,
            detail="Account has been disabled. Please contact an administrator."
        )

    # Verify password
    if not auth.verify_password(request.password, user.password_hash):
        rate_limiter.record_login_attempt(
            db, request.email, False, client_ip, user_agent,
            "Invalid password"
        )
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Successful login - record it
    rate_limiter.record_login_attempt(
        db, request.email, True, client_ip, user_agent
    )

    # Clear any previous failed attempts
    rate_limiter.clear_login_attempts(db, request.email)

    # Update last login timestamp
    from sqlalchemy import text
    db.execute(
        text("UPDATE users SET last_login_at = :now WHERE id = :user_id"),
        {"now": datetime.now().isoformat(), "user_id": user.id}
    )
    db.commit()

    # Create session
    session_id = auth.create_session(db, user.id)

    # Set as current user
    auth.set_current_user_setting(db, user.id)

    # Generate and store CSRF token
    csrf_token = csrf.generate_csrf_token()
    csrf.store_csrf_token(session_id, csrf_token)

    # Convert to response
    return schemas.LoginResponse(
        sessionId=session_id,
        csrfToken=csrf_token,
        user=schemas.User(
            id=user.id,
            name=user.name,
            email=user.email,
            role=user.role,
            avatar=user.avatar,
            availability=user.availability
        )
    )


@app.get("/api/auth/session", response_model=schemas.SessionResponse)
def check_session(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Check if there's a valid session"""
    user_id = None

    # Try to get user from session ID
    if session_id:
        user_id = auth.get_session_user(db, session_id)

    # If no session, try to get current user from settings (skip in test mode)
    if not user_id and os.getenv("TEST_MODE") != "e2e":
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
            availability=user.availability
        ),
        authenticated=True
    )


@app.post("/api/auth/logout")
def logout(session_id: str, db: Session = Depends(get_db)):
    """Logout user and delete session"""
    auth.delete_session(db, session_id)
    return {"message": "Logged out successfully"}


@app.post("/api/auth/change-password", response_model=schemas.ChangePasswordResponse)
def change_password(
    request: schemas.ChangePasswordRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Change user password with validation"""
    # Get session ID from header
    session_id = http_request.headers.get("X-Session-ID")
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Session ID required"
        )

    # Get user from session
    user_id = auth.get_session_user(db, session_id)
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    # Get user
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify current password
    if not auth.verify_password(request.current_password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Current password is incorrect"
        )

    # Validate new password strength
    is_valid, error_message = auth.validate_password_strength(
        request.new_password
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    # Check if new password is different from current
    if auth.verify_password(request.new_password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="New password must be different from current password"
        )

    # Hash new password
    new_password_hash = auth.hash_password(request.new_password)

    # Update password in database
    db.execute(
        text("""
            UPDATE users
            SET password_hash = :password_hash,
                password_changed_at = :changed_at
            WHERE id = :user_id
        """),
        {
            "password_hash": new_password_hash,
            "changed_at": datetime.now().isoformat(),
            "user_id": user_id
        }
    )
    db.commit()

    # Invalidate all other sessions except current one
    auth.invalidate_user_sessions(db, user_id, except_session_id=session_id)

    # Clear CSRF token (will be regenerated on next state-changing request)
    csrf.clear_csrf_token(session_id)

    return schemas.ChangePasswordResponse(
        success=True,
        message="Password changed successfully"
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
