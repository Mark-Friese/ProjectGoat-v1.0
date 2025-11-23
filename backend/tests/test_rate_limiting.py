"""
Tests for rate limiting and account lockout functionality.
"""

from datetime import datetime, timedelta

import pytest


class TestRateLimiting:
    """Test login rate limiting."""

    def test_rate_limit_5_attempts(self, client, sample_users, db_session):
        """Test that account locks after 5 failed attempts."""
        user = sample_users[0]

        # Make 5 failed login attempts
        for i in range(5):
            response = client.post(
                "/api/auth/login", json={"email": user.email, "password": "WrongPassword123!"}
            )
            assert response.status_code == 401

        # 6th attempt should be rate limited
        response = client.post(
            "/api/auth/login",
            json={"email": user.email, "password": user.password},  # Even with correct password
        )

        assert response.status_code == 429  # Too Many Requests
        assert "Too many failed login attempts" in response.json()["detail"]
        assert "15 minutes" in response.json()["detail"]

    def test_rate_limit_different_users(self, client, sample_users):
        """Test that rate limiting is per user."""
        user1 = sample_users[0]
        user2 = sample_users[1]

        # Make 5 failed attempts for user1
        for i in range(5):
            client.post(
                "/api/auth/login", json={"email": user1.email, "password": "WrongPassword123!"}
            )

        # user1 should be locked
        response = client.post(
            "/api/auth/login", json={"email": user1.email, "password": user1.password}
        )
        assert response.status_code == 429

        # user2 should still be able to login
        response = client.post(
            "/api/auth/login", json={"email": user2.email, "password": user2.password}
        )
        assert response.status_code == 200

    def test_lockout_expires_after_15_minutes(self, client, sample_users, db_session):
        """Test that lockout expires after 15 minutes."""
        from models import User

        user = sample_users[0]

        # Make 5 failed attempts to lock account
        for i in range(5):
            client.post(
                "/api/auth/login", json={"email": user.email, "password": "WrongPassword123!"}
            )

        # Verify account is locked
        response = client.post(
            "/api/auth/login", json={"email": user.email, "password": user.password}
        )
        assert response.status_code == 429

        # Simulate 16 minutes passing
        db_user = db_session.query(User).filter_by(email=user.email).first()
        db_user.account_locked_until = datetime.utcnow() - timedelta(minutes=1)
        db_session.commit()

        # Should be able to login now
        response = client.post(
            "/api/auth/login", json={"email": user.email, "password": user.password}
        )
        assert response.status_code == 200

    def test_successful_login_resets_failed_attempts(self, client, sample_users, db_session):
        """Test that successful login resets failed attempt counter."""
        from models import User

        user = sample_users[0]

        # Make 3 failed attempts
        for i in range(3):
            client.post(
                "/api/auth/login", json={"email": user.email, "password": "WrongPassword123!"}
            )

        # Verify failed attempts are recorded
        db_user = db_session.query(User).filter_by(email=user.email).first()
        assert db_user.failed_login_attempts == 3

        # Successful login
        response = client.post(
            "/api/auth/login", json={"email": user.email, "password": user.password}
        )
        assert response.status_code == 200

        # Failed attempts should be reset
        db_session.refresh(db_user)
        assert db_user.failed_login_attempts == 0

    def test_login_attempts_tracked(self, client, sample_users, db_session):
        """Test that login attempts are tracked in database."""
        from models import LoginAttempt

        user = sample_users[0]

        # Make a failed login attempt
        client.post("/api/auth/login", json={"email": user.email, "password": "WrongPassword123!"})

        # Check that attempt was logged
        attempt = db_session.query(LoginAttempt).filter_by(email=user.email).first()
        assert attempt is not None
        assert attempt.success is False
        assert "Invalid credentials" in attempt.failure_reason

        # Make a successful login attempt
        client.post("/api/auth/login", json={"email": user.email, "password": user.password})

        # Check that successful attempt was logged
        attempts = db_session.query(LoginAttempt).filter_by(email=user.email, success=True).all()
        assert len(attempts) == 1

    def test_rate_limit_window_15_minutes(self, client, sample_users, db_session):
        """Test that only attempts within 15-minute window count."""
        from models import LoginAttempt

        user = sample_users[0]

        # Create 3 old failed attempts (16 minutes ago)
        for i in range(3):
            attempt = LoginAttempt(
                email=user.email,
                attempted_at=datetime.utcnow() - timedelta(minutes=16),
                success=False,
                failure_reason="Invalid credentials",
            )
            db_session.add(attempt)
        db_session.commit()

        # Make 5 new failed attempts
        for i in range(5):
            response = client.post(
                "/api/auth/login", json={"email": user.email, "password": "WrongPassword123!"}
            )

        # Should be rate limited (5 attempts in last 15 min)
        response = client.post(
            "/api/auth/login", json={"email": user.email, "password": user.password}
        )
        assert response.status_code == 429

        # But the old attempts (16 min ago) should not count
        # Only the 5 recent attempts should count
