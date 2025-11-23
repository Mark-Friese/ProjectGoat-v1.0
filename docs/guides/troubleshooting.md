# Troubleshooting Guide

**Status:** 🚧 In Progress

## Common Issues and Solutions

This guide covers common problems you might encounter when developing or deploying ProjectGoat.

---

## Installation & Setup Issues

### Python Version Mismatch

**Symptom:** `SyntaxError` or incompatibility errors

**Cause:** Wrong Python version

**Solution:**
```bash
# Check Python version
python --version  # Should be 3.9+ (3.13 recommended)

# Use correct version explicitly
python3.13 --version
python3.13 -m venv .venv
```

### Virtual Environment Not Activated

**Symptom:** `ModuleNotFoundError: No module named 'fastapi'`

**Cause:** Virtual environment not activated

**Solution:**
```bash
# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

# Verify activation (should show .venv in prompt)
which python  # Should show path to .venv/bin/python
```

### Dependencies Not Installed

**Symptom:** Import errors for packages

**Cause:** Dependencies not installed or outdated

**Solution:**
```bash
# Install backend dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install -r requirements-dev.txt

# Install frontend dependencies
npm install

# Update dependencies
pip install --upgrade -r requirements.txt
npm update
```

---

## Database Issues

### Database Locked Error

**Symptom:** `sqlite3.OperationalError: database is locked`

**Cause:** Multiple processes accessing SQLite database

**Solutions:**
1. Close all connections:
   - Stop backend server
   - Close any SQLite browsers
   - Wait a few seconds

2. For development:
   ```bash
   # Delete and recreate
   rm projectgoat.db
   python backend/init_db.py
   ```

3. For production: Use PostgreSQL instead of SQLite

### Database Not Found

**Symptom:** `no such table: users` or similar

**Cause:** Database not initialized

**Solution:**
```bash
python backend/init_db.py
```

### Migration Errors

**Symptom:** Migration fails during init_db.py

**Cause:** Schema conflicts or migration issues

**Solution:**
```bash
# Backup first
cp projectgoat.db projectgoat.db.backup

# Start fresh (development only!)
rm projectgoat.db
python backend/init_db.py
```

See [Migrations Guide](migrations.md) for more details.

---

## Server Issues

### Port Already in Use

**Symptom:** `OSError: [Errno 48] Address already in use`

**Cause:** Another process using port 3000 or 8000

**Solution:**

**Windows:**
```bash
# Find process using port 8000 (backend)
netstat -ano | findstr :8000

# Find process using port 3000 (frontend)
netstat -ano | findstr :3000

# Kill process (use PID from above)
taskkill /PID <PID> /F
```

**Mac/Linux:**
```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Find and kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Backend Won't Start

**Symptoms:** Server crashes immediately or won't respond

**Troubleshooting Steps:**

1. Check Python version:
   ```bash
   python --version  # Should be 3.9+
   ```

2. Check dependencies:
   ```bash
   pip list | grep fastapi
   pip install --upgrade fastapi uvicorn
   ```

3. Check database:
   ```bash
   ls -la projectgoat.db  # Should exist
   python backend/init_db.py  # Reinitialize if needed
   ```

4. Check for errors:
   ```bash
   python run.py  # Look at error output
   ```

5. Check environment variables:
   ```bash
   # Verify .env or environment settings
   cat .env
   ```

### Frontend Won't Start

**Symptoms:** Vite server crashes or won't compile

**Troubleshooting Steps:**

1. Check Node version:
   ```bash
   node --version  # Should be 16+
   npm --version
   ```

2. Clear cache and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

3. Check for TypeScript errors:
   ```bash
   npx tsc --noEmit
   ```

4. Check Vite config:
   ```bash
   cat vite.config.ts  # Verify configuration
   ```

---

## Authentication & Session Issues

### Repeatedly Logged Out

**Symptoms:** Session expires too quickly or immediately

**Causes & Solutions:**

1. **System clock incorrect:**
   - Check system time is accurate
   - Sessions use timestamps

2. **Backend not running:**
   - Verify backend server is running
   - Check `http://localhost:8000/api/health`

