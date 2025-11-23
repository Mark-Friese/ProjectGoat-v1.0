"""
Tests for API CRUD endpoints (tasks, projects, users, risks, issues).
"""

import pytest
from conftest import get_auth_headers


class TestTasksAPI:
    """Test /api/tasks endpoints."""

    def test_get_all_tasks(self, authenticated_client, sample_tasks):
        """Test GET /api/tasks."""
        client, session_id, csrf_token, user = authenticated_client

        response = client.get("/api/tasks", headers={"X-Session-ID": session_id})

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == sample_tasks[0].title

    def test_get_task_by_id(self, authenticated_client, sample_tasks):
        """Test GET /api/tasks/{id}."""
        client, session_id, csrf_token, user = authenticated_client
        task = sample_tasks[0]

        response = client.get(f"/api/tasks/{task.id}", headers={"X-Session-ID": session_id})

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task.id
        assert data["title"] == task.title

    def test_create_task(self, authenticated_client, sample_projects):
        """Test POST /api/tasks."""
        client, session_id, csrf_token, user = authenticated_client

        task_data = {
            "title": "New Test Task",
            "description": "Task description",
            "status": "todo",
            "priority": "high",
            "assignee_id": user.id,
            "project_id": sample_projects[0].id,
            "start_date": "2025-01-01",
            "due_date": "2025-01-15",
        }

        response = client.post(
            "/api/tasks", json=task_data, headers=get_auth_headers(session_id, csrf_token)
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == task_data["title"]
        assert "id" in data

    def test_update_task(self, authenticated_client, sample_tasks):
        """Test PUT /api/tasks/{id}."""
        client, session_id, csrf_token, user = authenticated_client
        task = sample_tasks[0]

        update_data = {"title": "Updated Task Title", "status": "in-progress"}

        response = client.put(
            f"/api/tasks/{task.id}",
            json=update_data,
            headers=get_auth_headers(session_id, csrf_token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["status"] == update_data["status"]

    def test_delete_task(self, authenticated_client, sample_tasks):
        """Test DELETE /api/tasks/{id}."""
        client, session_id, csrf_token, user = authenticated_client
        task = sample_tasks[0]

        response = client.delete(
            f"/api/tasks/{task.id}", headers=get_auth_headers(session_id, csrf_token)
        )

        assert response.status_code == 200

        # Verify task is deleted
        response = client.get(f"/api/tasks/{task.id}", headers={"X-Session-ID": session_id})
        assert response.status_code == 404

    def test_update_task_status(self, authenticated_client, sample_tasks):
        """Test PATCH /api/tasks/{id}/status."""
        client, session_id, csrf_token, user = authenticated_client
        task = sample_tasks[0]

        response = client.patch(
            f"/api/tasks/{task.id}/status",
            json={"status": "done"},
            headers=get_auth_headers(session_id, csrf_token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "done"


class TestProjectsAPI:
    """Test /api/projects endpoints."""

    def test_get_all_projects(self, authenticated_client, sample_projects):
        """Test GET /api/projects."""
        client, session_id, csrf_token, user = authenticated_client

        response = client.get("/api/projects", headers={"X-Session-ID": session_id})

        assert response.status_code == 200
        projects = response.json()
        assert len(projects) == 1
        assert projects[0]["name"] == sample_projects[0].name

    def test_get_project_by_id(self, authenticated_client, sample_projects):
        """Test GET /api/projects/{id}."""
        client, session_id, csrf_token, user = authenticated_client
        project = sample_projects[0]

        response = client.get(f"/api/projects/{project.id}", headers={"X-Session-ID": session_id})

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == project.id
        assert data["name"] == project.name

    def test_create_project(self, authenticated_client):
        """Test POST /api/projects."""
        client, session_id, csrf_token, user = authenticated_client

        project_data = {
            "name": "New Test Project",
            "description": "Project description",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "color": "#3b82f6",
        }

        response = client.post(
            "/api/projects", json=project_data, headers=get_auth_headers(session_id, csrf_token)
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == project_data["name"]

    def test_update_project(self, authenticated_client, sample_projects):
        """Test PUT /api/projects/{id}."""
        client, session_id, csrf_token, user = authenticated_client
        project = sample_projects[0]

        update_data = {"name": "Updated Project Name"}

        response = client.put(
            f"/api/projects/{project.id}",
            json=update_data,
            headers=get_auth_headers(session_id, csrf_token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]

    def test_delete_project(self, authenticated_client, sample_projects):
        """Test DELETE /api/projects/{id}."""
        client, session_id, csrf_token, user = authenticated_client
        project = sample_projects[0]

        response = client.delete(
            f"/api/projects/{project.id}", headers=get_auth_headers(session_id, csrf_token)
        )

        assert response.status_code == 200


class TestUsersAPI:
    """Test /api/users endpoints."""

    def test_get_all_users(self, authenticated_client, sample_users):
        """Test GET /api/users."""
        client, session_id, csrf_token, user = authenticated_client

        response = client.get("/api/users", headers={"X-Session-ID": session_id})

        assert response.status_code == 200
        users = response.json()
        assert len(users) >= 2

    def test_get_user_by_id(self, authenticated_client, sample_users):
        """Test GET /api/users/{id}."""
        client, session_id, csrf_token, user = authenticated_client

        response = client.get(f"/api/users/{user.id}", headers={"X-Session-ID": session_id})

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == user.email

    def test_get_current_user(self, authenticated_client):
        """Test GET /api/users/me."""
        client, session_id, csrf_token, user = authenticated_client

        response = client.get("/api/users/me", headers={"X-Session-ID": session_id})

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["email"] == user.email

    def test_update_current_user_profile(self, authenticated_client):
        """Test PUT /api/users/me."""
        client, session_id, csrf_token, user = authenticated_client

        update_data = {"name": "Updated Name", "email": "updated@example.com"}

        response = client.put(
            "/api/users/me", json=update_data, headers=get_auth_headers(session_id, csrf_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["email"] == update_data["email"]

    def test_update_user(self, authenticated_client, sample_users):
        """Test PUT /api/users/{id}."""
        client, session_id, csrf_token, user = authenticated_client
        target_user = sample_users[1]

        update_data = {"availability": False}

        response = client.put(
            f"/api/users/{target_user.id}",
            json=update_data,
            headers=get_auth_headers(session_id, csrf_token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["availability"] is False


class TestRisksAPI:
    """Test /api/risks endpoints."""

    def test_get_all_risks(self, authenticated_client):
        """Test GET /api/risks."""
        client, session_id, csrf_token, user = authenticated_client

        response = client.get("/api/risks", headers={"X-Session-ID": session_id})

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_risk(self, authenticated_client):
        """Test POST /api/risks."""
        client, session_id, csrf_token, user = authenticated_client

        risk_data = {
            "title": "Test Risk",
            "description": "Risk description",
            "probability": "high",
            "impact": "high",
            "owner_id": user.id,
            "status": "open",
        }

        response = client.post(
            "/api/risks", json=risk_data, headers=get_auth_headers(session_id, csrf_token)
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == risk_data["title"]
        assert "id" in data

    def test_update_risk(self, authenticated_client):
        """Test PUT /api/risks/{id}."""
        client, session_id, csrf_token, user = authenticated_client

        # Create risk first
        risk_data = {
            "title": "Test Risk",
            "probability": "high",
            "impact": "high",
            "owner_id": user.id,
            "status": "open",
        }
        create_response = client.post(
            "/api/risks", json=risk_data, headers=get_auth_headers(session_id, csrf_token)
        )
        risk_id = create_response.json()["id"]

        # Update risk
        update_data = {"status": "mitigated"}
        response = client.put(
            f"/api/risks/{risk_id}",
            json=update_data,
            headers=get_auth_headers(session_id, csrf_token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "mitigated"

    def test_delete_risk(self, authenticated_client):
        """Test DELETE /api/risks/{id}."""
        client, session_id, csrf_token, user = authenticated_client

        # Create risk first
        risk_data = {
            "title": "Test Risk",
            "probability": "high",
            "impact": "high",
            "owner_id": user.id,
            "status": "open",
        }
        create_response = client.post(
            "/api/risks", json=risk_data, headers=get_auth_headers(session_id, csrf_token)
        )
        risk_id = create_response.json()["id"]

        # Delete risk
        response = client.delete(
            f"/api/risks/{risk_id}", headers=get_auth_headers(session_id, csrf_token)
        )

        assert response.status_code == 200


class TestIssuesAPI:
    """Test /api/issues endpoints."""

    def test_get_all_issues(self, authenticated_client):
        """Test GET /api/issues."""
        client, session_id, csrf_token, user = authenticated_client

        response = client.get("/api/issues", headers={"X-Session-ID": session_id})

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_issue(self, authenticated_client):
        """Test POST /api/issues."""
        client, session_id, csrf_token, user = authenticated_client

        issue_data = {
            "title": "Test Issue",
            "description": "Issue description",
            "priority": "high",
            "assignee_id": user.id,
            "status": "open",
        }

        response = client.post(
            "/api/issues", json=issue_data, headers=get_auth_headers(session_id, csrf_token)
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == issue_data["title"]
        assert "id" in data

    def test_update_issue(self, authenticated_client):
        """Test PUT /api/issues/{id}."""
        client, session_id, csrf_token, user = authenticated_client

        # Create issue first
        issue_data = {
            "title": "Test Issue",
            "priority": "high",
            "assignee_id": user.id,
            "status": "open",
        }
        create_response = client.post(
            "/api/issues", json=issue_data, headers=get_auth_headers(session_id, csrf_token)
        )
        issue_id = create_response.json()["id"]

        # Update issue
        update_data = {"status": "resolved"}
        response = client.put(
            f"/api/issues/{issue_id}",
            json=update_data,
            headers=get_auth_headers(session_id, csrf_token),
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "resolved"

    def test_delete_issue(self, authenticated_client):
        """Test DELETE /api/issues/{id}."""
        client, session_id, csrf_token, user = authenticated_client

        # Create issue first
        issue_data = {
            "title": "Test Issue",
            "priority": "high",
            "assignee_id": user.id,
            "status": "open",
        }
        create_response = client.post(
            "/api/issues", json=issue_data, headers=get_auth_headers(session_id, csrf_token)
        )
        issue_id = create_response.json()["id"]

        # Delete issue
        response = client.delete(
            f"/api/issues/{issue_id}", headers=get_auth_headers(session_id, csrf_token)
        )

        assert response.status_code == 200


class TestAuthenticationRequired:
    """Test that authentication is required for protected endpoints."""

    def test_tasks_require_authentication(self, client):
        """Test that tasks endpoints require authentication."""
        response = client.get("/api/tasks")
        assert response.status_code == 401

    def test_projects_require_authentication(self, client):
        """Test that projects endpoints require authentication."""
        response = client.get("/api/projects")
        assert response.status_code == 401

    def test_users_require_authentication(self, client):
        """Test that users endpoints require authentication."""
        response = client.get("/api/users")
        assert response.status_code == 401

    def test_risks_require_authentication(self, client):
        """Test that risks endpoints require authentication."""
        response = client.get("/api/risks")
        assert response.status_code == 401

    def test_issues_require_authentication(self, client):
        """Test that issues endpoints require authentication."""
        response = client.get("/api/issues")
        assert response.status_code == 401
