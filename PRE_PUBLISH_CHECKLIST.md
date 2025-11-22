# Pre-Publish Security Checklist

Complete this checklist before publishing ProjectGoat to GitHub.

## ✅ Security Review

### Code Security
- [x] No hardcoded passwords or API keys
- [x] Session secrets use environment variables
- [x] Sensitive data not logged
- [x] SQL injection protection (using ORM)
- [x] Input validation implemented (Pydantic schemas)
- [x] CSRF protection enabled
- [x] Rate limiting on authentication

### File Security
- [x] `.gitignore` properly configured
- [x] `.env` files excluded from git
- [x] `*.db` files excluded (database files)
- [x] `venv/` and `.venv/` excluded
- [x] `__pycache__/` excluded
- [x] No secrets in git history

### Configuration Security
- [x] Default `SESSION_SECRET` is placeholder only
- [x] Database defaults to SQLite (localhost only)
- [x] Default host is `127.0.0.1` (not exposed to network)
- [x] Production mode requires explicit configuration
- [x] `.env.example` provided (no actual secrets)

## ✅ Repository Setup

### Required Files
- [x] `LICENSE` - MIT License
- [x] `README.md` - Project documentation
- [x] `SECURITY.md` - Security policy
- [x] `CONTRIBUTING.md` - Contribution guidelines
- [x] `DEPLOYMENT.md` - Deployment instructions
- [x] `.gitignore` - Ignore sensitive files
- [x] `.env.example` - Environment variable template

### Documentation
- [ ] README.md is complete and accurate
- [ ] Installation instructions are clear
- [ ] Usage examples provided
- [ ] Screenshots/demos included (optional)
- [ ] License is specified
- [ ] Contact information provided

## ✅ Clean Git History

### Before Publishing
```bash
# 1. Check for sensitive data in git history
git log --all --full-history -- .env
git log --all --full-history -- *.db
git log --all --full-history -- *secret*

# 2. Check for large files (database backups, etc.)
git rev-list --objects --all | grep -E '\.(db|sql|dump)$'

# 3. Verify .gitignore is working
git status --ignored

# 4. Check what will be pushed
git log origin/main..HEAD
```

### If Sensitive Data Found
```bash
# Remove sensitive files from history (use with caution!)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch path/to/sensitive/file' \
  --prune-empty --tag-name-filter cat -- --all

# Alternative: Use BFG Repo-Cleaner
# https://rtyley.github.io/bfg-repo-cleaner/
```

## ✅ Pre-Push Verification

### Files to Check
- [ ] No `.env` files in repository
- [ ] No `*.db` files in repository
- [ ] No hardcoded credentials in code
- [ ] No API keys in code or config
- [ ] No personal information in code
- [ ] No large binary files (unless intentional)

### Test Clean Clone
```bash
# Clone to temporary directory
cd /tmp
git clone /path/to/ProjectGoat temp-clone
cd temp-clone

# Verify it works
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py

# Should start with SQLite, localhost, no errors
```

## ✅ GitHub Repository Settings

### Before Making Public
- [ ] Repository description added
- [ ] Topics/tags added (python, fastapi, react, project-management)
- [ ] License selected (MIT)
- [ ] README preview looks correct
- [ ] Security policy configured
- [ ] Issues enabled
- [ ] Discussions enabled (optional)
- [ ] Wiki enabled (optional)

### Security Settings
- [ ] Private vulnerability reporting enabled
- [ ] Dependabot alerts enabled
- [ ] Code scanning enabled (optional)
- [ ] Secret scanning enabled

## ✅ First Publish Checklist

```bash
# 1. Final security scan
grep -r "password" . --exclude-dir=.git --exclude-dir=node_modules
grep -r "secret" . --exclude-dir=.git --exclude-dir=node_modules
grep -r "api_key" . --exclude-dir=.git --exclude-dir=node_modules

# 2. Verify .gitignore
git ls-files | grep -E '\.(env|db)$'  # Should return nothing

# 3. Clean working directory
git status  # Should show "working tree clean"

# 4. Create/merge to main branch
git checkout main
git merge feature/dual-view-projects

# 5. Tag release (optional)
git tag -a v1.0.0 -m "Initial public release"

# 6. Push to GitHub
git remote add origin https://github.com/YourUsername/ProjectGoat.git
git push -u origin main
git push origin --tags  # If you created tags
```

## ✅ Post-Publish

### Immediate Actions
- [ ] Verify repository is accessible
- [ ] Check all files rendered correctly
- [ ] Test clone from GitHub works
- [ ] Verify README displays properly
- [ ] Check LICENSE is recognized by GitHub

### Optional Enhancements
- [ ] Add GitHub Actions for CI/CD
- [ ] Create releases with binaries
- [ ] Set up project board
- [ ] Add badge shields to README
- [ ] Create demo deployment

## 🔒 Security Best Practices

### What NEVER to commit:
- ❌ `.env` files with real credentials
- ❌ Database files (`*.db`)
- ❌ API keys or tokens
- ❌ Private keys or certificates
- ❌ Personal information
- ❌ Large binary files (>100MB)

### What's SAFE to commit:
- ✅ Source code (Python, TypeScript, etc.)
- ✅ Configuration templates (`.env.example`)
- ✅ Documentation (Markdown files)
- ✅ Test files
- ✅ Small static assets (logos, icons)
- ✅ Deployment configuration (Procfile, railway.json)

## 🆘 If You Accidentally Commit Secrets

1. **Immediately rotate/revoke the credential**
2. **Remove from git history** (see above)
3. **Force push** (if repository is private)
4. **Contact GitHub support** if credential was pushed to public repo

Remember: Once pushed to a public repository, assume the secret is compromised!

---

## Ready to Publish?

Once all checkboxes above are complete:

```bash
# Final push to GitHub
git push origin main

# 🎉 Your repository is now public!
```

**Note**: This checklist assumes you're publishing under `TeamGoat` organization or your personal GitHub account. Adjust accordingly.
