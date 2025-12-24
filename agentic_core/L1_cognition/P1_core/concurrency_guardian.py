from typing import Any, Optional, Protocol, Dict, List
import time

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone


LOGGER = logging.getLogger(__name__)

# --- Start of Refactor Changes for Dependency Inversion ---

class LockStorageProtocol(Protocol):
    """
    Protocol defining the interface for distributed lock storage operations.
    This allows ConcurrencyGuardian to depend on an abstraction, not a concrete implementation.
    """
    async def acquire_lock(self, key: str, timeout: float) -> bool:
        """
        Acquire a distributed lock for a given key with a specified timeout.
        Returns True if the lock was acquired, False otherwise.
        """
        ...
    async def release_lock(self, key: str) -> bool:
        """
        Release a previously acquired distributed lock for a given key.
        Returns True if the lock was successfully released, False otherwise.
        """
        ...

# Global variable to hold the injected lock implementation.
# This allows the module-level acquire_lock and release_lock functions
# to delegate to a concrete implementation provided at runtime.
_global_lock_implementation: Optional[LockStorageProtocol] = None

def configure_distributed_locks(lock_impl: LockStorageProtocol):
    """
    Configures the distributed lock implementation for the ConcurrencyGuardian module.
    This function should be called once at application startup or in the composition root
    to inject the concrete lock storage dependency.

    Args:
        lock_impl: An object implementing the LockStorageProtocol.
    """
    global _global_lock_implementation
    if not isinstance(lock_impl, LockStorageProtocol):
        raise TypeError("Provided lock_impl must implement LockStorageProtocol.")
    _global_lock_implementation = lock_impl
    LOGGER.info("Distributed lock implementation configured for ConcurrencyGuardian module.")

def _get_lock_implementation() -> LockStorageProtocol:
    """
    Internal helper to retrieve the configured lock implementation.
    Raises a RuntimeError if the implementation has not been configured.
    """
    if _global_lock_implementation is None:
        raise RuntimeError(
            "Distributed lock implementation not configured. "
            "Call configure_distributed_locks() before using ConcurrencyGuardian "
            "or any function that relies on distributed locks."
        )
    return _global_lock_implementation

# These module-level functions replace the direct import from L4_state.
# They delegate calls to the globally configured lock implementation.
async def acquire_lock(key: str, timeout: float) -> bool:
    """
    Acquire a distributed lock using the configured implementation.
    This function is intended for internal use by ConcurrencyGuardian and
    other components within this module that need to interact with the
    distributed lock system.
    """
    return await _get_lock_implementation().acquire_lock(key, timeout)

async def release_lock(key: str) -> bool:
    """
    Release a distributed lock using the configured implementation.
    This function is intended for internal use by ConcurrencyGuardian and
    other components within this module that need to interact with the
    distributed lock system.
    """
    return await _get_lock_implementation().release_lock(key)

# --- End of Refactor Changes ---


# Constants - Using env vars for security and flexibility
DEFAULT_LOCK_TIMEOUT = int(os.getenv("DEFAULT_LOCK_TIMEOUT", "30"))
MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "0.5"))

# Configuration
FEW_SHOT_CONCURRENCY = """
You are the ConcurrencyGuardian, an expert in managing concurrent operations.

Your role is to:
1. Prevent race conditions in multi-agent execution
2. Manage resource locks efficiently
3. Detect and resolve deadlocks
4. Ensure thread-safe operations

Rules:
- Always acquire locks before accessing shared resources
- Release locks promptly after use
- Use timeouts to prevent deadlocks
- Prefer async operations when possible
"""

class LockInfo:
    """Information about an active lock."""

    def __init__(self, key: str, owner: str, timeout: float):
        self.key = key
        self.owner = owner
        self.timeout = timeout
        self.acquired_at = datetime.now(timezone.utc)
        self.expires_at = self.acquired_at + timedelta(seconds=timeout)

    def is_expired(self) -> bool:
        """Check if lock has expired using UTC-aware comparison."""
        return datetime.now(timezone.utc) > self.expires_at

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "owner": self.owner,
            "timeout": self.timeout,
            "acquired_at": self.acquired_at.isoformat(),
            "expires_at": self.expires_at.isoformat()
        }


class ConcurrencyGuardian:
    """
    Manages concurrent operations and prevents conflicts.

    Features:
    - Distributed lock management
    - Deadlock detection
    - Resource access tracking
    - Automatic lock cleanup
    """

    def __init__(self):
        """Initialize the ConcurrencyGuardian."""
        self.active_locks: Dict[str, LockInfo] = {}
        self.lock_history: List[Dict] = []
        self.enabled = True

        # Statistics
        self.stats = {
            "locks_acquired": 0,
            "locks_released": 0,
            "timeouts": 0,
            "conflicts": 0
        }

        LOGGER.info("ConcurrencyGuardian initialized")

    async def acquire_lock(self, key: str, owner: str = None,
                          timeout: float = None) -> bool:
        """
        Acquire a distributed lock with async retry logic.

        Args:
            key: Lock key
            owner: Lock owner identifier
            timeout: Lock timeout in seconds

        Returns:
            True if lock acquired successfully
        """
        if not self.enabled:
            return True

        try:
            current_task = asyncio.current_task()
            task_id = id(current_task) if current_task else "main"
        except RuntimeError:
            task_id = "no-loop"

        owner = owner or f"process-{task_id}"
        timeout = timeout or DEFAULT_LOCK_TIMEOUT

        for attempt in range(MAX_RETRY_ATTEMPTS):
            # Check if lock already exists locally
            if key in self.active_locks:
                existing = self.active_locks[key]
                if not existing.is_expired():
                    self.stats["conflicts"] += 1
                    LOGGER.warning(f"Lock conflict for {key} (held by {existing.owner}) - Attempt {attempt + 1}")
                    if attempt < MAX_RETRY_ATTEMPTS - 1:
                        await asyncio.sleep(RETRY_DELAY)
                        continue
                    return False
                else:
                    # Clean up expired lock
                    self.active_locks.pop(key, None)

            # Try to acquire distributed lock using the module-level function
            acquired = await acquire_lock(key, timeout)

            if acquired:
                # Record lock
                lock_info = LockInfo(key, owner, timeout)
                self.active_locks[key] = lock_info
                self.stats["locks_acquired"] += 1
                LOGGER.info(f"Lock acquired: {key} by {owner}")
                return True

            if attempt < MAX_RETRY_ATTEMPTS - 1:
                await asyncio.sleep(RETRY_DELAY)

        return False

    async def release_lock(self, key: str) -> bool:
        """
        Release a distributed lock.

        Args:
            key: Lock key

        Returns:
            True if lock released successfully
        """
        if key not in self.active_locks:
            LOGGER.debug(f"Release requested for inactive lock: {key}")
            return False

        # Release distributed lock using the module-level function
        success = await release_lock(key)
        if success:
            lock_info = self.active_locks.pop(key, None)
            if lock_info:
                self.lock_history.append(lock_info.to_dict())
                # Maintain history limit
                if len(self.lock_history) > 100:
                    self.lock_history.pop(0)

            self.stats["locks_released"] += 1
            LOGGER.info(f"Lock released: {key}")
            return True

        LOGGER.error(f"Failed to release distributed lock: {key}")
        return False

    async def cleanup_expired_locks(self):
        """Periodically clean up expired local lock records."""
        expired_keys = [k for k, v in self.active_locks.items() if v.is_expired()]
        for key in expired_keys:
            self.active_locks.pop(key, None)
            self.stats["timeouts"] += 1
            LOGGER.debug(f"Cleaned up expired lock record: {key}")