"""
Database configuration and session management
"""
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get project root directory (one level up from backend)
PROJECT_ROOT = Path(__file__).parent.parent

# Use test database if TEST_MODE environment variable is set
if os.getenv("TEST_MODE") == "e2e":
    DATABASE_PATH = PROJECT_ROOT / "projectgoat-test.db"
else:
    DATABASE_PATH = PROJECT_ROOT / "projectgoat.db"

# SQLite database file
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite
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
