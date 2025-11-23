"""
Tests for authentication endpoints and session management.
"""

from datetime import datetime, timedelta

import pytest


class TestLogin:
    """Test login functionality."""

    def test_login_success(self, client, sample_users):
        """Test successful login."""
        user = sample_users[0]
        response = client.post(
            "/api/auth/login", json={"email": user.email, "password": user.password}
        )

        assert response.status_code == 200
        data = response.json()
        assert "sessionId" in data
        assert "csrfToken" in data
        assert data["user"]["email"] == user.email
        assert data["user"]["name"] == user.name
        assert data["user"]["role"] == user.role

    def test_login_wrong_password(self, client, sample_users):
        """Test login with incorrect password."""
        user = sample_users[0]
        response = client.post(
            "/api/auth/login", json={"email": user.email, "password": "WrongPassword123!"}
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post(
            "/api/auth/login", json={"email": "nonexistent@example.com", "password": "Test123!@#"}
        )

        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_missing_fields(self, client):
        """Test login with missing fields."""
        # Missing password
        response = client.post("/api/auth/login", json={"email": "test@example.com"})
        assert response.status_code == 422  # Validation error

        # Missing email
        response = client.post("/api/auth/login", json={"password": "Test123!@#"})
        assert response.status_code == 422  # Validation error

    def test_login_inactive_user(self, client, sample_users, db_session):
        """Test login with inactive user account."""
        user = sample_users[0]
        user.is_active = False
        db_session.commit()

        response = client.post(
            "/api/auth/login", json={"email": user.email, "password": user.password}
        )

        assert response.status_code == 403
        assert "Account has been disabled" in response.json()["detail"]


class TestLogout:
    """Test logout functionality."""

    def test_logout_success(self, authenticated_client):
        """Test successful logout."""
        client, session_id, csrf_token, user = authenticated_client

        # Logout
        response = client.post(
            "/api/auth/logout",
            json={"session_id": session_id},
            headers={"X-CSRF-Token": csrf_token},
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

        # Verify session is invalidated - check session should return unauthenticated
        response = client.get("/api/auth/session", params={"session_id": session_id})

        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert data["user"] is None

    def test_logout_without_session(self, client):
        """Test logout without session (requires session_id parameter)."""
        response = client.post("/api/auth/logout", json={})

        # Should return 422 validation error for missing session_id
        assert response.status_code == 422


class TestSessionValidation:
    """Test session validation and management."""

    def test_check_session_valid(self, authenticated_client):
        """Test checking a valid session."""
        client, session_id, csrf_token, user = authenticated_client

        response = client.get("/api/auth/session", params={"session_id": session_id})

        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert data["user"]["email"] == user.email

    def test_check_session_invalid(self, client):
        """Test checking an invalid session."""
        response = client.get("/api/auth/session", params={"session_id": "invalid_session_id"})

        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert data["user"] is None

    def test_check_session_no_header(self, client):
        """Test checking session without session parameter."""
        response = client.get("/api/auth/session")

        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert data["user"] is None

    def test_session_activity_tracking(self, authenticated_client, db_session):
        """Test that session activity is tracked."""
        from models import UserSession

        client, session_id, csrf_token, user = authenticated_client

        # Get initial last_activity_at
        session = db_session.query(UserSession).filter_by(id=session_id).first()
        initial_activity = session.last_accessed

        # Wait a moment and make another request
        import time

        time.sleep(1)

        # Make a request to trigger activity update
        client.get("/api/auth/session", params={"session_id": session_id})

        # Check that last_accessed was updated
        db_session.refresh(session)
        assert session.last_accessed > initial_activity


class TestPasswordChange:
    """Test password change functionality."""

    def test_change_password_success(self, authenticated_client, db_session):
        """Test successful password change."""
        client, session_id, csrf_token, user = authenticated_client

        new_password = "NewPassword123!@#"
        response = client.post(
            "/api/auth/change-password",
            json={
                "current_password": user.password,
                "new_password": new_password,
            },
            headers={"X-Session-ID": session_id, "X-CSRF-Token": csrf_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Password changed successfully"
        assert "csrfToken" in data  # New CSRF token should be returned

        # Verify old session is invalidated
        response = client.get("/api/auth/session", params={"session_id": session_id})
        assert response.status_code == 200
        assert response.json()["authenticated"] is False

        # Verify new password works
        response = client.post(
            "/api/auth/login", json={"email": user.email, "password": new_password}
        )
        assert response.status_code == 200

    def test_change_password_wrong_current(self, authenticated_client):
        """Test password change with wrong current password."""
        client, session_id, csrf_token, user = authenticated_client

        response = client.post(
            "/api/auth/change-password",
            json={
                "current_password": "WrongPassword123!",
                "new_password": "NewPassword123!@#",
            },
            headers={"X-Session-ID": session_id, "X-CSRF-Token": csrf_token},
        )

        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["detail"]

    def test_change_password_weak_password(self, authenticated_client):
        """Test password change with weak password."""
        client, session_id, csrf_token, user = authenticated_client

        # Too short
        response = client.post(
            "/api/auth/change-password",
            json={
                "current_password": user.password,
                "new_password": "Weak1!",
            },
            headers={"X-Session-ID": session_id, "X-CSRF-Token": csrf_token},
        )
        assert response.status_code == 400
        assert "at least 8 characters" in response.json()["detail"]

    def test_change_password_unauthenticated(self, client):
        """Test password change without authentication."""
        response = client.post(
            "/api/auth/change-password",
            json={
                "current_password": "Test123!@#",
                "new_password": "NewPassword123!@#",
            },
        )

        assert response.status_code == 401


class TestSessionTimeout:
    """Test session timeout functionality."""

    def test_idle_timeout(self, authenticated_client, db_session):
        """Test session idle timeout (30 minutes)."""
        from models import UserSession

        client, session_id, csrf_token, user = authenticated_client

        # Simulate 31 minutes of inactivity
        session = db_session.query(UserSession).filter_by(id=session_id).first()
        session.last_activity_at = datetime.utcnow() - timedelta(minutes=31)
        db_session.commit()

        # Session should be expired
        response = client.get("/api/auth/session", params={"session_id": session_id})

        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert data["user"] is None

    def test_absolute_timeout(self, authenticated_client, db_session):
        """Test session absolute timeout (8 hours)."""
        from models import UserSession

        client, session_id, csrf_token, user = authenticated_client

        # Simulate 9 hours since creation (with recent activity)
        session = db_session.query(UserSession).filter_by(id=session_id).first()
        session.created_at = datetime.utcnow() - timedelta(hours=9)
        session.last_activity_at = datetime.utcnow()  # Recent activity
        db_session.commit()

        # Session should be expired due to absolute timeout
        response = client.get("/api/auth/session", params={"session_id": session_id})

        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert data["user"] is None
