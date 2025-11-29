"""
Authentication and Authorization - Section 18

Provides AuthN/AuthZ implementation for the deployment layer
with session management and user access control.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from enum import Enum
import hashlib
import secrets
import json
import logging

logger = logging.getLogger(__name__)


class UserRole(str, Enum):
    """User roles for authorization."""
    ADMIN = "admin"
    DEVELOPER = "developer"
    USER = "user"
    GUEST = "guest"


class Permission(str, Enum):
    """System permissions."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    EXECUTE = "execute"
    MANAGE_USERS = "manage_users"
    VIEW_LOGS = "view_logs"


@dataclass
class User:
    """User entity for authentication."""
    id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    permissions: Set[Permission] = field(default_factory=set)
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission."""
        return permission in self.permissions or Permission.ADMIN in self.permissions
    
    def add_permission(self, permission: Permission) -> None:
        """Add permission to user."""
        self.permissions.add(permission)
    
    def remove_permission(self, permission: Permission) -> None:
        """Remove permission from user."""
        self.permissions.discard(permission)


@dataclass
class Session:
    """User session for session management."""
    session_id: str
    user_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: Optional[datetime] = None
    last_accessed: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        if not self.expires_at:
            return False
        return datetime.now(UTC) > self.expires_at
    
    def extend(self, minutes: int = 30) -> None:
        """Extend session expiration."""
        self.expires_at = datetime.now(UTC) + timedelta(minutes=minutes)
        self.last_accessed = datetime.now(UTC)


@dataclass
class AuthToken:
    """Authentication token for API access."""
    token_id: str
    user_id: str
    token_type: str  # access, refresh
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: Optional[datetime] = None
    scopes: List[str] = field(default_factory=list)
    is_revoked: bool = False
    
    def is_expired(self) -> bool:
        """Check if token is expired."""
        if not self.expires_at:
            return False
        return datetime.now(UTC) > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if token is valid (not expired and not revoked)."""
        return not self.is_expired() and not self.is_revoked


