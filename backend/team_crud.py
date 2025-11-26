"""
Team CRUD Operations
Database operations for teams, memberships, and invitations
"""

import secrets
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

try:
    from . import models, schemas
    from .auth import hash_password
except ImportError:
    import models
    import schemas
    from auth import hash_password


INVITATION_EXPIRY_DAYS = 7


# ==================== Teams ====================


def get_team(db: Session, team_id: str) -> Optional[models.Team]:
    """Get a team by ID."""
    return (
        db.query(models.Team)
        .filter(models.Team.id == team_id, models.Team.is_archived.is_(False))
        .first()
    )


def get_teams_for_user(db: Session, user_id: str) -> List[models.Team]:
    """Get all teams a user belongs to."""
    memberships = (
        db.query(models.TeamMembership).filter(models.TeamMembership.user_id == user_id).all()
    )

    team_ids = [m.team_id for m in memberships]
    return (
        db.query(models.Team)
        .filter(models.Team.id.in_(team_ids), models.Team.is_archived.is_(False))
        .all()
    )


def create_team(
    db: Session, name: str, account_type: str = "single", created_by_user_id: Optional[str] = None
) -> models.Team:
    """Create a new team."""
    team_id = f"team_{uuid.uuid4().hex[:8]}"
    team = models.Team(
        id=team_id,
        name=name,
        account_type=account_type,
        created_at=datetime.utcnow(),
        created_by_user_id=created_by_user_id,
        is_archived=False,
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def update_team(db: Session, team_id: str, name: str) -> Optional[models.Team]:
    """Update team name."""
    team = get_team(db, team_id)
    if not team:
        return None
    team.name = name
    db.commit()
    db.refresh(team)
    return team


def archive_team(db: Session, team_id: str) -> Optional[models.Team]:
    """Archive a team (soft delete)."""
    team = get_team(db, team_id)
    if not team:
        return None
    team.is_archived = True
    team.archived_at = datetime.utcnow()
    db.commit()
    db.refresh(team)
    return team


# ==================== Team Memberships ====================


def get_team_membership(db: Session, team_id: str, user_id: str) -> Optional[models.TeamMembership]:
    """Get a specific team membership."""
    return (
        db.query(models.TeamMembership)
        .filter(models.TeamMembership.team_id == team_id, models.TeamMembership.user_id == user_id)
        .first()
    )


def get_team_members(db: Session, team_id: str) -> List[Tuple[models.User, models.TeamMembership]]:
    """Get all members of a team with their membership info."""
    return (
        db.query(models.User, models.TeamMembership)
        .join(models.TeamMembership, models.User.id == models.TeamMembership.user_id)
        .filter(models.TeamMembership.team_id == team_id)
        .all()
    )


def get_user_role_in_team(db: Session, team_id: str, user_id: str) -> Optional[str]:
    """Get user's role in a specific team."""
    membership = get_team_membership(db, team_id, user_id)
    return membership.role if membership else None


def add_member_to_team(
    db: Session, team_id: str, user_id: str, role: str = "member"
) -> models.TeamMembership:
    """Add a user to a team."""
    membership_id = f"tm_{uuid.uuid4().hex[:8]}"
    membership = models.TeamMembership(
        id=membership_id, team_id=team_id, user_id=user_id, role=role, joined_at=datetime.utcnow()
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def update_member_role(
    db: Session, team_id: str, user_id: str, new_role: str
) -> Optional[models.TeamMembership]:
    """Update a member's role in a team."""
    membership = get_team_membership(db, team_id, user_id)
    if not membership:
        return None
    membership.role = new_role
    db.commit()
    db.refresh(membership)
    return membership


def remove_member_from_team(
    db: Session, team_id: str, user_id: str, task_action: str = "unassign"
) -> bool:
    """
    Remove a member from a team.

    task_action options:
    - 'unassign': Set assignee_id to NULL for their tasks
    - 'reassign_admin': Reassign to first admin in team
    - 'keep': Keep assignments as-is (shows as former member)
    """
    membership = get_team_membership(db, team_id, user_id)
    if not membership:
        return False

    # Handle task assignments
    if task_action == "unassign":
        # Get all projects in this team
        projects = db.query(models.Project).filter(models.Project.team_id == team_id).all()
        project_ids = [p.id for p in projects]

        # Unassign tasks
        if project_ids:
            db.query(models.Task).filter(
                models.Task.project_id.in_(project_ids), models.Task.assignee_id == user_id
            ).update({models.Task.assignee_id: None}, synchronize_session=False)

        # Unassign issues
        db.query(models.Issue).filter(
            models.Issue.team_id == team_id, models.Issue.assignee_id == user_id
        ).update({models.Issue.assignee_id: None}, synchronize_session=False)

    elif task_action == "reassign_admin":
        # Find first admin
        admin_membership = (
            db.query(models.TeamMembership)
            .filter(
                models.TeamMembership.team_id == team_id,
                models.TeamMembership.role == "admin",
                models.TeamMembership.user_id != user_id,
            )
            .first()
        )

        if admin_membership:
            admin_id = admin_membership.user_id

            # Get all projects in this team
            projects = db.query(models.Project).filter(models.Project.team_id == team_id).all()
            project_ids = [p.id for p in projects]

            # Reassign tasks
            if project_ids:
                db.query(models.Task).filter(
                    models.Task.project_id.in_(project_ids), models.Task.assignee_id == user_id
                ).update({models.Task.assignee_id: admin_id}, synchronize_session=False)

            # Reassign issues
            db.query(models.Issue).filter(
                models.Issue.team_id == team_id, models.Issue.assignee_id == user_id
            ).update({models.Issue.assignee_id: admin_id}, synchronize_session=False)

    # Remove membership
    db.delete(membership)
    db.commit()
    return True


def count_team_admins(db: Session, team_id: str) -> int:
    """Count number of admins in a team."""
    return (
        db.query(models.TeamMembership)
        .filter(models.TeamMembership.team_id == team_id, models.TeamMembership.role == "admin")
        .count()
    )


# ==================== Invitations ====================


def create_invitation(
    db: Session, team_id: str, email: str, role: str, invited_by_user_id: str
) -> models.Invitation:
    """Create a new invitation."""
    invitation_id = f"inv_{uuid.uuid4().hex[:8]}"
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=INVITATION_EXPIRY_DAYS)

    invitation = models.Invitation(
        id=invitation_id,
        team_id=team_id,
        email=email.lower(),
        role=role,
        invited_by_user_id=invited_by_user_id,
        token=token,
        expires_at=expires_at,
        created_at=datetime.utcnow(),
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return invitation


def get_invitation_by_token(db: Session, token: str) -> Optional[models.Invitation]:
    """Get an invitation by its token."""
    return (
        db.query(models.Invitation)
        .filter(models.Invitation.token == token, models.Invitation.accepted_at.is_(None))
        .first()
    )


def get_pending_invitations(db: Session, team_id: str) -> List[models.Invitation]:
    """Get all pending invitations for a team."""
    now = datetime.utcnow()
    return (
        db.query(models.Invitation)
        .filter(
            models.Invitation.team_id == team_id,
            models.Invitation.accepted_at.is_(None),
            models.Invitation.expires_at > now,
        )
        .all()
    )


def get_invitation_by_email(db: Session, team_id: str, email: str) -> Optional[models.Invitation]:
    """Get a pending invitation by email for a specific team."""
    now = datetime.utcnow()
    return (
        db.query(models.Invitation)
        .filter(
            models.Invitation.team_id == team_id,
            models.Invitation.email == email.lower(),
            models.Invitation.accepted_at.is_(None),
            models.Invitation.expires_at > now,
        )
        .first()
    )


def accept_invitation(
    db: Session, invitation: models.Invitation, user_id: str
) -> models.TeamMembership:
    """Mark invitation as accepted and create team membership."""
    invitation.accepted_at = datetime.utcnow()

    # Create membership
    membership = add_member_to_team(db, invitation.team_id, user_id, invitation.role)

    db.commit()
    return membership


def revoke_invitation(db: Session, invitation_id: str, team_id: str) -> bool:
    """Delete an invitation."""
    invitation = (
        db.query(models.Invitation)
        .filter(
            models.Invitation.id == invitation_id,
            models.Invitation.team_id == team_id,
            models.Invitation.accepted_at.is_(None),
        )
        .first()
    )

    if not invitation:
        return False

    db.delete(invitation)
    db.commit()
    return True


# ==================== Registration ====================


def register_team_with_admin(
    db: Session,
    team_name: str,
    account_type: str,
    admin_name: str,
    admin_email: str,
    admin_password: str,
) -> Tuple[models.Team, models.User]:
    """
    Register a new team with an admin user.
    Returns (team, user) tuple.
    """
    # Create user first
    user_id = f"u_{uuid.uuid4().hex[:8]}"
    user = models.User(
        id=user_id,
        name=admin_name,
        email=admin_email.lower(),
        role="admin",  # Keep for backward compatibility
        password_hash=hash_password(admin_password),
        is_active=True,
        created_at=datetime.utcnow(),
        availability=True,
    )
    db.add(user)
    db.flush()  # Get the user ID

    # Create team
    team = create_team(db, team_name, account_type, user_id)

    # Add user as admin
    add_member_to_team(db, team.id, user_id, "admin")

    db.commit()
    db.refresh(user)
    db.refresh(team)

    return team, user


def create_team_member(
    db: Session, team_id: str, name: str, email: str, password: str, role: str = "member"
) -> models.User:
    """
    Create a new user and add them to a team.
    Used by admin to directly create users.
    """
    user_id = f"u_{uuid.uuid4().hex[:8]}"
    user = models.User(
        id=user_id,
        name=name,
        email=email.lower(),
        role=role,  # Keep for backward compatibility
        password_hash=hash_password(password),
        is_active=True,
        created_at=datetime.utcnow(),
        availability=True,
    )
    db.add(user)
    db.flush()

    # Add to team
    add_member_to_team(db, team_id, user_id, role)

    db.commit()
    db.refresh(user)
    return user
