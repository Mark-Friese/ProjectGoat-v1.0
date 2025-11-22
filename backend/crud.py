"""
CRUD Operations
Database Create, Read, Update, Delete functions
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

try:
    from . import models
    from . import schemas
except ImportError:
    import models
    import schemas

import json

# ==================== Users ====================

def get_users(db: Session) -> List[models.User]:
    return db.query(models.User).all()

def get_user(db: Session, user_id: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: str, user: schemas.UserUpdate) -> Optional[models.User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    for key, value in user.model_dump().items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


# ==================== Projects ====================

def get_projects(db: Session) -> List[models.Project]:
    return db.query(models.Project).all()

def get_project(db: Session, project_id: str) -> Optional[models.Project]:
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def create_project(db: Session, project: schemas.ProjectCreate) -> models.Project:
    db_project = models.Project(**project.model_dump(by_alias=False))
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def update_project(db: Session, project_id: str, project: schemas.ProjectUpdate) -> Optional[models.Project]:
    db_project = get_project(db, project_id)
    if not db_project:
        return None
    for key, value in project.model_dump(by_alias=False).items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: str) -> bool:
    db_project = get_project(db, project_id)
    if not db_project:
        return False
    db.delete(db_project)
    db.commit()
    return True


# ==================== Tasks ====================

def get_tasks(
    db: Session,
    project_id: Optional[str] = None,
    assignee_id: Optional[str] = None,
    status: Optional[str] = None,
    is_blocked: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0
) -> List[models.Task]:
    query = db.query(models.Task)

    if project_id:
        query = query.filter(models.Task.project_id == project_id)
    if assignee_id:
        query = query.filter(models.Task.assignee_id == assignee_id)
    if status:
        query = query.filter(models.Task.status == status)
    if is_blocked is not None:
        query = query.filter(models.Task.is_blocked == is_blocked)

    return query.offset(offset).limit(limit).all()

def get_task(db: Session, task_id: str) -> Optional[models.Task]:
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def create_task(db: Session, task: schemas.TaskCreate) -> models.Task:
    task_data = task.model_dump(by_alias=False, exclude={'comments', 'blocker'})

    # Convert lists to JSON strings
    if 'tags' in task_data:
        task_data['tags'] = json.dumps(task_data['tags'])
    if 'dependencies' in task_data:
        task_data['dependencies'] = json.dumps(task_data['dependencies'])

    db_task = models.Task(**task_data)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: str, task: schemas.TaskUpdate) -> Optional[models.Task]:
    db_task = get_task(db, task_id)
    if not db_task:
        return None

    task_data = task.model_dump(by_alias=False, exclude={'comments', 'blocker'})

    # Convert lists to JSON strings
    if 'tags' in task_data:
        task_data['tags'] = json.dumps(task_data['tags'])
    if 'dependencies' in task_data:
        task_data['dependencies'] = json.dumps(task_data['dependencies'])

    for key, value in task_data.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)
    return db_task

def update_task_status(db: Session, task_id: str, status: str) -> Optional[models.Task]:
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    db_task.status = status
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: str) -> bool:
    db_task = get_task(db, task_id)
    if not db_task:
        return False
    db.delete(db_task)
    db.commit()
    return True


# ==================== Comments ====================

def create_comment(db: Session, task_id: str, comment: schemas.CommentCreate) -> models.Comment:
    import uuid
    db_comment = models.Comment(
        id=f"c{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        **comment.model_dump(by_alias=False),
        timestamp=datetime.now()
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

def delete_comment(db: Session, comment_id: str) -> bool:
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not db_comment:
        return False
    db.delete(db_comment)
    db.commit()
    return True


# ==================== Blockers ====================

def create_blocker(db: Session, task_id: str, blocker: schemas.BlockerCreate) -> models.Blocker:
    import uuid
    db_blocker = models.Blocker(
        id=f"b{uuid.uuid4().hex[:8]}",
        task_id=task_id,
        description=blocker.description,
        created_at=datetime.now()
    )

    # Also mark task as blocked
    db_task = get_task(db, task_id)
    if db_task:
        db_task.is_blocked = True

    db.add(db_blocker)
    db.commit()
    db.refresh(db_blocker)
    return db_blocker

def resolve_blocker(db: Session, blocker_id: str, resolution: schemas.BlockerResolve) -> Optional[models.Blocker]:
    db_blocker = db.query(models.Blocker).filter(models.Blocker.id == blocker_id).first()
    if not db_blocker:
        return None

    db_blocker.resolved_at = datetime.now()
    db_blocker.resolution_notes = resolution.resolution_notes

    # Unblock the task
    db_task = get_task(db, db_blocker.task_id)
    if db_task:
        db_task.is_blocked = False

    db.commit()
    db.refresh(db_blocker)
    return db_blocker

def delete_blocker(db: Session, blocker_id: str) -> bool:
    db_blocker = db.query(models.Blocker).filter(models.Blocker.id == blocker_id).first()
    if not db_blocker:
        return False

    # Unblock the task
    db_task = get_task(db, db_blocker.task_id)
    if db_task:
        db_task.is_blocked = False

    db.delete(db_blocker)
    db.commit()
    return True


# ==================== Sprints ====================

def get_sprints(db: Session) -> List[models.Sprint]:
    return db.query(models.Sprint).all()

def create_sprint(db: Session, sprint: schemas.SprintCreate) -> models.Sprint:
    sprint_data = sprint.model_dump(by_alias=False)

    # Convert lists to JSON strings
    if 'goals' in sprint_data:
        sprint_data['goals'] = json.dumps(sprint_data['goals'])
    if 'task_ids' in sprint_data:
        sprint_data['task_ids'] = json.dumps(sprint_data['task_ids'])

    db_sprint = models.Sprint(**sprint_data)
    db.add(db_sprint)
    db.commit()
    db.refresh(db_sprint)
    return db_sprint


# ==================== Risks ====================

def get_risks(db: Session) -> List[models.Risk]:
    return db.query(models.Risk).all()

def get_risk(db: Session, risk_id: str) -> Optional[models.Risk]:
    return db.query(models.Risk).filter(models.Risk.id == risk_id).first()

def create_risk(db: Session, risk: schemas.RiskCreate) -> models.Risk:
    db_risk = models.Risk(**risk.model_dump(by_alias=False))
    db.add(db_risk)
    db.commit()
    db.refresh(db_risk)
    return db_risk

def update_risk(db: Session, risk_id: str, risk: schemas.RiskUpdate) -> Optional[models.Risk]:
    db_risk = get_risk(db, risk_id)
    if not db_risk:
        return None
    for key, value in risk.model_dump(by_alias=False).items():
        setattr(db_risk, key, value)
    db.commit()
    db.refresh(db_risk)
    return db_risk

def delete_risk(db: Session, risk_id: str) -> bool:
    db_risk = get_risk(db, risk_id)
    if not db_risk:
        return False
    db.delete(db_risk)
    db.commit()
    return True


# ==================== Issues ====================

def get_issues(
    db: Session,
    status: Optional[str] = None,
    assignee_id: Optional[str] = None
) -> List[models.Issue]:
    query = db.query(models.Issue)

    if status:
        query = query.filter(models.Issue.status == status)
    if assignee_id:
        query = query.filter(models.Issue.assignee_id == assignee_id)

    return query.all()

def get_issue(db: Session, issue_id: str) -> Optional[models.Issue]:
    return db.query(models.Issue).filter(models.Issue.id == issue_id).first()

def create_issue(db: Session, issue: schemas.IssueCreate) -> models.Issue:
    issue_data = issue.model_dump(by_alias=False)

    # Convert list to JSON string
    if 'related_task_ids' in issue_data:
        issue_data['related_task_ids'] = json.dumps(issue_data['related_task_ids'])

    db_issue = models.Issue(**issue_data, created_at=datetime.now())
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue

def update_issue(db: Session, issue_id: str, issue: schemas.IssueUpdate) -> Optional[models.Issue]:
    db_issue = get_issue(db, issue_id)
    if not db_issue:
        return None

    issue_data = issue.model_dump(by_alias=False)

    # Convert list to JSON string
    if 'related_task_ids' in issue_data:
        issue_data['related_task_ids'] = json.dumps(issue_data['related_task_ids'])

    for key, value in issue_data.items():
        setattr(db_issue, key, value)

    db.commit()
    db.refresh(db_issue)
    return db_issue

def resolve_issue(db: Session, issue_id: str) -> Optional[models.Issue]:
    db_issue = get_issue(db, issue_id)
    if not db_issue:
        return None

    db_issue.status = "resolved"
    db_issue.resolved_at = datetime.now()

    db.commit()
    db.refresh(db_issue)
    return db_issue

def delete_issue(db: Session, issue_id: str) -> bool:
    db_issue = get_issue(db, issue_id)
    if not db_issue:
        return False
    db.delete(db_issue)
    db.commit()
    return True
