# GitHub Actions CI/CD Setup Guide

**Status:** 📋 Planning - Not Yet Implemented
**Priority:** High
**Estimated Effort:** 2-3 hours
**Last Updated:** 2025-11-23

## Overview

This guide provides complete instructions for setting up GitHub Actions CI/CD workflows for ProjectGoat, including automated testing, code quality checks, and build verification.

### What Will Be Automated

After setup, GitHub Actions will automatically:
- ✅ Run backend tests on every push/PR
- ✅ Run E2E tests on every push/PR
- ✅ Check code quality (linting, formatting)
- ✅ Verify frontend builds successfully
- ✅ Generate test coverage reports
- ✅ Upload test artifacts for debugging

### Benefits

- **Catch bugs early** - Tests run before merge
- **Enforce quality** - Code must pass checks
- **Fast feedback** - Results in minutes
- **Team confidence** - Automated validation
- **Professional** - Industry-standard CI/CD

---

## Prerequisites

### Before You Begin

1. **Repository on GitHub:**
   - ProjectGoat must be pushed to GitHub
   - Public or private repository (both supported)

2. **Tests working locally:**
   ```bash
   python -m pytest          # Backend tests pass
   npm run test:e2e          # E2E tests pass
   ```

3. **Pre-commit hooks configured:**
   - Hooks should be set up and working
   - See [Automation Setup Guide](../guides/automation-setup.md)

### GitHub Actions Limits

**Public repositories:**
- ✅ Unlimited minutes (free)
- ✅ All features available

**Private repositories:**
- 2,000 minutes/month free
- Additional minutes available (paid)

---

## Workflow Overview

We'll create 4 workflows:

| Workflow | Purpose | Runs On | Duration |
|----------|---------|---------|----------|
| **Backend Tests** | Run pytest with coverage | Backend changes | ~2-3 min |
| **E2E Tests** | Run Playwright tests | Any code changes | ~3-5 min |
| **Code Quality** | Pre-commit hooks | Any code changes | ~1-2 min |
| **Build** | Verify frontend builds | Frontend changes | ~2-3 min |

**Total CI time per push:** ~5-8 minutes (runs in parallel)

---

## Part 1: Backend Tests Workflow

### Create Workflow File

**File:** `.github/workflows/backend-tests.yml`

```yaml
name: Backend Tests

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'backend/**'
      - 'requirements*.txt'
      - 'pyproject.toml'
      - '.github/workflows/backend-tests.yml'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'backend/**'
      - 'requirements*.txt'
      - 'pyproject.toml'

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python 3.13
      uses: actions/setup-python@v5
      with:
        python-version: '3.13'
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests with coverage
      run: |
        python -m pytest \
          --cov=backend \
          --cov-report=xml \
          --cov-report=term \
          --verbose

    - name: Upload coverage to Codecov (optional)
      uses: codecov/codecov-action@v4
      if: github.event_name == 'push'
      with:
        file: ./coverage.xml
        flags: backend
        name: backend-coverage
        token: ${{ secrets.CODECOV_TOKEN }}
      continue-on-error: true

    - name: Upload coverage artifact
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: backend-coverage
        path: |
          coverage.xml
          htmlcov/
        retention-days: 7
```

### What This Workflow Does

1. **Triggers:**
   - On push to main/develop
   - On pull requests
   - Only when backend files change

2. **Steps:**
   - Checks out code
   - Sets up Python 3.13
   - Caches pip dependencies (faster runs)
   - Installs dependencies
   - Runs pytest with coverage
   - Uploads coverage report (optional Codecov integration)
   - Saves coverage artifacts

3. **Optimizations:**
   - `cache: 'pip'` - Reuses dependencies between runs
   - `paths:` filter - Only runs when backend changes
   - `timeout-minutes: 10` - Prevents hung tests

---

## Part 2: End-to-End Tests Workflow

### Create Workflow File

**File:** `.github/workflows/e2e-tests.yml`

