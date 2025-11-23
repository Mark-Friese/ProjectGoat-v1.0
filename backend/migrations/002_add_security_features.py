"""
Database Migration 002: Add Comprehensive Security Features
Adds tables and columns for:
- Rate limiting and login attempt tracking
- Role-based permissions
- Admin audit logging
- Enhanced session management
- User account security features
"""

import sqlite3
from datetime import datetime
from pathlib import Path

# Get project root and database path
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATABASE_PATH = PROJECT_ROOT / "projectgoat.db"


def migrate():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    print("=" * 60)
    print("Running Migration 002: Security Features")
    print("=" * 60)

    # ========================================
    # 1. Create login_attempts table
    # ========================================
    print("\n1. Creating login_attempts table...")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS login_attempts (
            id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            attempted_at DATETIME NOT NULL,
            success BOOLEAN NOT NULL DEFAULT 0,
            failure_reason TEXT
        )
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_login_attempts_email
        ON login_attempts(email)
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_login_attempts_attempted_at
        ON login_attempts(attempted_at)
    """
    )
    print("   [OK] login_attempts table created")

    # ========================================
    # 2. Create user_permissions table
    # ========================================
    print("\n2. Creating user_permissions table...")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_permissions (
            id TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            resource TEXT NOT NULL,
            action TEXT NOT NULL,
            allowed BOOLEAN NOT NULL DEFAULT 1
        )
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_user_permissions_role
        ON user_permissions(role)
    """
    )

    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_user_permissions_unique
        ON user_permissions(role, resource, action)
    """
    )
    print("   [OK] user_permissions table created")

    # ========================================
    # 3. Create audit_log table
    # ========================================
    print("\n3. Creating audit_log table...")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            target_user_id TEXT,
            details TEXT,
            ip_address TEXT,
            timestamp DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_audit_log_user
        ON audit_log(user_id)
    """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp
        ON audit_log(timestamp)
    """
    )
    print("   [OK] audit_log table created")

    # ========================================
    # 4. Add new columns to users table
    # ========================================
    print("\n4. Adding new columns to users table...")

    new_user_columns = [
        ("is_active", "BOOLEAN NOT NULL DEFAULT 1"),
        ("must_change_password", "BOOLEAN NOT NULL DEFAULT 0"),
        ("password_changed_at", "DATETIME"),
        ("created_at", "DATETIME"),
        ("last_login_at", "DATETIME"),
        ("failed_login_attempts", "INTEGER DEFAULT 0"),
        ("account_locked_until", "DATETIME"),
    ]

    # Check which columns already exist
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    for column_name, column_type in new_user_columns:
        if column_name not in existing_columns:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
            print(f"   [OK] Added column: {column_name}")
        else:
            print(f"   - Column already exists: {column_name}")

    # Set created_at for existing users if not set
    cursor.execute(
        """
        UPDATE users
        SET created_at = ?
        WHERE created_at IS NULL
    """,
        (datetime.now().isoformat(),),
    )

    # ========================================
    # 5. Add new columns to sessions table
    # ========================================
    print("\n5. Adding new columns to sessions table...")

    new_session_columns = [
        ("is_active", "BOOLEAN NOT NULL DEFAULT 1"),
        ("last_activity_at", "DATETIME"),
        ("ip_address", "TEXT"),
        ("user_agent", "TEXT"),
    ]

    # Check which columns already exist
    cursor.execute("PRAGMA table_info(sessions)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    for column_name, column_type in new_session_columns:
        if column_name not in existing_columns:
            cursor.execute(f"ALTER TABLE sessions ADD COLUMN {column_name} {column_type}")
            print(f"   [OK] Added column: {column_name}")
        else:
            print(f"   - Column already exists: {column_name}")

    # Set last_activity_at for existing sessions
    cursor.execute(
        """
        UPDATE sessions
        SET last_activity_at = last_accessed
        WHERE last_activity_at IS NULL
    """
    )

    conn.commit()
    conn.close()

    print("\n" + "=" * 60)
    print("Migration 002 completed successfully!")
    print("=" * 60)
    print("\nNew tables created:")
    print("  - login_attempts (for rate limiting)")
    print("  - user_permissions (for RBAC)")
    print("  - audit_log (for admin actions)")
    print("\nEnhanced tables:")
    print("  - users (security & account management)")
    print("  - sessions (activity tracking)")
    print("=" * 60)


if __name__ == "__main__":
    migrate()
