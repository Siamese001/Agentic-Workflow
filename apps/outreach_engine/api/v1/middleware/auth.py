"""
Authentication Middleware for Outreach Engine
LEVEL 5 - Authentication and authorization for outreach API endpoints
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import jwt
from datetime import datetime, timedelta
import hashlib
import secrets

security = HTTPBearer()

class OutreachAuthMiddleware:
    """Handles authentication and authorization for outreach engine"""

    def __init__(self):
        self.secret_key = secrets.token_urlsafe(32)
        self.algorithm = "HS256"
        self.token_expiry = timedelta(hours=24)

        # User roles and permissions
        self.roles = {
            "admin": ["read", "write", "delete", "manage_users", "view_analytics"],
            "premium": ["read", "write", "delete", "view_analytics"],
            "basic": ["read", "write"],
            "trial": ["read", "write", "limited_api_calls"]
        }

        # Rate limits by role
        self.rate_limits = {
            "admin": 1000,      # per hour
            "premium": 500,
            "basic": 100,
            "trial": 25
        }

        # In-memory user store (in production, use database)
        self.users = {
            "admin_user": {
                "password_hash": self._hash_password("admin_pass"),
                "role": "admin",
                "api_key": "sk-admin-1234567890abcdef",
                "active": True,
                "created_at": datetime.utcnow()
            },
            "premium_user": {
                "password_hash": self._hash_password("premium_pass"),
                "role": "premium",
                "api_key": "sk-premium-1234567890abcdef",
                "active": True,
                "created_at": datetime.utcnow()
            },
            "basic_user": {
                "password_hash": self._hash_password("basic_pass"),
                "role": "basic",
                "api_key": "sk-basic-1234567890abcdef",
                "active": True,
                "created_at": datetime.utcnow()
            }
        }

        # API usage tracking
        self.api_usage = {}

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return self._hash_password(password) == password_hash

    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        payload = {
            "user_id": user_data["user_id"],
            "username": user_data["username"],
            "role": user_data["role"],
            "exp": datetime.utcnow() + self.token_expiry,
            "iat": datetime.utcnow(),
            "type": "access"
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check if token is expired
            if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )

            # Check if user is still active
            username = payload.get("username")
            if username not in self.users or not self.users[username]["active"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User account is inactive"
                )

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    def authenticate_api_key(self, api_key: str) -> Dict[str, Any]:
        """Authenticate using API key"""
        for username, user_data in self.users.items():
            if user_data.get("api_key") == api_key and user_data["active"]:
                return {
                    "user_id": username,
                    "username": username,
                    "role": user_data["role"],
                    "authenticated_via": "api_key"
                }

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    def check_permissions(self, user_role: str, required_permission: str) -> bool:
        """Check if user role has required permission"""
        user_permissions = self.roles.get(user_role, [])
        return required_permission in user_permissions

    def check_rate_limit(self, user_id: str) -> bool:
        """Check if user has exceeded rate limit"""
        current_hour = datetime.utcnow().replace(minute=0, second=0, microsecond=0)

        if user_id not in self.api_usage:
            self.api_usage[user_id] = {}

        if current_hour not in self.api_usage[user_id]:
            self.api_usage[user_id][current_hour] = 0

        # Get user's rate limit
        user_role = self.users.get(user_id, {}).get("role", "trial")
        max_calls = self.rate_limits.get(user_role, 25)

        # Check current usage
        current_usage = self.api_usage[user_id][current_hour]

        if current_usage >= max_calls:
            return False

        # Increment usage
        self.api_usage[user_id][current_hour] += 1
        return True

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict[str, Any]:
        """Get current authenticated user from JWT token"""
        token = credentials.credentials
        return self.verify_token(token)

    async def get_current_user_optional(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> Optional[Dict[str, Any]]:
        """Get current user optionally (doesn't raise exception if no token)"""
        if not credentials:
            return None

        try:
            return self.verify_token(credentials.credentials)
        except HTTPException:
            return None

    def require_permission(self, permission: str):
        """Decorator to require specific permission"""
        def permission_dependency(current_user: Dict[str, Any] = Depends(self.get_current_user)):
            user_role = current_user.get("role", "trial")

            if not self.check_permissions(user_role, permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission}"
                )

            return current_user

        return permission_dependency

    def require_role(self, required_role: str):
        """Decorator to require specific role"""
        def role_dependency(current_user: Dict[str, Any] = Depends(self.get_current_user)):
            user_role = current_user.get("role")

            if user_role != required_role and user_role != "admin":  # Admin can access everything
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient role. Required: {required_role}"
                )

            return current_user

        return role_dependency

    def check_rate_limit_dependency(self, current_user: Dict[str, Any] = Depends(get_current_user)):
        """Dependency to check rate limits"""
        user_id = current_user.get("user_id")

        if not self.check_rate_limit(user_id):
            user_role = current_user.get("role", "trial")
            max_calls = self.rate_limits.get(user_role, 25)

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {max_calls} calls per hour."
            )

        return current_user

