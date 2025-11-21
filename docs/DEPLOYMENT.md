# ProjectGoat - Deployment Guide

## Overview
This guide covers deploying ProjectGoat to your work laptop with restricted environment.

## Prerequisites

### Work Laptop Requirements
- **Python 3.9+** (required)
- **Web browser** (any modern browser)
- **200MB disk space** (for application and database)
- **No Node.js required** on work laptop

### Development Machine Requirements (one-time)
- Node.js (for building frontend)
- Python 3.9+ (for testing backend)

## Deployment Process

### Step 1: Build Frontend (Development Machine)

```bash
# Navigate to project directory
cd C:\Users\mfrie\Projects\TeamGoat\ProjectGoat

# Install dependencies (if not done)
npm install

# Create production build
npm run build
```

This creates a `build/` directory with static files:
```
build/
├── index.html
├── assets/
│   ├── index-[hash].js
│   ├── index-[hash].css
│   └── logo.png
└── ...
```

### Step 2: Prepare Backend (Development Machine)

No build step needed - Python files run as-is.

### Step 3: Create Deployment Package

Create folder structure:
```
ProjectGoat-Deployment/
├── build/                  # Copy from build/ (906 KB production bundle)
│   ├── index.html
│   └── assets/
│       ├── index-[hash].js
│       └── index-[hash].css
├── backend/                # Python backend files
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── auth.py
│   ├── csrf.py
│   ├── rate_limiter.py
│   └── init_db.py
├── run.py                 # Startup script
├── requirements.txt       # Python dependencies
└── README.md             # Quick start guide
```

#### Copy Frontend Files
```bash
# Copy built frontend (production bundle)
xcopy build\* ProjectGoat-Deployment\build\ /E /I /Y
```

#### Copy Backend Files
```bash
# Copy backend files
xcopy backend\* ProjectGoat-Deployment\backend\ /E /I /Y
copy run.py ProjectGoat-Deployment\
copy requirements.txt ProjectGoat-Deployment\
```

### Step 4: Transfer to Work Laptop

Options:
1. **USB Drive** - Copy folder to USB, transfer to work laptop
2. **Network Share** - Copy via internal network share
3. **Email** - Zip and email (if size permits and allowed)
4. **Git** - Push to internal Git server, clone on work laptop

```bash
# Option: Create zip file
powershell Compress-Archive -Path ProjectGoat-Deployment -DestinationPath ProjectGoat.zip
```

### Step 5: Setup on Work Laptop

#### 5.1 Extract Files
```bash
# If using zip
powershell Expand-Archive -Path ProjectGoat.zip -DestinationPath C:\ProjectGoat
cd C:\ProjectGoat
```

#### 5.2 Verify Python Installation
```bash
python --version
# Should show Python 3.9 or higher
```

If Python not installed:
- Request installation from IT
- Or use portable Python (if allowed)

#### 5.3 Install Python Dependencies
```bash
# Install required packages
pip install -r requirements.txt

# Packages installed:
# - fastapi
# - sqlalchemy
# - pydantic
# - uvicorn[standard]
```

If `pip install` fails (firewall/proxy):
```bash
# Option 1: Use internal PyPI mirror
pip install -r requirements.txt --index-url http://internal-pypi

# Option 2: Install from wheels (pre-downloaded)
pip install --no-index --find-links=./wheels -r requirements.txt
```

#### 5.4 Initialize Database
```bash
# Create and populate database
python backend/init_db.py
```

This creates `projectgoat.db` with initial data.

#### 5.5 Start Application
```bash
# Start server
python run.py
```

