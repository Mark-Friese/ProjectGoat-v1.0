# ProjectGoat - Environment Constraints

## Work Environment Limitations

### Network & Connectivity
- **No online database access** - Firewall/security restrictions prevent connections to external databases
- **No cloud services** - Cannot use Firebase, Supabase, AWS, or similar cloud platforms
- **Internal network only** - Application runs on local network

### Software Installation Restrictions
- **No PostgreSQL installation** - Cannot install traditional database servers
- **No Node.js on target laptop** - Runtime not available on deployment machine
- **Limited admin rights** - Restricted ability to install software

### Browser & Data Management
- **Browser data cleared regularly** - IT policy automatically clears browser cache/localStorage
- **No control over browser settings** - Managed by IT department
- **Data persistence required** - Must survive browser clears

### Available Technologies
- **Python** ✅ - Available or easier to get approved
- **Static HTML/CSS/JS files** ✅ - Can be deployed
- **File-based storage** ✅ - SQLite and similar file-based solutions work

## Chosen Solution

### Architecture
**Frontend:** React + TypeScript + Vite (built to static files)
**Backend:** Python + FastAPI + SQLAlchemy
**Database:** SQLite (single .db file)

### Why This Works
1. **No Node.js needed on work laptop** - Frontend built once, then just static files
2. **No database server** - SQLite is file-based, no installation required
3. **Python backend** - Likely available or approvable
4. **File persistence** - Data stored in .db file, survives browser clears
5. **Portable** - Entire app in one folder, easy to copy/move
6. **Offline** - No internet connectivity required

## Deployment Model

```
Work Laptop
├── ProjectGoat/
│   ├── frontend/ (static HTML/CSS/JS)
│   ├── backend/ (Python FastAPI server)
│   └── projectgoat.db (SQLite database)
```

**Run Command:** `python run.py`
**Access:** `http://localhost:8000`

## Security Considerations
- All data stored locally on work laptop
- No external network calls
- Complies with corporate security policies
- No sensitive data leaves the machine
