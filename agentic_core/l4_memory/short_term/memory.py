"""
Short Term Memory Implementation
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import deque


@dataclass
class MemoryItem:
    """An item stored in memory"""
    key: str
    value: Any
    timestamp: datetime
    ttl: Optional[timedelta] = None
    access_count: int = 0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

    def is_expired(self) -> bool:
        """Check if this memory item has expired"""
        if self.ttl is None:
            return False
        return datetime.now() > self.timestamp + self.ttl

    def access(self) -> Any:
        """Access the memory item and update access count"""
        self.access_count += 1
        return self.value


class ShortTermMemory:
    """Short term memory implementation with TTL and size limits"""

    def __init__(self, max_size: int = 1000, default_ttl: timedelta = None):
        self.max_size = max_size
        self.default_ttl = default_ttl or timedelta(hours=1)
        self.memory: Dict[str, MemoryItem] = {}
        self.access_order = deque()  # Track access order for LRU eviction
        self.created_at = datetime.now()
        self.stats = {
            "total_sets": 0,
            "total_gets": 0,
            "total_deletes": 0,
            "evictions": 0
        }

    def set(self, key: str, value: Any, ttl: timedelta = None) -> bool:
        """Store a value in short term memory"""
        try:
            memory_item = MemoryItem(
                key=key,
                value=value,
                timestamp=datetime.now(),
                ttl=ttl or self.default_ttl
            )

            # Evict if necessary
            if len(self.memory) >= self.max_size and key not in self.memory:
                self._evict_lru()

            self.memory[key] = memory_item
            self.access_order.append(key)
            self.stats["total_sets"] += 1
            return True

        except Exception:
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from short term memory"""
        if key not in self.memory:
            self.stats["total_gets"] += 1
            return default

        memory_item = self.memory[key]

        # Check if expired
        if memory_item.is_expired():
            del self.memory[key]
            self.access_order = deque(k for k in self.access_order if k != key)
            self.stats["total_gets"] += 1
            return default

        # Update access order
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)

        self.stats["total_gets"] += 1
        return memory_item.access()

    def delete(self, key: str) -> bool:
        """Delete a value from short term memory"""
        if key in self.memory:
            del self.memory[key]
            self.access_order = deque(k for k in self.access_order if k != key)
            self.stats["total_deletes"] += 1
            return True
        return False

    def exists(self, key: str) -> bool:
        """Check if a key exists in memory"""
        if key not in self.memory:
            return False

        # Check if expired
        if self.memory[key].is_expired():
            del self.memory[key]
            self.access_order = deque(k for k in self.access_order if k != key)
            return False

        return True

    def clear(self):
        """Clear all memory"""
        self.memory.clear()
        self.access_order.clear()

    def cleanup_expired(self) -> int:
        """Remove expired items and return count of removed items"""
        expired_keys = []
        # Note: current_time would be used in a real implementation for TTL checks
        # datetime.now()  # Placeholder for time-based expiration

        for key, item in self.memory.items():
            if item.is_expired():
                expired_keys.append(key)

        for key in expired_keys:
            del self.memory[key]
            self.access_order = deque(k for k in self.access_order if k != key)

        return len(expired_keys)

    def _evict_lru(self):
        """Evict least recently used item"""
        if self.access_order:
            lru_key = self.access_order.popleft()
            if lru_key in self.memory:
                del self.memory[lru_key]
                self.stats["evictions"] += 1

    def keys(self) -> List[str]:
        """Get all keys in memory"""
        self.cleanup_expired()
        return list(self.memory.keys())

    def size(self) -> int:
        """Get current memory size"""
        self.cleanup_expired()
        return len(self.memory)

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            "max_size": self.max_size,
            "current_size": self.size(),
            "stats": self.stats.copy(),
            "created_at": self.created_at.isoformat()
        }

    def get_memory_info(self) -> Dict[str, Any]:
        """Get detailed memory information"""
        items = []
        for key, item in self.memory.items():
            items.append({
                "key": key,
                "timestamp": item.timestamp.isoformat(),
                "ttl": item.ttl.total_seconds() if item.ttl else None,
                "access_count": item.access_count,
                "is_expired": item.is_expired()
            })

        return {
            "items": items,
            "stats": self.get_stats()
        }

    def __len__(self):
        return self.size()

    def __contains__(self, key: str):
        return self.exists(key)

    def __str__(self):
        return f"ShortTermMemory(size={self.size()}/{self.max_size})"

    def __repr__(self):
        return self.__str__()
