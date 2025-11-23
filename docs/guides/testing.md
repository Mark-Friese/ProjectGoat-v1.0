# Testing Guide

**Status:** 🚧 In Progress

## Overview

ProjectGoat has comprehensive testing infrastructure covering both backend (Python/pytest) and end-to-end (Playwright) tests.

## Backend Testing

### Running Backend Tests

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux

# Run all backend tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest backend/tests/test_auth.py

# Run specific test class
python -m pytest backend/tests/test_api_endpoints.py::TestTasksAPI

# Run specific test method
python -m pytest backend/tests/test_api_endpoints.py::TestTasksAPI::test_create_task
```

### Running Tests with Coverage

```bash
# Run tests with coverage report
python -m pytest --cov=backend

# Generate HTML coverage report
python -m pytest --cov=backend --cov-report=html

# View HTML report
# Open htmlcov/index.html in your browser
```

### Test Structure

**Location:** `backend/tests/`

**Key Files:**
- `conftest.py` - Test fixtures and configuration
- `test_api_endpoints.py` - API endpoint tests
- `test_auth.py` - Authentication and session tests
- `test_rate_limiting.py` - Rate limiting tests

### Test Fixtures

Available fixtures (from `conftest.py`):
- `db_session` - In-memory test database session
- `client` - FastAPI test client
- `sample_users` - Pre-created test users
- `sample_projects` - Pre-created test projects
- `sample_tasks` - Pre-created test tasks
- `authenticated_client` - Returns (client, session_id, csrf_token, user)

### Example: Writing a Test

```python
def test_create_task(authenticated_client, sample_projects):
    client, session_id, csrf_token, user = authenticated_client
    project = sample_projects[0]

    headers = {"X-Session-ID": session_id, "X-CSRF-Token": csrf_token}

    response = client.post(
        "/api/tasks",
        json={
            "title": "New Task",
            "description": "Test task",
            "status": "To Do",
            "priority": "medium",
            "project_id": project.id
        },
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Task"
```

## End-to-End Testing

### Running E2E Tests

```bash
# Install Playwright browsers (first time only)
npx playwright install

# Run all E2E tests
npm run test:e2e

# Run E2E tests in headed mode (see browser)
npx playwright test --headed

# Run specific test file
npx playwright test tests/e2e/auth.spec.ts

# Run tests in debug mode
npx playwright test --debug
```

### E2E Test Structure

**Location:** `tests/e2e/`

**Test Files:**
- `auth.spec.ts` - Login/logout flows
- `tasks.spec.ts` - Task management
- Additional test files for other features

### Playwright Configuration

**Config:** `playwright.config.ts`

**Key Settings:**
- Base URL: `http://localhost:3000`
- Browser: Chromium
- Automatic server startup (backend + frontend)
- Screenshots on failure
- HTML reporter

### Example: E2E Test

```typescript
import { test, expect } from '@playwright/test';

test('user can create a task', async ({ page }) => {
  // Login
  await page.goto('/');
  await page.fill('input[type="email"]', 'sarah@example.com');
  await page.fill('input[type="password"]', 'password123');
  await page.click('button[type="submit"]');

  // Create task
  await page.click('button:has-text("New Task")');
  await page.fill('input[name="title"]', 'Test Task');
  await page.fill('textarea[name="description"]', 'Test Description');
  await page.click('button:has-text("Create")');

  // Verify task appears
  await expect(page.locator('text=Test Task')).toBeVisible();
});
```

## Test Data

### Test Database

Backend tests use an in-memory SQLite database created fresh for each test session. This is configured in `backend/tests/conftest.py`.

### Test Users

Default test users (created by fixtures):
- Sarah (Admin) - `sarah@example.com` / `password123`
- Mike (Member) - `mike@example.com` / `password123`
- Jane (Viewer) - `jane@example.com` / `password123`

## Coverage

### Viewing Coverage Reports

After running tests with coverage:

```bash
# Terminal report (shows immediately)
python -m pytest --cov=backend

# HTML report (detailed, interactive)
python -m pytest --cov=backend --cov-report=html
# Open htmlcov/index.html

# XML report (for CI/CD)
python -m pytest --cov=backend --cov-report=xml
```

### Coverage Configuration

Configured in `pyproject.toml`:
- **Source:** backend/
- **Omit:** tests/, migrations/, venvs/
- **Branch coverage:** Enabled
- **Target:** Aim for >80% coverage

## Continuous Integration

### Pre-commit Hooks

Tests run automatically via pre-commit hooks (configured in `.pre-commit-config.yaml`).

### Future: GitHub Actions

*TODO: Add GitHub Actions workflow for automated testing on push/PR*

## Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError` when running tests
- **Solution:** Ensure virtual environment is activated

**Issue:** Tests fail with database errors
- **Solution:** Tests use in-memory DB, should be isolated. Check for test database pollution.

**Issue:** E2E tests timeout
- **Solution:** Ensure backend and frontend servers start properly. Check `playwright.config.ts` webServer settings.

**Issue:** Port already in use
- **Solution:** Kill processes on ports 3000 (frontend) and 8000 (backend)

## Best Practices

1. **Test Isolation:** Each test should be independent
2. **Use Fixtures:** Leverage pytest fixtures for common setup
3. **Clear Names:** Test names should describe what they test
4. **Assertions:** Use descriptive assertion messages
5. **Clean Up:** Tests should clean up after themselves (fixtures handle this)
6. **Fast Tests:** Keep unit tests fast, use E2E sparingly
7. **Coverage:** Aim for >80% but focus on critical paths

## Contributing

When adding new features:
1. Write tests for new API endpoints
2. Write tests for new components (when unit tests added)
3. Add E2E tests for critical user flows
4. Run tests locally before committing
5. Ensure coverage doesn't decrease

---

**Next Steps:**
- [ ] Add frontend unit tests (React Testing Library)
- [ ] Add GitHub Actions CI/CD
- [ ] Increase coverage to 90%+
- [ ] Add performance tests
- [ ] Add load testing

**See Also:**
- [Contributing Guide](CONTRIBUTING.md)
- [API Reference](../reference/api-endpoints.md)
