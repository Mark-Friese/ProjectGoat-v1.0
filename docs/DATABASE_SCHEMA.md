# ProjectGoat - Database Schema

## Database: SQLite

## Tables

### 1. users
User accounts and profiles

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Unique user identifier |
| name | VARCHAR(200) | NOT NULL | User's full name |
| email | VARCHAR(200) | NOT NULL, UNIQUE | User's email address |
| role | VARCHAR(20) | NOT NULL | Role: admin, member, viewer |
| avatar | TEXT | NULLABLE | Avatar URL or base64 |
| availability | BOOLEAN | NOT NULL, DEFAULT TRUE | User availability status |

**Indexes:**
- `idx_users_email` ON email

---

### 2. projects
Projects that contain tasks

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Unique project identifier |
| name | VARCHAR(200) | NOT NULL | Project name |
| description | TEXT | NULLABLE | Project description |
| start_date | DATE | NOT NULL | Project start date |
| end_date | DATE | NOT NULL | Project end date |
| color | VARCHAR(7) | NOT NULL | Hex color code (#xxxxxx) |

---

### 3. tasks
Tasks and their properties

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Unique task identifier |
| title | VARCHAR(300) | NOT NULL | Task title |
| description | TEXT | NULLABLE | Task description |
| status | VARCHAR(20) | NOT NULL | todo, in-progress, review, done |
| priority | VARCHAR(10) | NOT NULL | low, medium, high |
| assignee_id | VARCHAR(50) | FOREIGN KEY (users.id), NULLABLE | Assigned user |
| start_date | DATE | NOT NULL | Task start date |
| due_date | DATE | NOT NULL | Task due date |
| progress | INTEGER | NOT NULL, DEFAULT 0 | Progress percentage (0-100) |
| tags | TEXT | NULLABLE | JSON array of tags |
| is_blocked | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether task is blocked |
| is_milestone | BOOLEAN | NOT NULL, DEFAULT FALSE | Whether task is a milestone |
| dependencies | TEXT | NULLABLE | JSON array of task IDs |
| story_points | INTEGER | NULLABLE | Story points estimate |
| parent_id | VARCHAR(50) | FOREIGN KEY (tasks.id), NULLABLE | Parent task ID (subtasks) |
| project_id | VARCHAR(50) | FOREIGN KEY (projects.id), NOT NULL | Project this task belongs to |

**Indexes:**
- `idx_tasks_project` ON project_id
- `idx_tasks_assignee` ON assignee_id
- `idx_tasks_status` ON status
- `idx_tasks_due_date` ON due_date

---

### 4. comments
Comments on tasks

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Unique comment identifier |
| task_id | VARCHAR(50) | FOREIGN KEY (tasks.id), NOT NULL | Task this comment belongs to |
| user_id | VARCHAR(50) | FOREIGN KEY (users.id), NOT NULL | User who wrote comment |
| text | TEXT | NOT NULL | Comment text |
| timestamp | DATETIME | NOT NULL | When comment was created |

**Indexes:**
- `idx_comments_task` ON task_id

---

### 5. blockers
Task blockers

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Unique blocker identifier |
| task_id | VARCHAR(50) | FOREIGN KEY (tasks.id), NOT NULL, UNIQUE | Blocked task (one blocker per task) |
| description | TEXT | NOT NULL | Blocker description |
| created_at | DATETIME | NOT NULL | When blocker was created |
| resolved_at | DATETIME | NULLABLE | When blocker was resolved |
| resolution_notes | TEXT | NULLABLE | How blocker was resolved |

**Indexes:**
- `idx_blockers_task` ON task_id (UNIQUE)

---

### 6. sprints
Sprint planning

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Unique sprint identifier |
| name | VARCHAR(200) | NOT NULL | Sprint name |
| start_date | DATE | NOT NULL | Sprint start date |
| end_date | DATE | NOT NULL | Sprint end date |
| goals | TEXT | NULLABLE | JSON array of goals |
| task_ids | TEXT | NULLABLE | JSON array of task IDs |
| velocity | INTEGER | NOT NULL, DEFAULT 0 | Sprint velocity |

---

### 7. risks
Project risks

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Unique risk identifier |
| title | VARCHAR(300) | NOT NULL | Risk title |
| description | TEXT | NULLABLE | Risk description |
| probability | VARCHAR(10) | NOT NULL | low, medium, high |
| impact | VARCHAR(10) | NOT NULL | low, medium, high |
| owner_id | VARCHAR(50) | FOREIGN KEY (users.id), NOT NULL | Risk owner |
| mitigation | TEXT | NULLABLE | Mitigation plan |
| status | VARCHAR(20) | NOT NULL | open, mitigated, closed |

**Indexes:**
- `idx_risks_owner` ON owner_id
- `idx_risks_status` ON status

---

### 8. issues
Project issues

| Column | Type | Constraints | Description |
|--------|------|------------|-------------|
| id | VARCHAR(50) | PRIMARY KEY | Unique issue identifier |
| title | VARCHAR(300) | NOT NULL | Issue title |
| description | TEXT | NULLABLE | Issue description |
| priority | VARCHAR(10) | NOT NULL | low, medium, high |
| assignee_id | VARCHAR(50) | FOREIGN KEY (users.id), NOT NULL | Assigned user |
| status | VARCHAR(20) | NOT NULL | open, in-progress, resolved |
| related_task_ids | TEXT | NULLABLE | JSON array of related task IDs |
| created_at | DATETIME | NOT NULL | When issue was created |
| resolved_at | DATETIME | NULLABLE | When issue was resolved |

**Indexes:**
- `idx_issues_assignee` ON assignee_id
- `idx_issues_status` ON status

---

## Relationships

```
users (1) ──────────────▶ (N) tasks (assignee)
users (1) ──────────────▶ (N) comments
users (1) ──────────────▶ (N) risks (owner)
users (1) ──────────────▶ (N) issues (assignee)

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
INSERT INTO users VALUES
('u1', 'Sarah Chen', 'sarah@example.com', 'admin', NULL, TRUE),
('u2', 'Marcus Thompson', 'marcus@example.com', 'member', NULL, TRUE);
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
