"""
Resume Engine Authentication Middleware
LEVEL 5 - JWT-based authentication and authorization
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import jwt
import time
from datetime import datetime, timedelta

security = HTTPBearer()

class AuthMiddleware:
    """Handles JWT authentication for resume engine endpoints"""
    
    def __init__(self, secret_key: str = "resume_engine_secret_key"):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.token_expiry = timedelta(hours=24)
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT access token for authenticated user"""
        payload = {
            "user_id": user_data.get("user_id"),
            "email": user_data.get("email"),
            "permissions": user_data.get("permissions", ["resume:read", "resume:write"]),
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + self.token_expiry
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def check_permission(self, payload: Dict[str, Any], required_permission: str) -> bool:
        """Check if user has required permission"""
        permissions = payload.get("permissions", [])
        return required_permission in permissions

# Dependency for protected endpoints
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Get current authenticated user from JWT token"""
    auth_middleware = AuthMiddleware()
    payload = auth_middleware.verify_token(credentials.credentials)
    return payload

async def require_resume_write_permission(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require resume write permission"""
    auth_middleware = AuthMiddleware()
    if not auth_middleware.check_permission(current_user, "resume:write"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for resume operations"
        )
    return current_user

__all__ = [
    "AuthMiddleware", 
    "get_current_user", 
    "require_resume_write_permission",
    "security"
]