Expected output:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://localhost:8000
```

#### 5.6 Access Application
Open web browser and navigate to:
```
http://localhost:8000
```

The app should load immediately!

---

## File: run.py (Startup Script)

The startup script is already configured at the project root:

```python
"""
ProjectGoat Startup Script
Starts FastAPI backend server with integrated frontend serving
"""
import uvicorn
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def main():
    """Start the ProjectGoat application server"""
    print("\n" + "=" * 60)
    print("  ProjectGoat by TeamGoat")
    print("=" * 60)
    print("  Backend API: http://127.0.0.1:8000/api")
    print("  API Docs:    http://127.0.0.1:8000/docs")
    print("  Health:      http://127.0.0.1:8000/api/health")
    print("=" * 60)
    print("  Press CTRL+C to stop the server")
    print("=" * 60 + "\n")

    # Start uvicorn server
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
```

**Key features:**
- Serves both API (on `/api/*`) and frontend (on `/`) from single process
- No Node.js required - uses FastAPI's static file serving
- Automatically detects and serves from `build/` directory
- Localhost only for security (127.0.0.1)

---

## File: requirements.txt

```
fastapi==0.115.0
sqlalchemy==2.0.36
pydantic==2.10.0
uvicorn[standard]==0.32.1
python-multipart==0.0.20
```

---

## File: backend/main.py (Static File Serving Configuration)

The backend is configured to serve the production build automatically. This section is already implemented at the end of `backend/main.py`:

```python
# ==================== Serve Frontend (Production) ====================

# Check if build directory exists (production mode)
BUILD_PATH = Path(__file__).parent.parent / "build"
if BUILD_PATH.exists():
    from fastapi.responses import FileResponse

    # Mount static assets (JS, CSS, images, etc.)
    app.mount("/assets", StaticFiles(directory=str(BUILD_PATH / "assets")), name="assets")

    # Serve static files from build root (favicon, logo, etc.)
    @app.get("/favicon.ico")
    async def favicon():
        return FileResponse(BUILD_PATH / "favicon.ico")

    @app.get("/project-goat-logo.svg")
    async def logo():
        logo_path = BUILD_PATH / "project-goat-logo.svg"
        if logo_path.exists():
            return FileResponse(logo_path)
        raise HTTPException(status_code=404, detail="Logo not found")

    # Catch-all route for SPA - must be last!
    # This serves index.html for all non-API routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't intercept API routes
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")

        # Serve index.html for all other routes (SPA routing)
        return FileResponse(BUILD_PATH / "index.html")
```

This configuration:
- Serves static assets from `/assets` directory
- Handles SPA routing by serving `index.html` for all non-API routes
- Protects API routes from being caught by the catch-all
- Only activates when `build/` directory exists

---

## Troubleshooting

### Problem: Python not found
**Solution:** Install Python 3.9+ or request from IT

### Problem: pip install fails (no internet)
**Solution:**
1. Download wheel files on dev machine:
   ```bash
   pip download -r requirements.txt -d ./wheels
   ```
2. Copy `wheels/` folder to deployment package
3. Install offline:
   ```bash
   pip install --no-index --find-links=./wheels -r requirements.txt
   ```

### Problem: Port 8000 already in use
**Solution:** Change port in `run.py`:
```python
PORT = 8001  # or any available port
```

### Problem: Database file permission error
**Solution:** Ensure write permissions in application directory

### Problem: Frontend shows blank page
**Solutions:**
1. Check browser console (F12) for errors
2. Verify frontend files copied correctly to `build/` directory
3. Check backend logs for errors
4. Ensure `index.html` and `assets/` folder are in `build/` directory
5. Verify `build/` directory is in same location as `backend/` and `run.py`

### Problem: API calls fail (CORS error)
**Solution:** Update CORS origins in `main.py` to match your URL

### Problem: Application slow to start
**Solution:** Normal - first start initializes database and loads data

---

## Daily Usage

### Starting the App
```bash
cd C:\ProjectGoat
python run.py
```

### Stopping the App
Press `CTRL+C` in the terminal

### Accessing the App
Open browser: `http://localhost:8000`

---

## Data Management

### Backup Database
```bash
# Copy database file
copy projectgoat.db projectgoat_backup_2025-11-18.db
```

### Restore Database
```bash
# Replace with backup
copy projectgoat_backup_2025-11-18.db projectgoat.db
```

### Reset Database
```bash
# Delete and reinitialize
del projectgoat.db
python backend/init_db.py
```

---

## Updates & Maintenance

### Updating the App
1. Build new version on dev machine
2. Copy updated files to work laptop
3. Restart application
4. Database persists automatically

### Updating Data
- All changes saved automatically to database
- No manual save required
- Data persists across restarts

---

## Performance Tips

### For Better Performance
1. Close browser tabs when not using
2. Regularly backup database
3. Keep application directory on local drive (not network)
4. Use latest Python version available

---

## Security Notes

### Current Security Model

- **Authentication:** Session-based authentication with bcrypt password hashing
- **Default Credentials:**
  - Email: `sarah@example.com`
  - Password: `password123`
  - **Important:** Change password immediately after first login
- **Session Management:**
  - Idle timeout: 30 minutes of inactivity
  - Absolute timeout: 8 hours from login
  - Session warning: 2 minutes before timeout
- **CSRF Protection:** All state-changing operations protected
- **Rate Limiting:** 5 failed login attempts per 15 minutes
- **Network:** Localhost only (127.0.0.1), no external network access
- **Data Storage:** All data stored locally in SQLite database

### Security Best Practices

1. **Change Default Password:** Immediately change the default password on first login
2. **Strong Passwords:** Use passwords with 8+ characters, mixed case, numbers, and special characters
3. **Regular Backups:** Back up `projectgoat.db` regularly to prevent data loss
4. **Local Access Only:** Do not expose the application to external networks
5. **Keep Updated:** Keep Python and dependencies updated for security patches

### Future Enhancements

If multi-user or network deployment needed:

- Add HTTPS/TLS encryption
- Implement additional role-based permissions
- Add OAuth/SSO integration
- Enhanced audit logging
- Network deployment considerations

---

## Support & Documentation

### Help Resources
- [REQUIREMENTS.md](./REQUIREMENTS.md) - Feature documentation
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Technical design
- [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) - Database structure
- [API_ENDPOINTS.md](./API_ENDPOINTS.md) - API reference

### Common Tasks
- View tasks: Navigate to Kanban or List view
- Create task: Click "New Task" button
- Update task: Click on any task card
- Switch projects: Use project selector in sidebar
- View team: Click "Team Members" in sidebar

---

## System Requirements Summary

| Component | Requirement | Size |
|-----------|-------------|------|
| Python | 3.9+ | ~100MB |
| Application | Static files + Python code | ~50MB |
| Database | SQLite | ~5-50MB (grows with data) |
| Memory | RAM during operation | ~100MB |
| Disk Space | Total recommended | 200MB |

---

## Quick Reference Card

```
┌─────────────────────────────────────────┐
│      ProjectGoat Quick Reference         │
├─────────────────────────────────────────┤
│ Start: python run.py                    │
│ Stop:  CTRL+C                           │
│ URL:   http://localhost:8000            │
│                                         │
│ Files:                                  │
│  projectgoat.db - Your data             │
│  backend/       - Server code           │
│  build/         - Web interface (906KB) │
│  run.py         - Startup script        │
│                                         │
│ Backup:                                 │
│  copy projectgoat.db backup.db          │
└─────────────────────────────────────────┘
```
