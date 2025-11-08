"""
CRUD operations for authentication and authorization
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from app.models_auth import User, RefreshToken, AuditLog, Team
from app.auth_utils import hash_password, verify_password, hash_token
from app.permissions import can_manage_user


# User operations

def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    role: str,
    full_name: Optional[str] = None,
    manager_id: Optional[UUID] = None,
    team_id: Optional[UUID] = None,
    created_by_id: Optional[UUID] = None,
) -> User:
    """Create a new user."""
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role,
        full_name=full_name,
        manager_id=manager_id,
        team_id=team_id,
        created_by_id=created_by_id,
        is_active=True,
        must_change_password=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(
    db: Session,
    user_id: UUID,
    email: Optional[str] = None,
    full_name: Optional[str] = None,
    role: Optional[str] = None,
    manager_id: Optional[UUID] = None,
    team_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
) -> Optional[User]:
    """Update user information."""
    user = get_user_by_id(db, user_id)
    if not user:
        return None
    
    if email is not None:
        user.email = email
    if full_name is not None:
        user.full_name = full_name
    if role is not None:
        user.role = role
    if manager_id is not None:
        user.manager_id = manager_id
    if team_id is not None:
        user.team_id = team_id
    if is_active is not None:
        user.is_active = is_active
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


def change_password(
    db: Session,
    user_id: UUID,
    old_password: str,
    new_password: str,
) -> bool:
    """Change user password."""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    if not verify_password(old_password, user.password_hash):
        return False
    
    user.password_hash = hash_password(new_password)
    user.must_change_password = False
    user.updated_at = datetime.utcnow()
    db.commit()
    return True


def reset_password(db: Session, user_id: UUID, new_password: str) -> bool:
    """Reset user password (admin action)."""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.password_hash = hash_password(new_password)
    user.must_change_password = True
    user.updated_at = datetime.utcnow()
    db.commit()
    return True


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user with username and password."""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return user


def list_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    manager_id: Optional[UUID] = None,
) -> tuple[List[User], int]:
    """List users with filtering and pagination."""
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if manager_id:
        query = query.filter(User.manager_id == manager_id)
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    return users, total


def deactivate_user(db: Session, user_id: UUID) -> bool:
    """Deactivate a user account."""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.commit()
    return True


def activate_user(db: Session, user_id: UUID) -> bool:
    """Activate a user account."""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    user.is_active = True
    user.updated_at = datetime.utcnow()
    db.commit()
    return True


# Refresh token operations

def create_refresh_token(
    db: Session,
    user_id: UUID,
    token: str,
    expires_at: datetime,
) -> RefreshToken:
    """Create a refresh token."""
    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=hash_token(token),
        expires_at=expires_at,
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return refresh_token


def get_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
    """Get refresh token by token value."""
    token_hash = hash_token(token)
    return db.query(RefreshToken).filter(
        and_(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.utcnow(),
        )
    ).first()


def revoke_refresh_token(db: Session, token: str) -> bool:
    """Revoke a refresh token."""
    token_hash = hash_token(token)
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).first()
    
    if not refresh_token:
        return False
    
    refresh_token.revoked_at = datetime.utcnow()
    db.commit()
    return True


def revoke_all_user_tokens(db: Session, user_id: UUID) -> int:
    """Revoke all refresh tokens for a user."""
    result = db.query(RefreshToken).filter(
        and_(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
    ).update({"revoked_at": datetime.utcnow()})
    db.commit()
    return result


# Audit log operations

def create_audit_log(
    db: Session,
    user_id: Optional[UUID],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[UUID] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> AuditLog:
    """Create an audit log entry."""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log


def list_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[UUID] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> tuple[List[AuditLog], int]:
    """List audit logs with filtering and pagination."""
    query = db.query(AuditLog)
    
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(AuditLog.created_at <= end_date)
    
    query = query.order_by(AuditLog.created_at.desc())
    
    total = query.count()
    logs = query.offset(skip).limit(limit).all()
    
    return logs, total


# Team operations

def create_team(
    db: Session,
    name: str,
    description: Optional[str] = None,
    manager_id: Optional[UUID] = None,
) -> Team:
    """Create a new team."""
    team = Team(
        name=name,
        description=description,
        manager_id=manager_id,
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def get_team_by_id(db: Session, team_id: UUID) -> Optional[Team]:
    """Get team by ID."""
    return db.query(Team).filter(Team.id == team_id).first()


def list_teams(db: Session, skip: int = 0, limit: int = 100) -> tuple[List[Team], int]:
    """List all teams."""
    query = db.query(Team)
    total = query.count()
    teams = query.offset(skip).limit(limit).all()
    return teams, total
