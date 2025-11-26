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
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

# Import database and models
try:
    from backend.database import SessionLocal, engine
    from backend.models import Team, TeamMembership, User
except ImportError:
    from database import SessionLocal, engine
    from models import Team, TeamMembership, User


DEFAULT_TEAM_NAME = "My Team"
DEFAULT_TEAM_ID = "default-team"


def is_postgres():
    """Check if we're using PostgreSQL."""
    return "postgresql" in str(engine.url)


def column_exists_check(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table using a fresh connection."""
    db = SessionLocal()
    try:
        if is_postgres():
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
        else:
            # SQLite
            result = db.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
            return any(row[1] == column_name for row in result)
    except Exception as e:
        print(f"  Error checking column {table_name}.{column_name}: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def column_exists(db, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    try:
        if is_postgres():
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
        else:
            # SQLite
            result = db.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
            return any(row[1] == column_name for row in result)
    except Exception:
        db.rollback()
        return False


def table_exists(db, table_name: str) -> bool:
    """Check if a table exists."""
    try:
        if is_postgres():
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
        else:
            # SQLite
            result = db.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
                {"name": table_name},
            ).fetchone()
            return result is not None
    except Exception:
        db.rollback()
        return False


def add_column_if_not_exists(table_name: str, column_name: str, column_type: str):
    """Add a column to a table if it doesn't exist. Uses fresh connection."""
    # Check with fresh connection
    if column_exists_check(table_name, column_name):
        print(f"  Column {table_name}.{column_name} already exists, skipping")
        return False

    # Add column with fresh connection
    db = SessionLocal()
    try:
        db.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"))
        db.commit()
        print(f"  Added column {table_name}.{column_name}")
        return True
    except (OperationalError, ProgrammingError) as e:
        # Column might already exist (race condition) or other error
        error_str = str(e).lower()
        if "already exists" in error_str or "duplicate column" in error_str:
            print(f"  Column {table_name}.{column_name} already exists")
        else:
            print(f"  Error adding column {table_name}.{column_name}: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def create_tables():
    """Create new tables using SQLAlchemy metadata."""
    from models import Base

    try:
        Base.metadata.create_all(bind=engine)
        print("Created/verified all tables")
    except Exception as e:
        print(f"Note: create_all encountered: {e}")
        print("Continuing with migration...")


def migrate_existing_data():
    """Migrate existing data to use teams. Uses fresh connections for each operation."""
    db = SessionLocal()
    try:
        # Check if default team already exists
        existing_team = db.execute(
            text("SELECT id FROM teams WHERE id = :id"), {"id": DEFAULT_TEAM_ID}
        ).fetchone()

        if existing_team:
            print(f"Default team '{DEFAULT_TEAM_ID}' already exists")
            team_id = DEFAULT_TEAM_ID
        else:
            # Create default team
            now = datetime.now(timezone.utc).isoformat()
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
                text(
                    "SELECT id FROM team_memberships WHERE team_id = :team_id AND user_id = :user_id"
                ),
                {"team_id": team_id, "user_id": user_id},
            ).fetchone()

            if existing:
                continue

            # Create membership
            membership_id = f"tm_{uuid.uuid4().hex[:8]}"
            now = datetime.now(timezone.utc).isoformat()
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
    except Exception as e:
        print(f"Error in team/membership migration: {e}")
        db.rollback()
    finally:
        db.close()

    # Update data with team_id - use fresh connections for each table
    tables_to_update = [
        ("projects", "team_id"),
        ("risks", "team_id"),
        ("issues", "team_id"),
        ("sprints", "team_id"),
        ("sessions", "current_team_id"),
    ]

    for table_name, column_name in tables_to_update:
        if column_exists_check(table_name, column_name):
            db = SessionLocal()
            try:
                updated = db.execute(
                    text(
                        f"UPDATE {table_name} SET {column_name} = :team_id WHERE {column_name} IS NULL"
                    ),
                    {"team_id": DEFAULT_TEAM_ID},
                )
                db.commit()
                print(f"Updated {updated.rowcount} {table_name} with {column_name}")
            except Exception as e:
                print(f"Error updating {table_name}: {e}")
                db.rollback()
            finally:
                db.close()


def run_migration():
    """Run the full migration."""
    print("=" * 50)
    print("Multi-tenancy Migration")
    print("=" * 50)

    # Step 1: Create tables
    print("\nStep 1: Creating/verifying tables...")
    create_tables()

    # Step 2: Add columns if needed (for existing tables that don't have them)
    print("\nStep 2: Checking/adding columns...")
    tables_to_check = [
        ("projects", "team_id", "VARCHAR(50)"),
        ("risks", "team_id", "VARCHAR(50)"),
        ("issues", "team_id", "VARCHAR(50)"),
        ("sprints", "team_id", "VARCHAR(50)"),
        ("sessions", "current_team_id", "VARCHAR(50)"),
    ]

    for table, column, col_type in tables_to_check:
        add_column_if_not_exists(table, column, col_type)

    # Step 3: Migrate existing data
    print("\nStep 3: Migrating existing data...")
    migrate_existing_data()

    print("\n" + "=" * 50)
    print("Migration complete!")
    print("=" * 50)


if __name__ == "__main__":
    run_migration()
