"""
FastAPI Main Application
Defines all REST API endpoints
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import json

import crud
import models
import schemas
from database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="ProjectGoat API",
    description="Project management and team collaboration API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8000", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


# ==================== Serve Frontend (Production) ====================

# Uncomment this in production to serve frontend static files
# frontend_path = Path(__file__).parent.parent / "frontend"
# if frontend_path.exists():
#     app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
