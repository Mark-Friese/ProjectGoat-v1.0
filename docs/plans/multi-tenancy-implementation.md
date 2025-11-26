# Multi-Tenancy Implementation Plan

## Overview

Add multi-team support to ProjectGoat, enabling:
- **Single-team accounts**: One team, users belong only to that team
- **Multi-team accounts**: Users can belong to multiple teams and switch between them
- Both account types register an Admin during initial setup
- Admins can create users directly OR send invitations for self-registration

## Design Decisions

### Account Type Model
- Account type is a **team-level setting**, not user-level
- Single-team: Team is locked to one team, simpler UI
- Multi-team: Users can be invited to multiple teams, team switcher visible

### Data Isolation
- All data (projects, tasks, issues, risks, sprints) scoped to a team
- Users see only their team's data
- Users can belong to multiple teams with different roles per team

---

## Phase 1: Database Schema Changes

### New Tables

#### 1. `teams` table
```sql
CREATE TABLE teams (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    account_type VARCHAR(20) NOT NULL,  -- 'single' or 'multi'
    created_at DATETIME NOT NULL,
    created_by_user_id VARCHAR(50)  -- The admin who created the team
);
```

#### 2. `team_memberships` table (replaces user.role for team context)
```sql
CREATE TABLE team_memberships (
    id VARCHAR(50) PRIMARY KEY,
    team_id VARCHAR(50) NOT NULL REFERENCES teams(id),
    user_id VARCHAR(50) NOT NULL REFERENCES users(id),
    role VARCHAR(20) NOT NULL,  -- 'admin', 'member', 'viewer'
    joined_at DATETIME NOT NULL,
    UNIQUE(team_id, user_id)
);
```

#### 3. `invitations` table
```sql
CREATE TABLE invitations (
    id VARCHAR(50) PRIMARY KEY,
    team_id VARCHAR(50) NOT NULL REFERENCES teams(id),
    email VARCHAR(200) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- role they'll have when they join
    invited_by_user_id VARCHAR(50) NOT NULL REFERENCES users(id),
    token VARCHAR(255) NOT NULL UNIQUE,  -- secure token for invite link
    expires_at DATETIME NOT NULL,
    accepted_at DATETIME,
    created_at DATETIME NOT NULL
);
```

### Modified Tables (add team_id foreign key)

| Table | Change |
|-------|--------|
| `projects` | Add `team_id VARCHAR(50) NOT NULL REFERENCES teams(id)` |
| `tasks` | Already linked via project, no change needed |
| `risks` | Add `team_id VARCHAR(50) NOT NULL REFERENCES teams(id)` |
| `issues` | Add `team_id VARCHAR(50) NOT NULL REFERENCES teams(id)` |
| `sprints` | Add `team_id VARCHAR(50) NOT NULL REFERENCES teams(id)` |
| `users` | Keep global (users can be in multiple teams) |
| `sessions` | Add `current_team_id VARCHAR(50) REFERENCES teams(id)` |

### User Table Changes
- Remove `role` column (now per-team in team_memberships)
- Keep all other fields (name, email, password_hash, etc.)

---

## Phase 2: Backend API Changes

### New Endpoints

#### Registration & Team Setup
```
POST /api/auth/register
  - Creates new team + admin user
  - Body: { teamName, accountType, adminName, adminEmail, adminPassword }
  - Returns: { sessionId, csrfToken, user, team }
```

#### Team Management
```
GET  /api/teams/current          - Get current team details
PUT  /api/teams/current          - Update current team (admin only)
GET  /api/teams                  - List teams user belongs to (multi-team)
POST /api/teams/switch           - Switch to different team
```

#### User Management (Admin)
```
POST /api/teams/current/users    - Admin creates user directly
GET  /api/teams/current/users    - List team members
PUT  /api/teams/current/users/:id - Update member role
DELETE /api/teams/current/users/:id - Remove member from team
```

#### Invitations (Admin)
```
POST /api/invitations            - Create invitation
GET  /api/invitations            - List pending invitations
DELETE /api/invitations/:id      - Revoke invitation
POST /api/invitations/:token/accept - Accept invitation (creates user if needed)
GET  /api/invitations/:token     - Get invitation details (for registration page)
```

### Modified Endpoints (add team filtering)

All existing data endpoints need team context:

```python
# Example: get_projects now filters by team
@app.get("/api/projects")
def list_projects(db: Session = Depends(get_db), auth: AuthContext = Depends(require_auth)):
    return crud.get_projects(db, team_id=auth.team_id)
```

**Endpoints requiring team filter:**
- `/api/projects` - filter by team_id
- `/api/tasks` - filter via project.team_id
- `/api/risks` - filter by team_id
- `/api/issues` - filter by team_id
- `/api/sprints` - filter by team_id
- `/api/users` - return only team members

### Auth Context Changes

```python
class AuthContext:
    user_id: str
    team_id: str
    role: str  # Role in current team
```

