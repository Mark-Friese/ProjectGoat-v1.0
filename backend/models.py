"""
SQLAlchemy ORM Models
Defines database tables and relationships
"""
from sqlalchemy import Column, String, Integer, Boolean, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import json

class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True, index=True)
    role = Column(String(20), nullable=False)  # admin, member, viewer
    avatar = Column(Text, nullable=True)
    availability = Column(Boolean, nullable=False, default=True)
    password_hash = Column(Text, nullable=True)  # Hashed password for authentication

    # Security and account management fields
    is_active = Column(Boolean, nullable=False, default=True)
    must_change_password = Column(Boolean, nullable=False, default=False)
    password_changed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime, nullable=True)

    # Relationships
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    comments = relationship("Comment", back_populates="user")
    owned_risks = relationship("Risk", back_populates="owner")
    assigned_issues = relationship("Issue", back_populates="assignee")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    """
    User authentication sessions.
    Note: Named 'UserSession' to avoid conflict with sqlalchemy.orm.Session
    """
    __tablename__ = "sessions"

    id = Column(String(255), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    last_accessed = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    last_activity_at = Column(DateTime, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    csrf_token = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    color = Column(String(7), nullable=False)  # Hex color #xxxxxx

    # Relationships
    tasks = relationship("Task", back_populates="project")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(50), primary_key=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, index=True)  # todo, in-progress, review, done
    priority = Column(String(10), nullable=False)  # low, medium, high
    assignee_id = Column(String(50), ForeignKey("users.id"), nullable=True, index=True)
    start_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False, index=True)
    progress = Column(Integer, nullable=False, default=0)  # 0-100
    tags = Column(Text, nullable=True)  # JSON array
    is_blocked = Column(Boolean, nullable=False, default=False)
    is_milestone = Column(Boolean, nullable=False, default=False)
    dependencies = Column(Text, nullable=True)  # JSON array of task IDs
    story_points = Column(Integer, nullable=True)
    parent_id = Column(String(50), ForeignKey("tasks.id"), nullable=True)
    project_id = Column(String(50), ForeignKey("projects.id"), nullable=False, index=True)

    # Relationships
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assignee_id])
    project = relationship("Project", back_populates="tasks")
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    blocker = relationship("Blocker", back_populates="task", uselist=False, cascade="all, delete-orphan")
    parent = relationship("Task", remote_side=[id], backref="subtasks")

    @property
    def tags_list(self):
        """Convert tags JSON string to list"""
        if self.tags:
            return json.loads(self.tags)
        return []

    @tags_list.setter
    def tags_list(self, value):
        """Convert tags list to JSON string"""
        self.tags = json.dumps(value) if value else None

    @property
    def dependencies_list(self):
        """Convert dependencies JSON string to list"""
        if self.dependencies:
            return json.loads(self.dependencies)
        return []

    @dependencies_list.setter
    def dependencies_list(self, value):
        """Convert dependencies list to JSON string"""
        self.dependencies = json.dumps(value) if value else None


class Comment(Base):
    __tablename__ = "comments"

    id = Column(String(50), primary_key=True)
    task_id = Column(String(50), ForeignKey("tasks.id"), nullable=False, index=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)

    # Relationships
    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="comments")


class Blocker(Base):
    __tablename__ = "blockers"

    id = Column(String(50), primary_key=True)
    task_id = Column(String(50), ForeignKey("tasks.id"), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Relationships
    task = relationship("Task", back_populates="blocker")


class Sprint(Base):
    __tablename__ = "sprints"

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    goals = Column(Text, nullable=True)  # JSON array
    task_ids = Column(Text, nullable=True)  # JSON array
    velocity = Column(Integer, nullable=False, default=0)

    @property
    def goals_list(self):
        """Convert goals JSON string to list"""
        if self.goals:
            return json.loads(self.goals)
        return []

    @goals_list.setter
    def goals_list(self, value):
        """Convert goals list to JSON string"""
        self.goals = json.dumps(value) if value else None

    @property
    def task_ids_list(self):
        """Convert task_ids JSON string to list"""
        if self.task_ids:
            return json.loads(self.task_ids)
        return []

    @task_ids_list.setter
    def task_ids_list(self, value):
        """Convert task_ids list to JSON string"""
        self.task_ids = json.dumps(value) if value else None


class Risk(Base):
    __tablename__ = "risks"

    id = Column(String(50), primary_key=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    probability = Column(String(10), nullable=False)  # low, medium, high
    impact = Column(String(10), nullable=False)  # low, medium, high
    owner_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    mitigation = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, index=True)  # open, mitigated, closed

    # Relationships
    owner = relationship("User", back_populates="owned_risks")


class Issue(Base):
    __tablename__ = "issues"

    id = Column(String(50), primary_key=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(10), nullable=False)  # low, medium, high
    assignee_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)  # open, in-progress, resolved
    related_task_ids = Column(Text, nullable=True)  # JSON array
    created_at = Column(DateTime, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    assignee = relationship("User", back_populates="assigned_issues")

    @property
    def related_task_ids_list(self):
        """Convert related_task_ids JSON string to list"""
        if self.related_task_ids:
            return json.loads(self.related_task_ids)
        return []

    @related_task_ids_list.setter
    def related_task_ids_list(self, value):
        """Convert related_task_ids list to JSON string"""
        self.related_task_ids = json.dumps(value) if value else None


class LoginAttempt(Base):
    __tablename__ = "login_attempts"

    id = Column(String(50), primary_key=True)
    email = Column(String(200), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    attempted_at = Column(DateTime, nullable=False, index=True)
    success = Column(Boolean, nullable=False, default=False)
    failure_reason = Column(Text, nullable=True)


class UserPermission(Base):
    """
    User permissions table (PLANNED - NOT YET IMPLEMENTED)

    Future feature for role-based access control (RBAC).
    Will define granular permissions for different user roles.

    Example usage:
    - role='admin', resource='projects', action='delete', allowed=True
    - role='viewer', resource='projects', action='delete', allowed=False

    TODO: Implement permission checking middleware/decorators
    """
    __tablename__ = "user_permissions"

    id = Column(String(50), primary_key=True)
    role = Column(String(20), nullable=False, index=True)
    resource = Column(String(50), nullable=False)
    action = Column(String(50), nullable=False)
    allowed = Column(Boolean, nullable=False, default=True)


class AuditLog(Base):
    """
    Audit log table (PLANNED - NOT YET IMPLEMENTED)

    Future feature for tracking all user actions for security and compliance.
    Will log all state-changing operations (create, update, delete).

    Use cases:
    - Security investigations
    - Compliance audits
    - User activity tracking
    - Rollback/recovery

    TODO: Implement audit logging middleware
    TODO: Add automatic population via decorators or middleware
    """
    __tablename__ = "audit_log"

    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    target_user_id = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)


class AppSettings(Base):
    """Application settings key-value store"""
    __tablename__ = "app_settings"

    key = Column(String(50), primary_key=True, index=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"<AppSettings(key={self.key}, value={self.value})>"
