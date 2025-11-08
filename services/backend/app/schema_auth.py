"""
Pydantic schemas for authentication and authorization
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import re


class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8)
    role: str = Field(..., pattern="^(DEV|DB_MANAGER|MANAGER|SUPERVISOR|STAFF|VIEWER)$")
    manager_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = Field(None, pattern="^(DEV|DB_MANAGER|MANAGER|SUPERVISOR|STAFF|VIEWER)$")
    manager_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: UUID
    role: str
    is_active: bool
    must_change_password: bool
    manager_id: Optional[UUID]
    team_id: Optional[UUID]
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema for paginated user list."""
    users: List[UserResponse]
    total: int
    skip: int
    limit: int


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Schema for password change request."""
    old_password: str
    new_password: str = Field(..., min_length=8)
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class ResetPasswordRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr


class PermissionCheck(BaseModel):
    """Schema for permission check request."""
    permission: str


class PermissionResponse(BaseModel):
    """Schema for permission check response."""
    has_permission: bool
    user_role: str
    permissions: List[str]


class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    id: UUID
    user_id: Optional[UUID]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[UUID]
    details: Optional[dict]
    ip_address: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Schema for paginated audit log list."""
    logs: List[AuditLogResponse]
    total: int
    skip: int
    limit: int
