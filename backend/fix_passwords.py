"""
Fix password hashes - convert from SHA-256 to bcrypt
"""

import sqlite3

import bcrypt

DATABASE_PATH = "../projectgoat.db"


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def fix_passwords():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    print("Fixing password hashes...")

    # Get all users
    cursor.execute("SELECT id, email, name FROM users")
    users = cursor.fetchall()

    default_password = "password123"
    hashed = hash_password(default_password)

    # Update all users with bcrypt hashed password
    for user_id, email, name in users:
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed, user_id))
        print(f"  Updated password for: {name} ({email})")

    conn.commit()
    conn.close()

    print("\nDone! All passwords have been re-hashed with bcrypt.")
    print(f"Default password: {default_password}")


if __name__ == "__main__":
    fix_passwords()
