"""
Key Discipline Abstraction for L2 Execution
Provides injectable, testable key source with no ambient secrets.
"""

import os
from abc import ABC, abstractmethod
from typing import Final


class KeySource(ABC):
    """Abstract base for key sources - must be injected, never ambient."""

    @abstractmethod
    def get_secret(self) -> bytes:
        """Return the secret key for signing/verification."""
        pass


class TestKeySource(KeySource):
    """Deterministic test key source for unit tests."""

    # Fixed test key - matches Phase 1 tests
    TEST_SECRET: Final[bytes] = b"phase1-test-secret-key"

    def get_secret(self) -> bytes:
        return self.TEST_SECRET


class EnvKeySource(KeySource):
    """Environment-based key source for production (edge only)."""

    def __init__(self, env_var: str = "L2_EXECUTION_SECRET"):
        self.env_var = env_var
        if env_var not in os.environ:
            raise ValueError(f"Environment variable {env_var} not set")

    def get_secret(self) -> bytes:
        return os.environ[self.env_var].encode()


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
