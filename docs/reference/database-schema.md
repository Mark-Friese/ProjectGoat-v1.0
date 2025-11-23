# ProjectGoat - Database Schema

## Database: SQLite

## Tables

### 1. users

User accounts and profiles

| Column                | Type         | Constraints             | Description                           |
| --------------------- | ------------ | ----------------------- | ------------------------------------- |
| id                    | VARCHAR(50)  | PRIMARY KEY             | Unique user identifier                |
| name                  | VARCHAR(200) | NOT NULL                | User's full name                      |
| email                 | VARCHAR(200) | NOT NULL, UNIQUE        | User's email address                  |
| role                  | VARCHAR(20)  | NOT NULL                | Role: admin, member, viewer           |
| avatar                | TEXT         | NULLABLE                | Avatar URL or base64                  |
| availability          | BOOLEAN      | NOT NULL, DEFAULT TRUE  | User availability status              |
| password_hash         | VARCHAR(255) | NOT NULL                | bcrypt password hash                  |
| is_active             | BOOLEAN      | NOT NULL, DEFAULT TRUE  | Whether account is active             |
| must_change_password  | BOOLEAN      | NOT NULL, DEFAULT FALSE | Require password change on next login |
| password_changed_at   | DATETIME     | NULLABLE                | When password was last changed        |
| created_at            | DATETIME     | NOT NULL                | When user was created                 |
| last_login_at         | DATETIME     | NULLABLE                | Last successful login                 |
| failed_login_attempts | INTEGER      | NOT NULL, DEFAULT 0     | Count of consecutive failed logins    |
| account_locked_until  | DATETIME     | NULLABLE                | Account lockout expiration            |

**Indexes:**

- `idx_users_email` ON email

---

### 2. projects

Projects that contain tasks

