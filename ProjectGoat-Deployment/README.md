# ProjectGoat - Deployment Package

## Quick Start

### Prerequisites
- Python 3.9 or higher
- Web browser

### Installation Steps

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the application:**
   ```bash
   python run.py
   ```

   Note: Database is already initialized with sample data and working authentication!

3. **Access the application:**
   Open your browser to: http://localhost:8000

### Default Login Credentials

All users have the default password: **Password123!**

| Email | Password | Role |
|-------|----------|------|
| sarah@example.com | Password123! | admin |
| marcus@example.com | Password123! | member |
| elena@example.com | Password123! | member |
| james@example.com | Password123! | member |
| priya@example.com | Password123! | viewer |

**Important:** All users are flagged to change password on first login for security.

## What's Included

```
ProjectGoat-Deployment/
├── build/              # Frontend (906 KB production bundle)
├── backend/            # Python backend code (with password hashing)
├── projectgoat.db      # Pre-initialized database with hashed passwords
├── run.py             # Startup script
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Fixed Issues

✅ **Login Authentication** - Password hashing now working correctly
✅ **AppSettings Table** - Database includes app_settings table
✅ **Favicon Endpoint** - Removed (not needed for deployment)
✅ **NULL Password Prevention** - Defensive checks added

## Troubleshooting

### Port Already in Use
If port 8000 is already in use, edit `run.py` and change the port number.

### Permission Errors
Ensure you have write permissions in the application directory for database access.

### Missing Dependencies
If `pip install` fails, you may need to configure proxy settings or use an internal PyPI mirror.

## Data Management

### Backup Database
```bash
copy projectgoat.db projectgoat_backup_YYYY-MM-DD.db
```

### Reset Database
If you need to reset the database, you can delete `projectgoat.db` and run:
```bash
python backend/init_db.py
```

## Daily Usage

**Starting:** `python run.py`
**Stopping:** Press CTRL+C
**Access:** http://localhost:8000

## Security Features

- ✅ Session-based authentication with bcrypt password hashing
- ✅ CSRF protection on all state-changing operations
- ✅ Rate limiting: 5 failed login attempts per 15 minutes
- ✅ Session timeouts: 30 minutes idle, 8 hours absolute
- ✅ Password complexity validation
- ✅ Localhost only - no external network access
- ✅ Defensive NULL checks to prevent crashes

---

**ProjectGoat by TeamGoat**
Version 1.0.1 - Production Ready
All critical login issues resolved!
