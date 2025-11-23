"""
Configuration module for ProjectGoat

Supports dual-mode deployment:
- Local (SQLite, localhost, development)
- Online (PostgreSQL, production, cloud hosting)

All settings use environment variables with sensible defaults for laptop deployment.
"""

import os
from typing import List

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Settings:
    """Application settings with environment-based configuration"""

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Server configuration
    HOST: str = os.getenv("HOST", "127.0.0.1")  # localhost for local deployment
    PORT: int = int(os.getenv("PORT", "8000"))

    # Database configuration
    # Default: SQLite (no admin rights needed, file-based)
    # Production: Set DATABASE_URL to PostgreSQL connection string
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///projectgoat.db")

    # CORS configuration
    # Always include localhost origins for development and local deployment
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8000",
    ]

    # Add production origin if specified
    production_origin = os.getenv("PRODUCTION_ORIGIN")
    if production_origin:
        ALLOWED_ORIGINS.append(production_origin)

    # Add custom origins from comma-separated list
    custom_origins = os.getenv("CUSTOM_ORIGINS", "")
    if custom_origins:
        ALLOWED_ORIGINS.extend(custom_origins.split(","))

    # Security settings
    # Secure cookies only in production (HTTPS required)
    SECURE_COOKIES: bool = ENVIRONMENT == "production"

    # Session configuration
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "development-secret-change-in-production")

    # Utility properties
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database"""
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def is_postgres(self) -> bool:
        """Check if using PostgreSQL database"""
        return self.DATABASE_URL.startswith("postgresql") or self.DATABASE_URL.startswith(
            "postgres"
        )

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.ENVIRONMENT == "production"

    def validate(self) -> None:
        """Validate configuration for production deployment"""
        if self.is_production:
            # Ensure SESSION_SECRET has been changed from default
            if self.SESSION_SECRET == "development-secret-change-in-production":
                raise ValueError(
                    "SESSION_SECRET must be changed in production! "
                    "Generate a secure secret with: "
                    'python -c "import secrets; print(secrets.token_urlsafe(32))"'
                )

            # Warn if using SQLite in production (not recommended for multi-user)
            if self.is_sqlite:
                import warnings

                warnings.warn(
                    "Using SQLite in production is not recommended for multi-user scenarios. "
                    "Consider using PostgreSQL by setting DATABASE_URL environment variable.",
                    UserWarning,
                )

    def __repr__(self) -> str:
        """String representation for debugging"""
        db_type = "SQLite" if self.is_sqlite else "PostgreSQL" if self.is_postgres else "Unknown"
        return (
            f"Settings("
            f"environment={self.ENVIRONMENT}, "
            f"database={db_type}, "
            f"host={self.HOST}:{self.PORT})"
        )


# Global settings instance
settings = Settings()

# Validate configuration on startup
settings.validate()
