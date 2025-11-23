"""
Database Migration 003: Add CSRF token to sessions table
"""

import sqlite3
from pathlib import Path

# Get project root and database path
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATABASE_PATH = PROJECT_ROOT / "projectgoat.db"


def migrate():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    print("=" * 60)
    print("Running Migration 003: Add CSRF token to sessions")
    print("=" * 60)

    # Check if csrf_token column already exists
    cursor.execute("PRAGMA table_info(sessions)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    if "csrf_token" not in existing_columns:
        cursor.execute("ALTER TABLE sessions ADD COLUMN csrf_token TEXT")
        print("\n[OK] Added csrf_token column to sessions table")
    else:
        print("\n[OK] csrf_token column already exists in sessions table")

    conn.commit()
    conn.close()

    print("=" * 60)
    print("Migration 003 completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    migrate()
