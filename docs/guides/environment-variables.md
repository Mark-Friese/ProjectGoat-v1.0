# Environment Variables Reference

**Status:** 🚧 In Progress

## Overview

ProjectGoat uses environment variables for configuration, allowing the same codebase to run in different environments (development, production) without code changes.

## Configuration Sources

Environment variables are loaded from (in order of precedence):

1. **System environment variables** (highest priority)
2. **`.env` file** in project root (if exists)
3. **Default values** in `backend/config.py` (lowest priority)

## Using .env Files

### Creating .env File

```bash
# Copy the example
cp .env.example .env

# Edit with your values
nano .env  # or your preferred editor
```

### .env File Format

```bash
# Comments start with #
# Format: KEY=value (no spaces around =)
# No quotes needed for simple values

ENVIRONMENT=development
DATABASE_URL=sqlite:///projectgoat.db
PORT=8000
```

**Important:** Never commit `.env` files! They're in `.gitignore`.

---

## Core Environment Variables

### ENVIRONMENT

**Description:** Deployment environment mode

**Values:**
- `development` (default) - Development mode
- `production` - Production mode with stricter validation

**Default:** `development`

**Example:**
```bash
ENVIRONMENT=production
```

**Effects:**
- **Development:** Debug logging, relaxed CORS, SQLite OK, default secrets OK
- **Production:** Info logging, strict CORS, PostgreSQL recommended, validates SESSION_SECRET

---

### HOST

**Description:** Server host to bind to

**Values:**
- `127.0.0.1` - Localhost only (development)
- `0.0.0.0` - All network interfaces (production)

**Default:** `127.0.0.1`

**Example:**
```bash
HOST=0.0.0.0
```

**Security Note:** Only use `0.0.0.0` when deploying to production with proper security (HTTPS, firewall).

---

### PORT

**Description:** Server port number

**Values:** Any valid port number (1-65535)

**Default:** `8000`

**Example:**
```bash
PORT=8080
```

**Note:** Railway, Render, and other platforms often set this automatically.

---

## Database Configuration

### DATABASE_URL

**Description:** Database connection URL

**Format:**
```
dialect://username:password@host:port/database
```

**Examples:**

**SQLite (Local):**
```bash
DATABASE_URL=sqlite:///projectgoat.db  # Relative path
DATABASE_URL=sqlite:////absolute/path/to/projectgoat.db  # Absolute path
```

**PostgreSQL (Production):**
```bash
DATABASE_URL=postgresql://user:password@localhost/projectgoat
DATABASE_URL=postgresql://user:password@host.example.com:5432/dbname
```

**Platform-managed (Railway, Render):**
```bash
# These platforms set DATABASE_URL automatically
# Example: postgresql://user:pass@host.railway.internal:5432/railway
```

**Default:** `sqlite:///projectgoat.db`

**Important:**
- SQLite is fine for development and single-user local deployment
- PostgreSQL is **required** for production multi-user deployments
- Never commit DATABASE_URL with actual credentials

---

## Security Configuration

### SESSION_SECRET

**Description:** Secret key for session encryption and CSRF tokens

**Format:** Random string (32+ characters recommended)

**Generate Secure Secret:**
```bash
# Method 1: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Method 2: OpenSSL
openssl rand -base64 32
```

**Default:** `development-secret-change-in-production`

**Example:**
```bash
SESSION_SECRET=super_secret_random_string_change_in_production
```

