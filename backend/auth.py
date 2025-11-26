"""
Authentication and Session Management
Handles password hashing, session creation, and validation
"""

import re
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

import bcrypt
from models import UserSession
from sqlalchemy.orm import Session as DBSession

# Session timeout configuration
IDLE_TIMEOUT_MINUTES = 30  # Logout after 30 minutes of inactivity
ABSOLUTE_TIMEOUT_HOURS = 8  # Logout after 8 hours regardless of activity


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    if hashed is None:
        return False  # Prevent crash when password_hash is NULL
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_session(
    db: DBSession, user_id: str, team_id: Optional[str] = None, expires_days: int = 30
) -> str:
    """Create a new session for a user, optionally with a team context"""
    session_id = secrets.token_urlsafe(32)
    created_at = datetime.now()
    expires_at = created_at + timedelta(days=expires_days)

    session = UserSession(
        id=session_id,
        user_id=user_id,
        current_team_id=team_id,
        created_at=created_at,
        expires_at=expires_at,
        last_accessed=created_at,
        is_active=True,
        last_activity_at=created_at,
    )
    db.add(session)
    db.commit()

    return session_id


def get_session_user(db: DBSession, session_id: str) -> Optional[str]:
    """Get user ID from a session if it's valid and not expired"""
    session = db.query(UserSession).filter_by(id=session_id).first()

    if not session:
        return None

    now = datetime.now()

    # Check absolute expiration (30 days from creation)
    if now > session.expires_at:
        delete_session(db, session_id)
        return None

    # Check absolute timeout (8 hours from creation)
    absolute_timeout = session.created_at + timedelta(hours=ABSOLUTE_TIMEOUT_HOURS)
    if now > absolute_timeout:
        delete_session(db, session_id)
        return None

    # Check idle timeout (30 minutes since last activity)
    if session.last_activity_at:
        idle_timeout = session.last_activity_at + timedelta(minutes=IDLE_TIMEOUT_MINUTES)
        if now > idle_timeout:
            delete_session(db, session_id)
            return None

    # Session is valid - update last accessed time
    # (not last_activity_at, that's for middleware)
    session.last_accessed = now
    db.commit()

    return session.user_id


def delete_session(db: DBSession, session_id: str):
    """Delete a session"""
    session = db.query(UserSession).filter_by(id=session_id).first()
    if session:
        db.delete(session)
        db.commit()


def get_current_user_setting(db: DBSession) -> Optional[str]:
    """Get the current user ID from app settings"""
    from sqlalchemy import text

    result = db.execute(
        text("SELECT value FROM app_settings WHERE key = 'current_user_id'")
    ).fetchone()

    return result[0] if result else None


def set_current_user_setting(db: DBSession, user_id: str):
    """Set the current user ID in app settings"""
    from config import settings
    from sqlalchemy import text

    # Use database-appropriate UPSERT syntax
    if settings.is_postgres:
        # PostgreSQL: Use INSERT ... ON CONFLICT
        query = """
            INSERT INTO app_settings (key, value, updated_at)
            VALUES ('current_user_id', :user_id, :updated_at)
            ON CONFLICT (key)
            DO UPDATE SET value = EXCLUDED.value, updated_at = EXCLUDED.updated_at
        """
    else:
        # SQLite: Use INSERT OR REPLACE
        query = """
            INSERT OR REPLACE INTO app_settings (key, value, updated_at)
            VALUES ('current_user_id', :user_id, :updated_at)
        """

    db.execute(
        text(query),
        {"user_id": user_id, "updated_at": datetime.now().isoformat()},
    )
    db.commit()


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets security requirements

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return (False, "Password must be at least 8 characters long")

    if not re.search(r"[A-Z]", password):
        return (False, "Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        return (False, "Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        return (False, "Password must contain at least one number")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return (False, "Password must contain at least one special character")

    return (True, "")


def invalidate_user_sessions(db: DBSession, user_id: str, except_session_id: Optional[str] = None):
    """
    Invalidate all sessions for a user

    Args:
        db: Database session
        user_id: User ID whose sessions to invalidate
        except_session_id: Optional session ID to keep active (current session)
    """
    query = db.query(UserSession).filter_by(user_id=user_id)

    if except_session_id:
        query = query.filter(UserSession.id != except_session_id)

    query.delete(synchronize_session=False)
    db.commit()


def get_session(db: DBSession, session_id: str) -> Optional[UserSession]:
    """Get a session object if it's valid and not expired"""
    session = db.query(UserSession).filter_by(id=session_id).first()

    if not session:
        return None

    now = datetime.now()

    # Check absolute expiration (30 days from creation)
    if now > session.expires_at:
        delete_session(db, session_id)
        return None

    # Check absolute timeout (8 hours from creation)
    absolute_timeout = session.created_at + timedelta(hours=ABSOLUTE_TIMEOUT_HOURS)
    if now > absolute_timeout:
        delete_session(db, session_id)
        return None

    # Check idle timeout (30 minutes since last activity)
    if session.last_activity_at:
        idle_timeout = session.last_activity_at + timedelta(minutes=IDLE_TIMEOUT_MINUTES)
        if now > idle_timeout:
            delete_session(db, session_id)
            return None

    # Session is valid - update last accessed time
    session.last_accessed = now
    db.commit()

    return session


def switch_team(db: DBSession, session_id: str, team_id: str) -> bool:
    """Switch the current team for a session"""
    session = db.query(UserSession).filter_by(id=session_id).first()
    if not session:
        return False

    session.current_team_id = team_id
    db.commit()
    return True


def get_session_team_id(db: DBSession, session_id: str) -> Optional[str]:
    """Get the current team ID from a session"""
    session = db.query(UserSession).filter_by(id=session_id).first()
    return session.current_team_id if session else None
