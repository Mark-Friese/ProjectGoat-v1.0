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
├── frontend/               # Copy from build/
│   ├── index.html
│   └── assets/
├── backend/                # Python backend files
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   └── init_db.py
├── run.py                 # Startup script
├── requirements.txt       # Python dependencies
└── README.md             # Quick start guide
```

#### Copy Frontend Files
```bash
# Copy built frontend
xcopy build\* ProjectGoat-Deployment\frontend\ /E /I /Y
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

```python
"""
ProjectGoat Startup Script
Starts FastAPI backend and serves frontend
"""
import uvicorn
import os
from pathlib import Path

# Configuration
HOST = "127.0.0.1"  # localhost only
PORT = 8000
FRONTEND_DIR = Path(__file__).parent / "frontend"
BACKEND_DIR = Path(__file__).parent / "backend"

# Add backend to Python path
import sys
sys.path.insert(0, str(BACKEND_DIR))

def main():
    print("=" * 50)
    print("ProjectGoat by TeamGoat")
    print("=" * 50)
    print(f"Starting server on http://{HOST}:{PORT}")
    print("Press CTRL+C to stop")
    print("=" * 50)

    # Start uvicorn server
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,  # No reload in production
        log_level="info"
    )

if __name__ == "__main__":
    main()
```

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

## File: backend/main.py (Updated for Static Files)

Add static file serving to FastAPI:

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI(title="ProjectGoat API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# ... all other API routes ...

# Serve frontend static files
frontend_path = Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
```

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
2. Verify frontend files copied correctly
3. Check backend logs for errors
4. Ensure `index.html` is in `frontend/` directory

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
- Single-user application
- Localhost only (127.0.0.1)
- No authentication required
- No external network access
- All data stored locally

### Future Enhancements
If multi-user support needed:
- Add user authentication
- Implement role-based access
- Add HTTPS
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
│  frontend/      - Web interface         │
│                                         │
│ Backup:                                 │
│  copy projectgoat.db backup.db          │
└─────────────────────────────────────────┘
```
