# Code Quality Automation Setup Guide

**ProjectGoat Pre-commit Hooks** Automated code quality checks for backend
(Python) and frontend (TypeScript/React)

---

## Quick Start

```bash
# 1. Install development dependencies
pip install -r requirements-dev.txt

# 2. Install pre-commit hooks
pre-commit install

# 3. (Optional) Run on all files to test
pre-commit run --all-files

# 4. Done! Hooks now run automatically on commit
git commit -m "Your message"
```

---

## What Gets Checked Automatically

Every time you commit, these checks run automatically:

### ✅ Backend (Python in `backend/`)

- **Black** - Auto-formats Python code to consistent style
- **isort** - Sorts Python imports alphabetically
- **flake8** - Checks for style issues and potential bugs
- **mypy** (optional) - Type checking

### ✅ Frontend (TypeScript/React in `src/`)

- **Prettier** - Auto-formats TypeScript/React/CSS/JSON
- **ESLint** - Checks for TypeScript and React best practices

### ✅ All Files

- Remove trailing whitespace
- Ensure files end with newline
- Validate YAML syntax
- Validate JSON syntax
- Prevent large files (>500KB)
- Check for merge conflict markers

---

## Installation

### Prerequisites

```bash
# Python 3.11+ required
python --version

# Node.js/npm required
node --version
npm --version
```

### Step 1: Install Python Dependencies

```bash
pip install -r requirements-dev.txt
```

This installs:

- `pre-commit` - Hook framework
- `black` - Python formatter
- `isort` - Import sorter
- `flake8` - Python linter
- Plus testing tools (pytest, mypy, etc.)

### Step 2: Install Git Hooks

```bash
pre-commit install
```

This installs hooks into `.git/hooks/` directory.

### Step 3: Test Installation

```bash
# Run hooks on all files (not just changed files)
pre-commit run --all-files
```

This will:

- Format all Python files with Black
- Sort all Python imports
- Format all TypeScript files with Prettier
- Check for style issues

**Note:** First run downloads hook dependencies (slow), subsequent runs are
fast!

---

## How It Works

### Normal Workflow

```bash
# Edit some files
vim src/components/MyComponent.tsx
vim backend/main.py

# Stage changes
git add .

# Commit (hooks run automatically)
git commit -m "Add new feature"

↓ Pre-commit runs automatically ↓

✅ black....................................Passed
✅ isort....................................Passed
✅ flake8...................................Passed
✅ prettier.................................Passed
✅ eslint...................................Passed
✅ trailing-whitespace......................Passed

[main abc123] Add new feature
 2 files changed, 50 insertions(+)
```

### When Checks Fail

```bash
git commit -m "Add feature"

✅ black....................................Passed
✅ isort....................................Passed
❌ flake8...................................Failed

backend/main.py:42:1: E302 expected 2 blank lines, found 1

❌ Commit blocked!
```

**Fix the issue and try again:**

```bash
# Fix the file (or let Black fix it)
black backend/main.py

# Stage the fixes
git add backend/main.py

# Try commit again
git commit -m "Add feature"
✅ All checks pass - commit succeeds!
```

---

## Configuration Files

All configuration is in the project root:

| File                      | Purpose                                     |
| ------------------------- | ------------------------------------------- |
| `.pre-commit-config.yaml` | Defines which hooks to run                  |
| `pyproject.toml`          | Python tool settings (Black, isort, pytest) |
| `.flake8`                 | Python linter settings                      |
| `.prettierrc`             | Frontend formatter settings                 |
| `.prettierignore`         | Files to exclude from Prettier              |

---

## Customization

### Enable Strict Type Checking (mypy)

Edit `.pre-commit-config.yaml`:

```yaml
# Uncomment these lines:
- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.8.0
  hooks:
    - id: mypy
```

### Adjust Line Length

Edit `pyproject.toml` and `.flake8`:

```toml
[tool.black]
line-length = 120  # Change from 100
```

```ini
[flake8]
max-line-length = 120  # Change from 100
```

### Add More Hooks

Browse available hooks: https://pre-commit.com/hooks.html

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit # Security linter
```

---

## Bypassing Hooks (Emergency Only!)

### Skip All Hooks

```bash
git commit --no-verify -m "Emergency fix"
```

### Skip Specific Hook

```bash
SKIP=eslint git commit -m "Skip only ESLint"
SKIP=black,flake8 git commit -m "Skip multiple"
```

**⚠️ Use sparingly!** Bypassing hooks defeats the purpose.

---

## Troubleshooting

### Hooks Not Running

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Verify installation
ls .git/hooks/pre-commit  # Should exist
```