```yaml
name: E2E Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python 3.13
      uses: actions/setup-python@v5
      with:
        python-version: '3.13'
        cache: 'pip'

    - name: Set up Node.js 20
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'

    - name: Install backend dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Install frontend dependencies
      run: npm ci

    - name: Install Playwright browsers
      run: npx playwright install --with-deps chromium

    - name: Run E2E tests
      run: npm run test:e2e
      env:
        CI: true

    - name: Upload Playwright report
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: playwright-report
        path: playwright-report/
        retention-days: 7

    - name: Upload test results
      uses: actions/upload-artifact@v4
      if: failure()
      with:
        name: test-results
        path: test-results/
        retention-days: 7
```

### What This Workflow Does

1. **Triggers:**
   - On every push to main/develop
   - On all pull requests
   - (Runs more frequently as E2E tests the full stack)

2. **Steps:**
   - Sets up Python and Node.js
   - Installs both backend and frontend dependencies
   - Installs Playwright browsers (Chromium only for speed)
   - Runs E2E test suite
   - Uploads reports on failure (for debugging)

3. **Key Points:**
   - Uses `npm ci` instead of `npm install` (faster, more reliable)
   - Only installs Chromium (faster than all browsers)
   - Uploads artifacts even on failure (for debugging)
   - 15-minute timeout (E2E tests can be slow)

---

## Part 3: Code Quality Workflow

### Create Workflow File

**File:** `.github/workflows/code-quality.yml`

```yaml
name: Code Quality

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python 3.13
      uses: actions/setup-python@v5
      with:
        python-version: '3.13'
        cache: 'pip'

    - name: Install pre-commit
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt

    - name: Run pre-commit hooks
      uses: pre-commit/action@v3.0.1

    - name: Show pre-commit results
      if: always()
      run: |
        echo "Pre-commit hooks completed"
        echo "Check the logs above for any issues"
```

### What This Workflow Does

1. **Runs all pre-commit hooks:**
   - Black (Python formatting)
   - isort (Import sorting)
   - flake8 (Linting)
   - Trailing whitespace removal
   - End-of-file fixing
   - YAML/JSON validation
   - And all other configured hooks

2. **Fast execution:**
   - Typically completes in 1-2 minutes
   - Uses pre-commit action (optimized)

3. **Prevents:**
   - Committing unformatted code
   - Style violations
   - Common mistakes

---

## Part 4: Build Verification Workflow

### Create Workflow File

**File:** `.github/workflows/build.yml`

**Note:** Adjust paths based on whether you've renamed src/ to frontend/

```yaml
name: Build Verification

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'src/**'  # Change to 'frontend/**' if renamed
      - 'package*.json'
      - 'vite.config.ts'
      - 'tsconfig*.json'
      - '.github/workflows/build.yml'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'src/**'  # Change to 'frontend/**' if renamed
      - 'package*.json'

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Node.js 20
      uses: actions/setup-node@v4
      with:
        node-version: '20'
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Type check
      run: npx tsc --noEmit

    - name: Build
      run: npm run build

    - name: Upload build artifacts
      uses: actions/upload-artifact@v4
      with:
        name: build
        path: build/
        retention-days: 7

    - name: Check build size
      run: |
        du -sh build/
        echo "Build completed successfully"
```

### What This Workflow Does

1. **Verifies:**
   - TypeScript types are correct
   - Frontend builds without errors
   - Build artifacts are created

2. **Uploads:**
   - Build artifacts (for potential deployment)
   - Build size information

3. **Path filtering:**
   - Only runs when frontend code changes
   - Saves CI minutes

---

## Part 5: Setup & Testing

### Create All Workflow Files

```bash
# Create workflows directory if .github/ doesn't exist yet
# (Should already exist if you moved community files)
mkdir -p .github/workflows

# Create all 4 workflow files
# (Copy content from sections above into each file)
```

### Files to Create

1. `.github/workflows/backend-tests.yml`
2. `.github/workflows/e2e-tests.yml`
3. `.github/workflows/code-quality.yml`
4. `.github/workflows/build.yml`

### Commit and Push

```bash
# Add workflow files
git add .github/workflows/

# Commit
git commit -m "ci: Add GitHub Actions workflows

- Backend tests with coverage
- E2E tests with Playwright
- Code quality checks (pre-commit)
- Build verification

All workflows configured with caching for performance."

# Push to trigger workflows
git push origin main
```

