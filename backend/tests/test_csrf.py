"""
Tests for CSRF protection middleware.
"""

import pytest


class TestCSRFProtection:
    """Test CSRF token validation."""

    def test_csrf_required_for_post(self, authenticated_client, sample_projects):
        """Test that CSRF token is required for POST requests."""
        client, session_id, csrf_token, user = authenticated_client

        # POST without CSRF token should fail
        response = client.post(
            "/api/tasks",
            json={
                "title": "Test Task",
                "status": "todo",
                "priority": "high",
                "project_id": sample_projects[0].id,
                "start_date": "2025-01-01",
                "due_date": "2025-01-15",
            },
            headers={"X-Session-ID": session_id},  # No CSRF token
        )

        assert response.status_code == 403
        assert "CSRF token missing" in response.json()["detail"]

    def test_csrf_required_for_put(self, authenticated_client, sample_tasks):
        """Test that CSRF token is required for PUT requests."""
        client, session_id, csrf_token, user = authenticated_client
        task = sample_tasks[0]

        # PUT without CSRF token should fail
        response = client.put(
            f"/api/tasks/{task.id}",
            json={"title": "Updated Task"},
            headers={"X-Session-ID": session_id},  # No CSRF token
        )

        assert response.status_code == 403
        assert "CSRF token missing" in response.json()["detail"]

    def test_csrf_required_for_delete(self, authenticated_client, sample_tasks):
        """Test that CSRF token is required for DELETE requests."""
        client, session_id, csrf_token, user = authenticated_client
        task = sample_tasks[0]

        # DELETE without CSRF token should fail
        response = client.delete(
            f"/api/tasks/{task.id}", headers={"X-Session-ID": session_id}  # No CSRF token
        )

        assert response.status_code == 403
        assert "CSRF token missing" in response.json()["detail"]

    def test_csrf_not_required_for_get(self, authenticated_client):
        """Test that CSRF token is not required for GET requests."""
        client, session_id, csrf_token, user = authenticated_client

        # GET without CSRF token should work
        response = client.get("/api/tasks", headers={"X-Session-ID": session_id})  # No CSRF token

        assert response.status_code == 200

    def test_csrf_invalid_token(self, authenticated_client, sample_projects):
        """Test that invalid CSRF token is rejected."""
        client, session_id, csrf_token, user = authenticated_client

        # POST with invalid CSRF token
        response = client.post(
            "/api/tasks",
            json={
                "title": "Test Task",
                "status": "todo",
                "priority": "high",
                "project_id": sample_projects[0].id,
                "start_date": "2025-01-01",
                "due_date": "2025-01-15",
            },
            headers={"X-Session-ID": session_id, "X-CSRF-Token": "invalid_csrf_token"},
        )

        assert response.status_code == 403
        assert "Invalid CSRF token" in response.json()["detail"]

    def test_csrf_valid_token_works(self, authenticated_client, sample_projects):
        """Test that valid CSRF token allows request."""
        client, session_id, csrf_token, user = authenticated_client

        # POST with valid CSRF token should work
        response = client.post(
            "/api/tasks",
            json={
                "title": "Test Task",
                "status": "todo",
                "priority": "high",
                "assignee_id": user.id,
                "project_id": sample_projects[0].id,
                "start_date": "2025-01-01",
                "due_date": "2025-01-15",
            },
            headers={"X-Session-ID": session_id, "X-CSRF-Token": csrf_token},
        )

        assert response.status_code == 201

    def test_csrf_not_required_for_login(self, client, sample_users):
        """Test that CSRF token is not required for login endpoint."""
        user = sample_users[0]

        # Login should work without CSRF token
        response = client.post(
            "/api/auth/login", json={"email": user.email, "password": user.password}
        )

        assert response.status_code == 200

    def test_csrf_token_regenerated_on_password_change(self, authenticated_client):
        """Test that CSRF token is regenerated after password change."""
        client, session_id, old_csrf_token, user = authenticated_client

        # Change password
        response = client.post(
            "/api/auth/change-password",
            json={
                "current_password": user.password,
                "new_password": "NewPassword123!@#",
            },
            headers={"X-Session-ID": session_id, "X-CSRF-Token": old_csrf_token},
        )

        assert response.status_code == 200
        new_csrf_token = response.json()["csrfToken"]

        # New CSRF token should be different
        assert new_csrf_token != old_csrf_token

    def test_csrf_token_per_session(self, client, sample_users):
        """Test that each session gets its own CSRF token."""
        user = sample_users[0]

        # Create first session
        response1 = client.post(
            "/api/auth/login", json={"email": user.email, "password": user.password}
        )
        csrf_token1 = response1.json()["csrfToken"]

        # Logout
        client.post(
            "/api/auth/logout",
            headers={"X-Session-ID": response1.json()["sessionId"], "X-CSRF-Token": csrf_token1},
        )

        # Create second session
        response2 = client.post(
            "/api/auth/login", json={"email": user.email, "password": user.password}
        )
        csrf_token2 = response2.json()["csrfToken"]

        # CSRF tokens should be different
        assert csrf_token1 != csrf_token2
