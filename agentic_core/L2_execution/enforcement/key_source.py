"""
Key Discipline Abstraction for L2 Execution
Provides injectable, testable key source with no ambient secrets.
"""

import os
import time
from abc import ABC, abstractmethod
from typing import Final, Dict, Optional


class KeySource(ABC):
    """Abstract base for key sources - must be injected, never ambient."""

    @abstractmethod
    def get_secret(self) -> bytes:
        """Return the secret key for signing/verification."""
        pass
    
    @abstractmethod
    def assert_key_scope(self, artifact_type: str) -> None:
        """Assert that the key is scoped for the given artifact type."""
        pass
    
    @abstractmethod
    def reject_expired_key(self) -> None:
        """Reject if the key has expired."""
        pass


class TestKeySource(KeySource):
    """Deterministic test key source for unit tests."""

    # Fixed test key - matches Phase 1 tests
    TEST_SECRET: Final[bytes] = b"phase1-test-secret-key"
    
    def __init__(self):
        self._key_scopes: Dict[str, bool] = {
            "signature": True,
            "hmac": True,
            "audit": True,
            "trace": True
        }
        self._expiry_time: Optional[float] = None

    def get_secret(self) -> bytes:
        return self.TEST_SECRET
    
    def assert_key_scope(self, artifact_type: str) -> None:
        """Assert that the key is scoped for the given artifact type."""
        if artifact_type not in self._key_scopes:
            raise ValueError(f"Key not scoped for artifact type: {artifact_type}")
        if not self._key_scopes[artifact_type]:
            raise ValueError(f"Key scope invalid for artifact type: {artifact_type}")
    
    def reject_expired_key(self) -> None:
        """Reject if the key has expired."""
        if self._expiry_time and time.time() > self._expiry_time:
            raise ValueError("Key has expired")
    
    def set_key_scope(self, artifact_type: str, allowed: bool):
        """Set key scope for testing."""
        self._key_scopes[artifact_type] = allowed
    
    def set_expiry_time(self, expiry_time: Optional[float]):
        """Set expiry time for testing."""
        self._expiry_time = expiry_time


class EnvKeySource(KeySource):
    """Environment-based key source for production (edge only)."""

    def __init__(self, env_var: str = "L2_EXECUTION_SECRET"):
        self.env_var = env_var
        if env_var not in os.environ:
            raise ValueError(f"Environment variable {env_var} not set")
        
        # Default scopes for production
        self._key_scopes: Dict[str, bool] = {
            "signature": True,
            "hmac": True,
            "audit": True,
            "trace": True
        }
        # Keys expire after 24 hours by default
        self._creation_time = time.time()
        self._ttl = 24 * 60 * 60  # 24 hours in seconds

    def get_secret(self) -> bytes:
        return os.environ[self.env_var].encode()
    
    def assert_key_scope(self, artifact_type: str) -> None:
        """Assert that the key is scoped for the given artifact type."""
        if artifact_type not in self._key_scopes:
            raise ValueError(f"Key not scoped for artifact type: {artifact_type}")
        if not self._key_scopes[artifact_type]:
            raise ValueError(f"Key scope invalid for artifact type: {artifact_type}")
    
    def reject_expired_key(self) -> None:
        """Reject if the key has expired."""
        if time.time() > self._creation_time + self._ttl:
            raise ValueError("Production key has expired")
    
    def set_key_scope(self, artifact_type: str, allowed: bool):
        """Set key scope (for configuration)."""
        self._key_scopes[artifact_type] = allowed
    
    def set_ttl(self, ttl_seconds: int):
        """Set time-to-live for key."""
        self._ttl = ttl_seconds


# Global injection point - must be explicitly set
_injected_key_source: KeySource | None = None


def inject_key_source(source: KeySource) -> None:
    """Inject a key source - must be called at application edge."""
    global _injected_key_source
    _injected_key_source = source


def get_key_source() -> KeySource:
    """Get the injected key source - fails if not injected."""
    global _injected_key_source
    if _injected_key_source is None:
        raise RuntimeError("KeySource not injected - call inject_key_source() first")
    return _injected_key_source


def get_current_secret() -> bytes:
    """Convenience helper to get current secret."""
    return get_key_source().get_secret()