Update `require_auth` dependency to:
1. Validate session
2. Get current_team_id from session
3. Verify user is member of that team
4. Return AuthContext with user_id, team_id, and role

---

## Phase 3: Frontend Changes

### New Pages/Components

#### 1. Registration Page (`/register`)
```
- Team name input
- Account type selector (Single-team / Multi-team)
- Admin details (name, email, password)
- Submit creates team + admin + logs in
```

#### 2. Invitation Accept Page (`/invite/:token`)
```
- Shows team name and inviter
- If user exists: just join team
- If new user: create account form
```

#### 3. Team Settings Page (Admin only)
```
- Team name editor
- Account type display
- Member list with role management
- Invitation management (send, revoke)
```

#### 4. Team Switcher (Multi-team only)
```
- Dropdown in header showing current team
- List of user's teams
- Click to switch
```

### Modified Components

#### LoginScreen
- Add "Create new team" link to registration page
- Handle invitation tokens in URL

#### Header/Navigation
- Show current team name
- Add team switcher for multi-team accounts
- Add "Team Settings" link for admins

#### All Data Views
- No changes needed (API handles filtering)
- Data automatically scoped to current team

---

## Phase 4: Migration Strategy

### For Existing Data (Work Laptop)

1. Create default team on first run:
   ```python
   if no_teams_exist():
       create_default_team(name="My Team", account_type="single")
       migrate_existing_data_to_default_team()
   ```

2. Migration steps:
   - Create default team
   - Add team_id to all existing projects, risks, issues, sprints
   - Create team_membership for all existing users
   - First user with role='admin' becomes team admin

### For Render (Fresh Deploy)
- No migration needed
- Users must register to create first team

---

## Phase 5: Implementation Order

### Step 1: Database Schema (Backend)
- [ ] Add Team model
- [ ] Add TeamMembership model
- [ ] Add Invitation model
- [ ] Add team_id to Project, Risk, Issue, Sprint models
- [ ] Add current_team_id to UserSession model
- [ ] Create migration script for existing data

### Step 2: Auth & Registration (Backend)
- [ ] Create `/api/auth/register` endpoint
- [ ] Update `require_auth` to return AuthContext
- [ ] Add team context to session management

### Step 3: Team Management (Backend)
- [ ] Team CRUD endpoints
- [ ] Team switching endpoint
- [ ] Member management endpoints
- [ ] Invitation endpoints

### Step 4: Data Filtering (Backend)
- [ ] Update all CRUD functions with team_id parameter
- [ ] Update all API endpoints to filter by team

### Step 5: Frontend - Registration
- [ ] Create RegistrationPage component
- [ ] Create InvitationAcceptPage component
- [ ] Update routing

### Step 6: Frontend - Team UI
- [ ] Create TeamSettingsPage
- [ ] Create TeamSwitcher component
- [ ] Add team context to App state
- [ ] Update Header component

### Step 7: Testing & Polish
- [ ] Unit tests for new endpoints
- [ ] E2E tests for registration flow
- [ ] E2E tests for invitation flow
- [ ] E2E tests for team switching

---

## API Examples

### Register New Team
```http
POST /api/auth/register
Content-Type: application/json

{
  "teamName": "Acme Corp",
  "accountType": "multi",
  "admin": {
    "name": "John Admin",
    "email": "john@acme.com",
    "password": "SecurePass123!"
  }
}
```

Response:
```json
{
  "sessionId": "abc123...",
  "csrfToken": "xyz789...",
  "user": {
    "id": "u1",
    "name": "John Admin",
    "email": "john@acme.com"
  },
  "team": {
    "id": "t1",
    "name": "Acme Corp",
    "accountType": "multi"
  }
}
```

### Send Invitation
```http
POST /api/invitations
X-Session-ID: abc123...
Content-Type: application/json

{
  "email": "jane@acme.com",
  "role": "member"
}
```

### Accept Invitation (New User)
```http
POST /api/invitations/token123/accept
Content-Type: application/json

{
  "name": "Jane Member",
  "password": "SecurePass456!"
}
```

---

## Security Considerations

1. **Team Isolation**: All queries MUST filter by team_id
2. **Role Enforcement**: Admin-only endpoints check role in current team
3. **Invitation Security**:
   - Tokens are cryptographically secure
   - Tokens expire after 7 days
   - One-time use (marked as accepted)
4. **Cross-Team Access**: Users cannot access data from teams they don't belong to
5. **Session Security**: current_team_id validated on every request

---

## Questions for User Clarification

1. **Invitation expiry**: 7 days reasonable? Or configurable?
2. **User removal**: When removing a user from a team, should their tasks be:
   - Unassigned?
   - Reassigned to admin?
   - Keep assignment but mark user as "former member"?
3. **Team deletion**: Should this be allowed? What happens to data?
4. **Default team name for work laptop**: "My Team"? Or prompt on first run?
