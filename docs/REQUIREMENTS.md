# ProjectGoat - Requirements Document

## Project Overview
**Name:** ProjectGoat by TeamGoat
**Type:** Project Management & Team Collaboration Tool
**Purpose:** Track tasks, projects, team workload, and progress in a restricted work environment

## Core Features

### 1. Task Management
- Create, read, update, delete tasks
- Task properties:
  - Title, description
  - Status: todo, in-progress, review, done
  - Priority: low, medium, high
  - Assignee
  - Start date and due date
  - Progress percentage
  - Tags
  - Story points
  - Dependencies between tasks
  - Milestones
- Block/unblock tasks with blocker descriptions
- Task comments with timestamps
- Parent-child task relationships

### 2. Multiple Views
- **Dashboard** - Overview with statistics and charts
- **Kanban Board** - Drag-and-drop columns by status
- **List View** - Tabular view with filtering and sorting
- **Gantt Chart** - Timeline visualization
- **Calendar View** - Calendar-based task view
- **Team Workload** - Workload distribution across team members
- **Team Members** - Team directory with availability status
- **Reports** - Analytics, risks, and issues tracking

### 3. User Management
- User profiles (name, email, role, avatar)
- Roles: admin, member, viewer
- Availability status
- User assignments to tasks

### 4. Project Management
- Multiple projects support
- Project properties:
  - Name, description
  - Start and end dates
  - Color coding
- Switch between projects

### 5. Sprint Planning
- Sprint creation and management
- Sprint goals
- Velocity tracking
- Task assignment to sprints

### 6. Risk & Issue Tracking
- **Risks:**
  - Title, description
  - Probability and impact levels
  - Risk owner
  - Mitigation plans
  - Status: open, mitigated, closed
- **Issues:**
  - Title, description
  - Priority levels
  - Assignee
  - Status: open, in-progress, resolved
  - Related tasks
  - Resolution tracking

### 7. Data Persistence
- All data must persist across:
  - Application restarts
  - Browser closes
  - Browser data clears
- Data stored in local SQLite database

### 8. Authentication & Security

- **User Authentication:**
  - Email and password based login
  - Secure password hashing with bcrypt
  - Session-based authentication
  - Logout functionality
- **Session Management:**
  - Idle timeout: 30 minutes of inactivity
  - Absolute timeout: 8 hours from login
  - Session activity tracking
  - Warning dialog 2 minutes before timeout
  - Automatic session invalidation on password change
- **Password Security:**
  - Strong password requirements (8+ chars, mixed case, numbers, special chars)
  - Password change functionality
  - Password change tracking
- **Security Features:**
  - CSRF protection on all state-changing operations
  - Rate limiting: 5 failed attempts per 15 minutes
  - Account lockout: 15 minutes after exceeding failed attempts
  - IP address and user agent tracking
- **Profile Management:**
  - View and edit user profile (name, email)
  - View login history (last 10 attempts)
  - Role-based access display
  - Account creation date tracking

## Non-Functional Requirements

### Performance
- Fast load times (< 2 seconds)
- Smooth UI interactions
- Efficient data queries

### Usability
- Intuitive interface
- Responsive design (desktop and mobile)
- Clear visual hierarchy
- Accessible components

### Portability
- Single folder deployment
- No installation required (beyond Python)
- Easy to copy between machines

### Reliability
- Data integrity maintained
- Graceful error handling
- No data loss on crashes

## Technical Constraints
See [CONSTRAINTS.md](./CONSTRAINTS.md) for detailed environment limitations

## Future Enhancements (Out of Scope - Phase 1)

- File attachments
- Export to Excel/PDF
- Email notifications
- Time tracking
- Burndown charts
- Custom fields
- Templates
- Webhooks/integrations
