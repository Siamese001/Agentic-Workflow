"""
Security Utils - Stub module for backwards compatibility.
"""
from typing import Any, Dict, List, Optional
import hashlib


def hash_data(data: str) -> str:
    """Hash data using SHA256."""
    return hashlib.sha256(data.encode()).hexdigest()


def sanitize_input(text: str) -> str:
    """Sanitize input string."""
    import re
    return re.sub(r'[<>"\']', '', text).strip()


class SecurityContext:
    """Context for security operations."""
    def __init__(self, user: str = "anonymous"):
        self.user = user
        self._permissions = set()
    
    def grant(self, permission: str) -> None:
        self._permissions.add(permission)
    
    def has_permission(self, permission: str) -> bool:
        return permission in self._permissions


__all__ = ['hash_data', 'sanitize_input', 'SecurityContext']
