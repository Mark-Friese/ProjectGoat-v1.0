"""
Database configuration and session management

Supports dual-mode deployment:
- SQLite for local/laptop deployment (default)
- PostgreSQL for online/production deployment
"""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

try:
    from backend.config import settings
except ImportError:
    # Fallback for imports from different contexts
    from config import settings

# Get project root directory (one level up from backend)
PROJECT_ROOT = Path(__file__).parent.parent

# Determine database URL
# Priority: TEST_MODE > Environment Variable (DATABASE_URL) > Default (SQLite)
if os.getenv("TEST_MODE") == "e2e":
    # E2E test mode: use test database
    DATABASE_PATH = PROJECT_ROOT / "projectgoat-test.db"
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
else:
    # Use DATABASE_URL from settings (environment variable or default)
    DATABASE_URL = settings.DATABASE_URL

    # If using default SQLite, ensure it's in project root
    if DATABASE_URL == "sqlite:///projectgoat.db":
        DATABASE_PATH = PROJECT_ROOT / "projectgoat.db"
        DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create engine with database-specific configuration
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},  # Needed for SQLite
        echo=False  # Set to True for SQL query logging
    )
else:
    # PostgreSQL configuration
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before using
        pool_size=5,  # Number of connections to maintain
        max_overflow=10,  # Additional connections when pool is exhausted
        echo=False  # Set to True for SQL query logging
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# Dependency to get database session
def get_db():
    """
    Dependency function to get database session.
    Used with FastAPI's Depends.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
