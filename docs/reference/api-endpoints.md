# ProjectGoat - API Endpoints Documentation

## Base URL

`http://localhost:8000/api`

## Authentication

Session-based authentication using secure HTTP-only session IDs and CSRF tokens.

### Required Headers

- **X-Session-ID**: Session identifier (required for authenticated endpoints)
- **X-CSRF-Token**: CSRF token (required for POST/PUT/DELETE/PATCH operations)

### Exempt Endpoints

- `POST /api/auth/login` - No CSRF token required
- All `GET` requests - No CSRF token required
- `/api/health` - No authentication required

## Response Format

All responses are JSON with standard HTTP status codes:

- `200 OK` - Successful GET/PUT/PATCH
- `201 Created` - Successful POST
- `204 No Content` - Successful DELETE
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Authentication required or invalid session
- `403 Forbidden` - CSRF token invalid or insufficient permissions
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded (login attempts)
- `500 Internal Server Error` - Server error

## Endpoints

### Authentication & Profile

#### POST /api/auth/login

Authenticate user and create session

**Request Body:**

```json
{
  "email": "sarah@example.com",
  "password": "password123"
}
```

**Response:** `200 OK`

```json
{
  "sessionId": "abc123...",
  "csrfToken": "xyz789...",
  "user": {
    "id": "u1",
    "name": "Sarah Chen",
    "email": "sarah@example.com",
    "role": "admin"
  }
}
```

**Rate Limiting:**

- Maximum 5 failed attempts per 15-minute window
- Account locked for 15 minutes after 5 failed attempts

**Error Responses:**

- `400 Bad Request` - Invalid credentials
- `403 Forbidden` - Account locked due to too many failed attempts
- `429 Too Many Requests` - Rate limit exceeded

---

#### POST /api/auth/logout

Logout and invalidate session

**Headers:**

- `X-Session-ID`: Required

**Request Body:**

```json
{
  "session_id": "abc123..."
}
```

**Response:** `200 OK`

```json
{
  "message": "Logged out successfully"
}
```

---

#### GET /api/auth/session

Check if session is valid and get current user

**Query Parameters:**

- `session_id` (optional): Session ID to validate

**Response:** `200 OK`

```json
{
  "user": {
    "id": "u1",
    "name": "Sarah Chen",
    "email": "sarah@example.com",
    "role": "admin"
  },
  "authenticated": true
}
```

**Response (unauthenticated):**

```json
{
  "user": null,
  "authenticated": false
}
```

---

#### POST /api/auth/change-password

Change user password

**Headers:**

- `X-Session-ID`: Required
- `X-CSRF-Token`: Required

**Request Body:**

```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword123"
}
```

**Password Requirements:**

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

**Response:** `200 OK`

```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

**Error Responses:**

- `400 Bad Request` - Invalid current password or weak new password
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Invalid CSRF token

---

#### GET /api/users/me

Get current user's profile with login history

**Headers:**

- `X-Session-ID`: Required

**Response:** `200 OK`

```json
{
  "id": "u1",
  "name": "Sarah Chen",
  "email": "sarah@example.com",
  "role": "admin",
  "createdAt": "2025-11-19T00:00:00Z",
  "lastLoginAt": "2025-11-21T10:08:57Z",
  "passwordChangedAt": "2025-11-21T10:15:39Z",
  "loginHistory": [
    {
      "ipAddress": "127.0.0.1",
      "userAgent": "Mozilla/5.0...",
      "attemptedAt": "2025-11-21T10:08:57Z",
      "success": true
    },
    {
      "ipAddress": "127.0.0.1",
      "userAgent": "Mozilla/5.0...",
      "attemptedAt": "2025-11-21T09:30:22Z",
      "success": false
    }
  ]
}
```

**Error Responses:**

- `401 Unauthorized` - Not authenticated

---

#### PUT /api/users/me

Update current user's profile (name and email only)

**Headers:**

- `X-Session-ID`: Required
- `X-CSRF-Token`: Required

**Request Body:**

```json
{
  "name": "Sarah Chen Updated",
  "email": "sarah.new@example.com"
}
```

**Response:** `200 OK`

```json
{
  "id": "u1",
  "name": "Sarah Chen Updated",
  "email": "sarah.new@example.com",
  "role": "admin"
}
```

**Notes:**

- Users cannot change their own role (privilege escalation protection)
- Only name and email can be updated via this endpoint

**Error Responses:**

- `400 Bad Request` - Invalid input or attempted role change
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Invalid CSRF token or attempted to change role

---

#### GET /api/settings/current-user

Get current user ID from application settings

**Response:** `200 OK`

```json
{
  "userId": "u1"
}
```

---

#### PUT /api/settings/current-user

Set current user ID in application settings

**Headers:**

- `X-CSRF-Token`: Required

**Request Body:**

```json
{
  "user_id": "u1"
}
```

**Response:** `200 OK`

```json
{
  "message": "Current user updated successfully",
  "userId": "u1"
}
```

---

### Users

#### GET /api/users

List all users

**Response:**

```json
[
  {
    "id": "u1",
    "name": "Sarah Chen",
    "email": "sarah@example.com",
    "role": "admin",
    "avatar": null,
    "availability": true
  }
]
```

#### GET /api/users/{id}

Get specific user

**Response:**

```json
{
  "id": "u1",
  "name": "Sarah Chen",
  "email": "sarah@example.com",
  "role": "admin",
  "avatar": null,
  "availability": true
}
```

#### POST /api/users

Create new user

**Request Body:**

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "role": "member",
  "avatar": null,
  "availability": true
}
```

