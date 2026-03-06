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
_MAX_TTL_SECONDS: int = 86400  # 24 hours hard cap
_REDIS_SOCKET_TIMEOUT_S: float = 0.3  # socket timeout for all Redis connections; fail-fast to prevent hangs


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

    Raises
    ------
    TypeError
        If obj contains non-JSON-serializable types (bytes, set, custom classes).
    ValueError
        If obj contains NaN or Infinity floats.
    """
    try:
        return json.dumps(
            obj,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    except TypeError as exc:
        raise TypeError(
            f"Object contains non-JSON-serializable type: {exc}. "
            "Only dict, list, str, int, float, bool, None are allowed."
        ) from exc
    except ValueError as exc:
        raise ValueError(f"Object contains NaN or Infinity: {exc}") from exc


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

    @staticmethod
    def _tcp_reachable(host: str, port: int) -> bool:
        """Fast TCP pre-check bounded by _REDIS_SOCKET_TIMEOUT_S.

        redis-py's socket_connect_timeout is bypassed by the OS TCP stack on
        Windows when no listener is present (no RST, so the kernel timer governs
        instead).  A raw socket.create_connection() honours the Python timeout
        correctly and fails fast.
        """
        import socket as _socket  # noqa: PLC0415

        try:
            with _socket.create_connection((host, port), timeout=_REDIS_SOCKET_TIMEOUT_S):
                return True
        except OSError:
            return False

    def _connect(self) -> Any:
        """Return a live redis.Redis connection, falling back gracefully."""
        if self._use_fallback:
            return None
        if self._conn is not None:
            return self._conn
        try:
            import redis as _redis  # noqa: PLC0415

            parsed = urllib.parse.urlparse(self._redis_url)
            host = parsed.hostname or "localhost"
            port = int(parsed.port or 6379)

            # Raw socket pre-check: fail fast before redis-py even attempts the
            # handshake.  On Windows, the OS TCP timeout ignores redis-py's
            # socket_connect_timeout for closed ports, causing multi-second hangs.
            if not self._tcp_reachable(host, port):
                raise OSError(
                    f"TCP pre-check failed: {host}:{port} unreachable within {_REDIS_SOCKET_TIMEOUT_S}s"
                )

            params: dict[str, Any] = {
                "host": host,
                "port": port,
                "db": int(self._db),
                "decode_responses": False,  # we handle bytes ourselves
                "socket_timeout": _REDIS_SOCKET_TIMEOUT_S,
                "socket_connect_timeout": _REDIS_SOCKET_TIMEOUT_S,
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
        if any(c in key for c in ("\x00", "\n", "\r", "\t")):
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
            If the value exceeds the 10 MB safety cap, or TTL is invalid.
        """
        self._validate_key(key)
        if not isinstance(value, bytes):
            raise TypeError(f"Cache value must be bytes, got {type(value).__name__}")
        if len(value) > _MAX_VALUE_BYTES:
            raise ValueError(f"Cache value too large ({len(value)} bytes > {_MAX_VALUE_BYTES})")
        if ttl_seconds <= 0:
            raise ValueError(f"TTL must be positive, got {ttl_seconds}")
        if ttl_seconds > _MAX_TTL_SECONDS:
            raise ValueError(f"TTL exceeds {_MAX_TTL_SECONDS}s limit, got {ttl_seconds}")

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
        fallback_deleted = self._fallback.delete(key)
        return deleted or fallback_deleted

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
        """Retrieve and deserialise a JSON value; returns ``None`` on miss or corrupt bytes."""
        raw = self.get(key, replay_mode=replay_mode)
        if raw is None:
            return None
        try:
            return json.loads(raw.decode("ascii"))
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            return None

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

        Raises
        ------
        ValueError
            If holder_id, nonce are empty, semantic_clock_tick < 0, or TTL invalid.
        """
        self._validate_key(key)
        if not holder_id:
            raise ValueError("holder_id must be non-empty")
        if not nonce:
            raise ValueError("nonce must be non-empty")
        if semantic_clock_tick < 0:
            raise ValueError(f"semantic_clock_tick must be >= 0, got {semantic_clock_tick}")
        if ttl_seconds <= 0:
            raise ValueError(f"Lease TTL must be positive, got {ttl_seconds}")
        if ttl_seconds > _MAX_TTL_SECONDS:
            raise ValueError(f"Lease TTL exceeds {_MAX_TTL_SECONDS}s limit, got {ttl_seconds}")
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

        Raises
        ------
        ValueError
            If holder_id or nonce are empty.
        """
        self._validate_key(key)
        if not holder_id:
            raise ValueError("holder_id must be non-empty")
        if not nonce:
            raise ValueError("nonce must be non-empty")
        raw = self.get(key)
        if raw is None:
            return False
        try:
            stored = json.loads(raw.decode("ascii"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return False
        if not isinstance(stored, dict):
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


# ---------------------------------------------------------------------------
# Redis health-check helper (F4 — infrastructure verification)
# ---------------------------------------------------------------------------


def check_redis_health(redis_url: str | None = None) -> dict[str, object]:
    """Probe Redis availability and return a structured health report.

    Does NOT raise on failure — returns a dict with ``"healthy": False`` so
    callers can decide how to react.  Emits a clear actionable log message
    when Redis is unreachable, including the WSL2 start command.

    Args:
        redis_url: Override URL (default: ``REDIS_URL`` env var or
            ``redis://localhost:6379``).

    Returns:
        ``dict`` with keys:
            - ``"healthy"`` (bool): True when Redis responded to PING.
            - ``"url"`` (str): The URL that was probed.
            - ``"using_fallback"`` (bool): True when the singleton is on LRU.
            - ``"error"`` (str | None): Error message when not healthy.
            - ``"fix"`` (str | None): Actionable remediation hint.
    """
    url = redis_url or os.environ.get("REDIS_URL", "redis://localhost:6379")
    result: dict[str, object] = {
        "healthy": False,
        "url": url,
        "using_fallback": True,
        "error": None,
        "fix": None,
    }
    try:
        import redis as _redis  # noqa: PLC0415

        parsed = urllib.parse.urlparse(url)
        conn = _redis.Redis(
            host=parsed.hostname or "localhost",
            port=int(parsed.port or 6379),
            db=0,
            socket_timeout=_REDIS_SOCKET_TIMEOUT_S,
            socket_connect_timeout=_REDIS_SOCKET_TIMEOUT_S,
        )
        conn.ping()
        info = conn.info("memory")
        result["healthy"] = True
        result["using_fallback"] = False
        result["used_memory_human"] = info.get("used_memory_human", "unknown")
        result["maxmemory_human"] = info.get("maxmemory_human", "0B")
        logger.info("Redis health OK: url=%s mem=%s", url, result["used_memory_human"])
    except ImportError:
        result["error"] = "redis package not installed"
        result["fix"] = "pip install redis"
        logger.error("Redis health FAIL: redis package not installed. Fix: pip install redis")
    except Exception as exc:  # guardian: allow-silent_swallower
        result["error"] = str(exc)
        result["fix"] = (
            "Start Redis before launching the agent stack.\n"
            "  WSL2:    sudo apt install redis-server && redis-server --daemonize yes\n"
            "  Windows: winget install Redis.Redis\n"
            "  Docker:  docker run -d -p 6379:6379 redis:7-alpine\n"
            "  Env var: set REDIS_URL=redis://localhost:6379"
        )
        logger.error(
            "Redis health FAIL: url=%s error=%s\n%s",
            url,
            exc,
            result["fix"],
        )
    return result
