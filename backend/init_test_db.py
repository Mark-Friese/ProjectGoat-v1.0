"""
Initialize test database with sample data for E2E tests
"""
import os
import sys
from pathlib import Path

# Set TEST_MODE before importing database module
os.environ["TEST_MODE"] = "e2e"

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from datetime import date, datetime
from database import engine, Base, get_db
from models import User, Project, Task, Risk, Issue
from auth import hash_password
from sqlalchemy import text

def init_test_database():
    """Initialize test database with sample data"""
    print("=" * 60)
    print("  Initializing Test Database for E2E Tests")
    print("=" * 60)

    # Drop all tables
    print("\n[1/4] Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)

    # Create all tables
    print("[2/4] Creating tables...")
    Base.metadata.create_all(bind=engine)

    # Get database session
    db = next(get_db())

    try:
        # Create app_settings table
        print("[3/4] Creating app_settings table...")
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """))
        db.commit()

        # Add sample data
        print("[4/4] Adding sample data...")

        # Add users
        users_data = [
            {
                "id": "u1",
                "name": "Sarah Chen",
                "email": "sarah@example.com",
                "password": "password123",
                "role": "admin",
                "avatar": "/avatars/avatar1.jpg"
            },
            {
                "id": "u2",
                "name": "Marcus Rodriguez",
                "email": "marcus@example.com",
                "password": "password123",
                "role": "member",
                "avatar": "/avatars/avatar2.jpg"
            },
            {
                "id": "u3",
                "name": "Elena Popov",
                "email": "elena@example.com",
                "password": "password123",
                "role": "member",
                "avatar": "/avatars/avatar3.jpg"
            }
        ]

        for user_data in users_data:
            password = user_data.pop("password")
            user = User(
                **user_data,
                password_hash=hash_password(password),
                is_active=True,
                availability=True,
                created_at=datetime.utcnow()
            )
            db.add(user)

        # Add projects
        projects_data = [
            {
                "id": "p1",
                "name": "Website Redesign",
                "description": "Complete overhaul of company website with modern design",
                "start_date": date(2025, 1, 1),
                "end_date": date(2025, 6, 30),
                "color": "#3b82f6"
            }
        ]

        for project_data in projects_data:
            project = Project(**project_data)
            db.add(project)

        # Add tasks
        tasks_data = [
            {
                "id": "t1",
                "title": "Design Homepage Mockup",
                "description": "Create high-fidelity mockup for new homepage",
                "status": "in_progress",
                "priority": "high",
                "assignee_id": "u1",
                "project_id": "p1",
                "start_date": date(2025, 1, 15),
                "due_date": date(2025, 2, 15),
                "progress": 65,
                "is_blocked": False,
                "is_milestone": False
            },
            {
                "id": "t2",
                "title": "Implement Navigation Menu",
                "description": "Build responsive navigation with dropdown menus",
                "status": "todo",
                "priority": "medium",
                "assignee_id": "u2",
                "project_id": "p1",
                "start_date": date(2025, 2, 1),
                "due_date": date(2025, 2, 28),
                "progress": 0,
                "is_blocked": False,
                "is_milestone": False
            }
        ]

        for task_data in tasks_data:
            task = Task(**task_data)
            db.add(task)

        db.commit()

        print("\n" + "=" * 60)
        print("  [SUCCESS] Test Database Initialized Successfully!")
        print("=" * 60)
        print(f"\n  Users created: {len(users_data)}")
        print(f"  Projects created: {len(projects_data)}")
        print(f"  Tasks created: {len(tasks_data)}")
        print("\n  Test credentials:")
        print("    Email: sarah@example.com")
        print("    Password: password123")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_test_database()
