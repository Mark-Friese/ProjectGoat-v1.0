"""
Authentication and Session Management
Handles password hashing, session creation, and validation
"""
import bcrypt
import secrets
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text

# Session timeout configuration
IDLE_TIMEOUT_MINUTES = 30  # Logout after 30 minutes of inactivity
ABSOLUTE_TIMEOUT_HOURS = 8  # Logout after 8 hours regardless of activity


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def create_session(db: Session, user_id: str, expires_days: int = 30) -> str:
    """Create a new session for a user"""
    session_id = secrets.token_urlsafe(32)
    created_at = datetime.now()
    expires_at = created_at + timedelta(days=expires_days)

    db.execute(
        text("""
            INSERT INTO sessions (
                id, user_id, created_at, expires_at, last_accessed
            )
            VALUES (
                :id, :user_id, :created_at, :expires_at, :last_accessed
            )
        """),
        {
            "id": session_id,
            "user_id": user_id,
            "created_at": created_at.isoformat(),
            "expires_at": expires_at.isoformat(),
            "last_accessed": created_at.isoformat()
        }
    )
    db.commit()

    return session_id


def get_session_user(db: Session, session_id: str) -> Optional[str]:
    """Get user ID from a session if it's valid and not expired"""
    result = db.execute(
        text("""
            SELECT user_id, expires_at, created_at, last_activity_at
            FROM sessions
            WHERE id = :session_id
        """),
        {"session_id": session_id}
    ).fetchone()

    if not result:
        return None

    user_id, expires_at_str, created_at_str, last_activity_at_str = result
    now = datetime.now()

    # Check absolute expiration (30 days from creation)
    expires_at = datetime.fromisoformat(expires_at_str)
    if now > expires_at:
        delete_session(db, session_id)
        return None

    # Check absolute timeout (8 hours from creation)
    created_at = datetime.fromisoformat(created_at_str)
    absolute_timeout = created_at + timedelta(
        hours=ABSOLUTE_TIMEOUT_HOURS
    )
    if now > absolute_timeout:
        delete_session(db, session_id)
        return None

    # Check idle timeout (30 minutes since last activity)
    if last_activity_at_str:
        last_activity_at = datetime.fromisoformat(last_activity_at_str)
        idle_timeout = last_activity_at + timedelta(minutes=IDLE_TIMEOUT_MINUTES)
        if now > idle_timeout:
            delete_session(db, session_id)
            return None

    # Session is valid - update last accessed time (not last_activity_at, that's for middleware)
    db.execute(
        text("UPDATE sessions SET last_accessed = :now WHERE id = :session_id"),
        {"now": now.isoformat(), "session_id": session_id}
    )
    db.commit()

    return user_id


def delete_session(db: Session, session_id: str):
    """Delete a session"""
    db.execute(
        text("DELETE FROM sessions WHERE id = :session_id"),
        {"session_id": session_id}
    )
    db.commit()


def get_current_user_setting(db: Session) -> Optional[str]:
    """Get the current user ID from app settings"""
    result = db.execute(
        text("SELECT value FROM app_settings WHERE key = 'current_user_id'")
    ).fetchone()

    return result[0] if result else None


def set_current_user_setting(db: Session, user_id: str):
    """Set the current user ID in app settings"""
    db.execute(
        text("""
            INSERT OR REPLACE INTO app_settings (key, value, updated_at)
            VALUES ('current_user_id', :user_id, :updated_at)
        """),
        {"user_id": user_id, "updated_at": datetime.now().isoformat()}
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

    if not re.search(r'[A-Z]', password):
        return (False, "Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        return (False, "Password must contain at least one lowercase letter")

    if not re.search(r'\d', password):
        return (False, "Password must contain at least one number")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return (False, "Password must contain at least one special character")

    return (True, "")


def invalidate_user_sessions(
    db: Session,
    user_id: str,
    except_session_id: Optional[str] = None
):
    """
    Invalidate all sessions for a user

    Args:
        db: Database session
        user_id: User ID whose sessions to invalidate
        except_session_id: Optional session ID to keep active (current session)
    """
    if except_session_id:
        db.execute(
            text("""
                DELETE FROM sessions
                WHERE user_id = :user_id
                  AND id != :except_session_id
            """),
            {"user_id": user_id, "except_session_id": except_session_id}
        )
    else:
        db.execute(
            text("DELETE FROM sessions WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
    db.commit()
