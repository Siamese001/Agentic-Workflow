from __future__ import annotations

'\n[PHASE 23] LifecycleMixin - Async Resource Management Protocol.\n\nEnforces async startup/shutdown protocols for proper resource management.\nReplaces logic often wrongly placed in __init__ that requires async operations.\n\nThis is the foundation for the Lifecycle-Aware Component System, replacing\nthe "Uber-Mixin" inheritance approach with explicit lifecycle management.\n\nKey Principles:\n1. __init__ is for synchronous, non-blocking setup only\n2. startup() is for async resource initialization (Redis, DB, MCP connections)\n3. shutdown() is for cleanup, connection closing, and graceful termination\n4. Lifecycle state is tracked to prevent double-init or use-before-ready\n\nUsage:\n    class MyAgent(LifecycleMixin, SovereignBaseAgent):\n        async def startup(self):\n            await super().startup()\n            self.redis = await self._connect_redis()\n\n        async def shutdown(self):\n            await self.redis.close()\n            await super().shutdown()\n\n[SSOT] Foundation for all lifecycle-aware mixins.\n'
import asyncio
import logging
import time
from abc import ABC
from enum import Enum
from typing import Any

Logger = logging.getLogger(__name__)


class LifecycleState(Enum):
    """Lifecycle states for component tracking."""

    CREATED = "created"
    STARTING = "starting"
    READY = "ready"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"


class LifecycleError(Exception):
    """Raised when lifecycle protocol is violated."""

    pass


class LifecycleMixin(ABC):
    """
    [PHASE 23] Enforces async startup/shutdown protocols.

    Replaces logic often wrongly placed in __init__ that requires:
    - Async operations (await)
    - Network connections (Redis, DB, MCP)
    - Resource allocation that needs cleanup

    State Machine:
        CREATED -> STARTING -> READY -> STOPPING -> STOPPED
                      |                     |
                      v                     v
                   FAILED               FAILED

    Thread Safety:
        Uses asyncio.Lock to prevent concurrent startup/shutdown.

    Attributes:
        _lifecycle_state: Current lifecycle state
        _lifecycle_error: Error that caused FAILED state
        _startup_time: Timestamp when startup() completed
        _shutdown_time: Timestamp when shutdown() completed
    """

    _lifecycle_state: LifecycleState = LifecycleState.CREATED
    _lifecycle_error: Exception | None = None
    _startup_time: float | None = None
    _shutdown_time: float | None = None
    _lifecycle_lock: asyncio.Lock | None = None

    def __init__(self, *args, **kwargs):
        """
        Synchronous initialization only.

        DO NOT perform async operations here.
        DO NOT open network connections here.
        DO NOT allocate resources that need cleanup here.

        Use startup() for all of the above.
        """
        super().__init__(*args, **kwargs)
        self._lifecycle_state = LifecycleState.CREATED
        self._lifecycle_error = None
        self._startup_time = None
        self._shutdown_time = None
        self._lifecycle_lock = None

    def _get_lifecycle_lock(self) -> asyncio.Lock:
        """Get or create the lifecycle lock (must be called in async context)."""
        if self._lifecycle_lock is None:
            self._lifecycle_lock = asyncio.Lock()
        return self._lifecycle_lock

    @property
    def is_ready(self) -> bool:
        """Check if component is ready for use."""
        return self._lifecycle_state == LifecycleState.READY

    @property
    def is_stopped(self) -> bool:
        """Check if component has been stopped."""
        return self._lifecycle_state in (LifecycleState.STOPPED, LifecycleState.FAILED)

    @property
    def lifecycle_state(self) -> LifecycleState:
        """Get current lifecycle state."""
        return self._lifecycle_state

    def require_ready(self) -> None:
        """
        Assert that component is ready for use.

        Raises:
            LifecycleError: If component is not in READY state
        """
        if self._lifecycle_state != LifecycleState.READY:
            raise LifecycleError(
                f"{self.__class__.__name__} is not ready. Current state: {self._lifecycle_state.value}. Call startup() first."
            )

    async def startup(self) -> None:
        """
        Initialize async resources (Redis, DB, MCP connections, etc).

        Override this method to perform async initialization.
        Always call super().startup() first.

        Raises:
            LifecycleError: If already started or starting
        """
        async with self._get_lifecycle_lock():
            if self._lifecycle_state == LifecycleState.READY:
                Logger.debug(f"[{self.__class__.__name__}] Already started, skipping")
                return
            if self._lifecycle_state == LifecycleState.STARTING:
                raise LifecycleError(f"{self.__class__.__name__} startup already in progress")
            if self._lifecycle_state == LifecycleState.STOPPED:
                raise LifecycleError(f"{self.__class__.__name__} has been stopped and cannot be restarted")
            self._lifecycle_state = LifecycleState.STARTING
            Logger.debug(f"[{self.__class__.__name__}] Starting...")
            try:
                await self._do_startup()
                self._lifecycle_state = LifecycleState.READY
                self._startup_time = time.time()
                Logger.info(f"[{self.__class__.__name__}] Started successfully")
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                self._lifecycle_state = LifecycleState.FAILED
                self._lifecycle_error = e
                Logger.error(f"[{self.__class__.__name__}] Startup failed: {e}")
                raise

    async def _do_startup(self) -> None:
        """
        Override this method to implement actual startup logic.

        This is called within the lifecycle lock, so it's safe to
        modify state without additional synchronization.
        """
        pass

    async def shutdown(self) -> None:
        """
        Cleanup resources, close connections.

        Override this method to perform async cleanup.
        Always call super().shutdown() last.

        Raises:
            LifecycleError: If not started or already stopping
        """
        async with self._get_lifecycle_lock():
            if self._lifecycle_state == LifecycleState.STOPPED:
                Logger.debug(f"[{self.__class__.__name__}] Already stopped, skipping")
                return
            if self._lifecycle_state == LifecycleState.STOPPING:
                raise LifecycleError(f"{self.__class__.__name__} shutdown already in progress")
            if self._lifecycle_state == LifecycleState.CREATED:
                self._lifecycle_state = LifecycleState.STOPPED
                return
            self._lifecycle_state = LifecycleState.STOPPING
            Logger.debug(f"[{self.__class__.__name__}] Stopping...")
            try:
                await self._do_shutdown()
                self._lifecycle_state = LifecycleState.STOPPED
                self._shutdown_time = time.time()
                Logger.info(f"[{self.__class__.__name__}] Stopped successfully")
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                self._lifecycle_state = LifecycleState.FAILED
                self._lifecycle_error = e
                Logger.error(f"[{self.__class__.__name__}] Shutdown failed: {e}")
                raise

    async def _do_shutdown(self) -> None:
        """
        Override this method to implement actual shutdown logic.

        This is called within the lifecycle lock, so it's safe to
        modify state without additional synchronization.
        """
        pass

    def get_lifecycle_stats(self) -> dict[str, Any]:
        """Get lifecycle statistics."""
        return {
            "state": self._lifecycle_state.value,
            "startup_time": self._startup_time,
            "shutdown_time": self._shutdown_time,
            "uptime_seconds": time.time() - self._startup_time
            if self._startup_time and self._lifecycle_state == LifecycleState.READY
            else None,
            "error": str(self._lifecycle_error) if self._lifecycle_error else None,
        }

    async def __aenter__(self):
        """Async context manager entry - calls startup()."""
        await self.startup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - calls shutdown()."""
        await self.shutdown()
        return False