# Create auth middleware instance
auth_middleware = OutreachAuthMiddleware()

# Common dependencies
get_current_user = auth_middleware.get_current_user
get_current_user_optional = auth_middleware.get_current_user_optional

# Permission dependencies
require_write_permission = auth_middleware.require_permission("write")
require_delete_permission = auth_middleware.require_permission("delete")
require_analytics_permission = auth_middleware.require_permission("view_analytics")

# Role dependencies
require_admin_role = auth_middleware.require_role("admin")
require_premium_role = auth_middleware.require_role("premium")

# Rate limit dependency
check_rate_limit = auth_middleware.check_rate_limit_dependency

class OutreachAuthUtils:
    """Utility functions for outreach authentication"""

    @staticmethod
    def create_user_session(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create user session data"""
        return {
            "user_id": user_data["user_id"],
            "username": user_data["username"],
            "role": user_data["role"],
            "permissions": auth_middleware.roles.get(user_data["role"], []),
            "rate_limit": auth_middleware.rate_limits.get(user_data["role"], 25),
            "session_created": datetime.utcnow().isoformat()
        }

    @staticmethod
    def validate_outreach_access(user_role: str, outreach_type: str) -> bool:
        """Validate if user can access specific outreach type"""
        # Define outreach type restrictions
        restricted_types = {
            "trial": ["email", "linkedin"],
            "basic": ["email", "linkedin", "follow_up"],
            "premium": ["email", "linkedin", "cold_call", "follow_up", "networking"],
            "admin": ["email", "linkedin", "cold_call", "follow_up", "networking",
                     "referral_request", "interview_request", "partnership_proposal"]
        }

        allowed_types = restricted_types.get(user_role, [])
        return outreach_type in allowed_types

    @staticmethod
    def get_user_quota(user_role: str) -> Dict[str, int]:
        """Get user's quota limits"""
        quotas = {
            "trial": {
                "daily_messages": 10,
                "monthly_messages": 100,
                "concurrent_tasks": 1
            },
            "basic": {
                "daily_messages": 50,
                "monthly_messages": 1000,
                "concurrent_tasks": 3
            },
            "premium": {
                "daily_messages": 200,
                "monthly_messages": 5000,
                "concurrent_tasks": 10
            },
            "admin": {
                "daily_messages": 1000,
                "monthly_messages": 50000,
                "concurrent_tasks": 50
            }
        }

        return quotas.get(user_role, quotas["trial"])

__all__ = [
    "auth_middleware",
    "get_current_user",
    "get_current_user_optional",
    "require_write_permission",
    "require_delete_permission",
    "require_analytics_permission",
    "require_admin_role",
    "require_premium_role",
    "check_rate_limit",
    "OutreachAuthMiddleware",
    "OutreachAuthUtils"
]
