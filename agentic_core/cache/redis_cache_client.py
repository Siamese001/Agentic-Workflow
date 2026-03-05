"""Deterministic, non-authoritative Redis cache client.

Design invariants enforced here:
  1. NON-AUTHORITATIVE: This cache never becomes the source of truth.
     L4 remains the sole persistence authority.  Every value stored here
     is a deterministic derivative of a hash-addressed L4 artifact.
  2. HASH-ONLY KEYING: Cache keys are composed exclusively from content
     hashes supplied by callers.  No wall-clock timestamps, no random
     nonces, no "latest" sentinel values appear in any key.
  3. REPLAY SAFETY: When ``replay_mode=True`` is passed to ``get()``,
     the method returns ``None`` unconditionally so the caller re-derives
     the value from L4 and records it in the deterministic transcript.
  4. CANONICAL SERIALIZATION: ``canonical_json_bytes`` produces a stable
     byte sequence (sorted keys, ASCII-only, no trailing whitespace) that
     is safe to SHA-256 and store as a cache value.
  5. GRACEFUL FALLBACK: When the Redis server is unavailable the client
     silently switches to a bounded in-process LRU store so callers never
     see a hard failure due to cache infrastructure.
  6. TWO DATABASE NAMESPACES:
       DB 0 — hot caches  (L0, L1/Assembly, L3, L5) with configurable TTLs
       DB 1 — coordination (L2 leases / idempotency keys) with short TTLs
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import urllib.parse
from collections import OrderedDict
from dataclasses import dataclass
from enum import IntEnum
from typing import Any

logger = logging.getLogger(__name__)

_MAX_KEY_LEN: int = 512
_MAX_VALUE_BYTES: int = 10 * 1024 * 1024  # 10 MB safety cap
_FALLBACK_MAX_ENTRIES: int = 4096


class CacheDB(IntEnum):
    """Redis logical database index."""

    HOT = 0
    COORDINATION = 1


# ---------------------------------------------------------------------------
# Canonical serialisation helpers
# ---------------------------------------------------------------------------


def canonical_json_bytes(obj: Any) -> bytes:
    """Produce a deterministic, ASCII-safe JSON byte sequence.

    Rules applied:
    - Keys sorted recursively.
    - Separators ``(',', ':')`` — no trailing whitespace.
    - ``ensure_ascii=True`` — safe for SHA-256 and Redis storage.
    - ``allow_nan=False`` — NaN/Infinity in floats would break determinism.
    """
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def content_hash(data: bytes) -> str:
    """Return the SHA-256 hex digest of *data* (64 lowercase hex chars)."""
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# In-process bounded LRU fallback
# ---------------------------------------------------------------------------


class _BoundedLRU:
    """Thread-unsafe, process-local LRU used when Redis is unreachable."""

    def __init__(self, maxsize: int = _FALLBACK_MAX_ENTRIES) -> None:
        self._store: OrderedDict[str, bytes] = OrderedDict()
        self._maxsize = maxsize

    def get(self, key: str) -> bytes | None:
        if key not in self._store:
            return None
        self._store.move_to_end(key)
        return self._store[key]

    def set(self, key: str, value: bytes) -> None:
        if key in self._store:
            self._store.move_to_end(key)
        else:
            if len(self._store) >= self._maxsize:
                self._store.popitem(last=False)
            self._store[key] = value

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def exists(self, key: str) -> bool:
        return key in self._store

    def clear(self) -> None:
        self._store.clear()

    def __len__(self) -> int:
        return len(self._store)


# ---------------------------------------------------------------------------
# Core deterministic Redis cache client
# ---------------------------------------------------------------------------


@dataclass
class CacheStats:
    """Accumulated hit/miss counters (informational only)."""

    hits: int = 0
    misses: int = 0
    fallback_hits: int = 0
    fallback_misses: int = 0
    errors: int = 0
    bypassed_replay: int = 0


class DeterministicRedisCache:
    """Non-authoritative, hash-keyed Redis cache with in-process LRU fallback.

    Instances are lightweight; construct one per DB namespace per process
    (``CacheDB.HOT`` for L0/L1/L3/L5, ``CacheDB.COORDINATION`` for L2).

    Parameters
    ----------
    db:
        Redis logical database index (``CacheDB.HOT`` or
        ``CacheDB.COORDINATION``).
    redis_url:
        Redis connection URL.  Defaults to the ``REDIS_URL`` env-var or
        ``redis://localhost:6379``.  ``rediss://`` enables TLS.
    fallback_maxsize:
        Maximum number of entries retained in the in-process fallback store.
    """

    def __init__(
        self,
        db: CacheDB = CacheDB.HOT,
        redis_url: str | None = None,
        fallback_maxsize: int = _FALLBACK_MAX_ENTRIES,
    ) -> None:
        self._db = db
        self._redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self._conn: Any = None  # lazy redis.Redis
        self._use_fallback: bool = False
        self._fallback = _BoundedLRU(maxsize=fallback_maxsize)
        self.stats = CacheStats()

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def _connect(self) -> Any:
        """Return a live redis.Redis connection, falling back gracefully."""
        if self._use_fallback:
            return None
        if self._conn is not None:
            return self._conn
        try:
            import redis as _redis  # noqa: PLC0415

            parsed = urllib.parse.urlparse(self._redis_url)
            params: dict[str, Any] = {
                "host": parsed.hostname or "localhost",
                "port": int(parsed.port or 6379),
                "db": int(self._db),
                "decode_responses": False,  # we handle bytes ourselves
                "socket_timeout": 2.0,
                "socket_connect_timeout": 2.0,
            }
            if parsed.password:
                params["password"] = parsed.password
            if parsed.scheme == "rediss":
                params["ssl"] = True
                params["ssl_cert_reqs"] = None

            self._conn = _redis.Redis(**params)
            self._conn.ping()
            return self._conn
        except Exception as exc:
            logger.warning(
                "[cache] Redis unavailable (db=%s): %s — switching to in-process fallback",
                int(self._db),
                exc,
            )
            self._use_fallback = True
            self._conn = None
            return None

    def _mark_failed(self, exc: Exception) -> None:
        logger.warning("[cache] Redis operation failed: %s — using fallback", exc)
        self._use_fallback = True
        self._conn = None
        self.stats.errors += 1

    # ------------------------------------------------------------------
    # Key validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_key(key: str) -> None:
        if not key or not isinstance(key, str):
            raise ValueError("Cache key must be a non-empty string")
        if len(key) > _MAX_KEY_LEN:
            raise ValueError(f"Cache key exceeds {_MAX_KEY_LEN}-char limit: {key[:80]}…")
        if any(c in key for c in ("\x00", "\n", "\r")):
            raise ValueError(f"Cache key contains illegal control character: {key!r}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, key: str, *, replay_mode: bool = False) -> bytes | None:
        """Return cached bytes for *key*, or ``None`` on miss / bypass.

        When ``replay_mode=True`` the method always returns ``None`` so the
        caller re-derives the value from L4 and appends it to the transcript,
        preserving replay determinism.
        """
        self._validate_key(key)

        if replay_mode:
            self.stats.bypassed_replay += 1
            return None

        conn = self._connect()
        if conn is not None:
            try:
                raw = conn.get(key)
                if raw is not None:
                    self.stats.hits += 1
                    return raw
                self.stats.misses += 1
                return None
            # guardian: allow-silent-swallow
            except Exception as exc:
                self._mark_failed(exc)

        # Fallback path
        result = self._fallback.get(key)
        if result is not None:
            self.stats.fallback_hits += 1
            return result
        self.stats.fallback_misses += 1
        return None

    def set(self, key: str, value: bytes, ttl_seconds: int = 3600) -> bool:
        """Persist *value* bytes under *key* with the given TTL.

        Returns ``True`` on success (either Redis or fallback).

        Raises
        ------
        TypeError
            If *value* is not ``bytes``.
        ValueError
            If the value exceeds the 10 MB safety cap.
        """
        self._validate_key(key)
        if not isinstance(value, bytes):
            raise TypeError(f"Cache value must be bytes, got {type(value).__name__}")
        if len(value) > _MAX_VALUE_BYTES:
            raise ValueError(f"Cache value too large ({len(value)} bytes > {_MAX_VALUE_BYTES})")

        conn = self._connect()
        if conn is not None:
            try:
                conn.setex(key, ttl_seconds, value)
                return True
            # guardian: allow-silent-swallow
            except Exception as exc:
                self._mark_failed(exc)

        self._fallback.set(key, value)
        return True

    def delete(self, key: str) -> bool:
        """Evict *key* from Redis and the fallback store."""
        self._validate_key(key)
        conn = self._connect()
        deleted = False
        if conn is not None:
            try:
                deleted = bool(conn.delete(key))
            # guardian: allow-silent-swallow
            except Exception as exc:
                self._mark_failed(exc)
        self._fallback.delete(key)
        return deleted

    def exists(self, key: str) -> bool:
        """Return ``True`` if *key* is present in the cache (Redis or fallback)."""
        self._validate_key(key)
        conn = self._connect()
        if conn is not None:
            try:
                return bool(conn.exists(key))
            # guardian: allow-silent-swallow
            except Exception as exc:
                self._mark_failed(exc)
        return self._fallback.exists(key)

    def set_json(self, key: str, obj: Any, ttl_seconds: int = 3600) -> bool:
        """Serialise *obj* via ``canonical_json_bytes`` and store it."""
        return self.set(key, canonical_json_bytes(obj), ttl_seconds=ttl_seconds)

    def get_json(self, key: str, *, replay_mode: bool = False) -> Any | None:
        """Retrieve and deserialise a JSON value; returns ``None`` on miss."""
        raw = self.get(key, replay_mode=replay_mode)
        if raw is None:
            return None
        return json.loads(raw.decode("ascii"))

    # ------------------------------------------------------------------
    # Lease / coordination helpers (DB 1 — L2 only)
    # ------------------------------------------------------------------

    def acquire_lease(
        self,
        key: str,
        holder_id: str,
        nonce: str,
        semantic_clock_tick: int,
        ttl_seconds: int = 30,
    ) -> bool:
        """Acquire an exclusive lease.  Returns ``True`` if acquired.

        Uses Redis SET NX (set-if-not-exists) for atomic acquisition.
        Falls back to in-process LRU when Redis is unavailable (single-
        process exclusivity only — cross-process coordination requires
        a live Redis).

        Parameters
        ----------
        key:
            Deterministic lease key (e.g. ``lease:{plan_hash}``).
        holder_id:
            Stable identifier of the process/agent claiming the lease.
        nonce:
            A value that is part of the deterministic run transcript
            (must NOT be random unless also stored in the transcript).
        semantic_clock_tick:
            Current semantic clock tick from ``SemanticClockSnapshot``.
        ttl_seconds:
            Lease TTL.  Coordination DB (DB 1) uses short TTLs.
        """
        self._validate_key(key)
        payload = canonical_json_bytes(
            {
                "holder_id": holder_id,
                "nonce": nonce,
                "semantic_clock_tick": semantic_clock_tick,
            }
        )

        conn = self._connect()
        if conn is not None:
            try:
                result = conn.set(key, payload, nx=True, ex=ttl_seconds)
                return bool(result)
            # guardian: allow-silent-swallow
            except Exception as exc:
                self._mark_failed(exc)

        # Fallback: in-process NX
        if self._fallback.exists(key):
            return False
        self._fallback.set(key, payload)
        return True

    def release_lease(self, key: str, holder_id: str, nonce: str) -> bool:
        """Release a lease only if the caller still holds it.

        Verifies ``holder_id`` and ``nonce`` before deletion to prevent
        accidental release by a competing process.
        """
        self._validate_key(key)
        raw = self.get(key)
        if raw is None:
            return False
        try:
            stored = json.loads(raw.decode("ascii"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return False
        if stored.get("holder_id") != holder_id or stored.get("nonce") != nonce:
            return False
        return self.delete(key)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def get_stats(self) -> dict[str, Any]:
        return {
            "db": int(self._db),
            "using_fallback": self._use_fallback,
            "fallback_entries": len(self._fallback),
            "hits": self.stats.hits,
            "misses": self.stats.misses,
            "fallback_hits": self.stats.fallback_hits,
            "fallback_misses": self.stats.fallback_misses,
            "errors": self.stats.errors,
            "bypassed_replay": self.stats.bypassed_replay,
        }


# ---------------------------------------------------------------------------
# Module-level singleton factories
# ---------------------------------------------------------------------------

_hot_cache: DeterministicRedisCache | None = None
_coordination_cache: DeterministicRedisCache | None = None


def get_hot_cache() -> DeterministicRedisCache:
    """Return the process-global DB-0 hot cache (L0/L1/L3/L5)."""
    global _hot_cache
    if _hot_cache is None:
        _hot_cache = DeterministicRedisCache(db=CacheDB.HOT)
    return _hot_cache


def get_coordination_cache() -> DeterministicRedisCache:
    """Return the process-global DB-1 coordination cache (L2 leases/idempotency)."""
    global _coordination_cache
    if _coordination_cache is None:
        _coordination_cache = DeterministicRedisCache(db=CacheDB.COORDINATION)
    return _coordination_cache


def reset_cache_singletons() -> None:
    """[TESTING ONLY] Reset module-level singletons."""
    global _hot_cache, _coordination_cache
    _hot_cache = None
    _coordination_cache = None