### Hook Failures

```bash
# Update hook versions
pre-commit autoupdate

# Clean hook cache
pre-commit clean

# Reinstall all hooks
pre-commit install --install-hooks
```

### Slow Performance

First run is slow (downloads dependencies). Subsequent runs are fast.

**If consistently slow:**

```bash
# Check what's slow
pre-commit run --all-files --verbose

# Disable slow hooks temporarily
SKIP=mypy,eslint git commit -m "Fast commit"
```

### Import Errors in Python

If you see `ModuleNotFoundError`:

```bash
# Ensure in virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements-dev.txt
```

---

## Manual Tool Usage

You can run tools manually outside of commits:

### Python Backend

```bash
# Format code
black backend/

# Sort imports
isort backend/

# Lint code
flake8 backend/

# Type check
mypy backend/

# Run all
black backend/ && isort backend/ && flake8 backend/
```

### TypeScript Frontend

```bash
# Format code
npx prettier --write src/

# Lint code
npm run lint

# Type check
npx tsc --noEmit
```

---

## CI/CD Integration

Pre-commit works great with GitHub Actions:

```yaml
# .github/workflows/ci.yml
jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - uses: pre-commit/action@v3.0.0
```

This runs ALL pre-commit hooks on CI.

---

## IDE Integration

### VS Code

Install extensions:

- **Python** (Microsoft) - Supports Black, flake8
- **ESLint** (Microsoft)
- **Prettier** (Prettier)

Settings:

```json
{
  "editor.formatOnSave": true,
  "python.formatting.provider": "black",
  "python.linting.flake8Enabled": true,
  "eslint.autoFixOnSave": true,
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### PyCharm / IntelliJ

- **Settings** → **Tools** → **Black** → Enable
- **Settings** → **Languages** → **Prettier** → Enable

---

## What's Different from Normal Development?

**Before:**

```bash
# Write code however
# Commit without checks
git commit -m "Add feature"
# Hope code review catches issues
```

**After:**

```bash
# Write code however
# Hooks auto-fix most issues
git commit -m "Add feature"
# Black formats, isort organizes, Prettier formats
# Only real issues block commit
```

**Benefits:**

- ✅ Consistent code style automatically
- ✅ Catch bugs before committing
- ✅ Less time in code review arguing about style
- ✅ Learn best practices through feedback

---

## Advanced Usage

### Run Specific Hook

```bash
pre-commit run black --all-files
pre-commit run prettier --all-files
pre-commit run flake8 --files backend/main.py
```

### Update Hook Versions

```bash
# Check for updates
pre-commit autoupdate

# Updates .pre-commit-config.yaml to latest versions
```

### Hook on Push (not just commit)

```bash
pre-commit install --hook-type pre-push
```

Now hooks run on `git push` instead of commit.

---

## FAQ

**Q: Why is the first run so slow?** A: Pre-commit downloads hook environments.
Cached after first run.

**Q: Can I use this without pre-commit framework?** A: Yes! Run tools manually:
`black backend/`, `prettier --write src/`

**Q: Do hooks run on unchanged files?** A: No, only on files you've staged for
commit.

**Q: What if I disagree with Black's formatting?** A: Black is opinionated and
non-configurable. This is intentional. If team agrees, can switch to autopep8
(configurable).

**Q: Will this slow down my commits?** A: Slightly (1-3 seconds for small
changes). But catches issues immediately, saving much more time debugging later.

**Q: Can I run this on Windows?** A: Yes! All tools are cross-platform.

---

## Getting Help

If you encounter issues:

1. Check this guide's Troubleshooting section
2. Run `pre-commit run --verbose` to see detailed output
3. Check `.pre-commit-config.yaml` for hook configuration
4. Search: https://pre-commit.com/
5. Ask team for help!

---

## Summary

Pre-commit hooks provide:

- ⚡ **Fast feedback** - Catch issues in seconds, not hours
- 🎨 **Automatic formatting** - Never think about code style again
- 🐛 **Bug prevention** - Catch common mistakes before they reach main
- 📚 **Learning tool** - See what good code looks like
- 🆓 **Free** - No cost, runs on your machine

**Recommended:** Use pre-commit hooks from day one on all projects!

---

**Happy coding!** 🚀