**Important:**
- **MUST** be changed in production (app won't start if using default in production mode)
- **MUST** be kept secret
- **MUST NOT** be committed to version control
- Changing this invalidates all existing sessions

**Security Impact:**
- Used for signing session cookies
- Used for CSRF token generation
- Compromise = all sessions compromised

---

## CORS Configuration

### PRODUCTION_ORIGIN

**Description:** Frontend URL for CORS when in production

**Format:** Full URL including protocol

**Example:**
```bash
PRODUCTION_ORIGIN=https://myapp.com
PRODUCTION_ORIGIN=https://projectgoat.railway.app
```

**Default:** None (uses permissive CORS in development)

**When to Set:**
- Production deployment where frontend and backend are on different domains
- When using custom domain

**Example Deployment:**
```
Frontend: https://myapp.com
Backend:  https://api.myapp.com
```

Set:
```bash
PRODUCTION_ORIGIN=https://myapp.com
```

---

### CUSTOM_ORIGINS

**Description:** Additional allowed CORS origins (comma-separated)

**Format:** Comma-separated list of URLs

**Example:**
```bash
CUSTOM_ORIGINS=https://staging.myapp.com,https://preview.myapp.com
```

**Default:** None

**Use Cases:**
- Multiple frontend domains (staging, production, preview)
- Mobile app development
- Third-party integrations

---

## Development vs Production

### Development Configuration

```bash
# .env (development)
ENVIRONMENT=development
HOST=127.0.0.1
PORT=8000
DATABASE_URL=sqlite:///projectgoat.db
SESSION_SECRET=development-secret-change-in-production
# PRODUCTION_ORIGIN not needed
# CUSTOM_ORIGINS not needed
```

**Characteristics:**
- Runs on localhost only
- SQLite database (fast, simple)
- Permissive CORS (allows localhost)
- Default secrets OK
- Debug logging enabled

### Production Configuration

```bash
# .env or platform environment (production)
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000  # Often set by platform
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SESSION_SECRET=<generated-secure-random-string>
PRODUCTION_ORIGIN=https://yourdomain.com
CUSTOM_ORIGINS=https://staging.yourdomain.com  # if needed
```

**Characteristics:**
- Exposes to network (0.0.0.0)
- PostgreSQL database (scalable)
- Strict CORS (only allowed origins)
- Secure secrets required
- Info/Warning logging only

---

## Platform-Specific Variables

### Railway

Railway automatically sets:
- `PORT` - Dynamically assigned
- `DATABASE_URL` - If PostgreSQL addon added
- `RAILWAY_ENVIRONMENT` - Environment name

You still need to set:
- `ENVIRONMENT=production`
- `SESSION_SECRET=<your-secret>`
- `PRODUCTION_ORIGIN=https://your-app.railway.app`

### Render

Render automatically sets:
- `PORT` - Always 10000
- `DATABASE_URL` - If PostgreSQL addon added

You still need to set:
- `ENVIRONMENT=production`
- `SESSION_SECRET=<your-secret>`
- `PRODUCTION_ORIGIN=https://your-app.onrender.com`

### Heroku

Heroku automatically sets:
- `PORT` - Dynamically assigned
- `DATABASE_URL` - If Postgres addon added

You still need to set:
- `ENVIRONMENT=production`
- `SESSION_SECRET=<your-secret>`
- `PRODUCTION_ORIGIN=https://your-app.herokuapp.com`

---

## Environment Variable Validation

### Production Mode Validation

When `ENVIRONMENT=production`, the app validates:

1. **SESSION_SECRET changed:**
   - Fails if still using default `development-secret-change-in-production`
   - Provides command to generate secure secret

2. **SQLite warning:**
   - Warns if using SQLite in production
   - Recommends PostgreSQL for multi-user deployments

### Validation Errors

**Error Example:**
```
ValueError: SESSION_SECRET must be changed in production!
Generate a secure secret with:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Solution:** Generate and set a secure SESSION_SECRET

---

## Configuration File

Variables are loaded and validated in `backend/config.py`:

```python
class Settings:
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Server
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///projectgoat.db"
    )

    # Security
    SESSION_SECRET: str = os.getenv(
        "SESSION_SECRET",
        "development-secret-change-in-production"
    )

    # CORS
    PRODUCTION_ORIGIN: Optional[str] = os.getenv("PRODUCTION_ORIGIN")
    CUSTOM_ORIGINS: Optional[str] = os.getenv("CUSTOM_ORIGINS")
```

---

## Best Practices

### 1. Never Commit Secrets

```bash
# .gitignore should include:
.env
.env.local
.env.production
*.secret
```

### 2. Use .env.example for Documentation

```bash
# .env.example (committed to repo)
ENVIRONMENT=development
HOST=127.0.0.1
PORT=8000
DATABASE_URL=sqlite:///projectgoat.db
SESSION_SECRET=development-secret-change-in-production

# Notes:
# - Copy this to .env and customize
# - Never commit .env with real credentials
# - Generate SESSION_SECRET: python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Use Different Secrets Per Environment

```bash
# development.env
SESSION_SECRET=dev-secret-12345

# production.env (never committed!)
SESSION_SECRET=<actual-secure-random-string>
```

### 4. Document All Variables

Keep this document updated when adding new variables.

### 5. Validate on Startup

Production deployments should fail fast if misconfigured (already implemented).

---

## Troubleshooting

### Variable Not Being Read

**Check:**
1. Variable name spelled correctly
2. .env file in correct location (project root)
3. .env file has correct format (KEY=value, no spaces)
4. No quotes needed for simple values
5. Restart server after changing .env

### Production Validation Fails

**Error:** "SESSION_SECRET must be changed in production"

**Solution:**
```bash
# Generate secure secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in environment or .env
export SESSION_SECRET=<generated-secret>
# or
echo "SESSION_SECRET=<generated-secret>" >> .env
```

### Database Connection Fails

**Check:**
1. DATABASE_URL format correct
2. Database exists
3. Credentials correct
4. Network accessible
5. Firewall allows connection

---

## Example Configurations

### Local Development

```bash
# .env
ENVIRONMENT=development
DATABASE_URL=sqlite:///projectgoat.db
# Other variables use defaults
```

### Staging Environment

```bash
# Platform environment variables
ENVIRONMENT=production
HOST=0.0.0.0
DATABASE_URL=postgresql://user:pass@staging-db:5432/projectgoat_staging
SESSION_SECRET=staging-secret-abc123xyz
PRODUCTION_ORIGIN=https://staging.projectgoat.com
```

### Production Environment

```bash
# Platform environment variables
ENVIRONMENT=production
HOST=0.0.0.0
DATABASE_URL=postgresql://user:pass@prod-db:5432/projectgoat
SESSION_SECRET=<secure-random-production-secret>
PRODUCTION_ORIGIN=https://projectgoat.com
CUSTOM_ORIGINS=https://app.projectgoat.com,https://mobile.projectgoat.com
```

---

## Future Variables

Planned environment variables (not yet implemented):

- `REDIS_URL` - For session storage (planned)
- `SMTP_HOST`, `SMTP_PORT` - Email notifications (planned)
- `LOG_LEVEL` - Logging level override (planned)
- `MAX_UPLOAD_SIZE` - File upload limit (planned)

---

**See Also:**
- [Deployment Guide](deployment.md) - Deployment instructions
- [Security Guide](../../SECURITY.md) - Security best practices
- [Troubleshooting](troubleshooting.md) - Common configuration issues
- `.env.example` - Template with all variables
