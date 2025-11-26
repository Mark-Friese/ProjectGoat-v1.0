"""
Pydantic Schemas for Request/Response Validation
Handles data validation and serialization
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

# ==================== Team Schemas ====================


class TeamBase(BaseModel):
    name: str = Field(..., max_length=200)
    account_type: str = Field(default="single", pattern="^(single|multi)$", alias="accountType")

    class Config:
        populate_by_name = True


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)

    class Config:
        populate_by_name = True


class Team(TeamBase):
    id: str
    created_at: datetime = Field(alias="createdAt")
    is_archived: bool = Field(default=False, alias="isArchived")

    class Config:
        from_attributes = True
        populate_by_name = True


# ==================== Team Membership Schemas ====================


class TeamMembershipBase(BaseModel):
    role: str = Field(..., pattern="^(admin|member|viewer)$")


class TeamMember(BaseModel):
    """Team member with user details"""

    id: str  # user id
    name: str
    email: str
    role: str  # role in this team
    avatar: Optional[str] = None
    availability: bool = True
    joined_at: datetime = Field(alias="joinedAt")

    class Config:
        populate_by_name = True


class TeamMemberRoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(admin|member|viewer)$")


class RemoveMemberOptions(BaseModel):
    """Options for what to do with member's assigned tasks when removing them"""

    task_action: str = Field(
        default="unassign", pattern="^(unassign|reassign_admin|keep)$", alias="taskAction"
    )

    class Config:
        populate_by_name = True


# ==================== Invitation Schemas ====================


class InvitationCreate(BaseModel):
    email: EmailStr
    role: str = Field(default="member", pattern="^(admin|member|viewer)$")


class Invitation(BaseModel):
    id: str
    email: str
    role: str
    invited_by_name: str = Field(alias="invitedByName")
    expires_at: datetime = Field(alias="expiresAt")
    created_at: datetime = Field(alias="createdAt")

    class Config:
        populate_by_name = True


class InvitationDetails(BaseModel):
    """Details shown when viewing an invitation (for accept page)"""

    team_name: str = Field(alias="teamName")
    team_account_type: str = Field(alias="teamAccountType")
    invited_by_name: str = Field(alias="invitedByName")
    email: str
    role: str
    expires_at: datetime = Field(alias="expiresAt")

    class Config:
        populate_by_name = True


class InvitationAccept(BaseModel):
    """Request to accept an invitation"""

    name: str = Field(..., max_length=200)
    password: str = Field(..., min_length=8)


# ==================== User Schemas ====================


class UserBase(BaseModel):
    name: str = Field(..., max_length=200)
    email: EmailStr
    role: str = Field(..., pattern="^(admin|member|viewer)$")
    avatar: Optional[str] = None
    availability: bool = True


class UserCreate(UserBase):
    id: str = Field(..., max_length=50)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, pattern="^(admin|member|viewer)$")
    avatar: Optional[str] = None
    availability: Optional[bool] = None


class User(UserBase):
    id: str

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    email: Optional[EmailStr] = None
    role: Optional[str] = None  # Will be validated to prevent self-elevation


class LoginHistoryEntry(BaseModel):
    ip_address: Optional[str] = Field(None, alias="ipAddress")
    user_agent: Optional[str] = Field(None, alias="userAgent")
    attempted_at: str = Field(alias="attemptedAt")
    success: bool

    class Config:
        populate_by_name = True


