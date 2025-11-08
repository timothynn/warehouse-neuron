"""
Permission and role-based access control configuration
"""
from typing import List, Dict
from functools import wraps
from fastapi import HTTPException, status

# Role hierarchy levels (lower number = higher authority)
ROLE_HIERARCHY = {
    "DEV": 1,
    "DB_MANAGER": 2,
    "MANAGER": 3,
    "SUPERVISOR": 4,
    "STAFF": 5,
    "VIEWER": 6,
}

# Permission mappings
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "DEV": ["*"],  # All permissions
    
    "DB_MANAGER": [
        "db.*",
        "system.logs.view",
        "inventory.*",
        "stock.*",
        "location.*",
        "report.*",
        "user.view",
    ],
    
    "MANAGER": [
        "inventory.sku.create",
        "inventory.sku.update",
        "inventory.sku.view",
        "stock.*",
        "location.*",
        "report.*",
        "user.create",
        "user.update",
        "user.deactivate",
        "user.view",
    ],
    
    "SUPERVISOR": [
        "inventory.sku.view",
        "stock.intake",
        "stock.transfer",
        "stock.adjustment",
        "stock.approve",
        "stock.view",
        "location.view",
        "report.inventory",
        "report.movement",
        "user.view",
    ],
    
    "STAFF": [
        "stock.intake",
        "stock.transfer",
        "stock.view",
        "location.view",
        "inventory.sku.view",
    ],
    
    "VIEWER": [
        "stock.view",
        "location.view",
        "inventory.sku.view",
        "report.inventory",
        "report.movement",
    ],
}


def get_user_permissions(role: str) -> List[str]:
    """Get all permissions for a role."""
    return ROLE_PERMISSIONS.get(role, [])


def has_permission(user_role: str, required_permission: str) -> bool:
    """
    Check if a user role has a specific permission.
    Supports wildcard matching (e.g., 'stock.*' matches 'stock.intake').
    """
    permissions = get_user_permissions(user_role)
    
    # DEV has all permissions
    if "*" in permissions:
        return True
    
    # Direct match
    if required_permission in permissions:
        return True
    
    # Wildcard match (e.g., 'stock.*' matches 'stock.intake')
    for perm in permissions:
        if perm.endswith(".*"):
            prefix = perm[:-2]
            if required_permission.startswith(prefix + "."):
                return True
    
    return False


def can_manage_user(manager_role: str, target_role: str) -> bool:
    """
    Check if a manager can manage a user with target_role.
    A user can only manage users with lower hierarchy levels.
    """
    manager_level = ROLE_HIERARCHY.get(manager_role, 999)
    target_level = ROLE_HIERARCHY.get(target_role, 999)
    
    return manager_level < target_level


def require_permission(permission: str):
    """
    Decorator to check if the current user has the required permission.
    
    Usage:
        @require_permission("stock.intake")
        async def create_intake(current_user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract current_user from kwargs
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check permission
            if not has_permission(current_user.role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required: {permission}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_any_permission(*permissions: str):
    """
    Decorator to check if the current user has ANY of the required permissions.
    
    Usage:
        @require_any_permission("stock.approve", "stock.intake")
        async def handle_stock(current_user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check if user has any of the permissions
            has_any = any(has_permission(current_user.role, perm) for perm in permissions)
            if not has_any:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission denied. Required one of: {', '.join(permissions)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(*roles: str):
    """
    Decorator to check if the current user has one of the required roles.
    
    Usage:
        @require_role("MANAGER", "SUPERVISOR")
        async def approve_movement(current_user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if current_user.role not in roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role denied. Required one of: {', '.join(roles)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator
