"""UWG Stage U4: CLAIM WRITE LOCK - Exclusive write access.

10C-REQ-125: Prevent ghost writes overlapping mutations claim exclusive
write-access to knowledge substrate.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any

from .uwg_clerk import WriteRequest


@dataclass
class WriteLock:
    """Represents an acquired write lock."""
    request_hash: str
    actor_id: str
    path: str
    acquired_at: float = field(default_factory=time.time)
    lock_id: str = field(default_factory=lambda: str(time.time()))


class UWGLocker:
    """UWG Stage U4: Write lock manager.

    10C-REQ-125: Prevent ghost writes overlapping mutations
    claim exclusive write-access to knowledge substrate.
    """

    def __init__(self) -> None:
        self._active_locks: dict[str, WriteLock] = {}  # path -> lock
        self._lock_mutex: threading.Lock = threading.Lock()
        self._lock_timeout: float = 30.0  # seconds

    def acquire(self, request: WriteRequest) -> WriteLock | None:
        """Acquire write lock for path.

        Returns lock if acquired, None if path already locked.
        """
        with self._lock_mutex:
            # Check if path is already locked
            if request.path in self._active_locks:
                existing = self._active_locks[request.path]
                # Check for lock timeout
                if time.time() - existing.acquired_at > self._lock_timeout:
                    # Lock expired, release it
                    del self._active_locks[request.path]
                else:
                    return None  # Path locked by another request

            # Acquire lock
            lock = WriteLock(
                request_hash=request.request_hash,
                actor_id=request.actor_id,
                path=request.path,
            )
            self._active_locks[request.path] = lock
            return lock

    def release(self, lock: WriteLock) -> bool:
        """Release write lock.

        Returns True if released, False if lock not found.
        """
        with self._lock_mutex:
            if lock.path in self._active_locks:
                existing = self._active_locks[lock.path]
                if existing.lock_id == lock.lock_id:
                    del self._active_locks[lock.path]
                    return True
            return False

    def is_locked(self, path: str) -> bool:
        """Check if path is currently locked."""
        with self._lock_mutex:
            if path in self._active_locks:
                lock = self._active_locks[path]
                # Check for timeout
                if time.time() - lock.acquired_at > self._lock_timeout:
                    del self._active_locks[path]
                    return False
                return True
            return False

    def get_lock_holder(self, path: str) -> str | None:
        """Get actor_id holding lock on path, if any."""
        with self._lock_mutex:
            if path in self._active_locks:
                lock = self._active_locks[path]
                if time.time() - lock.acquired_at <= self._lock_timeout:
                    return lock.actor_id
            return None

    def release_all_for_actor(self, actor_id: str) -> int:
        """Release all locks held by actor.

        Returns number of locks released.
        """
        with self._lock_mutex:
            to_release = [
                path for path, lock in self._active_locks.items()
                if lock.actor_id == actor_id
            ]
            for path in to_release:
                del self._active_locks[path]
            return len(to_release)

    def set_timeout(self, seconds: float) -> None:
        """Set lock timeout in seconds."""
        self._lock_timeout = max(1.0, seconds)
