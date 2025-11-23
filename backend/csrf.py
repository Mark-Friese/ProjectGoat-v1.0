"""
CSRF Protection Middleware and Utilities
Protects against Cross-Site Request Forgery attacks
"""

import secrets
from typing import Optional

from database import SessionLocal
from fastapi import HTTPException, Request
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


def generate_csrf_token() -> str:
    """Generate a new CSRF token"""
    return secrets.token_urlsafe(32)


def store_csrf_token(session_id: str, token: str):
    """Store CSRF token for a session in database"""
    db = SessionLocal()
    try:
        db.execute(
            text("UPDATE sessions SET csrf_token = :token WHERE id = :session_id"),
            {"token": token, "session_id": session_id},
        )
        db.commit()
    finally:
        db.close()


def get_csrf_token(session_id: str) -> Optional[str]:
    """Get CSRF token for a session from database"""
    db = SessionLocal()
    try:
        result = db.execute(
            text("SELECT csrf_token FROM sessions WHERE id = :session_id"),
            {"session_id": session_id},
        ).fetchone()
        return result[0] if result and result[0] else None
    finally:
        db.close()


def verify_csrf_token(session_id: str, token: str) -> bool:
    """Verify CSRF token matches the stored token"""
    stored_token = get_csrf_token(session_id)
    if not stored_token:
        return False
    return secrets.compare_digest(stored_token, token)


def clear_csrf_token(session_id: str):
    """Clear CSRF token for a session"""
    db = SessionLocal()
    try:
        db.execute(
            text("UPDATE sessions SET csrf_token = NULL WHERE id = :session_id"),
            {"session_id": session_id},
        )
        db.commit()
    finally:
        db.close()


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Middleware to protect against CSRF attacks
    Validates CSRF tokens for state-changing operations (POST, PUT, DELETE, PATCH)
    """

    # Exempt paths that don't require CSRF protection
    EXEMPT_PATHS = [
        "/api/auth/login",  # Login creates the session/token
        "/api/auth/csrf-token",  # Endpoint to get CSRF token
        "/api/health",  # Health check
        "/docs",  # API documentation
        "/openapi.json",  # OpenAPI schema
    ]

    async def dispatch(self, request: Request, call_next):
        # Only check CSRF for state-changing methods
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            # Check if path is exempt
            is_exempt = any(request.url.path.startswith(path) for path in self.EXEMPT_PATHS)

            if not is_exempt:
                # Get CSRF token from header
                csrf_token = request.headers.get("X-CSRF-Token")

                # Get session ID from header or body
                session_id = request.headers.get("X-Session-ID")

                if not csrf_token:
                    return Response(
                        content='{"detail": "CSRF token missing"}',
                        status_code=403,
                        media_type="application/json",
                    )

                if not session_id:
                    return Response(
                        content='{"detail": "Session ID missing"}',
                        status_code=403,
                        media_type="application/json",
                    )

                # Verify token
                if not verify_csrf_token(session_id, csrf_token):
                    return Response(
                        content='{"detail": "Invalid CSRF token"}',
                        status_code=403,
                        media_type="application/json",
                    )

        # Token is valid or not required, proceed
        response = await call_next(request)
        return response