**Response:** `201 Created` with created user

#### PUT /api/users/{id}

Update existing user

**Request Body:**

```json
{
  "name": "John Doe Updated",
  "email": "john.new@example.com",
  "role": "admin",
  "availability": false
}
```

**Response:** `200 OK` with updated user

---

### Projects

#### GET /api/projects

List all projects

**Response:**

```json
[
  {
    "id": "p1",
    "name": "Website Redesign",
    "description": "Complete overhaul of company website",
    "startDate": "2025-11-01",
    "endDate": "2025-12-31",
    "color": "#3b82f6"
  }
]
```

#### GET /api/projects/{id}

Get specific project

**Response:** Single project object

#### POST /api/projects

Create new project

**Request Body:**

```json
{
  "name": "New Project",
  "description": "Project description",
  "startDate": "2025-01-01",
  "endDate": "2025-12-31",
  "color": "#ef4444"
}
```

**Response:** `201 Created` with created project

#### PUT /api/projects/{id}

Update existing project

**Request Body:** Same as POST

**Response:** `200 OK` with updated project

#### DELETE /api/projects/{id}

Delete project

**Response:** `204 No Content`

---

### Tasks

#### GET /api/tasks

List all tasks with optional filtering

**Query Parameters:**

- `project_id` (optional) - Filter by project
- `assignee_id` (optional) - Filter by assignee
- `status` (optional) - Filter by status
- `is_blocked` (optional) - Filter blocked tasks
- `limit` (optional) - Pagination limit
- `offset` (optional) - Pagination offset

**Example:** `/api/tasks?project_id=p1&status=in-progress`

**Response:**

```json
[
  {
    "id": "t1",
    "title": "Design mockups",
    "description": "Create high-fidelity mockups",
    "status": "in-progress",
    "priority": "high",
    "assigneeId": "u1",
    "startDate": "2025-11-01",
    "dueDate": "2025-11-15",
    "progress": 60,
    "tags": ["design", "ui"],
    "isBlocked": false,
    "blocker": null,
    "isMilestone": false,
    "dependencies": [],
    "storyPoints": 5,
    "parentId": null,
    "comments": [],
    "projectId": "p1"
  }
]
```

#### GET /api/tasks/{id}

Get specific task with all details (including comments)

**Response:** Single task object with comments array populated

#### POST /api/tasks

Create new task

**Request Body:**

```json
{
  "title": "New Task",
  "description": "Task description",
  "status": "todo",
  "priority": "medium",
  "assigneeId": "u2",
  "startDate": "2025-11-20",
  "dueDate": "2025-11-30",
  "progress": 0,
  "tags": ["feature"],
  "isBlocked": false,
  "isMilestone": false,
  "dependencies": [],
  "storyPoints": 3,
  "projectId": "p1"
}
```

**Response:** `201 Created` with created task

#### PUT /api/tasks/{id}

Update existing task

**Request Body:** Same as POST (partial updates supported)

**Response:** `200 OK` with updated task

#### PATCH /api/tasks/{id}/status

Update only task status (optimized endpoint)

**Request Body:**

```json
{
  "status": "done"
}
```

**Response:** `200 OK` with updated task

#### DELETE /api/tasks/{id}

Delete task

**Response:** `204 No Content`

---

### Comments

#### POST /api/tasks/{task_id}/comments

Add comment to task

**Request Body:**

```json
{
  "userId": "u1",
  "text": "This looks good, let's proceed"
}
```

**Response:** `201 Created` with created comment

