"""W11 — Write Lock Manager (UWG)

Manages locks for L4 writes to prevent concurrent modification conflicts.
"""
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class LockStatus(Enum):
    """Status of a write lock."""
    PENDING = "pending"
    ACQUIRED = "acquired"
    RELEASED = "released"
    FAILED = "failed"


@dataclass(frozen=True)
class WriteLock:
    """Represents a lock for an L4 write operation."""
    lock_id: str
    commit_request_id: str
    run_id: str
    l4_namespace: str
    status: LockStatus
    
    acquired_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    released_at: Optional[str] = None
    
    def is_active(self) -> bool:
        """Check if lock is currently active."""
        return self.status == LockStatus.ACQUIRED


class WriteLockManager:
    """Manages write locks for UWG admission.
    
    Prevents concurrent writes to the same L4 namespace.
    """
    
    def __init__(self):
        """Initialize lock manager."""
        self._active_locks: Dict[str, WriteLock] = {}  # namespace -> lock
        self._lock_history: List[WriteLock] = []
    
    def acquire_lock(
        self,
        commit_request_id: str,
        run_id: str,
        l4_namespace: str
    ) -> Optional[WriteLock]:
        """Acquire write lock for L4 namespace.
        
        Args:
            commit_request_id: ID of commit request
            run_id: Associated run ID
            l4_namespace: Target L4 namespace
            
        Returns:
            WriteLock if acquired, None if namespace already locked
        """
        # Check if namespace already locked
        if l4_namespace in self._active_locks:
            existing = self._active_locks[l4_namespace]
            if existing.is_active():
                return None  # Lock conflict
        
        # Create and store lock
        lock = WriteLock(
            lock_id=f"lock-{commit_request_id}",
            commit_request_id=commit_request_id,
            run_id=run_id,
            l4_namespace=l4_namespace,
            status=LockStatus.ACQUIRED,
        )
        
        self._active_locks[l4_namespace] = lock
        self._lock_history.append(lock)
        
        return lock
    
    def release_lock(
        self,
        lock_id: str,
        success: bool = True
    ) -> Optional[WriteLock]:
        """Release write lock.
        
        Args:
            lock_id: ID of lock to release
            success: Whether the write succeeded
            
        Returns:
            Updated WriteLock or None if not found
        """
        # Find lock by ID
        for namespace, lock in self._active_locks.items():
            if lock.lock_id == lock_id:
                new_status = LockStatus.RELEASED if success else LockStatus.FAILED
                
                released_lock = WriteLock(
                    lock_id=lock.lock_id,
                    commit_request_id=lock.commit_request_id,
                    run_id=lock.run_id,
                    l4_namespace=lock.l4_namespace,
                    status=new_status,
                    acquired_at=lock.acquired_at,
                    released_at=datetime.now(timezone.utc).isoformat(),
                )
                
                del self._active_locks[namespace]
                self._lock_history.append(released_lock)
                
                return released_lock
        
        return None
    
    def get_active_locks(self) -> Dict[str, WriteLock]:
        """Get all currently active locks."""
        return dict(self._active_locks)
    
    def is_namespace_locked(self, l4_namespace: str) -> bool:
        """Check if namespace is currently locked."""
        if l4_namespace not in self._active_locks:
            return False
        return self._active_locks[l4_namespace].is_active()
    
    def get_lock_history(
        self,
        run_id: Optional[str] = None
    ) -> List[WriteLock]:
        """Get lock history, optionally filtered by run ID."""
        if run_id is None:
            return list(self._lock_history)
        
        return [lock for lock in self._lock_history if lock.run_id == run_id]


# Global lock manager instance (per-process)
default_lock_manager = WriteLockManager()
