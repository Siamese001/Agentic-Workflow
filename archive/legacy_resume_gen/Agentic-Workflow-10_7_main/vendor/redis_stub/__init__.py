"""
redis_stub – safe minimal Redis replacement for offline tests.

This stub:
 - does NOT shadow the real 'redis' client
 - is only active when vendor stubs are enabled
 - provides get / set / setex / delete used in v10.7 CacheManager
"""

from __future__ import annotations
import time
from typing import Dict, Any, Optional


class RedisStubStore:
    """In-memory key-value store with optional TTL support."""

    def __init__(self):
        self._store: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}

    def cleanup(self):
        """Remove expired keys."""
        now = time.time()
        to_delete = [k for k, exp in self._expiry.items() if exp <= now]
        for k in to_delete:
            self._store.pop(k, None)
            self._expiry.pop(k, None)

    def get(self, key: str) -> Optional[str]:
        self.cleanup()
        return self._store.get(key)

    def set(self, key: str, value: str) -> None:
        self._store[key] = value

    def setex(self, key: str, ttl: int, value: str) -> None:
        self._store[key] = value
        self._expiry[key] = time.time() + ttl

    def delete(self, key: str):
        self._store.pop(key, None)
        self._expiry.pop(key, None)


class Redis:
    """
    Minimal Redis stub for offline use.
    Supports only what CacheManager needs:
      - get
      - set
      - setex
      - delete
    """

    def __init__(self, *args, **kwargs):
        self._store = RedisStubStore()

    def get(self, key: str):
        return self._store.get(key)

    def set(self, key: str, value: str):
        self._store.set(key, value)

    def setex(self, key: str, ttl: int, value: str):
        self._store.setex(key, ttl, value)

    def delete(self, key: str):
        self._store.delete(key)


__all__ = ["Redis"]
