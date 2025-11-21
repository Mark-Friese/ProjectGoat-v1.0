# ProjectGoat - System Architecture

## Overview
ProjectGoat uses a **decoupled architecture** with a React frontend and Python FastAPI backend, connected via REST API.

## Architecture Diagram

```
┌─────────────────────────────────────────────┐
│           Work Laptop (localhost)           │
│                                             │
│  ┌────────────────┐      ┌───────────────┐ │
│  │   Browser      │      │  Python       │ │
│  │                │─────▶│  FastAPI      │ │
│  │  React App     │ HTTP │  Backend      │ │
│  │  (Static)      │◀─────│  (Port 8000)  │ │
│  └────────────────┘      └───────┬───────┘ │
│                                  │         │
│                          ┌───────▼───────┐ │
│                          │  SQLite DB    │ │
│                          │ projectgoat.db│ │
│                          └───────────────┘ │
└─────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **Framework:** React 18.3.1
- **Language:** TypeScript
- **Build Tool:** Vite 6.3.5
- **Styling:** Tailwind CSS v4.1.3
- **UI Components:** Radix UI + shadcn/ui
- **Charts:** Recharts
- **Icons:** Lucide React
- **State Management:** React useState/useEffect (local state)

### Backend
- **Framework:** FastAPI
- **Language:** Python 3.9+
- **ORM:** SQLAlchemy 2.0
- **Validation:** Pydantic
- **Server:** Uvicorn
- **Database:** SQLite3

### Database
- **Type:** SQLite (file-based, embedded)
- **File:** `projectgoat.db`
- **Benefits:**
  - No server installation required
  - Single file storage
  - ACID compliant
  - Built into Python
  - Portable

## Component Architecture

### Frontend Layer
```
src/
├── components/          # React components
│   ├── DashboardView.tsx
│   ├── KanbanView.tsx
│   ├── ListView.tsx
│   ├── GanttView.tsx
│   ├── CalendarView.tsx
│   ├── WorkloadView.tsx
│   ├── TeamView.tsx
│   ├── ReportsView.tsx
│   ├── TaskDialog.tsx
│   └── ui/             # Reusable UI components
├── services/           # API communication layer
│   ├── api.ts          # Base API client with CSRF & session handling
│   ├── auth.ts         # Authentication API calls
│   ├── tasks.ts        # Task API calls
│   ├── users.ts        # User API calls
│   └── projects.ts     # Project API calls
├── types/              # TypeScript type definitions
├── assets/             # Static assets (images, logo)
└── App.tsx             # Main app component
```

### Backend Layer
```
backend/
├── main.py             # FastAPI application & routes
├── database.py         # Database connection & session
├── models.py           # SQLAlchemy ORM models
├── schemas.py          # Pydantic request/response schemas
├── crud.py             # Database operations
├── auth.py             # Authentication & session management
├── csrf.py             # CSRF protection middleware
├── rate_limiter.py     # Login rate limiting
├── migrations/         # Database migrations
├── init_db.py          # Database initialization
└── requirements.txt    # Python dependencies
```

## Data Flow

### Reading Data (GET)
```
1. User interacts with UI
2. React component calls API service
3. Service sends HTTP GET to FastAPI
4. FastAPI queries SQLite via SQLAlchemy
5. Data returned as JSON
6. React updates UI
```

### Writing Data (POST/PUT/DELETE)
```
1. User submits form/action
2. React validates and sends to API service
3. Service sends HTTP POST/PUT/DELETE to FastAPI
4. FastAPI validates with Pydantic schemas
5. SQLAlchemy executes database operation
6. Success/error response returned
7. React updates UI optimistically or on confirmation
```

## API Design

### RESTful Principles
- Resource-based URLs
- HTTP methods: GET, POST, PUT, DELETE, PATCH
- JSON request/response bodies
- HTTP status codes: 200, 201, 400, 401 (Unauthorized), 403 (Forbidden), 404, 429 (Rate Limited), 500

### Base URL
- **Development:** `http://localhost:8000/api`
- **Production:** `http://localhost:8000/api`

### Endpoints Structure
```
/api/auth           - Authentication (login, logout, session, change-password)
/api/users          - User management & profile
/api/projects       - Project management
/api/tasks          - Task management
/api/risks          - Risk tracking
/api/issues         - Issue tracking
/api/settings       - Application settings
```

