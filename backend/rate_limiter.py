"""
Rate Limiting for Authentication
Prevents brute force attacks on login
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple

import models
from sqlalchemy import text
from sqlalchemy.orm import Session

# Configuration
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
ATTEMPT_WINDOW_MINUTES = 15


def check_rate_limit(
    db: Session, email: str, ip_address: Optional[str] = None
) -> Tuple[bool, int, Optional[datetime]]:
    """
    Check if login attempts exceed rate limit

    Args:
        db: Database session
        email: Email address attempting login
        ip_address: IP address (optional)

    Returns:
        Tuple of (is_allowed, attempts_remaining, locked_until)
        - is_allowed: True if login attempt should be allowed
        - attempts_remaining: Number of attempts remaining before lockout
        - locked_until: Datetime when account will be unlocked (if locked)
    """
    now = datetime.now()
    window_start = now - timedelta(minutes=ATTEMPT_WINDOW_MINUTES)

    # Check recent failed attempts within the time window
    result = db.execute(
        text(
            """
            SELECT COUNT(*) as count
            FROM login_attempts
            WHERE email = :email
              AND success = 0
              AND attempted_at > :window_start
        """
        ),
        {"email": email, "window_start": window_start.isoformat()},
    ).fetchone()

    failed_attempts = result[0] if result else 0

    # Calculate attempts remaining
    attempts_remaining = max(0, MAX_LOGIN_ATTEMPTS - failed_attempts)

    # If max attempts reached, calculate lockout time
    if failed_attempts >= MAX_LOGIN_ATTEMPTS:
        # Get the timestamp of the last failed attempt
        last_attempt_result = db.execute(
            text(
                """
                SELECT attempted_at
                FROM login_attempts
                WHERE email = :email
                  AND success = 0
                ORDER BY attempted_at DESC
                LIMIT 1
            """
            ),
            {"email": email},
        ).fetchone()

        if last_attempt_result:
            last_attempt = datetime.fromisoformat(last_attempt_result[0])
            locked_until = last_attempt + timedelta(minutes=LOCKOUT_DURATION_MINUTES)

            # Check if still locked
            if now < locked_until:
                return (False, 0, locked_until)

    # Not locked, attempts allowed
    return (True, attempts_remaining, None)


def record_login_attempt(
    db: Session,
    email: str,
    success: bool,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    failure_reason: Optional[str] = None,
):
    """
    Record a login attempt in the database

    Args:
        db: Database session
        email: Email address that attempted login
        success: Whether the login was successful
        ip_address: IP address (optional)
        user_agent: User agent string (optional)
        failure_reason: Reason for failure (optional)
    """
    attempt_id = secrets.token_urlsafe(16)
    now = datetime.now()

    db.execute(
        text(
            """
            INSERT INTO login_attempts (
                id, email, ip_address, user_agent, attempted_at,
                success, failure_reason
            )
            VALUES (
                :id, :email, :ip_address, :user_agent, :attempted_at,
                :success, :failure_reason
            )
        """
        ),
        {
            "id": attempt_id,
            "email": email,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "attempted_at": now.isoformat(),
            "success": success,
            "failure_reason": failure_reason,
        },
    )
    db.commit()


def clear_login_attempts(db: Session, email: str):
    """
    Clear all failed login attempts for an email after successful login

    Args:
        db: Database session
        email: Email address to clear attempts for
    """
    db.execute(
        text(
            """
            DELETE FROM login_attempts
            WHERE email = :email
              AND success = 0
        """
        ),
        {"email": email},
    )
    db.commit()


def cleanup_old_attempts(db: Session, days: int = 30):
    """
    Clean up login attempts older than specified days

    Args:
        db: Database session
        days: Number of days to keep (default: 30)
    """
    cutoff_date = datetime.now() - timedelta(days=days)

    db.execute(
        text(
            """
            DELETE FROM login_attempts
            WHERE attempted_at < :cutoff_date
        """
        ),
        {"cutoff_date": cutoff_date.isoformat()},
    )
    db.commit()