| Column      | Type         | Constraints | Description               |
| ----------- | ------------ | ----------- | ------------------------- |
| id          | VARCHAR(50)  | PRIMARY KEY | Unique project identifier |
| name        | VARCHAR(200) | NOT NULL    | Project name              |
| description | TEXT         | NULLABLE    | Project description       |
| start_date  | DATE         | NOT NULL    | Project start date        |
| end_date    | DATE         | NOT NULL    | Project end date          |
| color       | VARCHAR(7)   | NOT NULL    | Hex color code (#xxxxxx)  |

---

### 3. tasks

Tasks and their properties

| Column       | Type         | Constraints                         | Description                     |
| ------------ | ------------ | ----------------------------------- | ------------------------------- |
| id           | VARCHAR(50)  | PRIMARY KEY                         | Unique task identifier          |
| title        | VARCHAR(300) | NOT NULL                            | Task title                      |
| description  | TEXT         | NULLABLE                            | Task description                |
| status       | VARCHAR(20)  | NOT NULL                            | todo, in-progress, review, done |
| priority     | VARCHAR(10)  | NOT NULL                            | low, medium, high               |
| assignee_id  | VARCHAR(50)  | FOREIGN KEY (users.id), NULLABLE    | Assigned user                   |
| start_date   | DATE         | NOT NULL                            | Task start date                 |
| due_date     | DATE         | NOT NULL                            | Task due date                   |
| progress     | INTEGER      | NOT NULL, DEFAULT 0                 | Progress percentage (0-100)     |
| tags         | TEXT         | NULLABLE                            | JSON array of tags              |
| is_blocked   | BOOLEAN      | NOT NULL, DEFAULT FALSE             | Whether task is blocked         |
| is_milestone | BOOLEAN      | NOT NULL, DEFAULT FALSE             | Whether task is a milestone     |
| dependencies | TEXT         | NULLABLE                            | JSON array of task IDs          |
| story_points | INTEGER      | NULLABLE                            | Story points estimate           |
| parent_id    | VARCHAR(50)  | FOREIGN KEY (tasks.id), NULLABLE    | Parent task ID (subtasks)       |
| project_id   | VARCHAR(50)  | FOREIGN KEY (projects.id), NOT NULL | Project this task belongs to    |

**Indexes:**

- `idx_tasks_project` ON project_id
- `idx_tasks_assignee` ON assignee_id
- `idx_tasks_status` ON status
- `idx_tasks_due_date` ON due_date

---

### 4. comments

Comments on tasks

| Column    | Type        | Constraints                      | Description                  |
| --------- | ----------- | -------------------------------- | ---------------------------- |
| id        | VARCHAR(50) | PRIMARY KEY                      | Unique comment identifier    |
| task_id   | VARCHAR(50) | FOREIGN KEY (tasks.id), NOT NULL | Task this comment belongs to |
| user_id   | VARCHAR(50) | FOREIGN KEY (users.id), NOT NULL | User who wrote comment       |
| text      | TEXT        | NOT NULL                         | Comment text                 |
| timestamp | DATETIME    | NOT NULL                         | When comment was created     |

**Indexes:**

- `idx_comments_task` ON task_id

---

### 5. blockers

Task blockers

| Column           | Type        | Constraints                              | Description                         |
| ---------------- | ----------- | ---------------------------------------- | ----------------------------------- |
| id               | VARCHAR(50) | PRIMARY KEY                              | Unique blocker identifier           |
| task_id          | VARCHAR(50) | FOREIGN KEY (tasks.id), NOT NULL, UNIQUE | Blocked task (one blocker per task) |
| description      | TEXT        | NOT NULL                                 | Blocker description                 |
| created_at       | DATETIME    | NOT NULL                                 | When blocker was created            |
| resolved_at      | DATETIME    | NULLABLE                                 | When blocker was resolved           |
| resolution_notes | TEXT        | NULLABLE                                 | How blocker was resolved            |

**Indexes:**

- `idx_blockers_task` ON task_id (UNIQUE)

---

### 6. sprints

Sprint planning

| Column     | Type         | Constraints         | Description              |
| ---------- | ------------ | ------------------- | ------------------------ |
| id         | VARCHAR(50)  | PRIMARY KEY         | Unique sprint identifier |
| name       | VARCHAR(200) | NOT NULL            | Sprint name              |
| start_date | DATE         | NOT NULL            | Sprint start date        |
| end_date   | DATE         | NOT NULL            | Sprint end date          |
| goals      | TEXT         | NULLABLE            | JSON array of goals      |
| task_ids   | TEXT         | NULLABLE            | JSON array of task IDs   |
| velocity   | INTEGER      | NOT NULL, DEFAULT 0 | Sprint velocity          |

---

### 7. risks

Project risks

| Column      | Type         | Constraints                      | Description             |
| ----------- | ------------ | -------------------------------- | ----------------------- |
| id          | VARCHAR(50)  | PRIMARY KEY                      | Unique risk identifier  |
| title       | VARCHAR(300) | NOT NULL                         | Risk title              |
| description | TEXT         | NULLABLE                         | Risk description        |
| probability | VARCHAR(10)  | NOT NULL                         | low, medium, high       |
| impact      | VARCHAR(10)  | NOT NULL                         | low, medium, high       |
| owner_id    | VARCHAR(50)  | FOREIGN KEY (users.id), NOT NULL | Risk owner              |
| mitigation  | TEXT         | NULLABLE                         | Mitigation plan         |
| status      | VARCHAR(20)  | NOT NULL                         | open, mitigated, closed |

**Indexes:**

- `idx_risks_owner` ON owner_id
- `idx_risks_status` ON status

---

### 8. issues

Project issues

| Column           | Type         | Constraints                      | Description                    |
| ---------------- | ------------ | -------------------------------- | ------------------------------ |
| id               | VARCHAR(50)  | PRIMARY KEY                      | Unique issue identifier        |
| title            | VARCHAR(300) | NOT NULL                         | Issue title                    |
| description      | TEXT         | NULLABLE                         | Issue description              |
| priority         | VARCHAR(10)  | NOT NULL                         | low, medium, high              |
| assignee_id      | VARCHAR(50)  | FOREIGN KEY (users.id), NOT NULL | Assigned user                  |
| status           | VARCHAR(20)  | NOT NULL                         | open, in-progress, resolved    |
| related_task_ids | TEXT         | NULLABLE                         | JSON array of related task IDs |
| created_at       | DATETIME     | NOT NULL                         | When issue was created         |
| resolved_at      | DATETIME     | NULLABLE                         | When issue was resolved        |

**Indexes:**

- `idx_issues_assignee` ON assignee_id
- `idx_issues_status` ON status

---

### 9. sessions

User authentication sessions

| Column           | Type         | Constraints                      | Description                               |
| ---------------- | ------------ | -------------------------------- | ----------------------------------------- |
| id               | VARCHAR(255) | PRIMARY KEY                      | Unique session identifier (token)         |
| user_id          | VARCHAR(50)  | FOREIGN KEY (users.id), NOT NULL | User this session belongs to              |
| created_at       | DATETIME     | NOT NULL                         | When session was created                  |
| expires_at       | DATETIME     | NOT NULL                         | Session expiration (30 days)              |
| last_accessed    | DATETIME     | NOT NULL                         | Last request timestamp (for idle timeout) |
| is_active        | BOOLEAN      | NOT NULL, DEFAULT TRUE           | Whether session is active                 |
| last_activity_at | DATETIME     | NOT NULL                         | Last activity (updated on each request)   |
| ip_address       | VARCHAR(45)  | NULLABLE                         | IP address of session creation            |
| user_agent       | TEXT         | NULLABLE                         | Browser user agent                        |
| csrf_token       | VARCHAR(255) | NULLABLE                         | CSRF token for this session               |

**Indexes:**

- `idx_sessions_user` ON user_id
- `idx_sessions_expires` ON expires_at
- `idx_sessions_active` ON is_active

---

### 10. app_settings

Application-wide settings

| Column     | Type         | Constraints | Description                        |
| ---------- | ------------ | ----------- | ---------------------------------- |
| key        | VARCHAR(100) | PRIMARY KEY | Setting key                        |
| value      | TEXT         | NOT NULL    | Setting value (JSON or plain text) |
| updated_at | DATETIME     | NOT NULL    | When setting was last updated      |

**Note:** Used to store current_user_id for single-user mode

---

### 11. login_attempts

Login attempt tracking for rate limiting and security

| Column         | Type         | Constraints               | Description                  |
| -------------- | ------------ | ------------------------- | ---------------------------- |
| id             | INTEGER      | PRIMARY KEY AUTOINCREMENT | Unique attempt identifier    |
| email          | VARCHAR(200) | NOT NULL                  | Email used for login attempt |
| ip_address     | VARCHAR(45)  | NULLABLE                  | IP address of attempt        |
| user_agent     | TEXT         | NULLABLE                  | Browser user agent           |
| attempted_at   | DATETIME     | NOT NULL                  | When attempt was made        |
| success        | BOOLEAN      | NOT NULL                  | Whether login succeeded      |
| failure_reason | VARCHAR(255) | NULLABLE                  | Reason for failure           |

**Indexes:**

- `idx_login_attempts_email` ON email
- `idx_login_attempts_time` ON attempted_at

---

### 12. user_permissions

Role-based permissions (future use)

| Column   | Type        | Constraints               | Description                           |
| -------- | ----------- | ------------------------- | ------------------------------------- |
| id       | INTEGER     | PRIMARY KEY AUTOINCREMENT | Unique permission identifier          |
| role     | VARCHAR(20) | NOT NULL                  | Role: admin, member, viewer           |
| resource | VARCHAR(50) | NOT NULL                  | Resource type (tasks, projects, etc.) |
| action   | VARCHAR(20) | NOT NULL                  | Action: create, read, update, delete  |
| allowed  | BOOLEAN     | NOT NULL, DEFAULT FALSE   | Whether action is allowed             |

**Indexes:**

- `idx_permissions_role` ON role
- `idx_permissions_resource` ON resource

---

### 13. audit_log

Audit trail for sensitive operations (future use)

| Column         | Type         | Constraints                      | Description                       |
| -------------- | ------------ | -------------------------------- | --------------------------------- |
| id             | INTEGER      | PRIMARY KEY AUTOINCREMENT        | Unique log entry identifier       |
| user_id        | VARCHAR(50)  | FOREIGN KEY (users.id), NULLABLE | User who performed action         |
| action         | VARCHAR(100) | NOT NULL                         | Action performed                  |
| target_user_id | VARCHAR(50)  | FOREIGN KEY (users.id), NULLABLE | Target user (for user management) |
| details        | TEXT         | NULLABLE                         | JSON details of action            |
| ip_address     | VARCHAR(45)  | NULLABLE                         | IP address                        |
| timestamp      | DATETIME     | NOT NULL                         | When action occurred              |

**Indexes:**

- `idx_audit_user` ON user_id
- `idx_audit_timestamp` ON timestamp

---

## Relationships

```
users (1) ──────────────▶ (N) tasks (assignee)
users (1) ──────────────▶ (N) comments
users (1) ──────────────▶ (N) risks (owner)
users (1) ──────────────▶ (N) issues (assignee)
users (1) ──────────────▶ (N) sessions
users (1) ──────────────▶ (N) audit_log (user_id)
users (1) ──────────────▶ (N) audit_log (target_user_id)

projects (1) ────────────▶ (N) tasks

tasks (1) ───────────────▶ (N) comments
tasks (1) ───────────────▶ (1) blockers
tasks (1) ───────────────▶ (N) tasks (parent_id, self-referential)
```

## Entity Relationship Diagram

```
┌─────────────┐
│   users     │
├─────────────┤
│ id (PK)     │────┐
│ name        │    │
│ email       │    │
│ role        │    │
│ avatar      │    │
│ availability│    │
└─────────────┘    │
                   │
                   ├──────────┐
                   │          │
                   ▼          ▼
       ┌─────────────┐   ┌─────────────┐
       │  projects   │   │   tasks     │
       ├─────────────┤   ├─────────────┤
       │ id (PK)     │──▶│ id (PK)     │
       │ name        │   │ title       │
       │ description │   │ description │
       │ start_date  │   │ status      │
       │ end_date    │   │ priority    │
       │ color       │   │ assignee_id │(FK)
       └─────────────┘   │ project_id  │(FK)
                         │ parent_id   │(FK, self)
                         │ ...         │
                         └─────────────┘
                              │
                     ┌────────┴────────┐
                     ▼                 ▼
              ┌──────────────┐  ┌──────────────┐
              │  comments    │  │  blockers    │
              ├──────────────┤  ├──────────────┤
              │ id (PK)      │  │ id (PK)      │
              │ task_id (FK) │  │ task_id (FK) │
              │ user_id (FK) │  │ description  │
              │ text         │  │ created_at   │
              │ timestamp    │  │ resolved_at  │
              └──────────────┘  └──────────────┘

       ┌─────────────┐       ┌─────────────┐
       │   risks     │       │   issues    │
       ├─────────────┤       ├─────────────┤
       │ id (PK)     │       │ id (PK)     │
       │ title       │       │ title       │
       │ owner_id(FK)│       │ assignee_id │(FK)
       │ ...         │       │ ...         │
       └─────────────┘       └─────────────┘
```

## Sample Data

### Users

```sql
-- Note: Password hashes are bcrypt hashes of "password123"
INSERT INTO users (id, name, email, role, avatar, availability, password_hash,
                   is_active, must_change_password, created_at) VALUES
('u1', 'Sarah Chen', 'sarah@example.com', 'admin', NULL, TRUE,
 '$2b$12$...', TRUE, FALSE, '2025-11-19 00:00:00'),
('u2', 'Marcus Thompson', 'marcus@example.com', 'member', NULL, TRUE,
 '$2b$12$...', TRUE, FALSE, '2025-11-19 00:00:00');
```

### Projects

```sql
INSERT INTO projects VALUES
('p1', 'Website Redesign', 'Complete overhaul', '2025-11-01', '2025-12-31', '#3b82f6');
```

### Tasks

```sql
INSERT INTO tasks VALUES
('t1', 'Design mockups', 'Create high-fidelity mockups', 'in-progress', 'high',
 'u1', '2025-11-01', '2025-11-15', 60, '["design","ui"]', FALSE, FALSE, '[]',
 5, NULL, 'p1');
```

## Migration Strategy

### Initial Setup

1. Run `init_db.py` to create all tables
2. Populate with mock data from frontend
3. Verify relationships

### Future Migrations

- Use Alembic for schema migrations
- Version control database changes
- Support rollbacks

## Performance Optimizations

### Indexes

All foreign keys and frequently queried columns are indexed

### Query Patterns

- Use JOINs to fetch related data in single query
- Pagination for large result sets
- Filter at database level, not in Python

### Connection Management

- Connection pooling via SQLAlchemy
- Automatic session cleanup
- Transaction management

## Data Types

### Dates

- Stored as ISO 8601 strings
- Converted to Python datetime objects by SQLAlchemy
- Frontend receives as strings, converts to Date objects

### JSON Fields

- tags, dependencies, goals, task_ids, related_task_ids
- Stored as TEXT, parsed as JSON
- Validated by Pydantic schemas

### Booleans

- Stored as INTEGER (0/1) in SQLite
- SQLAlchemy converts automatically
