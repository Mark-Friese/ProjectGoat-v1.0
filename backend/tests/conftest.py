"""
Pytest configuration and shared fixtures for backend tests.
"""
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
from models import User, Project, Task, Risk, Issue, LoginAttempt, UserSession
import crud


# In-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database for each test.
    """
    from sqlalchemy import text

    # Create all tables (including sessions table via UserSession model)
    Base.metadata.create_all(bind=engine)

    # Create session
    session = TestingSessionLocal()

    # Create app_settings table (not part of Base models - managed via raw SQL)
    session.execute(text("""
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at DATETIME NOT NULL
        )
    """))
    session.commit()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a test client with test database.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_users(db_session):
    """
    Create sample users for testing.
    """
    from auth import hash_password
    from models import User
    from datetime import datetime

    users = [
        {
            "id": "test_user_1",
            "name": "Test User 1",
            "email": "test1@example.com",
            "role": "admin",
            "password": "Test123!@#",
        },
        {
            "id": "test_user_2",
            "name": "Test User 2",
            "email": "test2@example.com",
            "role": "member",
            "password": "Test456!@#",
        },
    ]

    created_users = []
    for user_data in users:
        password = user_data.pop("password")

        # Create user with hashed password
        user = User(
            id=user_data["id"],
            name=user_data["name"],
            email=user_data["email"],
            role=user_data["role"],
            password_hash=hash_password(password),
            is_active=True,
            availability=True,
            created_at=datetime.utcnow()
        )
        user.password = password  # Store plain password for testing

        db_session.add(user)
        created_users.append(user)

    db_session.commit()
    return created_users


@pytest.fixture(scope="function")
def sample_projects(db_session):
    """
    Create sample projects for testing.
    """
    from models import Project
    from datetime import date

    projects = [
        {
            "id": "test_project_1",
            "name": "Test Project 1",
            "description": "Test project description",
            "start_date": date(2025, 1, 1),
            "end_date": date(2025, 12, 31),
            "color": "#3b82f6",
        },
    ]

    created_projects = []
    for project_data in projects:
        project = Project(**project_data)
        db_session.add(project)
        created_projects.append(project)

    db_session.commit()
    return created_projects


@pytest.fixture(scope="function")
def sample_tasks(db_session, sample_users, sample_projects):
    """
    Create sample tasks for testing.
    """
    from models import Task
    from datetime import date

    tasks = [
        {
            "id": "test_task_1",
            "title": "Test Task 1",
            "description": "Test task description",
            "status": "todo",
            "priority": "high",
            "assignee_id": sample_users[0].id,
            "project_id": sample_projects[0].id,
            "start_date": date(2025, 1, 1),
            "due_date": date(2025, 1, 15),
            "progress": 0,
            "is_blocked": False,
            "is_milestone": False,
        },
    ]

    created_tasks = []
    for task_data in tasks:
        task = Task(**task_data)
        db_session.add(task)
        created_tasks.append(task)

    db_session.commit()
    return created_tasks


@pytest.fixture(scope="function")
def authenticated_client(client, sample_users, db_session):
    """
    Create an authenticated client with a valid session.
    Returns tuple of (client, session_id, csrf_token, user).
    """
    user = sample_users[0]

    # Login to get session
    response = client.post(
        "/api/auth/login",
        json={"email": user.email, "password": user.password}
    )

    assert response.status_code == 200
    data = response.json()

    session_id = data["sessionId"]
    csrf_token = data["csrfToken"]

    return client, session_id, csrf_token, user


def get_auth_headers(session_id: str, csrf_token: str):
    """
    Helper function to create authentication headers.
    """
    return {
        "X-Session-ID": session_id,
        "X-CSRF-Token": csrf_token,
    }
