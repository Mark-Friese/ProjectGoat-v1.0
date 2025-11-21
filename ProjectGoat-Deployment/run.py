"""
ProjectGoat Startup Script
Starts FastAPI backend server
"""
import uvicorn
import sys
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Configuration
HOST = "127.0.0.1"  # localhost only (change to "0.0.0.0" to allow network access)
PORT = 8000

def main():
    print("=" * 60)
    print("  ProjectGoat by TeamGoat")
    print("=" * 60)
    print(f"  Backend API: http://{HOST}:{PORT}/api")
    print(f"  API Docs:    http://{HOST}:{PORT}/docs")
    print(f"  Health:      http://{HOST}:{PORT}/api/health")
    print("=" * 60)
    print("  Press CTRL+C to stop the server")
    print("=" * 60)
    print()

    try:
        # Start uvicorn server
        uvicorn.run(
            "main:app",
            host=HOST,
            port=PORT,
            reload=False,  # Set to True for development auto-reload
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("  Server stopped")
        print("=" * 60)

if __name__ == "__main__":
    main()