### Monitor First Run

1. **Go to GitHub repository:**
   - Click "Actions" tab
   - Watch workflows run

2. **Check each workflow:**
   - Backend Tests - Should pass
   - E2E Tests - Should pass
   - Code Quality - Should pass
   - Build - Should pass

3. **If any fail:**
   - Click on failed workflow
   - Review logs
   - Fix issues
   - Push fixes
   - Workflows run again automatically

---

## Part 6: Add Status Badges to README

### Create Badges

Add to top of README.md (after title):

```markdown
# ProjectGoat

[![Backend Tests](https://github.com/YourUsername/ProjectGoat/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/YourUsername/ProjectGoat/actions/workflows/backend-tests.yml)
[![E2E Tests](https://github.com/YourUsername/ProjectGoat/actions/workflows/e2e-tests.yml/badge.svg)](https://github.com/YourUsername/ProjectGoat/actions/workflows/e2e-tests.yml)
[![Code Quality](https://github.com/YourUsername/ProjectGoat/actions/workflows/code-quality.yml/badge.svg)](https://github.com/YourUsername/ProjectGoat/actions/workflows/code-quality.yml)
[![Build](https://github.com/YourUsername/ProjectGoat/actions/workflows/build.yml/badge.svg)](https://github.com/YourUsername/ProjectGoat/actions/workflows/build.yml)

A comprehensive project management application...
```

**Replace `YourUsername` with your GitHub username!**

### Badge Benefits

- ✅ Shows build status at a glance
- ✅ Links to workflow runs
- ✅ Professional appearance
- ✅ Builds confidence in code quality

---

## Part 7: Optional Enhancements

### 7.1 Codecov Integration

**Purpose:** Track test coverage over time

