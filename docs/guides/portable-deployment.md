# Portable Deployment Guide

This guide explains how to create and deploy portable packages of ProjectGoat using GitHub Actions.

## Overview

The portable deployment solution allows you to:
- Build the entire application on GitHub Actions (no local build needed)
- Download a single ZIP file containing everything needed
- Deploy to restricted environments (no Node.js required on target)
- Run entirely from a folder with minimal dependencies (just Python)

## Architecture

```
Development Machine (You)
    ↓
GitHub Actions (Automated Build)
    ↓
ZIP Artifact Download
    ↓
Target Laptop (Restricted Environment)
```

**Key Benefits:**
- ✅ No Node.js on target laptop
- ✅ No database server needed (SQLite)
- ✅ Single folder deployment
- ✅ Works offline after initial setup
- ✅ Portable (can be copied/moved)

## Prerequisites

### On GitHub
- Repository must be pushed to GitHub
- GitHub Actions must be enabled

### On Target Laptop
- **Python 3.9+** (3.13 recommended)
- Modern web browser
- 200 MB disk space
- Ability to extract ZIP files

### NOT Required on Target Laptop
- ❌ Node.js
- ❌ Git
- ❌ PostgreSQL or any database server
- ❌ Admin/elevated privileges
- ❌ Internet connection (after initial setup)

## Creating a Portable Package

### Method 1: Manual Workflow Trigger (Recommended for Testing)

1. **Navigate to GitHub Actions:**
   - Go to your repository on GitHub
   - Click the **Actions** tab
   - Click **Build Portable Deployment Package** workflow

2. **Trigger the workflow:**
   - Click **Run workflow** button (top right)
   - Select the branch (usually `main`)
   - Click the green **Run workflow** button

3. **Wait for completion:**
   - The workflow takes ~5-10 minutes
   - Watch the progress in real-time
   - Green checkmark = success
   - Red X = failure (check logs)

4. **Download the artifact:**
   - Click on the completed workflow run
   - Scroll to **Artifacts** section (bottom of page)
   - Click on `ProjectGoat-{SHA}-portable` to download
   - The ZIP file will download to your computer

### Method 2: Automatic on Git Tags

1. **Create and push a version tag:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Workflow triggers automatically**
   - Navigate to Actions tab to monitor progress
   - Download artifact when complete

### Method 3: Automatic on Push

**Note:** Currently disabled by default (workflow only runs on `workflow_dispatch` and tags).

To enable automatic builds on every push to `main`:
1. Edit `.github/workflows/build-portable.yml`
2. Uncomment the `push: branches` trigger section
3. Commit and push changes

**Warning:** This will create an artifact for every push, which may consume GitHub storage quota.

## Package Contents

The downloaded ZIP file contains:

```
ProjectGoat-{SHA}-portable.zip
├── backend/                    # FastAPI Python backend
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── auth.py
│   └── ...
├── build/                      # Pre-built React frontend
│   ├── index.html
│   └── assets/
│       ├── index-{hash}.js
│       ├── index-{hash}.css
│       └── project-goat-logo-{hash}.svg
├── requirements.txt            # Python dependencies
├── run.bat                     # Windows startup script (MAIN)
├── init_db.bat                # Database reset script
├── .env.template              # Configuration template
├── README-PORTABLE.txt        # User instructions
└── CHANGELOG.txt              # Recent changes
```

## Deploying to Target Laptop

### Initial Deployment

1. **Transfer the ZIP file:**
   - USB drive
   - Network share
   - Email (if size permits, ~5-10 MB)
   - Internal file transfer system

