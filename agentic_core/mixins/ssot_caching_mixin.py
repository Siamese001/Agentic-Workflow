"""
SSOT Caching Mixin — Policy-Hash-Scoped Cache with Replay Safety.

Provides in-memory caching that:
  - Includes active_policy_hash in all cache keys
  - Disables TTL under replay mode (infinite cache lifetime)
  - Never stores secrets or sovereignty tokens
  - Isolates cache state per policy hash

Layer: L2 Execution Aid
Authority: Local cache only. No L4 mutation. No routing influence.
"""
from __future__ import annotations
import logging
import time
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
_logger = logging.getLogger('SSOTCaching')
_SENTINEL = object()

class SSOTCachingMixin:
    """Policy-hash-scoped in-memory cache with replay safety.

    Reads ``active_policy_hash`` and ``is_replay_mode`` from ReplayGuardMixin.
    All cache keys are prefixed with the policy hash.
    Under replay mode, TTL is disabled (entries never expire).
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._ssot_cache: dict[str, dict[str, Any]] = {}

    def cache_get(self, key: str) -> Any:
        """Retrieve a cached value by key (policy-hash-scoped).

        Returns None if key not found or expired.
        """
        scoped_key = self._scoped_key(key)
        entry = self._ssot_cache.get(scoped_key)
        if entry is None:
            return None
        is_replay = getattr(self, 'is_replay_mode', False)
        if not is_replay and entry.get('ttl') is not None:
            if time.time() - entry['created_at'] > entry['ttl']:
                del self._ssot_cache[scoped_key]
                return None
        return entry['value']

    def cache_set(self, key: str, value: Any, ttl: float | None=300.0) -> None:
        """Store a value in the cache (policy-hash-scoped).

        Parameters
        ----------
        key : str
            Cache key.
        value : Any
            Value to cache. Must not be a sovereignty token or secret.
        ttl : float | None
            Time-to-live in seconds. None = no expiry.
            Under replay mode, TTL is always disabled.
        """
        is_replay = getattr(self, 'is_replay_mode', False)
        effective_ttl = None if is_replay else ttl
        scoped_key = self._scoped_key(key)
        self._ssot_cache[scoped_key] = {'value': value, 'created_at': time.time(), 'ttl': effective_ttl, 'policy_hash': getattr(self, 'active_policy_hash', 'unknown')}
        _logger.debug('[SSOTCache] SET %s (ttl=%s)', scoped_key, effective_ttl)

    def cache_invalidate(self, key: str) -> bool:
        """Remove a key from the cache. Returns True if key existed."""
        scoped_key = self._scoped_key(key)
        if scoped_key in self._ssot_cache:
            del self._ssot_cache[scoped_key]
            return True
        return False

    def cache_clear(self) -> int:
        """Clear all cache entries. Returns count of cleared entries."""
        count = len(self._ssot_cache)
        self._ssot_cache.clear()
        return count

    def cache_size(self) -> int:
        """Return number of entries in the cache."""
        return len(self._ssot_cache)

    def _scoped_key(self, key: str) -> str:
        """Prefix key with active_policy_hash for isolation."""
        policy_hash = getattr(self, 'active_policy_hash', 'unknown')
        return f'{policy_hash}:{key}'
