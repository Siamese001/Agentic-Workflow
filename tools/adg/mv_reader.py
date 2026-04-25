"""ADG MV Reader — Read-through accessor for Redis-projected MVs and P-views.

Kept separate from `tools/adg/cache/redis_cache.py` so the canonical cache stays
focused on nodes/edges. This module is a pure reader: never mutates Redis,
always returns `None` on miss (caller falls back to SQLite).

SSOT: SQLite. Redis is optional acceleration.
"""

from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

CACHE_VERSION = "v1"
REDIS_TIMEOUT_MS = 75
REDIS_URL_DEFAULT = os.getenv("ADG_REDIS_URL", "redis://localhost:6379/0")


def _redis_key(snapshot_id: str, base: str) -> str:
    return f"adg:{CACHE_VERSION}:{snapshot_id}:{base}"


class MVRedisReader:
    """Thin read-only accessor over Redis MV/P-view projections.

    All methods fail-soft: return `None` on any Redis error. Callers are
    responsible for SQLite fallback.
    """

    def __init__(self, redis_url: str = REDIS_URL_DEFAULT, client: Any | None = None):
        self._redis_url = redis_url
        self._client: Any | None = client
        self._available = client is not None
        if client is None:
            self._attempt_connect()

    def _attempt_connect(self) -> None:
        try:
            import redis

            self._client = redis.from_url(
                self._redis_url,
                decode_responses=True,
                socket_connect_timeout=REDIS_TIMEOUT_MS / 1000,
                socket_timeout=REDIS_TIMEOUT_MS / 1000,
            )
            self._client.ping()
            self._available = True
        except (
            OSError,
            ValueError,
            TypeError,
            ImportError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- Redis client raises varied connection/auth/import errors; MVReader is optional accelerator
            logger.debug("MVRedisReader unavailable: %s", e)
            self._available = False
            self._client = None

    @property
    def available(self) -> bool:
        return self._available and self._client is not None

    def is_hot(self, snapshot_id: str) -> bool:
        """Return True if MV projection sentinel is set for this snapshot."""
        if not self.available:
            return False
        try:
            return bool(self._client.exists(_redis_key(snapshot_id, "_mv_hot")))
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- EXISTS failure is non-fatal; False is the safe default
            logger.debug("MVRedisReader.is_hot failed: %s", e)
            return False

    def get_mv_top(self, mv_name: str, snapshot_id: str, k: int = 20) -> list[tuple[str, float]] | None:
        """Return top-k `(member, score)` from a projected MV ZSET.

        Highest score first. Returns `None` on miss; empty list on known-empty ZSET.
        """
        if not self.available:
            return None
        try:
            key = _redis_key(snapshot_id, f"mv:{mv_name}")
            raw = self._client.zrevrange(key, 0, max(0, k - 1), withscores=True)
            if not raw:
                return []
            return [(str(m), float(s)) for m, s in raw]
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- ZREVRANGE failure is non-fatal; caller falls back to SQLite
            logger.debug("MVRedisReader.get_mv_top miss for %s: %s", mv_name, e)
            return None

    def get_mv_bottom(self, mv_name: str, snapshot_id: str, k: int = 20) -> list[tuple[str, float]] | None:
        """Return bottom-k (lowest score first) from a projected MV ZSET."""
        if not self.available:
            return None
        try:
            key = _redis_key(snapshot_id, f"mv:{mv_name}")
            raw = self._client.zrange(key, 0, max(0, k - 1), withscores=True)
            if not raw:
                return []
            return [(str(m), float(s)) for m, s in raw]
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- ZRANGE failure is non-fatal
            logger.debug("MVRedisReader.get_mv_bottom miss for %s: %s", mv_name, e)
            return None

    def get_mv_score(self, mv_name: str, member: str, snapshot_id: str) -> float | None:
        """Return the score for a specific member in a projected MV ZSET."""
        if not self.available:
            return None
        try:
            key = _redis_key(snapshot_id, f"mv:{mv_name}")
            raw = self._client.zscore(key, member)
            return float(raw) if raw is not None else None
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- ZSCORE failure is non-fatal
            logger.debug("MVRedisReader.get_mv_score miss for %s/%s: %s", mv_name, member, e)
            return None

    def mv_size(self, mv_name: str, snapshot_id: str) -> int | None:
        """Return cardinality of a projected MV ZSET."""
        if not self.available:
            return None
        try:
            key = _redis_key(snapshot_id, f"mv:{mv_name}")
            return int(self._client.zcard(key))
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- ZCARD failure is non-fatal
            logger.debug("MVRedisReader.mv_size miss for %s: %s", mv_name, e)
            return None

    def mv_meta(self, mv_name: str, snapshot_id: str) -> dict[str, str] | None:
        """Return the projection metadata hash (row_count, metric, projected_at)."""
        if not self.available:
            return None
        try:
            key = _redis_key(snapshot_id, f"mv:{mv_name}:meta")
            raw = self._client.hgetall(key)
            return {str(k): str(v) for k, v in raw.items()} if raw else {}
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- HGETALL failure is non-fatal
            logger.debug("MVRedisReader.mv_meta miss for %s: %s", mv_name, e)
            return None

    def get_pview_members(self, view_name: str, snapshot_id: str) -> set[str] | None:
        """Return the full member set of a projected P-view."""
        if not self.available:
            return None
        try:
            key = _redis_key(snapshot_id, f"pview:{view_name}")
            raw = self._client.smembers(key)
            return {str(m) for m in raw} if raw else set()
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- SMEMBERS failure is non-fatal
            logger.debug("MVRedisReader.get_pview_members miss for %s: %s", view_name, e)
            return None

    def pview_contains(self, view_name: str, member: str, snapshot_id: str) -> bool | None:
        """O(1) membership test. True/False on hit, None on miss (caller falls back)."""
        if not self.available:
            return None
        try:
            key = _redis_key(snapshot_id, f"pview:{view_name}")
            return bool(self._client.sismember(key, member))
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- SISMEMBER failure is non-fatal
            logger.debug("MVRedisReader.pview_contains miss for %s/%s: %s", view_name, member, e)
            return None

    def pview_size(self, view_name: str, snapshot_id: str) -> int | None:
        """Return cardinality of a projected P-view SET."""
        if not self.available:
            return None
        try:
            key = _redis_key(snapshot_id, f"pview:{view_name}")
            return int(self._client.scard(key))
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- SCARD failure is non-fatal
            logger.debug("MVRedisReader.pview_size miss for %s: %s", view_name, e)
            return None

    def list_projected_pviews(self, snapshot_id: str) -> list[str] | None:
        """Return names of all P-views currently projected for this snapshot."""
        if not self.available:
            return None
        try:
            pattern = _redis_key(snapshot_id, "pview:*")
            names: list[str] = []
            cursor = 0
            prefix = _redis_key(snapshot_id, "pview:")
            while True:
                cursor, keys = self._client.scan(cursor=cursor, match=pattern, count=100)
                for k in keys:
                    tail = k[len(prefix) :]
                    if tail and not tail.endswith(":meta"):
                        names.append(tail)
                if cursor == 0:
                    break
            return sorted(set(names))
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- SCAN failure is non-fatal
            logger.debug("MVRedisReader.list_projected_pviews failed: %s", e)
            return None

    def list_projected_mvs(self, snapshot_id: str) -> list[str] | None:
        """Return names of all MVs currently projected in Redis for this snapshot."""
        if not self.available:
            return None
        try:
            pattern = _redis_key(snapshot_id, "mv:*")
            names: list[str] = []
            cursor = 0
            prefix = _redis_key(snapshot_id, "mv:")
            while True:
                cursor, keys = self._client.scan(cursor=cursor, match=pattern, count=100)
                for k in keys:
                    tail = k[len(prefix) :]
                    # Skip :meta sidecars
                    if tail and not tail.endswith(":meta"):
                        names.append(tail)
                if cursor == 0:
                    break
            return sorted(set(names))
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- SCAN failure is non-fatal
            logger.debug("MVRedisReader.list_projected_mvs failed: %s", e)
            return None
