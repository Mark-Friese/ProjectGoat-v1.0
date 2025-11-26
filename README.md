# ProjectGoat

A comprehensive project management application designed for personal use on a work laptop. ProjectGoat provides task tracking, team management, sprint planning, and risk/issue management with a modern, intuitive interface.

## Features

### Core Functionality

- **Task Management**: Create, assign, and track tasks with multiple status states
  - Subtasks (parent-child relationships)
  - Task progress tracking (0-100%)
  - Story points for agile planning
  - Milestone markers
  - Task dependencies
  - Custom tags
- **Multiple Views**: Dashboard, Kanban Board, List View, Gantt Chart, Calendar, Team Workload, Reports
- **User Management**: Full user CRUD with role tracking (Admin, Member, Viewer - enforcement planned)
- **Project Management**: Organize work into projects with deadlines, priorities, and color coding
- **Sprint Planning**: Plan and track sprints with start/end dates and velocity tracking
- **Risk & Issue Tracking**: Identify and manage project risks and issues
- **Blocker Management**: Track and resolve task dependencies and blockers

### Authentication & Security

- **Session-Based Authentication**: Secure login/logout with bcrypt password hashing
- **Session Management**: 30-minute idle timeout, 8-hour absolute timeout
- **CSRF Protection**: Database-backed CSRF tokens for all state-changing operations
- **Rate Limiting**: 5 login attempts per 15 minutes with automatic account lockout
- **Password Policies**: Strong password requirements (8+ chars, mixed case, numbers, special chars)
- **Profile Management**: View/edit profile, change password, view login history
- **Activity Tracking**: Real-time session activity monitoring

## Technology Stack

### Frontend

- React 18.3.1 with TypeScript
- Vite (build tool and dev server)
- Radix UI component library
- Lucide React icons
- TailwindCSS for styling

### Backend

- FastAPI (Python async web framework)
- SQLAlchemy ORM with SQLite database
- Pydantic for data validation
- bcrypt for password hashing

## Quick Start

### Prerequisites

- Python 3.9+ (3.13 recommended)
- Node.js 16+
- Git

### Development Setup

1. **Clone Repository**

   ```bash
   git clone <repository-url>
   cd ProjectGoat
   ```

