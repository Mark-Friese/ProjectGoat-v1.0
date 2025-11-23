"""
ProjectGoat Startup Script
Starts FastAPI backend server with environment-based configuration

Supports dual-mode deployment:
- Local (SQLite, localhost, development)
- Online (PostgreSQL, production, cloud hosting)
"""
import uvicorn
import sys
from pathlib import Path

# Fix Windows console encoding for Unicode output (emojis)
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import settings after path setup
from config import settings


def main():
    # Determine database type for display
    if settings.is_sqlite:
        db_type = "SQLite (Local)"
    elif settings.is_postgres:
        db_type = "PostgreSQL (Production)"
    else:
        db_type = "Unknown"

    print("=" * 60)
    print("  🐐 ProjectGoat by TeamGoat")
    print("=" * 60)
    print(f"  Environment:  {settings.ENVIRONMENT}")
    print(f"  Database:     {db_type}")
    print(f"  Server:       http://{settings.HOST}:{settings.PORT}")
    print(f"  Backend API:  http://{settings.HOST}:{settings.PORT}/api")
    print(f"  API Docs:     http://{settings.HOST}:{settings.PORT}/docs")
    print(f"  Health Check: http://{settings.HOST}:{settings.PORT}/api/health")
    print("=" * 60)
    print("  Press CTRL+C to stop the server")
    print("=" * 60)
    print()

    try:
        # Start uvicorn server
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.is_development,  # Auto-reload in development
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("  Server stopped")
        print("=" * 60)

if __name__ == "__main__":
    main()
