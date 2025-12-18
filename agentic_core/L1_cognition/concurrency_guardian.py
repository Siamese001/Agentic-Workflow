"""
ConcurrencyGuardian - L1 Guardian for Concurrent Operations

Manages Redis/File locks and ensures safe concurrent execution.
Prevents race conditions and resource conflicts.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

from L4_state.storage import acquire_lock, release_lock

LOGGER = logging.getLogger(__name__)

# Constants
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

Example lock usage:
```python
lock_key = "resource:operation:id"
if await acquire_lock(lock_key, timeout=30):
    try:
        # Critical section
        await process_resource()
    finally:
        await release_lock(lock_key)
```
"""

# Configuration
DEFAULT_LOCK_TIMEOUT = 30  # seconds
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 0.5  # seconds


class LockInfo:
    """Information about an active lock."""
    
    def __init__(self, key: str, owner: str, timeout: float):
        self.key = key
        self.owner = owner
        self.timeout = timeout
        self.acquired_at = datetime.utcnow()
        self.expires_at = self.acquired_at + timedelta(seconds=timeout)
    
    def is_expired(self) -> bool:
        """Check if lock has expired."""
        return datetime.utcnow() > self.expires_at
    
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
        Acquire a distributed lock.
        
        Args:
            key: Lock key
            owner: Lock owner identifier
            timeout: Lock timeout in seconds
            
        Returns:
            True if lock acquired successfully
        """
        if not self.enabled:
            return True
        
        owner = owner or f"process-{id(asyncio.current_task())}"
        timeout = timeout or DEFAULT_LOCK_TIMEOUT
        
        # Check if lock already exists
        if key in self.active_locks:
            existing = self.active_locks[key]
            if not existing.is_expired():
                self.stats["conflicts"] += 1
                LOGGER.warning(f"Lock conflict for {key} (held by {existing.owner})")
                return False
            else:
                # Clean up expired lock
                del self.active_locks[key]
        
        # Try to acquire distributed lock
        acquired = await acquire_lock(key, timeout)
        
        if acquired:
            # Record lock
            lock_info = LockInfo(key, owner, timeout)
            self.active_locks[key] = lock_info
            self.stats["locks_acquired"] += 1
            
            LOGGER.debug(f"Lock acquired: {key} by {owner}")
            return True
        else:
            self.stats["timeouts"] += 1
            LOGGER.warning(f"Lock timeout: {key}")
            return False
    
    async def release_lock(self, key: str, owner: str = None) -> bool:
        """
        Release a distributed lock.
        
        Args:
            key: Lock key
            owner: Lock owner identifier
            
        Returns:
            True if lock released successfully
        """
        if not self.enabled:
            return True
        
        if key not in self.active_locks:
            LOGGER.warning(f"Attempted to release non-existent lock: {key}")
            return False
        
        lock_info = self.active_locks[key]
        
        # Check ownership
        if owner and lock_info.owner != owner:
            LOGGER.warning(f"Lock ownership mismatch: {key}")
            return False
        
        # Release distributed lock
        released = await release_lock(key)
        
        if released:
            # Record release
            self.lock_history.append(lock_info.to_dict())
            del self.active_locks[key]
            self.stats["locks_released"] += 1
            
            LOGGER.debug(f"Lock released: {key} by {owner}")
            return True
        else:
            LOGGER.error(f"Failed to release lock: {key}")
            return False
    
    async def with_lock(self, key: str, owner: str = None, 
                       timeout: float = None):
        """
        Context manager for lock-protected operations.
        
        Args:
            key: Lock key
            owner: Lock owner
            timeout: Lock timeout
            
        Returns:
            Context manager
        """
        return LockContext(self, key, owner, timeout)
    
    def cleanup_expired_locks(self) -> int:
        """
        Clean up expired locks.
        
        Returns:
            Number of locks cleaned up
        """
        expired_keys = []
        
        for key, lock_info in self.active_locks.items():
            if lock_info.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            lock_info = self.active_locks[key]
            self.lock_history.append(lock_info.to_dict())
            del self.active_locks[key]
            LOGGER.warning(f"Cleaned up expired lock: {key}")
        
        return len(expired_keys)
    
    def get_active_locks(self) -> List[Dict]:
        """Get information about active locks."""
        return [lock.to_dict() for lock in self.active_locks.values()]
    
    def get_statistics(self) -> Dict:
        """Get concurrency statistics."""
        return {
            "enabled": self.enabled,
            "active_locks": len(self.active_locks),
            "statistics": self.stats.copy(),
            "lock_history_size": len(self.lock_history)
        }
    
    def detect_deadlock(self) -> List[Dict]:
        """
        Detect potential deadlocks.
        
        Returns:
            List of potential deadlock scenarios
        """
        deadlocks = []
        
        # Simple deadlock detection: locks held too long
        for key, lock_info in self.active_locks.items():
            age = (datetime.utcnow() - lock_info.acquired_at).total_seconds()
            if age > lock_info.timeout * 2:  # Held twice as long as timeout
                deadlocks.append({
                    "type": "long_held_lock",
                    "key": key,
                    "owner": lock_info.owner,
                    "age_seconds": age,
                    "timeout": lock_info.timeout
                })
        
        return deadlocks


class LockContext:
    """Context manager for lock operations."""
    
    def __init__(self, guardian: ConcurrencyGuardian, key: str, 
                 owner: str = None, timeout: float = None):
        self.guardian = guardian
        self.key = key
        self.owner = owner
        self.timeout = timeout
        self.acquired = False
    
    async def __aenter__(self):
        """Acquire lock."""
        self.acquired = await self.guardian.acquire_lock(
            self.key, self.owner, self.timeout
        )
        if not self.acquired:
            raise RuntimeError(f"Failed to acquire lock: {self.key}")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release lock."""
        if self.acquired:
            await self.guardian.release_lock(self.key, self.owner)
        return False


