# ProjectGoat

A comprehensive project management application designed for personal use on a work laptop. ProjectGoat provides task tracking, team management, sprint planning, and risk/issue management with a modern, intuitive interface.

## Features

### Core Functionality

- **Task Management**: Create, assign, and track tasks with multiple status states
- **Multiple Views**: Dashboard, Kanban Board, List View, Gantt Chart, Calendar, Team Workload, Reports
- **User Management**: Full user CRUD with role-based access (Admin, Member, Viewer)
- **Project Management**: Organize work into projects with deadlines and priorities
- **Sprint Planning**: Plan and track sprints with start/end dates
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

### Development Setup

1. **Install Dependencies**

   ```bash
   npm install
   ```

2. **Initialize Database**

   ```bash
   python backend/init_db.py
   ```

3. **Start Development Server**

   ```bash
   npm run dev
   ```

4. **Access Application**
   - Frontend: <http://localhost:5173>
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

For production deployment instructions, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

Quick deployment steps:

1. Build frontend: `npm run build`
2. Install backend dependencies: `pip install -r backend/requirements.txt`
3. Initialize database: `python backend/init_db.py`
4. Start application: `python run.py`
5. Access at: <http://localhost:8000>

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [REQUIREMENTS.md](docs/REQUIREMENTS.md) - Feature requirements and specifications
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture and design
- [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) - Database schema and relationships
- [API_ENDPOINTS.md](docs/API_ENDPOINTS.md) - API endpoint documentation
- [DEPLOYMENT.md](docs/DEPLOYMENT.md) - Deployment guide and procedures
- [CONSTRAINTS.md](docs/CONSTRAINTS.md) - Environment constraints and limitations

## Development

### Running Tests

```bash
# Frontend tests (when implemented)
npm test

# Backend tests (when implemented)
pytest
```

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