**Setup:**
1. Sign up at [codecov.io](https://codecov.io)
2. Add ProjectGoat repository
3. Get Codecov token
4. Add as GitHub secret:
   - Settings → Secrets → Actions
   - New secret: `CODECOV_TOKEN`
5. Workflows already configured to use it

**Badge:**
```markdown
[![codecov](https://codecov.io/gh/YourUsername/ProjectGoat/branch/main/graph/badge.svg)](https://codecov.io/gh/YourUsername/ProjectGoat)
```

### 7.2 Dependabot

**Purpose:** Automated dependency updates

**File:** `.github/dependabot.yml`

```yaml
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "python"

  # JavaScript dependencies
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "javascript"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "github-actions"
```

### 7.3 Branch Protection Rules

**Recommended settings for main branch:**

Settings → Branches → Add rule

- ✅ Require pull request before merging
- ✅ Require status checks to pass before merging
  - Select: backend-tests
  - Select: e2e-tests
  - Select: code-quality
  - Select: build
- ✅ Require branches to be up to date
- ⚠️ Require approvals (if team)

### 7.4 Scheduled Tests

Run tests nightly to catch regressions:

```yaml
# Add to any workflow's 'on:' section
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight UTC
```

---

## Troubleshooting

### Workflow Not Running

**Symptom:** Pushed code but workflow didn't trigger

**Causes:**
1. Workflow file has YAML syntax error
2. Path filters exclude the changed files
3. Branch not in trigger list

**Solutions:**
```bash
# Validate YAML syntax
cat .github/workflows/backend-tests.yml | python -c "import sys, yaml; yaml.safe_load(sys.stdin)"

# Check workflow file is committed
git ls-files .github/workflows/

# Force workflow run (GitHub UI)
# Actions tab → Select workflow → Run workflow
```

### Tests Pass Locally But Fail on CI

**Common causes:**

1. **Environment differences:**
   - Different Python/Node versions
   - Missing environment variables
   - Different database state

2. **Timing issues:**
   - Tests too slow on CI
   - Race conditions in E2E tests

3. **File path issues:**
   - Case sensitivity (Linux vs Windows)
   - Absolute vs relative paths

**Solutions:**
```yaml
# Add debugging
- name: Debug environment
  run: |
    python --version
    node --version
    pwd
    ls -la
```

### Out of Minutes (Private Repos)

**Symptom:** Workflows stop running

**Solution:**
```yaml
# Optimize workflows to use fewer minutes:

# 1. Path filtering (only run when needed)
paths:
  - 'backend/**'

# 2. Reduce test matrix
# Instead of testing Python 3.9, 3.10, 3.11, 3.12, 3.13
# Just test 3.13

# 3. Use caching aggressively
cache: 'pip'
cache: 'npm'

# 4. Only run E2E on main branch
if: github.ref == 'refs/heads/main'
```

### Artifacts Taking Too Much Space

**Symptom:** Storage quota warnings

**Solution:**
```yaml
# Reduce retention
retention-days: 1  # Instead of 7

# Only upload on failure
if: failure()

# Upload smaller artifacts
path: |
  coverage.xml
  # Don't upload htmlcov/ (large)
```

---

## Monitoring & Maintenance

### Check Workflow Health

**Weekly review:**
1. Actions tab → Check success rate
2. Review failed runs
3. Update dependencies if needed
4. Monitor execution times

### Update Workflow Actions

GitHub Actions updates regularly:

```bash
# Check for updates
# Look for warnings in workflow runs about deprecated actions

# Update action versions
# Change: uses: actions/checkout@v3
# To:     uses: actions/checkout@v4
```

### Cost Monitoring (Private Repos)

Settings → Billing → Actions

- Monitor minutes used
- Set spending limit
- Get alerts before limit

---

## Performance Optimization

### Caching Strategy

Already implemented in workflows:

```yaml
# Python caching
- uses: actions/setup-python@v5
  with:
    cache: 'pip'  # ← Caches ~/.cache/pip

# Node caching
- uses: actions/setup-node@v4
  with:
    cache: 'npm'  # ← Caches ~/.npm
```

**Impact:** 2-3x faster dependency installation

### Parallelization

Workflows already run in parallel:
- All 4 workflows trigger simultaneously
- Complete in time of slowest workflow (~5-8 min total)

### Path Filtering

Already implemented:
- Backend tests only run on backend changes
- Build only runs on frontend changes
- E2E runs on all changes (tests full stack)

---

## Security Considerations

### Secrets Management

**Never commit:**
- API keys
- Passwords
- Tokens
- Private keys

**Use GitHub Secrets instead:**
```yaml
env:
  SECRET_KEY: ${{ secrets.MY_SECRET }}
```

### Pull Request Security

**Important:** GitHub Actions from forks:
- Run with limited permissions
- Cannot access secrets
- Prevents malicious PRs from stealing secrets

### Dependency Security

Dependabot will:
- Alert on vulnerable dependencies
- Create PRs to update them
- Run security audits

---

## Checklist

Before considering setup complete:

- [ ] All 4 workflow files created in `.github/workflows/`
- [ ] Workflows committed and pushed to GitHub
- [ ] All workflows ran successfully
- [ ] Status badges added to README.md
- [ ] Badges show "passing" status
- [ ] Tested workflow by making a small change
- [ ] Reviewed workflow logs for warnings
- [ ] (Optional) Codecov integration set up
- [ ] (Optional) Dependabot enabled
- [ ] (Optional) Branch protection rules configured
- [ ] Team notified about CI/CD setup

---

## Estimated Timeline

- Workflow file creation: 1 hour
- Testing and debugging: 1-2 hours
- Optional enhancements: 30-60 minutes
- Documentation: Included above
- **Total: 2-3 hours**

---

## Next Steps After Setup

1. **Make it a habit:**
   - Always check CI status before merging
   - Fix failing tests promptly
   - Keep workflows green

2. **Iterate:**
   - Add more tests over time
   - Improve coverage
   - Add deployment workflows (future)

3. **Share knowledge:**
   - Point team to this guide
   - Document any customizations
   - Update guide as needed

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Setup Python Action](https://github.com/actions/setup-python)
- [Setup Node Action](https://github.com/actions/setup-node)
- [Pre-commit Action](https://github.com/pre-commit/action)
- [Codecov Action](https://github.com/codecov/codecov-action)

---

**Status:** Ready to implement
**Risk Level:** Low
**Reversibility:** High (can disable/delete workflows anytime)
**Dependencies:** GitHub repository must exist