2. **Set Up Python Virtual Environment**

   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate virtual environment
   # Windows:
   .venv\Scripts\activate
   # Mac/Linux:
   source .venv/bin/activate
   ```

3. **Install Backend Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Frontend Dependencies**

   ```bash
   npm install
   ```

5. **Initialize Database**

   ```bash
   python backend/init_db.py
   ```

6. **Start Backend Server**

   ```bash
   # In terminal 1 (with venv activated):
   python run.py
   ```

7. **Start Frontend Development Server**

   ```bash
   # In terminal 2:
   npm run dev
   ```

8. **Access Application**
   - Frontend: <http://localhost:3000>
   - Backend API: <http://localhost:8000>
   - API Documentation: <http://localhost:8000/docs>

### Default Credentials

On first run, the database is initialized with a default admin user:

- **Email**: `sarah@example.com`
- **Password**: `password123`

**Important**: Change the password immediately after first login via Profile > Security > Change Password

## Project Structure

```text
ProjectGoat/
├── backend/                 # FastAPI backend
│   ├── main.py             # API endpoints
│   ├── database.py         # Database configuration
│   ├── models.py           # SQLAlchemy models
│   ├── schemas.py          # Pydantic schemas
│   ├── crud.py             # Database operations
│   ├── auth.py             # Authentication & sessions
│   ├── csrf.py             # CSRF protection
│   ├── rate_limiter.py     # Login rate limiting
│   ├── migrations/         # Database migrations
│   └── init_db.py          # Database initialization
├── src/                     # React frontend
│   ├── components/         # React components
│   ├── services/           # API service layer
│   ├── utils/              # Utility functions
│   └── App.tsx             # Main application
├── docs/                    # Documentation
└── .claude/                 # Claude Code commands
```

## Session Management

ProjectGoat uses secure session-based authentication with the following timeout policies:

- **Idle Timeout**: 30 minutes of inactivity
- **Absolute Timeout**: 8 hours from login (regardless of activity)
- **Warning Dialog**: Users receive a 2-minute warning before automatic logout

Sessions are tracked server-side with activity monitoring. All sessions are invalidated when a user changes their password (except the current session).

## Security Features

### Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Rate Limiting

- Maximum 5 failed login attempts per 15-minute window
- Automatic 15-minute account lockout after exceeding limit
- Failed attempts tracked with IP address and user agent

### CSRF Protection

- All state-changing requests (POST/PUT/DELETE/PATCH) require CSRF token
- Tokens stored in database and automatically included in API requests
- Exempt endpoints: /api/auth/login, GET requests, /api/health

## Production Deployment

For production deployment instructions, see [Deployment Guide](docs/guides/deployment.md).

Quick deployment steps:

1. Build frontend: `npm run build`
2. Install backend dependencies: `pip install -r requirements.txt`
3. Initialize database: `python backend/init_db.py`
4. Start application: `python run.py`
5. Access at: <http://localhost:8000>

## Documentation

Comprehensive documentation is available in the `docs/` directory:

### Deployment Strategy

**📋 [Complete Deployment Strategy](docs/DEPLOYMENT-STRATEGY.md)** - Executive summary and overview

- [Production Deployment Planning](docs/guides/production-deployment-planning.md) - Platform comparisons, costs, and web hosting strategy
- [Mobile Strategy](docs/guides/mobile-strategy.md) - PWA, Capacitor, and iOS App Store deployment

### Guides

- [Deployment Guide](docs/guides/deployment.md) - Deployment procedures and configuration
- [Testing Guide](docs/guides/testing.md) - Running and writing tests
- [Frontend Development](docs/guides/frontend-development.md) - Frontend architecture and development
- [Database Migrations](docs/guides/migrations.md) - Database migration guide
- [Troubleshooting](docs/guides/troubleshooting.md) - Common issues and solutions
- [Environment Variables](docs/guides/environment-variables.md) - Configuration reference
- [Automation Setup](docs/guides/automation-setup.md) - Pre-commit hooks and code quality

### Reference

- [API Endpoints](docs/reference/api-endpoints.md) - Complete API documentation
- [Database Schema](docs/reference/database-schema.md) - Database structure and relationships

### Architecture

- [System Design](docs/architecture/system-design.md) - System architecture overview
- [Requirements](docs/architecture/requirements.md) - Feature requirements and specifications
- [Constraints](docs/architecture/constraints.md) - Environment constraints and limitations
- [Neurodivergent Features](docs/architecture/neurodivergent-features.md) - Accessibility feature planning

## Development

### Running Tests

```bash
# Backend tests
python -m pytest

# Backend tests with coverage
python -m pytest --cov=backend --cov-report=html

# End-to-end tests
npm run test:e2e
```

For detailed testing instructions, see the [Testing Guide](docs/guides/testing.md).

### Database Migrations

Database migrations are located in `backend/migrations/` and should be run in order:

1. `001_initial_schema.py` - Core tables
2. `002_add_security_features.py` - Security tables
3. `003_add_csrf_to_sessions.py` - CSRF token column

### API Documentation

Interactive API documentation is available at <http://localhost:8000/docs> when the backend is running.

## Troubleshooting

### Database Issues

If you encounter database errors, try reinitializing:

```bash
rm projectgoat.db
python backend/init_db.py
```

### Session Expired Errors

If you're repeatedly logged out:

- Check system clock (sessions use timestamps)
- Verify backend is running
- Clear browser localStorage and log in again

### CSRF Token Errors

If you get "Invalid CSRF token" errors:

- Ensure you're logged in
- Try logging out and back in
- Check that backend migrations have been run

## License

Proprietary - For internal use only

## Support

For issues or questions, contact the development team.
