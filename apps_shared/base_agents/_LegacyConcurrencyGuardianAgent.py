from __future__ import annotations

import asyncio

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Protocol

Logger: Any = logging.getLogger(__name__)


class LockStorageProtocol(Protocol):
    """
    Protocol defining the interface for distributed lock storage operations.
    This allows ConcurrencyGuardianAgent to depend on an abstraction, not a concrete implementation.
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


_global_lock_implementation: LockStorageProtocol | None = None


def configure_distributed_locks(lock_impl: LockStorageProtocol) -> Any:
    """
    Configures the distributed lock implementation for the ConcurrencyGuardianAgent module.
    This function should be called once at application startup or in the composition root
    to inject the concrete lock storage dependency.

    Args:
        lock_impl: An object implementing the LockStorageProtocol.
    """
    global _global_lock_implementation
    if not isinstance(lock_impl, LockStorageProtocol):
        raise TypeError("Provided lock_impl must implement LockStorageProtocol.")
    _global_lock_implementation = lock_impl
    LOGGER.info("Distributed lock implementation configured for ConcurrencyGuardianAgent module.")


def _get_lock_implementation() -> LockStorageProtocol:
    """
    Internal helper to retrieve the configured lock implementation.
    Raises a RuntimeError if the implementation has not been configured.
    """
    if _global_lock_implementation is None:
        raise RuntimeError(
            "Distributed lock implementation not configured. Call configure_distributed_locks() before using ConcurrencyGuardianAgent or any function that relies on distributed locks."
        )
    return _global_lock_implementation


async def acquire_lock(key: str, timeout: float) -> bool:
    """
    Acquire a distributed lock using the configured implementation.
    This function is intended for internal use by ConcurrencyGuardianAgent and
    other components within this module that need to interact with the
    distributed lock system.
    """
    return await _get_lock_implementation().acquire_lock(key, timeout)


async def release_lock(key: str) -> bool:
    """
    Release a distributed lock using the configured implementation.
    This function is intended for internal use by ConcurrencyGuardianAgent and
    other components within this module that need to interact with the
    distributed lock system.
    """
    return await _get_lock_implementation().release_lock(key)


default_lock_timeout: Any = int(os.getenv("DEFAULT_LOCK_TIMEOUT", "30"))
max_retry_attempts: Any = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
retry_delay: Any = float(os.getenv("RETRY_DELAY", "0.5"))
few_shot_concurrency: Any = "\nfrom agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin\nfrom agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin\nYou are the ConcurrencyGuardianAgent, an expert in managing concurrent operations.\n\nYour role is to:\n1. Prevent race conditions in multi-agent execution\n2. Manage resource locks efficiently\n3. Detect and resolve deadlocks\n4. Ensure thread-safe operations\n\nRules:\n- Always acquire locks before accessing shared resources\n- Release locks promptly after use\n- Use timeouts to prevent deadlocks\n- Prefer async operations when possible\n"


class LockInfo:
    """Information about an active lock."""

    def __init__(self, key: str, owner: str, timeout: float) -> None:
        self.key = key
        self.owner = owner
        self.timeout = timeout
        self.acquired_at = datetime.now(timezone.utc)
        self.expires_at = self.acquired_at + timedelta(seconds=timeout)

    def is_expired(self) -> bool:
        """Check if lock has expired using UTC-aware comparison."""
        return datetime.now(timezone.utc) > self.expires_at

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "owner": self.owner,
            "timeout": self.timeout,
            "acquired_at": self.acquired_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }


from agentic_core.utils.core_extensions.healer_mixin import HealerMixin


# Legacy L1 version - use L2 canonical (concurrency is execution-level)
class _LegacyConcurrencyGuardianAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """
    Manages concurrent operations and prevents conflicts.

    Features:
    - Distributed lock management
    - Deadlock detection
    - Resource access tracking
    - Automatic lock cleanup
    """

    def __init__(self) -> None:
        """Initialize the ConcurrencyGuardianAgent."""
        self.active_locks: dict[str, LockInfo] = {}
        self.lock_history: list[dict] = []
        self.enabled = True
        self.stats = {"locks_acquired": 0, "locks_released": 0, "timeouts": 0, "conflicts": 0}
        LOGGER.info("ConcurrencyGuardianAgent initialized")

    async def acquire_lock(self, key: str, owner: str = None, timeout: float = None) -> bool:
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
            current_task: Any = asyncio.current_task()
            task_id: Any = id(current_task) if current_task else "main"
        except RuntimeError:
            task_id: Any = "no-loop"
        owner: Any = owner or f"process-{task_id}"
        timeout: Any = timeout or DEFAULT_LOCK_TIMEOUT
        for attempt in range(MAX_RETRY_ATTEMPTS):
            if key in self.active_locks:
                existing: Any = self.active_locks[key]
                if not existing.is_expired():
                    self.stats["conflicts"] += 1
                    LOGGER.warning(
                        f"Lock conflict for {key} (held by {existing.owner}) - Attempt {attempt + 1}"
                    )
                    if attempt < MAX_RETRY_ATTEMPTS - 1:
                        await asyncio.sleep(RETRY_DELAY)
                        continue
                    return False
                else:
                    self.active_locks.pop(key, None)
            acquired: Any = await acquire_lock(key, timeout)
            if acquired:
                LockInfo: Any = LockInfo(key, owner, timeout)
                self.active_locks[key] = LockInfo
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
        success: Any = await release_lock(key)
        if success:
            LockInfo: Any = self.active_locks.pop(key, None)
            if LockInfo:
                self.lock_history.append(LockInfo.to_dict())
                if len(self.lock_history) > 100:
                    self.lock_history.pop(0)
            self.stats["locks_released"] += 1
            LOGGER.info(f"Lock released: {key}")
            return True
        LOGGER.error(f"Failed to release distributed lock: {key}")
        return False

    async def cleanup_expired_locks(self) -> Any:
        """Periodically clean up expired local lock records."""
        expired_keys: Any = [k for k, v in self.active_locks.items() if v.is_expired()]
        for key in expired_keys:
            self.active_locks.pop(key, None)
            self.stats["timeouts"] += 1
            LOGGER.debug(f"Cleaned up expired lock record: {key}")

    def heal_repository(self) -> dict:
        """Invoke healing chain via super()."""
        return super().heal_repository()
