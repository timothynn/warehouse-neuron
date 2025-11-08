"""
User management routes - create, update, list, deactivate users
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.schema_auth import (
    UserCreate,
    UserResponse,
    UserUpdate,
    UserListResponse,
    AuditLogResponse,
    AuditLogListResponse,
)
from app import crud_auth
from app.auth_dependencies import get_current_user, get_client_ip, get_user_agent
from app.models_auth import User
from app.permissions import can_manage_user, has_permission
from app.auth_utils import generate_temp_password

router = APIRouter(prefix="/api/v1/users", tags=["User Management"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new user. Requires 'user.create' permission.
    Users can only create users with lower hierarchy levels.
    """
    # Check permission
    if not has_permission(current_user.role, "user.create"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: user.create required",
        )
    
    # Check if current user can manage the target role
    if not can_manage_user(current_user.role, user_data.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Cannot create user with role {user_data.role}",
        )
    
    # Check if username already exists
    if crud_auth.get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Check if email already exists
    if crud_auth.get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create user
    new_user = crud_auth.create_user(
        db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role,
        full_name=user_data.full_name,
        manager_id=user_data.manager_id,
        team_id=user_data.team_id,
        created_by_id=current_user.id,
    )
    
    # Log user creation
    crud_auth.create_audit_log(
        db,
        user_id=current_user.id,
        action="user.created",
        resource_type="user",
        resource_id=new_user.id,
        details={
            "username": new_user.username,
            "role": new_user.role,
        },
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    
    return UserResponse.model_validate(new_user)


@router.get("", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List users. Requires 'user.view' permission.
    Users only see users they can manage (lower hierarchy).
    """
    # Check permission
    if not has_permission(current_user.role, "user.view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: user.view required",
        )
    
    # List users
    users, total = crud_auth.list_users(
        db,
        skip=skip,
        limit=limit,
        role=role,
        is_active=is_active,
    )
    
    # Filter users based on hierarchy
    # Non-DEV users can only see users they can manage
    if current_user.role != "DEV":
        users = [
            u for u in users
            if can_manage_user(current_user.role, u.role) or u.id == current_user.id
        ]
        total = len(users)
    
    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get user by ID. Requires 'user.view' permission.
    """
    # Check permission
    if not has_permission(current_user.role, "user.view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: user.view required",
        )
    
    user = crud_auth.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if current user can view this user
    if current_user.role != "DEV":
        if not can_manage_user(current_user.role, user.role) and user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view this user",
            )
    
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update user information. Requires 'user.update' permission.
    """
    # Check permission
    if not has_permission(current_user.role, "user.update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: user.update required",
        )
    
    # Get user to update
    user = crud_auth.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if current user can manage this user
    if current_user.role != "DEV":
        if not can_manage_user(current_user.role, user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update this user",
            )
    
    # If changing role, check if can manage new role
    if user_data.role and user_data.role != user.role:
        if not can_manage_user(current_user.role, user_data.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Cannot assign role {user_data.role}",
            )
    
    # Update user
    updated_user = crud_auth.update_user(
        db,
        user_id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        manager_id=user_data.manager_id,
        team_id=user_data.team_id,
        is_active=user_data.is_active,
    )
    
    # Log update
    crud_auth.create_audit_log(
        db,
        user_id=current_user.id,
        action="user.updated",
        resource_type="user",
        resource_id=user_id,
        details=user_data.model_dump(exclude_unset=True),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    
    return UserResponse.model_validate(updated_user)


@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Deactivate a user. Requires 'user.deactivate' permission.
    """
    # Check permission
    if not has_permission(current_user.role, "user.deactivate"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: user.deactivate required",
        )
    
    # Cannot deactivate yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )
    
    # Get user
    user = crud_auth.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if can manage this user
    if not can_manage_user(current_user.role, user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot deactivate this user",
        )
    
    # Deactivate user
    success = crud_auth.deactivate_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to deactivate user",
        )
    
    # Revoke all tokens
    crud_auth.revoke_all_user_tokens(db, user_id)
    
    # Log deactivation
    crud_auth.create_audit_log(
        db,
        user_id=current_user.id,
        action="user.deactivated",
        resource_type="user",
        resource_id=user_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    
    return {"message": "User deactivated successfully"}


@router.post("/{user_id}/activate")
async def activate_user(
    user_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Activate a user. Requires 'user.update' permission.
    """
    # Check permission
    if not has_permission(current_user.role, "user.update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: user.update required",
        )
    
    # Get user
    user = crud_auth.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if can manage this user
    if not can_manage_user(current_user.role, user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot activate this user",
        )
    
    # Activate user
    success = crud_auth.activate_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to activate user",
        )
    
    # Log activation
    crud_auth.create_audit_log(
        db,
        user_id=current_user.id,
        action="user.activated",
        resource_type="user",
        resource_id=user_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    
    return {"message": "User activated successfully"}


@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Reset user password (admin action). Requires 'user.update' permission.
    Returns temporary password.
    """
    # Check permission
    if not has_permission(current_user.role, "user.update"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: user.update required",
        )
    
    # Get user
    user = crud_auth.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Check if can manage this user
    if not can_manage_user(current_user.role, user.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot reset password for this user",
        )
    
    # Generate temporary password
    temp_password = generate_temp_password()
    
    # Reset password
    success = crud_auth.reset_password(db, user_id, temp_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to reset password",
        )
    
    # Revoke all tokens
    crud_auth.revoke_all_user_tokens(db, user_id)
    
    # Log password reset
    crud_auth.create_audit_log(
        db,
        user_id=current_user.id,
        action="user.password.reset",
        resource_type="user",
        resource_id=user_id,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    
    return {
        "message": "Password reset successfully",
        "temporary_password": temp_password,
        "note": "User must change password on next login",
    }


@router.get("/{user_id}/audit-logs", response_model=AuditLogListResponse)
async def get_user_audit_logs(
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get audit logs for a specific user. Requires 'system.logs.view' permission.
    """
    # Check permission
    if not has_permission(current_user.role, "system.logs.view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied: system.logs.view required",
        )
    
    logs, total = crud_auth.list_audit_logs(
        db,
        skip=skip,
        limit=limit,
        user_id=user_id,
    )
    
    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        skip=skip,
        limit=limit,
    )