3. **Session expired legitimately:**
   - Idle timeout: 30 minutes
   - Absolute timeout: 8 hours
   - Solution: Log in again

4. **Clear stale session:**
   ```javascript
   // In browser console
   localStorage.clear();
   // Then refresh page and log in
   ```

### CSRF Token Errors

**Symptom:** `403 Forbidden: Invalid CSRF token`

**Causes & Solutions:**

1. **Not logged in:**
   - Ensure you're logged in first
   - CSRF tokens are session-specific

2. **Session expired:**
   - Log out and log back in

3. **Database migrations not run:**
   ```bash
   python backend/init_db.py
   ```

4. **Token not being sent:**
   - Check browser Network tab
   - Verify `X-CSRF-Token` header present
   - Check API service configuration

### Rate Limiting / Account Locked

**Symptom:** "Too many failed login attempts"

**Cause:** 5 failed logins in 15 minutes

**Solution:**
```python
# Wait 15 minutes, or for development:
# Clear login attempts (backend database):
python -c "
from backend.database import SessionLocal, engine
from backend.models import LoginAttempt
db = SessionLocal()
db.query(LoginAttempt).delete()
db.commit()
print('Login attempts cleared')
"
```

---

## Pre-commit Hook Issues

### Hooks Not Running

**Symptom:** Pre-commit hooks don't execute on commit

**Solution:**
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Verify installation
ls .git/hooks/pre-commit  # Should exist
```

### Black/isort Failures

**Symptom:** Pre-commit fails on formatting

**Solutions:**

1. Let hooks auto-fix:
   ```bash
   git add .
   git commit -m "message"
   # If it fails with "files were modified by this hook"
   git add .  # Re-add the auto-formatted files
   git commit -m "message"  # Commit again
   ```

2. Run manually:
   ```bash
   black backend/
   isort backend/
   git add .
   git commit -m "message"
   ```

### Flake8 Failures

**Symptom:** Linting errors block commit

**Solution:**
```bash
# See all errors
flake8 backend/

# Fix manually or:
# 1. Black handles most formatting
black backend/

# 2. isort handles imports
isort backend/

# 3. Fix remaining issues manually
# Common: line too long, unused imports, etc.
```

### Windows npm Cache Issues

**Symptom:** Prettier/ESLint hooks fail on Windows

**Current Status:** Frontend hooks temporarily disabled

**Workaround:**
```bash
# Run manually when needed
npx prettier --write src/
```

---

## API/Network Issues

### CORS Errors

**Symptom:** `Access-Control-Allow-Origin` error in browser

**Causes & Solutions:**

1. **Wrong origin configured:**
   ```bash
   # Check backend/config.py
   # Set PRODUCTION_ORIGIN or CUSTOM_ORIGINS
   export PRODUCTION_ORIGIN=https://your-domain.com
   ```

2. **Development mode:**
   - Should work with localhost automatically
   - Check `config.py` CORS settings

3. **Credentials not included:**
   - Verify API client sends credentials
   - Check `services/api.ts` configuration

### API Returns 404

**Symptom:** All API calls return 404

**Causes:**

1. **Backend not running:**
   ```bash
   # Check backend is running
   curl http://localhost:8000/api/health
   ```

2. **Wrong port:**
   - Backend should be on 8000
   - Frontend on 3000
   - Check your configuration

3. **Wrong API base URL:**
   - Check `services/api.ts`
   - Should be `http://localhost:8000/api` (development)

### API Returns 500

**Symptom:** Internal server error

**Solution:**
1. Check backend logs for error details
2. Check database is accessible
3. Verify request data is valid
4. Check for Python exceptions in terminal

---

## Testing Issues

### Pytest Import Errors

**Symptom:** `ModuleNotFoundError` when running tests

**Solution:**
```bash
# Run from project root
python -m pytest

# NOT just:
# pytest  # May have PATH issues
```

### E2E Tests Timeout

**Symptom:** Playwright tests hang or timeout

**Causes & Solutions:**

1. **Servers not starting:**
   ```bash
   # Check playwright.config.ts webServer settings
   # Verify backend and frontend start manually first
   ```

