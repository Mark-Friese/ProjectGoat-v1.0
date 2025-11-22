# ProjectGoat Deployment Guide

ProjectGoat supports **dual-mode deployment** from a single codebase:
- **Local Mode**: SQLite database, localhost-only, no admin rights required
- **Online Mode**: PostgreSQL database, cloud hosting, multi-user capable

## Table of Contents
- [Local Deployment (Laptop)](#local-deployment-laptop)
- [Online Deployment](#online-deployment)
- [Environment Variables](#environment-variables)
- [Database Comparison](#database-comparison)

---

## Local Deployment (Laptop)

### Requirements
- Python 3.9 or higher
- **No admin rights needed**
- **No additional database installation**

### Installation

1. **Clone or extract the repository**
   ```bash
   cd ProjectGoat
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv .venv

   # Windows
   .venv\Scripts\activate

   # Mac/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the application**
   - Open browser to: `http://localhost:8000`
   - API documentation: `http://localhost:8000/docs`

### Configuration
**None needed!** The application uses sensible defaults:
- Database: SQLite (local file `projectgoat.db`)
- Host: `127.0.0.1` (localhost only)
- Port: `8000`
- Environment: `development`

### What Gets Created
- `projectgoat.db` - SQLite database file (created automatically)
- `.venv/` - Python virtual environment (if you created one)

### Stopping the Server
Press `CTRL+C` in the terminal where it's running.

---

## Online Deployment

### Supported Platforms
- ✅ **Railway** (Recommended - easiest)
- ✅ **Render** (Free tier available)
- ✅ **Heroku**
- ✅ **DigitalOcean App Platform**
- ✅ **AWS / Google Cloud / Azure**

### Quick Deploy to Railway

1. **Sign up** for [Railway](https://railway.app)

2. **Create new project** from GitHub repository

3. **Add PostgreSQL database**
   - Click "New" → "Database" → "PostgreSQL"
   - Railway automatically sets `DATABASE_URL`

4. **Set environment variables**
   ```
   ENVIRONMENT=production
   HOST=0.0.0.0
   PRODUCTION_ORIGIN=https://your-app.railway.app
   SESSION_SECRET=<generate-random-string>
   ```

5. **Deploy!**
   - Railway auto-detects Python and deploys
   - Your app will be available at: `https://your-app.railway.app`

### Quick Deploy to Render

1. **Sign up** for [Render](https://render.com)

2. **Create new Web Service**
   - Connect GitHub repository
   - Render auto-detects `render.yaml`

3. **PostgreSQL database automatically created**

4. **Set environment variables** (if not using `render.yaml`)
   ```
   ENVIRONMENT=production
   HOST=0.0.0.0
   PRODUCTION_ORIGIN=https://your-app.onrender.com
   SESSION_SECRET=<generate-random-string>
   ```

5. **Deploy!**
   - Render builds and deploys automatically

### Manual Deployment (Any Platform)

1. **Install dependencies**
   ```bash
   pip install -r requirements-postgres.txt
   ```

2. **Set environment variables**
   ```bash
   export ENVIRONMENT=production
   export HOST=0.0.0.0
   export PORT=8000
   export DATABASE_URL=postgresql://user:password@host:5432/dbname
   export PRODUCTION_ORIGIN=https://your-domain.com
   export SESSION_SECRET=your-secret-key
   ```

3. **Initialize database** (first time only)
   ```bash
   python backend/init_db.py
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

---

## Environment Variables

All environment variables are **optional** with sensible defaults.

### Core Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | `development` or `production` |
| `HOST` | `127.0.0.1` | Server host (use `0.0.0.0` for production) |
| `PORT` | `8000` | Server port |

### Database Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///projectgoat.db` | Database connection URL |

**Examples:**
```bash
# SQLite (local)
DATABASE_URL=sqlite:///projectgoat.db

# PostgreSQL (local)
DATABASE_URL=postgresql://localhost/projectgoat

# PostgreSQL (production)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Automatic on Railway/Render
DATABASE_URL=postgresql://...  # Set by platform
```

### Security Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `SESSION_SECRET` | `development-secret...` | Secret key for sessions (change in production!) |
| `PRODUCTION_ORIGIN` | _(none)_ | Your production frontend URL |
| `CUSTOM_ORIGINS` | _(none)_ | Comma-separated additional CORS origins |

**Generate a secure session secret:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Using .env Files

Create a `.env` file in the project root (copy from `.env.example`):

```bash
# .env
ENVIRONMENT=development
HOST=127.0.0.1
PORT=8000
DATABASE_URL=sqlite:///projectgoat.db
```

The application automatically loads `.env` files using `python-dotenv`.

---

## Database Comparison

### SQLite (Local Mode)

**Use for:**
- Laptop/personal deployment
- Single-user scenarios
- Development and testing
- Environments without admin rights

**Pros:**
- No installation required
- No admin rights needed
- Simple file-based storage
- Perfect for single users

**Cons:**
- Limited concurrent writes
- Not suitable for 10+ users
- No network access
- File-based (no server)

**Performance:**
- **1 user**: Excellent
- **2-5 users**: Good
- **10+ users**: Poor (database locked errors)

### PostgreSQL (Online Mode)

**Use for:**
- Online/cloud deployment
- Multi-user scenarios
- Production environments
- Team collaboration

**Pros:**
- Excellent concurrent access
- Scalable to 1000+ users
- Network-accessible
- Full ACID compliance
- Advanced features

**Cons:**
- Requires database server
- More complex setup (locally)
- Platform-managed in cloud (easy)

**Performance:**
- **1 user**: Excellent
- **10 users**: Excellent
- **100+ users**: Excellent

---

## Switching Between Modes

### From Local to Online

No code changes needed! Just set environment variables:

```bash
# Before (local - using defaults)
python run.py

# After (online)
export ENVIRONMENT=production
export DATABASE_URL=postgresql://...
export HOST=0.0.0.0
python run.py
```

### From Online to Local

Remove environment variables or delete `.env` file:

```bash
# Returns to defaults (SQLite, localhost)
python run.py
```

---

## Deployment Checklist

### Local Deployment ✅
- [ ] Python 3.9+ installed
- [ ] Virtual environment created (optional but recommended)
- [ ] `pip install -r requirements.txt` completed
- [ ] Run `python run.py`
- [ ] Access `http://localhost:8000`

### Online Deployment ✅
- [ ] Choose hosting platform (Railway/Render recommended)
- [ ] Create PostgreSQL database
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `HOST=0.0.0.0`
- [ ] Set `DATABASE_URL` (or use platform-managed)
- [ ] Set `PRODUCTION_ORIGIN` to your domain
- [ ] Generate and set secure `SESSION_SECRET`
- [ ] Deploy application
- [ ] Initialize database (first time)
- [ ] Verify HTTPS is enabled
- [ ] Test all features

---

## Troubleshooting

### Local Deployment

**Issue**: `ModuleNotFoundError: No module named 'fastapi'`
- **Solution**: Run `pip install -r requirements.txt`

**Issue**: `Permission denied` writing to database
- **Solution**: Check file permissions on `projectgoat.db`

**Issue**: Application won't start
- **Solution**: Check Python version (`python --version` should be 3.9+)

### Online Deployment

**Issue**: `database locked` errors
- **Solution**: You're using SQLite in production. Switch to PostgreSQL:
  ```bash
  export DATABASE_URL=postgresql://...
  ```

**Issue**: CORS errors in browser
- **Solution**: Set `PRODUCTION_ORIGIN` environment variable:
  ```bash
  export PRODUCTION_ORIGIN=https://your-domain.com
  ```

**Issue**: Connection refused
- **Solution**: Ensure `HOST=0.0.0.0` (not `127.0.0.1`)

**Issue**: Database connection failed
- **Solution**: Verify `DATABASE_URL` is correct and database exists

---

## Cost Estimates

### Local Deployment
**Cost**: **Free** (uses your laptop)

### Online Deployment

| Platform | Monthly Cost | Notes |
|----------|--------------|-------|
| **Railway** | $10-20 | Includes PostgreSQL, starts at $5 credit/month |
| **Render** | Free - $14 | Free tier spins down when inactive |
| **Heroku** | $16+ | No free tier, $7 web + $9 database |
| **DigitalOcean** | $21+ | $6 app + $15 managed database |

**Recommendation**: Start with Railway ($10-20/month) or Render free tier.

---

## Security Notes

### Local Deployment
- **Access**: Localhost only (127.0.0.1)
- **SSL/HTTPS**: Not needed (local)
- **Firewall**: Not needed (not exposed)
- **Authentication**: Still required (login system active)

### Online Deployment
- **Access**: Internet-facing (0.0.0.0)
- **SSL/HTTPS**: Required (automatic on Railway/Render)
- **Firewall**: Platform-managed
- **Authentication**: Required (login system active)
- **Additional**:
  - Change `SESSION_SECRET` to secure random string
  - Set `PRODUCTION_ORIGIN` to restrict CORS
  - Enable platform security features
  - Regular database backups
  - Monitor error logs

---

## Support

For issues or questions:
- Check this deployment guide
- Review `.env.example` for configuration options
- Verify environment variables are set correctly
- Check logs for error messages

## Architecture

ProjectGoat uses environment-based configuration that automatically adapts to deployment mode:

```
┌─────────────────┐
│ No env vars set │──> SQLite + localhost (local mode)
└─────────────────┘

┌─────────────────┐
│ DATABASE_URL    │──> PostgreSQL + 0.0.0.0 (online mode)
│ ENVIRONMENT=... │
└─────────────────┘
```

**One codebase, two modes, zero configuration needed for local deployment!**