class UserProfile(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: Optional[str] = Field(None, alias="createdAt")
    last_login_at: Optional[str] = Field(None, alias="lastLoginAt")
    password_changed_at: Optional[str] = Field(None, alias="passwordChangedAt")
    login_history: List[LoginHistoryEntry] = Field(alias="loginHistory")

    class Config:
        from_attributes = True
        populate_by_name = True


# ==================== Project Schemas ====================


class ProjectBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    start_date: date = Field(alias="startDate")
    end_date: date = Field(alias="endDate")
    color: str = Field(..., pattern="^#[0-9A-Fa-f]{6}$")  # Hex color

    class Config:
        populate_by_name = True


class ProjectCreate(ProjectBase):
    id: str = Field(..., max_length=50)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    start_date: Optional[date] = Field(None, alias="startDate")
    end_date: Optional[date] = Field(None, alias="endDate")
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")

    class Config:
        populate_by_name = True


class Project(ProjectBase):
    id: str

    class Config:
        from_attributes = True
        populate_by_name = True  # Allow both snake_case and camelCase


# ==================== Comment Schemas ====================


class CommentBase(BaseModel):
    user_id: str = Field(..., max_length=50, alias="userId")
    text: str

    class Config:
        populate_by_name = True


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

    class Config:
        populate_by_name = True


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

    class Config:
        populate_by_name = True


class TaskCreate(TaskBase):
    id: str = Field(..., max_length=50)


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(todo|in-progress|review|done)$")
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    assignee_id: Optional[str] = Field(None, max_length=50, alias="assigneeId")
    start_date: Optional[date] = Field(None, alias="startDate")
    due_date: Optional[date] = Field(None, alias="dueDate")
    progress: Optional[int] = Field(None, ge=0, le=100)
    tags: Optional[List[str]] = None
    is_blocked: Optional[bool] = Field(None, alias="isBlocked")
    is_milestone: Optional[bool] = Field(None, alias="isMilestone")
    dependencies: Optional[List[str]] = None
    story_points: Optional[int] = Field(None, alias="storyPoints")
    parent_id: Optional[str] = Field(None, max_length=50, alias="parentId")
    project_id: Optional[str] = Field(None, max_length=50, alias="projectId")

    class Config:
        populate_by_name = True


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

    class Config:
        populate_by_name = True


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

    class Config:
        populate_by_name = True


class RiskCreate(RiskBase):
    id: str = Field(..., max_length=50)


class RiskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    probability: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    impact: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    owner_id: Optional[str] = Field(None, max_length=50, alias="ownerId")
    mitigation: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(open|mitigated|closed)$")

    class Config:
        populate_by_name = True


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

    class Config:
        populate_by_name = True


class IssueCreate(IssueBase):
    id: str = Field(..., max_length=50)


class IssueUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=300)
    description: Optional[str] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    assignee_id: Optional[str] = Field(None, max_length=50, alias="assigneeId")
    status: Optional[str] = Field(None, pattern="^(open|in-progress|resolved)$")
    related_task_ids: Optional[List[str]] = Field(None, alias="relatedTaskIds")

    class Config:
        populate_by_name = True


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
    csrf_token: str = Field(alias="csrfToken")
    user: User

    class Config:
        populate_by_name = True


class LogoutRequest(BaseModel):
    session_id: str


class SessionResponse(BaseModel):
    user: Optional[User] = None
    authenticated: bool


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ChangePasswordResponse(BaseModel):
    success: bool
    message: str
    csrf_token: str = Field(alias="csrfToken")

    class Config:
        populate_by_name = True


# ==================== Registration Schemas ====================


class AdminInfo(BaseModel):
    """Admin user info for registration"""

    name: str = Field(..., max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=8)


class RegisterRequest(BaseModel):
    """Request to register a new team with admin"""

    team_name: str = Field(..., max_length=200, alias="teamName")
    account_type: str = Field(default="single", pattern="^(single|multi)$", alias="accountType")
    admin: AdminInfo

    class Config:
        populate_by_name = True


class RegisterResponse(BaseModel):
    """Response after successful registration"""

    session_id: str = Field(alias="sessionId")
    csrf_token: str = Field(alias="csrfToken")
    user: User
    team: Team

    class Config:
        populate_by_name = True


class LoginResponseWithTeam(BaseModel):
    """Login response including team info"""

    session_id: str = Field(alias="sessionId")
    csrf_token: str = Field(alias="csrfToken")
    user: User
    team: Team
    teams: List[Team] = []  # All teams user belongs to (for multi-team accounts)

    class Config:
        populate_by_name = True


class SessionResponseWithTeam(BaseModel):
    """Session check response including team info"""

    user: Optional[User] = None
    team: Optional[Team] = None
    teams: List[Team] = []  # All teams user belongs to
    authenticated: bool

    class Config:
        populate_by_name = True


class TeamSwitchRequest(BaseModel):
    """Request to switch to a different team"""

    team_id: str = Field(alias="teamId")

    class Config:
        populate_by_name = True


class CreateTeamMemberRequest(BaseModel):
    """Request for admin to directly create a new team member"""

    name: str = Field(..., max_length=200)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = Field(default="member", pattern="^(admin|member|viewer)$")