2. **Extract on target laptop:**
   - Right-click ZIP → Extract All
   - Choose a permanent location (e.g., `C:\ProjectGoat\`)
   - **Important:** Don't extract to Desktop or Downloads (use a stable location)

3. **Verify Python installation:**
   ```cmd
   python --version
   ```
   - Should show Python 3.9 or higher
   - If not installed, download from [python.org](https://www.python.org/downloads/)
   - **During Python install:** Check "Add Python to PATH"

4. **First run:**
   - Double-click `run.bat`
   - Wait 2-3 minutes for initial setup
   - Script will:
     - Create virtual environment (`.venv/` folder)
     - Install all dependencies
     - Initialize database
     - Generate session secret
     - Start the server

5. **Access the application:**
   - Open browser to `http://localhost:8000`
   - Login with default credentials:
     - Email: `sarah@example.com`
     - Password: `password123`
   - **IMPORTANT:** Change password immediately!

### Daily Usage

**Starting the application:**
```cmd
Double-click run.bat
```
- Takes ~5-10 seconds (much faster than first run)
- Browser opens automatically to `http://localhost:8000`

**Stopping the application:**
- Press `Ctrl+C` in the command window
- Or close the command window

## Configuration

### Environment Variables

The `.env` file is auto-created from `.env.template` on first run.

**Default configuration:**
```env
ENVIRONMENT=production
HOST=127.0.0.1           # Localhost only
PORT=8000                # Default port
DATABASE_URL=sqlite:///projectgoat.db
SESSION_SECRET=          # Auto-generated
```

**To customize:**
1. Stop the application
2. Edit `.env` file in the deployment folder
3. Restart the application

**Common customizations:**
- Change port: `PORT=9000`
- Enable debug logging: `LOG_LEVEL=DEBUG`

### Changing the Port

If port 8000 is already in use:

1. Stop the application
2. Edit `.env` file
3. Change `PORT=8000` to another port (e.g., `PORT=8080`)
4. Save and close
5. Restart with `run.bat`
6. Access at `http://localhost:8080`

## Database Management

### Backup Database

**Manual backup:**
```cmd
copy projectgoat.db projectgoat-backup-2025-11-23.db
```

**What gets backed up:**
- All user accounts
- All tasks and data
- All settings

**Best practices:**
- Backup before major updates
- Include date in backup filename
- Store backups outside the application folder
- Test restoring from backup periodically

### Restore Database

1. Stop the application (`Ctrl+C`)
2. Delete or rename current database:
   ```cmd
   ren projectgoat.db projectgoat-old.db
   ```
3. Copy backup file:
   ```cmd
   copy projectgoat-backup-2025-11-23.db projectgoat.db
   ```
4. Restart application

### Reset Database

**Using the reset script:**
1. Stop the application
2. Double-click `init_db.bat`
3. Type `YES` to confirm
4. Database recreated with default data

**Manual reset:**
```cmd
del projectgoat.db
python backend\init_db.py
```

**Warning:** This deletes ALL data permanently!

## Updating to New Version

### Update Process

1. **Backup current data:**
   ```cmd
   copy projectgoat.db projectgoat-backup.db
   ```

2. **Download new version from GitHub Actions**
   - Follow "Creating a Portable Package" steps above
   - Download newer version artifact

3. **Extract to NEW folder:**
   - Example: `C:\ProjectGoat-v2\` (different from current)
   - Don't overwrite existing installation

4. **Copy database to new folder:**
   ```cmd
   copy C:\ProjectGoat\projectgoat.db C:\ProjectGoat-v2\projectgoat.db
   ```

5. **Test new version:**
   - Run `run.bat` in new folder
   - Verify everything works
   - Check that your data is present

6. **Switch to new version:**
   - If successful, use new folder going forward
   - Keep old folder as backup for a while

7. **Clean up old version (optional):**
   - After confirming new version works well
   - Delete old folder to save space

### Migration Notes

**Database compatibility:**
- Usually databases are compatible between versions
- Check CHANGELOG.txt for migration notes
- If incompatible, migration script will be provided

**Configuration changes:**
- Compare `.env` files between versions
- New settings may be added in `.env.template`
- Manually add new settings to your `.env` if needed

## Troubleshooting

### Common Issues

#### "Python is not installed or not in PATH"

**Problem:** Python not found

**Solutions:**
1. Install Python from [python.org](https://www.python.org/downloads/)
2. During install, check **"Add Python to PATH"**
3. Restart computer after installation
4. Verify: `python --version` in command prompt

#### "Failed to create virtual environment"

**Problem:** Python installation incomplete

**Solutions:**
1. Reinstall Python (ensure all components selected)
2. Or manually create: `python -m venv .venv`
3. Check disk space (need ~100 MB)

#### "Port 8000 is already in use"

**Problem:** Another application using port 8000

**Solutions:**
1. Stop other application using port 8000
2. Or change port in `.env` file (see Configuration section)
3. Check for other `run.bat` instances running

#### "Failed to install dependencies"

**Problem:** Can't install Python packages

**Solutions:**
1. **If first run:** Internet connection required for pip install
2. Check firewall/proxy settings
3. Manually install: `.venv\Scripts\pip.exe install -r requirements.txt`
4. Try using corporate proxy: `pip install --proxy=http://proxy:port -r requirements.txt`

#### Can't access http://localhost:8000

**Problem:** Application not accessible in browser

**Solutions:**
1. Verify `run.bat` shows "Application is starting..."
2. Check for error messages in command window
3. Try `http://127.0.0.1:8000` instead
4. Check Windows Firewall settings
5. Verify port in `.env` matches URL

#### "Database is locked"

**Problem:** Multiple instances accessing database

**Solutions:**
1. Close all `run.bat` windows
2. Check Task Manager for `python.exe` processes
3. Restart computer if needed
4. Check if database file is on network drive (not recommended)

#### Virtual environment activation fails

**Problem:** Can't activate `.venv`

**Solutions:**
1. Delete `.venv` folder
2. Run `run.bat` again (will recreate)
3. Check folder permissions
4. Run from local disk (not network drive)

### GitHub Actions Build Failures

#### Frontend build fails

**Check:**
- `package.json` dependencies
- Node.js version in workflow (currently 20)
- Build logs in Actions tab

**Fix:**
- Verify `npm run build` works locally
- Check for syntax errors in frontend code
- Update dependencies if needed

#### Python dependencies fail

**Check:**
- `requirements.txt` syntax
- Package versions compatibility
- Build logs in Actions tab

**Fix:**
- Test `pip install -r requirements.txt` locally
- Pin versions if needed
- Check for deprecated packages

#### Artifact upload fails

**Check:**
- Artifact size (max 2 GB for free tier)
- GitHub Actions quota
- Build logs

**Fix:**
- Reduce package size
- Check repository storage limits
- Contact GitHub support if quota issue

### Getting Help

1. **Check README-PORTABLE.txt** in the package
2. **Check logs:** Command window output
3. **Check GitHub Issues:** Search for similar problems
4. **Create GitHub Issue:** Include:
   - Version (commit SHA from filename)
   - Error messages (screenshots)
   - Python version: `python --version`
   - Windows version
   - Steps to reproduce

## Advanced Topics

### Customizing the Build

The workflow can be customized by editing `.github/workflows/build-portable.yml`.

**Common customizations:**
- Change Python version requirement
- Add pre-installed data to database
- Include additional files in package
- Customize README-PORTABLE.txt
- Add company branding

**Example: Add additional files**
```yaml
- name: Copy additional files
  run: |
    cp docs/user-guide.pdf deployment-package/
    cp company-logo.png deployment-package/
```

### Running on Linux/Mac

The workflow can be extended to support Linux/Mac:

1. Create `run.sh` startup script (similar to `run.bat`)
2. Add to workflow:
   ```yaml
   - name: Create run.sh
     run: |
       cat > deployment-package/run.sh << 'EOF'
       #!/bin/bash
       # Linux/Mac startup script
       # (similar logic to run.bat)
       EOF
       chmod +x deployment-package/run.sh
   ```

### Multiple Deployment Targets

To create packages for different environments:

1. Create separate workflow files:
   - `build-portable-windows.yml`
   - `build-portable-linux.yml`
   - `build-portable-mac.yml`

2. Customize each for the target platform

3. Or use matrix strategy in single workflow:
   ```yaml
   strategy:
     matrix:
       os: [windows, linux, macos]
   ```

### CI/CD Integration

**Automatic version releases:**
1. Tag release: `git tag v1.0.0`
2. Push tag: `git push origin v1.0.0`
3. Workflow runs automatically
4. Creates GitHub Release with artifact attached

**To enable:**
- Add GitHub Release creation step to workflow
- Use `softprops/action-gh-release` action

### Security Considerations

**SESSION_SECRET:**
- Auto-generated on first run
- Unique per deployment
- Stored in `.env` file
- Keep `.env` file secure

**Database security:**
- File-based SQLite (no network exposure)
- Passwords hashed with bcrypt
- Keep `projectgoat.db` secure
- Regular backups recommended

**Network security:**
- Binds to `127.0.0.1` (localhost only)
- Not accessible from network
- Firewall rules not needed
- Safe for restricted environments

## Best Practices

### For Developers

1. **Test before releasing:**
   - Build locally first
   - Test on clean VM
   - Verify all features work

2. **Version management:**
   - Use semantic versioning (v1.0.0)
   - Document breaking changes
   - Provide migration guides

3. **Documentation:**
   - Update README-PORTABLE.txt
   - Add migration notes to CHANGELOG
   - Document configuration changes

### For End Users

1. **Installation:**
   - Extract to permanent location (not Desktop/Downloads)
   - Use local drive (not network drive)
   - Keep folder name simple (no spaces)

2. **Daily usage:**
   - Don't move folder while app is running
   - Close properly (Ctrl+C, not just window close)
   - One instance only per database

3. **Data management:**
   - Regular backups (weekly recommended)
   - Store backups outside app folder
   - Test restore process periodically

4. **Updates:**
   - Always backup before updating
   - Test new version before switching
   - Keep old version as fallback

## FAQ

**Q: Can I run multiple instances?**
A: Yes, but each needs its own folder and database. Change PORT in `.env` to avoid conflicts.

**Q: Can I move the folder after installation?**
A: Yes, the entire folder is portable. Stop the app, move folder, restart.

**Q: Does it work offline?**
A: Yes, after initial setup. First run needs internet for `pip install`.

**Q: Can I customize the UI?**
A: Not in portable deployment. UI is pre-built. Customization requires rebuilding from source.

**Q: Where are passwords stored?**
A: In `projectgoat.db`, hashed with bcrypt. Not reversible.

**Q: Can I use PostgreSQL instead of SQLite?**
A: Not in portable deployment. Designed for SQLite simplicity. Use standard deployment for PostgreSQL.

**Q: How do I add more users?**
A: Currently single-user. Multi-user support planned for future release.

**Q: What's the maximum database size?**
A: SQLite supports up to 281 TB. Practical limit on Windows: disk space available.

**Q: Can I run this on a server?**
A: Yes, but change `HOST=0.0.0.0` in `.env` and configure firewall. Not recommended for multi-user production.

## Support

- **Documentation:** See main [README.md](../../README.md)
- **Issues:** [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions:** [GitHub Discussions](https://github.com/your-repo/discussions)

## Changelog

### v1.0.0 (Initial Release)
- GitHub Actions workflow for automated builds
- Windows support with `run.bat`
- SQLite database with auto-initialization
- Virtual environment creation
- Auto-generated session secrets
- Comprehensive documentation