class ResourceManager:
    """
    Manages access to shared resources.
    """
    
    def __init__(self, guardian: ConcurrencyGuardian):
        self.guardian = guardian
        self.resources: Dict[str, Dict] = {}
    
    async def access_resource(self, resource_id: str, operation: str, 
                            owner: str = None) -> bool:
        """
        Access a shared resource safely.
        
        Args:
            resource_id: Resource identifier
            operation: Operation type (read/write/execute)
            owner: Requesting owner
            
        Returns:
            True if access granted
        """
        lock_key = f"resource:{resource_id}:{operation}"
        
        async with await self.guardian.with_lock(lock_key, owner):
            # Check resource availability
            if resource_id not in self.resources:
                self.resources[resource_id] = {
                    "created_at": datetime.utcnow().isoformat(),
                    "access_count": 0
                }
            
            # Update access count
            self.resources[resource_id]["access_count"] += 1
            self.resources[resource_id]["last_access"] = datetime.utcnow().isoformat()
            
            return True
    
    def get_resource_info(self, resource_id: str) -> Optional[Dict]:
        """Get information about a resource."""
        return self.resources.get(resource_id)


# Global instance
_concurrency_guardian: Optional[ConcurrencyGuardian] = None
_resource_manager: Optional[ResourceManager] = None


def get_concurrency_guardian() -> ConcurrencyGuardian:
    """Get or create the global ConcurrencyGuardian instance."""
    global _concurrency_guardian
    if _concurrency_guardian is None:
        _concurrency_guardian = ConcurrencyGuardian()
    return _concurrency_guardian


def get_resource_manager() -> ResourceManager:
    """Get or create the global ResourceManager instance."""
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager(get_concurrency_guardian())
    return _resource_manager


async def initialize_concurrency_guardian():
    """Initialize the ConcurrencyGuardian system."""
    guardian = get_concurrency_guardian()
    LOGGER.info("ConcurrencyGuardian system initialized")


# Convenience functions
async def acquire_lock(key: str, owner: str = None, timeout: float = None) -> bool:
    """Acquire a distributed lock."""
    guardian = get_concurrency_guardian()
    return await guardian.acquire_lock(key, owner, timeout)


async def release_lock(key: str, owner: str = None) -> bool:
    """Release a distributed lock."""
    guardian = get_concurrency_guardian()
    return await guardian.release_lock(key, owner)


async def with_lock(key: str, owner: str = None, timeout: float = None):
    """Get a lock context manager."""
    guardian = get_concurrency_guardian()
    return await guardian.with_lock(key, owner, timeout)
