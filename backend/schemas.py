"""
Pydantic Schemas for Request/Response Validation
Handles data validation and serialization
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime

# ==================== User Schemas ====================

class UserBase(BaseModel):
    name: str = Field(..., max_length=200)
    email: EmailStr
    role: str = Field(..., pattern="^(admin|member|viewer)$")
    avatar: Optional[str] = None
    availability: bool = True

class UserCreate(UserBase):
    id: str = Field(..., max_length=50)

class UserUpdate(UserBase):
    pass

class User(UserBase):
    id: str

    class Config:
        from_attributes = True


# ==================== Project Schemas ====================

class ProjectBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")
    color: str = Field(..., pattern="^#[0-9A-Fa-f]{6}$")  # Hex color

class ProjectCreate(ProjectBase):
    id: str = Field(..., max_length=50)

class ProjectUpdate(ProjectBase):
    pass

class Project(ProjectBase):
    id: str

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow both snake_case and camelCase


# ==================== Comment Schemas ====================

class CommentBase(BaseModel):
    user_id: str = Field(..., max_length=50, alias="userId")
    text: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: str
    timestamp: datetime

    class Config:
        from_attributes = True
        populate_by_name = True


# ==================== Blocker Schemas ====================

class BlockerBase(BaseModel):
    description: str

class BlockerCreate(BlockerBase):
    pass

class BlockerResolve(BaseModel):
    resolution_notes: str = Field(alias="resolutionNotes")

class Blocker(BlockerBase):
    id: str
    created_at: datetime = Field(alias="createdAt")
    resolved_at: Optional[datetime] = Field(None, alias="resolvedAt")
    resolution_notes: Optional[str] = Field(None, alias="resolutionNotes")

    class Config:
        from_attributes = True
        populate_by_name = True


# ==================== Task Schemas ====================

class TaskBase(BaseModel):
    title: str = Field(..., max_length=300)
    description: Optional[str] = None
    status: str = Field(..., pattern="^(todo|in-progress|review|done)$")
    priority: str = Field(..., pattern="^(low|medium|high)$")
    assignee_id: Optional[str] = Field(None, max_length=50, alias="assigneeId")
    start_date: date = Field(alias="startDate")
    due_date: date = Field(alias="dueDate")
    progress: int = Field(default=0, ge=0, le=100)
    tags: List[str] = []
    is_blocked: bool = Field(default=False, alias="isBlocked")
    is_milestone: bool = Field(default=False, alias="isMilestone")
    dependencies: List[str] = []
    story_points: Optional[int] = Field(None, alias="storyPoints")
    parent_id: Optional[str] = Field(None, max_length=50, alias="parentId")
    project_id: str = Field(..., max_length=50, alias="projectId")

class TaskCreate(TaskBase):
    id: str = Field(..., max_length=50)

class TaskUpdate(TaskBase):
    pass

class TaskStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(todo|in-progress|review|done)$")

class Task(TaskBase):
    id: str
    comments: List[Comment] = []
    blocker: Optional[Blocker] = None

    class Config:
        from_attributes = True
        populate_by_name = True


# ==================== Sprint Schemas ====================

class SprintBase(BaseModel):
    name: str = Field(..., max_length=200)
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")
    goals: List[str] = []
    task_ids: List[str] = Field([], alias="taskIds")
    velocity: int = 0

class SprintCreate(SprintBase):
    id: str = Field(..., max_length=50)

class SprintUpdate(SprintBase):
    pass

class Sprint(SprintBase):
    id: str

    class Config:
        from_attributes = True
        populate_by_name = True


# ==================== Risk Schemas ====================

class RiskBase(BaseModel):
    title: str = Field(..., max_length=300)
    description: Optional[str] = None
    probability: str = Field(..., pattern="^(low|medium|high)$")
    impact: str = Field(..., pattern="^(low|medium|high)$")
    owner_id: str = Field(..., max_length=50, alias="ownerId")
    mitigation: Optional[str] = None
    status: str = Field(..., pattern="^(open|mitigated|closed)$")

class RiskCreate(RiskBase):
    id: str = Field(..., max_length=50)

class RiskUpdate(RiskBase):
    pass

class Risk(RiskBase):
    id: str

    class Config:
        from_attributes = True
        populate_by_name = True


# ==================== Issue Schemas ====================

class IssueBase(BaseModel):
    title: str = Field(..., max_length=300)
    description: Optional[str] = None
    priority: str = Field(..., pattern="^(low|medium|high)$")
    assignee_id: str = Field(..., max_length=50, alias="assigneeId")
    status: str = Field(..., pattern="^(open|in-progress|resolved)$")
    related_task_ids: List[str] = Field([], alias="relatedTaskIds")

class IssueCreate(IssueBase):
    id: str = Field(..., max_length=50)

class IssueUpdate(IssueBase):
    pass

class Issue(IssueBase):
    id: str
    created_at: datetime = Field(alias="createdAt")
    resolved_at: Optional[datetime] = Field(None, alias="resolvedAt")

    class Config:
        from_attributes = True
        populate_by_name = True


# ==================== Authentication Schemas ====================

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    session_id: str = Field(alias="sessionId")
    user: User

    class Config:
        populate_by_name = True

class SessionResponse(BaseModel):
    user: Optional[User] = None
    authenticated: bool