2. **Ports in use:**
   - Kill processes on ports 3000 and 8000
   - See "Port Already in Use" section above

3. **Increase timeout:**
   ```typescript
   // In test file
   test.setTimeout(60000); // 60 seconds
   ```

### Coverage Command Not Found

**Symptom:** `pytest-cov: command not found`

**Solution:**
```bash
pip install pytest-cov

# Or install all dev dependencies
pip install -r requirements-dev.txt
```

---

## Production Deployment Issues

### Environment Variable Not Set

**Symptom:** App uses defaults instead of environment config

**Solution:**
```bash
# Verify variables are set
echo $DATABASE_URL
echo $ENVIRONMENT
echo $SESSION_SECRET

# Set missing variables
export ENVIRONMENT=production
export DATABASE_URL=postgresql://...
export SESSION_SECRET=your-secret-key
```

### Database Connection Failed (PostgreSQL)

**Symptom:** Can't connect to PostgreSQL

**Troubleshooting:**

1. Check `DATABASE_URL` format:
   ```
   postgresql://user:password@host:5432/dbname
   ```

2. Verify database exists:
   ```bash
   psql $DATABASE_URL -c "SELECT 1;"
   ```

3. Check network/firewall:
   - Database host reachable?
   - Correct port (usually 5432)?
   - Firewall rules allow connection?

### Static Files Not Found (Production)

**Symptom:** 404 for CSS/JS files in production

**Solution:**
```bash
# Ensure frontend is built
npm run build

# Verify build/ directory exists with files
ls -la build/

# Check run.py serves static files correctly
# Should mount build/ directory
```

### Session Secret Not Changed Warning

**Symptom:** Warning about default SESSION_SECRET

**Solution:**
```bash
# Generate secure secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set environment variable
export SESSION_SECRET=<generated-secret>

# Or in .env file (not committed!)
echo "SESSION_SECRET=<generated-secret>" >> .env
```

---

## Development Workflow Issues

### Git Pre-commit Slow

**Symptom:** Commits take too long

**Causes:**
- First run downloads hook environments (normal)
- Checking many files

**Solutions:**
```bash
# Skip hooks temporarily (use sparingly!)
git commit --no-verify -m "message"

# Or skip specific hook
SKIP=flake8 git commit -m "message"
```

### Hot Reload Not Working

**Frontend:**
```bash
# Verify Vite dev server running
npm run dev

# Check file is saved
# Check browser console for errors
```

**Backend:**
```bash
# Uvicorn auto-reload enabled by default in dev
# If not working, restart server manually
```

---

## Getting Help

If you can't resolve an issue:

1. **Check documentation:**
   - This troubleshooting guide
   - [Testing Guide](testing.md)
   - [Frontend Guide](frontend-development.md)
   - [Migrations Guide](migrations.md)

2. **Check logs:**
   - Backend: Terminal running `python run.py`
   - Frontend: Browser console (F12)
   - Tests: Pytest output, Playwright HTML reports

3. **Search issues:**
   - GitHub issues for similar problems
   - Stack Overflow for framework-specific issues

4. **Create issue:**
   - Include error messages
   - Steps to reproduce
   - Environment details (OS, Python version, etc.)
   - Relevant logs

---

## Quick Reference

### Restart Everything (Development)

```bash
# Stop all servers (Ctrl+C in terminals)

# Backend
cd ProjectGoat
.venv\Scripts\activate  # Windows
python backend/init_db.py  # If needed
python run.py

# Frontend (new terminal)
npm run dev
```

### Fresh Start (Nuclear Option)

```bash
# WARNING: Deletes all data and dependencies

# Clean Python
rm -rf .venv
rm projectgoat.db
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python backend/init_db.py

# Clean Node
rm -rf node_modules package-lock.json
npm install

# Start servers
python run.py  # Terminal 1
npm run dev    # Terminal 2
```

---

**See Also:**
- [Deployment Guide](deployment.md)
- [Testing Guide](testing.md)
- [Contributing Guide](../../CONTRIBUTING.md)
