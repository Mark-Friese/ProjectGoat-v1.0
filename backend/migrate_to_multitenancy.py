"""
Migration script for multi-tenancy support.

This script:
1. Creates new tables (teams, team_memberships, invitations)
2. Adds team_id columns to existing tables
3. Creates a default team and migrates existing data

Run this script once after updating the models.
Safe to run multiple times - checks for existing data.
"""

import uuid
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

# Import database and models
try:
    from backend.database import SessionLocal, engine
    from backend.models import Team, TeamMembership, User
except ImportError:
    from database import SessionLocal, engine
    from models import Team, TeamMembership, User


DEFAULT_TEAM_NAME = "My Team"
DEFAULT_TEAM_ID = "default-team"


def column_exists(db, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    try:
        # SQLite
        result = db.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
        return any(row[1] == column_name for row in result)
    except Exception:
        # PostgreSQL
        try:
            result = db.execute(
                text(
                    """
                    SELECT column_name FROM information_schema.columns
                    WHERE table_name = :table AND column_name = :column
                """
                ),
                {"table": table_name, "column": column_name},
            ).fetchone()
            return result is not None
        except Exception:
            return False


def table_exists(db, table_name: str) -> bool:
    """Check if a table exists."""
    try:
        # SQLite
        result = db.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
            {"name": table_name},
        ).fetchone()
        return result is not None
    except Exception:
        # PostgreSQL
        try:
            result = db.execute(
                text(
                    """
                    SELECT table_name FROM information_schema.tables
                    WHERE table_name = :name
                """
                ),
                {"name": table_name},
            ).fetchone()
            return result is not None
        except Exception:
            return False


def add_column_if_not_exists(db, table_name: str, column_name: str, column_type: str):
    """Add a column to a table if it doesn't exist."""
    if column_exists(db, table_name, column_name):
        print(f"  Column {table_name}.{column_name} already exists, skipping")
        return False

    try:
        db.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
        db.commit()
        print(f"  Added column {table_name}.{column_name}")
        return True
    except OperationalError as e:
        print(f"  Error adding column {table_name}.{column_name}: {e}")
        db.rollback()
        return False


def create_tables():
    """Create new tables using SQLAlchemy metadata."""
    from models import Base

    Base.metadata.create_all(bind=engine)
    print("Created/verified all tables")


def migrate_existing_data(db):
    """Migrate existing data to use teams."""

    # Check if default team already exists
    existing_team = db.execute(
        text("SELECT id FROM teams WHERE id = :id"), {"id": DEFAULT_TEAM_ID}
    ).fetchone()

    if existing_team:
        print(f"Default team '{DEFAULT_TEAM_ID}' already exists")
        team_id = DEFAULT_TEAM_ID
    else:
        # Create default team
        now = datetime.utcnow().isoformat()
        db.execute(
            text(
                """
                INSERT INTO teams (id, name, account_type, created_at, is_archived)
                VALUES (:id, :name, :account_type, :created_at, :is_archived)
            """
            ),
            {
                "id": DEFAULT_TEAM_ID,
                "name": DEFAULT_TEAM_NAME,
                "account_type": "single",
                "created_at": now,
                "is_archived": False,
            },
        )
        db.commit()
        print(f"Created default team: {DEFAULT_TEAM_NAME}")
        team_id = DEFAULT_TEAM_ID

    # Migrate users to team memberships
    users = db.execute(text("SELECT id, role FROM users")).fetchall()
    migrated_count = 0

    for user in users:
        user_id, role = user[0], user[1]

        # Check if membership already exists
        existing = db.execute(
            text("SELECT id FROM team_memberships WHERE team_id = :team_id AND user_id = :user_id"),
            {"team_id": team_id, "user_id": user_id},
        ).fetchone()

        if existing:
            continue

        # Create membership
        membership_id = f"tm_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        db.execute(
            text(
                """
                INSERT INTO team_memberships (id, team_id, user_id, role, joined_at)
                VALUES (:id, :team_id, :user_id, :role, :joined_at)
            """
            ),
            {
                "id": membership_id,
                "team_id": team_id,
                "user_id": user_id,
                "role": role or "member",
                "joined_at": now,
            },
        )
        migrated_count += 1

    db.commit()
    print(f"Migrated {migrated_count} users to team memberships")

    # Update projects with team_id
    if column_exists(db, "projects", "team_id"):
        updated = db.execute(
            text("UPDATE projects SET team_id = :team_id WHERE team_id IS NULL"),
            {"team_id": team_id},
        )
        db.commit()
        print(f"Updated {updated.rowcount} projects with team_id")

    # Update risks with team_id
    if column_exists(db, "risks", "team_id"):
        updated = db.execute(
            text("UPDATE risks SET team_id = :team_id WHERE team_id IS NULL"), {"team_id": team_id}
        )
        db.commit()
        print(f"Updated {updated.rowcount} risks with team_id")

    # Update issues with team_id
    if column_exists(db, "issues", "team_id"):
        updated = db.execute(
            text("UPDATE issues SET team_id = :team_id WHERE team_id IS NULL"), {"team_id": team_id}
        )
        db.commit()
        print(f"Updated {updated.rowcount} issues with team_id")

    # Update sprints with team_id
    if column_exists(db, "sprints", "team_id"):
        updated = db.execute(
            text("UPDATE sprints SET team_id = :team_id WHERE team_id IS NULL"),
            {"team_id": team_id},
        )
        db.commit()
        print(f"Updated {updated.rowcount} sprints with team_id")

    # Update sessions with current_team_id
    if column_exists(db, "sessions", "current_team_id"):
        updated = db.execute(
            text("UPDATE sessions SET current_team_id = :team_id WHERE current_team_id IS NULL"),
            {"team_id": team_id},
        )
        db.commit()
        print(f"Updated {updated.rowcount} sessions with current_team_id")


def run_migration():
    """Run the full migration."""
    print("=" * 50)
    print("Multi-tenancy Migration")
    print("=" * 50)

    # Step 1: Create tables
    print("\nStep 1: Creating/verifying tables...")
    create_tables()

    # Step 2: Add columns if needed (for SQLite which doesn't auto-add)
    print("\nStep 2: Checking columns...")
    db = SessionLocal()
    try:
        # These should be created by create_all, but verify
        tables_to_check = [
            ("projects", "team_id", "VARCHAR(50)"),
            ("risks", "team_id", "VARCHAR(50)"),
            ("issues", "team_id", "VARCHAR(50)"),
            ("sprints", "team_id", "VARCHAR(50)"),
            ("sessions", "current_team_id", "VARCHAR(50)"),
        ]

        for table, column, col_type in tables_to_check:
            if not column_exists(db, table, column):
                add_column_if_not_exists(db, table, column, col_type)
            else:
                print(f"  {table}.{column} exists")

        # Step 3: Migrate existing data
        print("\nStep 3: Migrating existing data...")
        migrate_existing_data(db)

        print("\n" + "=" * 50)
        print("Migration complete!")
        print("=" * 50)

    finally:
        db.close()


if __name__ == "__main__":
    run_migration()
