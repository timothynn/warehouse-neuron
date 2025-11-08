"""
Authentication routes - login, logout, register, etc.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app.schema_auth import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserListResponse,
    ChangePasswordRequest,
    PermissionCheck,
    PermissionResponse,
)
from app import crud_auth
from app.auth_utils import (
    create_access_token,
    create_refresh_token,
    generate_temp_password,
)
from app.auth_dependencies import get_current_user, get_client_ip, get_user_agent
from app.models_auth import User
from app.permissions import (
    get_user_permissions,
    has_permission,
    can_manage_user,
)
from app.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Login with username and password.
    Returns access token and refresh token.
    """
    # Authenticate user
    user = crud_auth.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        # Log failed attempt
        crud_auth.create_audit_log(
            db,
            user_id=None,
            action="auth.login.failed",
            details={"username": login_data.username},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
        },
        expires_delta=access_token_expires,
    )
    
    # Create refresh token
    refresh_token = create_refresh_token()
    refresh_token_expires = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    crud_auth.create_refresh_token(
        db,
        user_id=user.id,
        token=refresh_token,
        expires_at=refresh_token_expires,
    )
    
    # Log successful login
    crud_auth.create_audit_log(
        db,
        user_id=user.id,
        action="auth.login.success",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout")
async def logout(
    refresh_data: RefreshRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Logout by revoking refresh token.
    """
    # Revoke the refresh token
    crud_auth.revoke_refresh_token(db, refresh_data.refresh_token)
    
    # Log logout
    crud_auth.create_audit_log(
        db,
        user_id=current_user.id,
        action="auth.logout",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshRequest,
    db: Session = Depends(get_db),
):
    """
    Get a new access token using refresh token.
    """
    # Validate refresh token
    refresh_token_obj = crud_auth.get_refresh_token(db, refresh_data.refresh_token)
    if not refresh_token_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    # Get user
    user = crud_auth.get_user_by_id(db, refresh_token_obj.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
        },
        expires_delta=access_token_expires,
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_data.refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information.
    """
    return UserResponse.model_validate(current_user)


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Change current user's password.
    """
    success = crud_auth.change_password(
        db,
        user_id=current_user.id,
        old_password=password_data.old_password,
        new_password=password_data.new_password,
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password",
        )
    
    # Log password change
    crud_auth.create_audit_log(
        db,
        user_id=current_user.id,
        action="auth.password.changed",
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
    )
    
    # Revoke all refresh tokens to force re-login
    crud_auth.revoke_all_user_tokens(db, current_user.id)
    
    return {"message": "Password changed successfully. Please login again."}


@router.get("/permissions", response_model=PermissionResponse)
async def get_my_permissions(current_user: User = Depends(get_current_user)):
    """
    Get current user's permissions.
    """
    permissions = get_user_permissions(current_user.role)
    return PermissionResponse(
        has_permission=True,
        user_role=current_user.role,
        permissions=permissions,
    )


@router.post("/check-permission", response_model=PermissionResponse)
async def check_permission(
    permission_data: PermissionCheck,
    current_user: User = Depends(get_current_user),
):
    """
    Check if current user has a specific permission.
    """
    has_perm = has_permission(current_user.role, permission_data.permission)
    permissions = get_user_permissions(current_user.role)
    
    return PermissionResponse(
        has_permission=has_perm,
        user_role=current_user.role,
        permissions=permissions,
    )