## Database Schema

See [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) for detailed table definitions.

### Key Design Decisions
- **UUID strings for IDs** - Flexible, globally unique
- **ISO date strings** - Easy serialization
- **JSON arrays for tags** - Simple, no joins needed for tags
- **Foreign keys** - Maintain referential integrity
- **Indexes** - On frequently queried fields (project_id, assignee_id, status)

## Deployment Model

### Development (Current Setup)
```
Terminal 1: npm run dev (frontend dev server)
Terminal 2: python main.py (backend server)
```

### Production (Work Laptop)
```
frontend/           # Built static files (npm run build)
backend/            # Python server
projectgoat.db      # Database file
run.py              # Startup script (starts backend, serves frontend)
```

**Single Command:** `python run.py`

## Security

### Authentication & Session Management

- **Password Security:**
  - bcrypt password hashing with automatic salt generation
  - Strong password requirements (8+ characters, uppercase, lowercase, number, special char)
  - Password change functionality with current password verification
  - Password change timestamp tracking

- **Session Management:**
  - Database-backed session storage (survives server restarts)
  - Session timeouts:
    - Idle timeout: 30 minutes of inactivity
    - Absolute timeout: 8 hours from login
    - 30-day maximum session expiration
  - Session activity tracking via middleware
  - Automatic session invalidation on password change (except current)
  - Session includes IP address and user agent tracking

- **CSRF Protection:**
  - Database-backed CSRF tokens (token stored in sessions table)
  - Automatic validation on all state-changing operations (POST/PUT/DELETE/PATCH)
  - Token regeneration on password change
  - Exempt endpoints: /api/auth/login, GET requests, /api/health
  - Frontend automatically includes X-CSRF-Token header

- **Rate Limiting:**
  - Maximum 5 failed login attempts per 15-minute window
  - Automatic 15-minute account lockout after exceeding limit
  - Failed attempts tracked with IP address and user agent
  - Automatic cleanup of old attempts on successful login
  - Implemented in `rate_limiter.py` module

- **Profile & Access Control:**
  - Role-based access (admin, member, viewer)
  - Users can view/edit their own profile (name, email)
  - Users cannot change their own role (privilege escalation protection)
  - Login history tracking (last 10 attempts with success/failure)

### Network Security

- CORS configured for localhost only
- No external network exposure
- Designed for internal work laptop use

### Future Considerations (If Multi-User/External)

- HTTPS/TLS encryption
- Additional role-based permissions
- OAuth/SSO integration
- Enhanced audit logging

## Performance Considerations

### Frontend
- Code splitting (Vite)
- Lazy loading components
- Virtual scrolling for long lists
- Optimistic UI updates

### Backend
- Database connection pooling
- Indexed queries
- Pagination for large datasets
- Efficient SQLAlchemy queries

### Database
- SQLite performs well for single-user scenarios
- Indexes on foreign keys and frequently filtered fields
- PRAGMA optimizations for better performance

## Scalability

### Current (Single User)
- SQLite is sufficient
- FastAPI handles concurrent requests efficiently
- No bottlenecks expected

### Future (Multi-User)
- Consider PostgreSQL for concurrent writes
- Add caching layer (Redis)
- WebSocket for real-time updates

## Error Handling

### Frontend
- Try-catch blocks around API calls
- User-friendly error messages
- Loading states
- Retry mechanisms

### Backend
- HTTP exception handlers
- Input validation (Pydantic)
- Database transaction rollbacks
- Logging for debugging

## Testing Strategy

### Frontend
- Component testing (React Testing Library)
- E2E testing (Playwright/Cypress)

### Backend
- Unit tests (pytest)
- API tests (FastAPI TestClient)
- Database tests (in-memory SQLite)

## Build & Deployment Process

1. **Build Frontend:**
   ```bash
   npm run build
   # Output: build/ directory
   ```

2. **Package Backend:**
   ```bash
   # Copy backend files
   # Include projectgoat.db (or init_db.py)
   ```

3. **Create Deployment Package:**
   ```
   ProjectGoat-Deployment/
   ├── frontend/
   ├── backend/
   ├── run.py
   └── README.md
   ```

4. **Deploy to Work Laptop:**
   - Copy folder
   - Install Python dependencies
   - Run application

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed steps.
