# Database Migrations Guide

**Status:** 🚧 In Progress

## Overview

ProjectGoat uses a simple migration system for managing database schema changes. This guide covers how migrations work and how to create new ones.

## Migration System

### Current Approach

ProjectGoat uses **custom Python migration scripts** instead of Alembic (a future enhancement recommended in backend-improvements.md).

**Location:** `backend/migrations/`

**Execution:** Migrations run automatically via `backend/init_db.py`

### Existing Migrations

1. **`001_initial_schema.py`** - Core tables (implied, base schema)
2. **`002_add_security_features.py`** - Security tables
   - Adds authentication fields to users table
   - Creates sessions table
   - Creates login_attempts table
3. **`003_add_csrf_to_sessions.py`** - CSRF protection
   - Adds csrf_token column to sessions table

## Running Migrations

### Initialize Database (First Time)

```bash
python backend/init_db.py
```

This script:
1. Creates all tables from models.py
2. Runs all migration files in order
3. Creates default admin user
4. Initializes default data

### Re-initialize Database (Development)

**Warning:** This deletes all data!

```bash
# Delete database file
rm projectgoat.db  # Mac/Linux
del projectgoat.db  # Windows

# Recreate from scratch
python backend/init_db.py
```

## Migration File Structure

### Example Migration

```python
# backend/migrations/002_add_security_features.py
from sqlalchemy import text

def upgrade(engine):
    """
    Apply migration (upgrade database schema)
    """
    with engine.connect() as conn:
        # Add columns to users table
        conn.execute(text("""
            ALTER TABLE users
            ADD COLUMN password_hash TEXT NOT NULL DEFAULT '';
        """))

        # Create new table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """))

        conn.commit()

def downgrade(engine):
    """
    Reverse migration (downgrade database schema)

    Note: Currently not implemented for most migrations
    """
    pass
```

## Creating a New Migration

### Step 1: Create Migration File

Create new file in `backend/migrations/`:

```bash
# Name format: NNN_description.py
# Example:
backend/migrations/004_add_task_tags.py
```

### Step 2: Write Migration Script

```python
# backend/migrations/004_add_task_tags.py
from sqlalchemy import text

def upgrade(engine):
    """
    Add tags column to tasks table
    """
    with engine.connect() as conn:
        # Add tags column (JSON array)
        conn.execute(text("""
            ALTER TABLE tasks
            ADD COLUMN tags TEXT DEFAULT '[]';
        """))

        conn.commit()

def downgrade(engine):
    """
    Remove tags column (optional)
    """
    with engine.connect() as conn:
        # SQLite doesn't support DROP COLUMN directly
        # Would need to recreate table without column
        pass
```

### Step 3: Update init_db.py (if needed)

If adding a new migration to the sequence, ensure `init_db.py` runs it:

```python
# backend/init_db.py
def run_migrations(engine):
    """Run all migration scripts"""
    migrations_dir = Path(__file__).parent / "migrations"

    # List all migration files
    migration_files = sorted(migrations_dir.glob("*.py"))

    for migration_file in migration_files:
        if migration_file.stem == "__init__":
            continue

        # Import and run migration
        # ... (see init_db.py for full implementation)
```

### Step 4: Test Migration

```bash
# Backup database first!
cp projectgoat.db projectgoat.db.backup

# Run init_db.py which executes migrations
python backend/init_db.py

# Verify schema changes
sqlite3 projectgoat.db ".schema tasks"  # or relevant table
```

## SQLite Constraints

### ALTER TABLE Limitations

SQLite has limited `ALTER TABLE` support:

**Supported:**
- ADD COLUMN
- RENAME COLUMN
- RENAME TABLE

**NOT Supported:**
- DROP COLUMN
- MODIFY COLUMN
- ADD CONSTRAINT

### Workaround for Unsupported Operations

To drop a column or modify constraints:

1. Create new table with desired schema
2. Copy data from old table
3. Drop old table
4. Rename new table

```python
def upgrade(engine):
    with engine.connect() as conn:
        # Create new table
        conn.execute(text("""
            CREATE TABLE tasks_new (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL
                -- (columns without the one being removed)
            );
        """))

        # Copy data
        conn.execute(text("""
            INSERT INTO tasks_new (id, title)
            SELECT id, title FROM tasks;
        """))

        # Drop old table
        conn.execute(text("DROP TABLE tasks;"))

        # Rename new table
        conn.execute(text("ALTER TABLE tasks_new RENAME TO tasks;"))

        conn.commit()
```