class AuthManager:
    """
    Authentication and authorization manager.
    
    Provides user management, session handling, and token-based
    authentication for the deployment layer.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize auth manager with configuration.
        
        Args:
            config: Authentication configuration
        """
        self.config = config or {}
        self._users: Dict[str, User] = {}
        self._sessions: Dict[str, Session] = {}
        self._tokens: Dict[str, AuthToken] = {}
        self._username_to_id: Dict[str, str] = {}
        
        # Default settings
        self.session_timeout_minutes = self.config.get("session_timeout_minutes", 30)
        self.access_token_expire_minutes = self.config.get("access_token_expire_minutes", 30)
        self.refresh_token_expire_days = self.config.get("refresh_token_expire_days", 7)
        self.password_min_length = self.config.get("password_min_length", 8)
        
        # Initialize default admin user
        self._initialize_default_users()
    
    def _initialize_default_users(self) -> None:
        """Initialize default users for the system."""
        # Create default admin user
        admin_password_hash = self._hash_password("admin123")
        admin_user = User(
            id="admin_default",
            username="admin",
            email="admin@example.com",
            password_hash=admin_password_hash,
            role=UserRole.ADMIN,
            permissions=set(Permission),
            is_verified=True
        )
        self._users[admin_user.id] = admin_user
        self._username_to_id[admin_user.username] = admin_user.id
        
        logger.info("Initialized default admin user")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256 (simplified implementation)."""
        # In production, use proper password hashing like bcrypt
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        try:
            salt, hash_value = password_hash.split(":", 1)
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == hash_value
        except ValueError:
            return False
    
    def _generate_token(self) -> str:
        """Generate secure random token."""
        return secrets.token_urlsafe(32)
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: UserRole = UserRole.USER,
        permissions: Optional[Set[Permission]] = None
    ) -> User:
        """
        Create a new user.
        
        Args:
            username: Unique username
            email: User email
            password: User password
            role: User role
            permissions: User permissions
            
        Returns:
            Created user
            
        Raises:
            ValueError: If username already exists or password is too short
        """
        if username in self._username_to_id:
            raise ValueError(f"Username '{username}' already exists")
        
        if len(password) < self.password_min_length:
            raise ValueError(f"Password must be at least {self.password_min_length} characters")
        
        user_id = secrets.token_hex(8)
        password_hash = self._hash_password(password)
        
        # Set default permissions based on role
        if permissions is None:
            permissions = self._get_default_permissions(role)
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            permissions=permissions
        )
        
        self._users[user_id] = user
        self._username_to_id[username] = user_id
        
        logger.info(f"Created user: {username} with role: {role.value}")
        return user
    
    def _get_default_permissions(self, role: UserRole) -> Set[Permission]:
        """Get default permissions for role."""
        if role == UserRole.ADMIN:
            return set(Permission)
        elif role == UserRole.DEVELOPER:
            return {Permission.READ, Permission.WRITE, Permission.EXECUTE}
        elif role == UserRole.USER:
            return {Permission.READ, Permission.EXECUTE}
        else:  # GUEST
            return {Permission.READ}
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password.
        
        Args:
            username: User username
            password: User password
            
        Returns:
            Authenticated user or None if authentication fails
        """
        user_id = self._username_to_id.get(username)
        if not user_id:
            return None
        
        user = self._users.get(user_id)
        if not user or not user.is_active:
            return None
        
        if self._verify_password(password, user.password_hash):
            user.last_login = datetime.now(UTC)
            logger.info(f"User authenticated: {username}")
            return user
        
        logger.warning(f"Authentication failed for user: {username}")
        return None
    
    def create_session(self, user: User, expires_in_minutes: Optional[int] = None) -> Session:
        """
        Create user session.
        
        Args:
            user: User to create session for
            expires_in_minutes: Session expiration in minutes
            
        Returns:
            Created session
        """
        if expires_in_minutes is None:
            expires_in_minutes = self.session_timeout_minutes
        
        session_id = self._generate_token()
        expires_at = datetime.now(UTC) + timedelta(minutes=expires_in_minutes)
        
        session = Session(
            session_id=session_id,
            user_id=user.id,
            expires_at=expires_at
        )
        
        self._sessions[session_id] = session
        logger.info(f"Created session for user: {user.username}")
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session or None if not found or expired
        """
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        if session.is_expired():
            # Clean up expired session
            del self._sessions[session_id]
            return None
        
        session.last_accessed = datetime.now(UTC)
        return session
    
    def revoke_session(self, session_id: str) -> bool:
        """
        Revoke user session.
        
        Args:
            session_id: Session ID to revoke
            
        Returns:
            True if session was revoked, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Revoked session: {session_id}")
            return True
        return False
    
    def create_token(
        self,
        user: User,
        token_type: str = "access",
        scopes: Optional[List[str]] = None,
        expires_in: Optional[timedelta] = None
    ) -> AuthToken:
        """
        Create authentication token.
        
        Args:
            user: User to create token for
            token_type: Token type (access, refresh)
            scopes: Token scopes
            expires_in: Token expiration time
            
        Returns:
            Created token
        """
        token_id = self._generate_token()
        
        if expires_in is None:
            if token_type == "access":
                expires_in = timedelta(minutes=self.access_token_expire_minutes)
            elif token_type == "refresh":
                expires_in = timedelta(days=self.refresh_token_expire_days)
            else:
                expires_in = timedelta(hours=1)
        
        expires_at = datetime.now(UTC) + expires_in
        
        token = AuthToken(
            token_id=token_id,
            user_id=user.id,
            token_type=token_type,
            expires_at=expires_at,
            scopes=scopes or []
        )
        
        self._tokens[token_id] = token
        logger.info(f"Created {token_type} token for user: {user.username}")
        return token
    
    def validate_token(self, token_id: str) -> Optional[AuthToken]:
        """
        Validate authentication token.
        
        Args:
            token_id: Token ID to validate
            
        Returns:
            Valid token or None if invalid
        """
        token = self._tokens.get(token_id)
        if not token:
            return None
        
        if not token.is_valid():
            # Clean up invalid token
            if token.is_expired():
                del self._tokens[token_id]
            return None
        
        return token
    
    def revoke_token(self, token_id: str) -> bool:
        """
        Revoke authentication token.
        
        Args:
            token_id: Token ID to revoke
            
        Returns:
            True if token was revoked, False if not found
        """
        if token_id in self._tokens:
            self._tokens[token_id].is_revoked = True
            logger.info(f"Revoked token: {token_id}")
            return True
        return False
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self._users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        user_id = self._username_to_id.get(username)
        return self._users.get(user_id) if user_id else None
    
    def update_user_role(self, user_id: str, new_role: UserRole) -> bool:
        """
        Update user role.
        
        Args:
            user_id: User ID
            new_role: New user role
            
        Returns:
            True if updated, False if user not found
        """
        user = self._users.get(user_id)
        if not user:
            return False
        
        user.role = new_role
        user.permissions = self._get_default_permissions(new_role)
        logger.info(f"Updated user {user.username} role to {new_role.value}")
        return True
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of cleaned sessions."""
        expired_sessions = [
            session_id for session_id, session in self._sessions.items()
            if session.is_expired()
        ]
        
        for session_id in expired_sessions:
            del self._sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    def get_user_sessions(self, user_id: str) -> List[Session]:
        """Get all active sessions for a user."""
        return [
            session for session in self._sessions.values()
            if session.user_id == user_id and not session.is_expired()
        ]
    
    def revoke_all_user_sessions(self, user_id: str) -> int:
        """Revoke all sessions for a user and return count of revoked sessions."""
        user_sessions = [
            session_id for session_id, session in self._sessions.items()
            if session.user_id == user_id
        ]
        
        for session_id in user_sessions:
            del self._sessions[session_id]
        
        logger.info(f"Revoked {len(user_sessions)} sessions for user: {user_id}")
        return len(user_sessions)


__all__ = [
    "AuthManager",
    "User",
    "Session", 
    "AuthToken",
    "UserRole",
    "Permission"
]
