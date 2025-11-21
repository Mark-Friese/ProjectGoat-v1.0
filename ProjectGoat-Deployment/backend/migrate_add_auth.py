"""
Database Migration: Add Authentication Support
Adds app_settings, sessions tables and password_hash to users table
"""
import sqlite3
from datetime import datetime
import hashlib

DATABASE_PATH = "../projectgoat.db"


def hash_password(password: str) -> str:
    """Simple password hashing using SHA-256 (will be replaced with bcrypt)"""
    return hashlib.sha256(password.encode()).hexdigest()


def migrate():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    print("Starting authentication migration...")

    try:
        # 1. Create app_settings table
        print("Creating app_settings table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at DATETIME NOT NULL
            )
        """)

        # 2. Create sessions table
        print("Creating sessions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                expires_at DATETIME NOT NULL,
                last_accessed DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # 3. Add password_hash column to users table
        print("Adding password_hash column to users table...")
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("  Column already exists, skipping...")
            else:
                raise

        # 4. Set default passwords for existing users
        print("Setting default passwords for existing users...")
        cursor.execute("SELECT id, name FROM users WHERE password_hash IS NULL")
        users_without_passwords = cursor.fetchall()

        default_password = "password123"  # Users should change this on first login
        hashed = hash_password(default_password)

        for user_id, name in users_without_passwords:
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (hashed, user_id)
            )
            print(f"  Set password for user: {name} (ID: {user_id})")

        # 5. Set default current user (first admin user)
        print("Setting default current user...")
        cursor.execute("SELECT id FROM users WHERE role = 'admin' LIMIT 1")
        admin_user = cursor.fetchone()
        if admin_user:
            cursor.execute(
                "INSERT OR REPLACE INTO app_settings (key, value, updated_at) VALUES (?, ?, ?)",
                ("current_user_id", admin_user[0], datetime.now().isoformat())
            )
            print(f"  Set current user to: {admin_user[0]}")

        conn.commit()
        print("\n✅ Migration completed successfully!")
        print("\n⚠️  IMPORTANT:")
        print(f"   Default password for all users: {default_password}")
        print("   Users should change their password after first login")
        print("   This will be replaced with bcrypt hashing in the next step")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