## Migration Best Practices

### 1. Always Backup First

Before running migrations on production data:

```bash
cp projectgoat.db projectgoat.db.backup
```

### 2. Make Migrations Reversible (when possible)

Implement `downgrade()` function for rollback capability.

### 3. Test on Copy of Data

Never test migrations on production database first.

### 4. Use Transactions

Wrap migrations in transactions for atomicity:

```python
with engine.connect() as conn:
    # All changes here
    conn.commit()
```

### 5. Handle Data Transformations Carefully

When changing column types or constraints, ensure existing data is compatible.

### 6. Document Migration

Add comments explaining what the migration does and why.

## Common Migration Scenarios

### Adding a Column

```python
conn.execute(text("""
    ALTER TABLE tasks
    ADD COLUMN estimated_hours REAL DEFAULT 0;
"""))
```

### Adding a Table

```python
conn.execute(text("""
    CREATE TABLE IF NOT EXISTS task_attachments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
    );
"""))
```

### Creating an Index

```python
conn.execute(text("""
    CREATE INDEX IF NOT EXISTS idx_tasks_assignee
    ON tasks(assignee_id);
"""))
```

### Adding Default Data

```python
conn.execute(text("""
    INSERT INTO app_settings (key, value)
    VALUES ('version', '1.0.0')
    ON CONFLICT (key) DO NOTHING;
"""))
```

## PostgreSQL vs SQLite

### Differences to Be Aware Of

When migrating to PostgreSQL (for production):

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| ALTER TABLE | Limited | Full support |
| AUTO INCREMENT | AUTOINCREMENT | SERIAL |
| Boolean | INTEGER (0/1) | BOOLEAN |
| JSON | TEXT | JSON/JSONB |
| Transactions | Yes | Yes |
| Concurrent writes | Limited | Excellent |

### Writing Portable Migrations

Use SQLAlchemy types instead of raw SQL when possible:

```python
from sqlalchemy import Column, Integer, String, DateTime
from backend.database import Base

# Define new model in models.py
class NewTable(Base):
    __tablename__ = "new_table"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
```

Then in migration:

```python
from backend.models import NewTable
from backend.database import Base

def upgrade(engine):
    # This works with both SQLite and PostgreSQL
    NewTable.__table__.create(engine)
```

## Future: Alembic Migration System

**Recommendation:** Migrate to Alembic for production use.

**Benefits:**
- Automatic migration generation
- Version tracking
- Downgrade support
- Better PostgreSQL support
- Industry standard

See `docs/development/backend-improvements.md` for implementation plan.

## Troubleshooting

### Migration Fails

**Error:** "table already exists"
- **Solution:** Migration already ran. Check database schema.

**Error:** "no such column"
- **Solution:** Ensure migrations run in correct order.

**Error:** "database is locked"
- **Solution:** Close all connections to database. Stop backend server.

### Rollback a Migration

Currently, rollback is manual:

1. Restore from backup
2. Or manually reverse changes via SQL

**Future:** Implement proper `downgrade()` functions

## Development vs Production

### Development

- Use `rm projectgoat.db && python backend/init_db.py` freely
- Test migrations on copies of data
- Experiment with schema changes

### Production

- **NEVER** delete production database
- **ALWAYS** backup before migrations
- **TEST** migrations on staging environment
- Have rollback plan ready

## Testing Migrations

### Manual Testing

```bash
# 1. Create test database
cp projectgoat.db test-migration.db

# 2. Modify database path in migration script
# 3. Run migration
python -c "
from backend.database import engine
from backend.migrations.004_example import upgrade
upgrade(engine)
"

# 4. Verify schema
sqlite3 test-migration.db ".schema"

# 5. Verify data integrity
sqlite3 test-migration.db "SELECT * FROM tasks LIMIT 5;"
```

### Automated Testing

*TODO: Add pytest tests for migrations*

---

**See Also:**
- [Backend Improvements](../development/backend-improvements.md) - Alembic migration plan
- [Database Schema](../reference/database-schema.md) - Current schema documentation
- [Testing Guide](testing.md) - Testing best practices
