"""
Authentication middleware for SECRIMPO using KeyAuth
"""
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .keyauth_config import auth_manager
import functools
from typing import Optional

# HTTP Bearer token security
security = HTTPBearer()

class AuthContext:
    """Context object containing user authentication data and permissions"""
    
    def __init__(self, user_data: dict, permissions: dict):
        self.user_data = user_data
        self.permissions = permissions
        self.username = user_data.get('username', 'unknown')
        self.subscription = user_data.get('subscription', 'restricted')
        self.expires = user_data.get('expires')
        self.created_at = user_data.get('created_at')
        self.last_login = user_data.get('last_login')
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        return self.permissions.get(permission, False)
    
    def is_admin(self) -> bool:
        """Check if user has admin privileges"""
        return self.subscription.lower() == 'admin'
    
    def is_agent(self) -> bool:
        """Check if user is an agent or higher"""
        return self.subscription.lower() in ['admin', 'agent']
    
    def can_modify_data(self) -> bool:
        """Check if user can create or edit data"""
        return self.has_permission('create_occurrence') or self.has_permission('edit_occurrence')

def verify_license(credentials: HTTPAuthorizationCredentials = Depends(security)) -> AuthContext:
    """
    Dependency to verify KeyAuth license and return user context
    """
    license_key = credentials.credentials
    
    # Validate license with KeyAuth
    user_context = auth_manager.validate_and_get_permissions(license_key)
    
    if not user_context:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired license key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Log successful authentication
    auth_manager.log_user_action(
        user_context["username"], 
        "AUTHENTICATED", 
        f"Subscription: {user_context['subscription']}"
    )
    
    return AuthContext(user_context["user_data"], user_context["permissions"])

def optional_verify_license(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[AuthContext]:
    """
    Optional dependency for endpoints that work with or without authentication
    """
    if not credentials:
        return None
    
    try:
        return verify_license(credentials)
    except HTTPException:
        return None

def require_permission(permission: str):
    """
    Decorator to require specific permission for endpoint access
    
    Usage:
    @app.get("/some-endpoint")
    @require_permission("create_occurrence")
    async def some_endpoint(auth: AuthContext = Depends(verify_license)):
        # Endpoint logic here
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Find AuthContext in kwargs
            auth_context = None
            for key, value in kwargs.items():
                if isinstance(value, AuthContext):
                    auth_context = value
                    break
            
            if not auth_context:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not auth_context.has_permission(permission):
                auth_manager.log_user_action(
                    auth_context.username,
                    "PERMISSION_DENIED",
                    f"Required: {permission}, Has: {auth_context.subscription}"
                )
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required. Your subscription level: {auth_context.subscription}"
                )
            
            # Log successful permission check
            auth_manager.log_user_action(
                auth_context.username,
                "PERMISSION_GRANTED",
                f"Action: {permission}"
            )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_admin(func):
    """
    Decorator to require admin privileges
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Find AuthContext in kwargs
        auth_context = None
        for key, value in kwargs.items():
            if isinstance(value, AuthContext):
                auth_context = value
                break
        
        if not auth_context or not auth_context.is_admin():
            if auth_context:
                auth_manager.log_user_action(
                    auth_context.username,
                    "ADMIN_ACCESS_DENIED",
                    f"Subscription: {auth_context.subscription}"
                )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrator privileges required"
            )
        
        auth_manager.log_user_action(
            auth_context.username,
            "ADMIN_ACCESS_GRANTED",
            "Administrator action executed"
        )
        
        return await func(*args, **kwargs)
    return wrapper

def require_agent_or_admin(func):
    """
    Decorator to require agent or admin privileges
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Find AuthContext in kwargs
        auth_context = None
        for key, value in kwargs.items():
            if isinstance(value, AuthContext):
                auth_context = value
                break
        
        if not auth_context or not auth_context.is_agent():
            if auth_context:
                auth_manager.log_user_action(
                    auth_context.username,
                    "AGENT_ACCESS_DENIED",
                    f"Subscription: {auth_context.subscription}"
                )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Agent or Administrator privileges required"
            )
        
        return await func(*args, **kwargs)
    return wrapper