```json
{
  "id": "c1",
  "userId": "u1",
  "text": "This looks good, let's proceed",
  "timestamp": "2025-11-18T10:30:00Z"
}
```

#### DELETE /api/comments/{id}

Delete comment

**Response:** `204 No Content`

---

### Blockers

#### POST /api/tasks/{task_id}/blocker

Add blocker to task

**Request Body:**

```json
{
  "description": "Waiting for API documentation"
}
```

**Response:** `201 Created` with created blocker

#### PUT /api/blockers/{id}/resolve

Resolve blocker

**Request Body:**

```json
{
  "resolutionNotes": "API docs received and reviewed"
}
```

**Response:** `200 OK` with updated blocker

#### DELETE /api/blockers/{id}

Remove blocker

**Response:** `204 No Content`

---

### Risks

#### GET /api/risks

List all risks

**Response:**

```json
[
  {
    "id": "r1",
    "title": "Budget overrun",
    "description": "Project might exceed budget",
    "probability": "medium",
    "impact": "high",
    "ownerId": "u1",
    "mitigation": "Track expenses weekly",
    "status": "open"
  }
]
```

#### GET /api/risks/{id}

Get specific risk

**Response:** Single risk object

#### POST /api/risks

Create new risk

**Request Body:**

```json
{
  "title": "Resource shortage",
  "description": "Team member might leave",
  "probability": "low",
  "impact": "high",
  "ownerId": "u1",
  "mitigation": "Cross-train team members",
  "status": "open"
}
```

**Response:** `201 Created` with created risk

#### PUT /api/risks/{id}

Update existing risk

**Request Body:** Same as POST

**Response:** `200 OK` with updated risk

#### DELETE /api/risks/{id}

Delete risk

**Response:** `204 No Content`

---

### Issues

#### GET /api/issues

List all issues

**Query Parameters:**

- `status` (optional) - Filter by status
- `assignee_id` (optional) - Filter by assignee

**Response:**

```json
[
  {
    "id": "i1",
    "title": "Bug in login flow",
    "description": "Users can't log in with special characters",
    "priority": "high",
    "assigneeId": "u2",
    "status": "in-progress",
    "relatedTaskIds": ["t5", "t6"],
    "createdAt": "2025-11-15T09:00:00Z",
    "resolvedAt": null
  }
]
```

#### GET /api/issues/{id}

Get specific issue

**Response:** Single issue object

#### POST /api/issues

Create new issue

**Request Body:**

```json
{
  "title": "Performance problem",
  "description": "Dashboard loads slowly",
  "priority": "medium",
  "assigneeId": "u3",
  "status": "open",
  "relatedTaskIds": ["t10"]
}
```

**Response:** `201 Created` with created issue

#### PUT /api/issues/{id}

Update existing issue

**Request Body:** Same as POST (partial updates supported)

**Response:** `200 OK` with updated issue

#### PATCH /api/issues/{id}/resolve

Resolve issue

**Response:** `200 OK` with updated issue (resolvedAt timestamp set)

#### DELETE /api/issues/{id}

Delete issue

**Response:** `204 No Content`

---

### Sprints

#### GET /api/sprints

List all sprints

**Response:**

```json
[
  {
    "id": "s1",
    "name": "Sprint 1",
    "startDate": "2025-11-01",
    "endDate": "2025-11-14",
    "goals": ["Complete login flow", "Set up CI/CD"],
    "taskIds": ["t1", "t2", "t3"],
    "velocity": 25
  }
]
```

#### POST /api/sprints

Create new sprint

**Request Body:**

```json
{
  "name": "Sprint 2",
  "startDate": "2025-11-15",
  "endDate": "2025-11-28",
  "goals": ["Build dashboard"],
  "taskIds": [],
  "velocity": 0
}
```

**Response:** `201 Created` with created sprint

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Validation error: field 'email' is required"
}
```

### 404 Not Found

```json
{
  "detail": "Task with id 't999' not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

## CORS Configuration

Development:

```python
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001"
]
```

Production:

```python
origins = ["http://localhost:8000"]
```

## Rate Limiting

None (local application, single user)

## Pagination

- Default limit: 100 items
- Max limit: 1000 items
- Use `limit` and `offset` query parameters

## Date Formats

- ISO 8601 format: `YYYY-MM-DD` for dates
- ISO 8601 format: `YYYY-MM-DDTHH:mm:ssZ` for datetimes

## Field Naming

- **Backend (Python):** snake_case
- **Frontend (TypeScript):** camelCase
- **API:** camelCase (Pydantic alias configuration)
