"""Redis Cache — Optional read-through accelerator, non-authoritative."""

import hashlib
import json
import logging
import time
from typing import Any

import redis

from tools.adg.core.models import ADGEdge, ADGNode
from tools.adg.shared_modules.config import resolve_adg_redis_url

logger = logging.getLogger(__name__)

# Strict timeout budget for Redis (ms)
REDIS_TIMEOUT_MS = 75
# Backoff between reconnect attempts when Redis is down
_RECONNECT_BACKOFF_S: float = 30.0
# Mark Redis unavailable after this many consecutive query failures
_MAX_CONSECUTIVE_ERRORS: int = 5
_EMPTY_SET_SENTINEL = "__empty__"
_HASH_JSON_PREFIX = "__json__:"


class RedisCache:
    """Read-through cache with tight timeout budget."""

    _client: redis.Redis | None = None
    _available: bool = False
    _cache_version: str = "v1"  # Bump on schema changes

    def __init__(self, redis_url: str | None = None):
        """Initialize RedisCache with explicit URL or ADG_REDIS_URL env var.

        SSOT: No localhost default per S-03. Must provide redis_url or set
        ADG_REDIS_URL environment variable.
        """
        # SSOT: ADG_REDIS_URL from env var or explicit parameter; no default
        resolved_url = resolve_adg_redis_url(redis_url)
        if not resolved_url:
            raise RuntimeError(
                "RedisCache requires redis_url parameter or ADG_REDIS_URL env var. "
                "No localhost default per ADG config SSOT (S-03)."
            )
        self._redis_url = resolved_url
        self._last_reconnect_attempt: float = 0.0
        self._consecutive_errors: int = 0
        self._attempt_connect()

    def _attempt_connect(self) -> None:
        """Try to connect to Redis, but never fail on error."""
        try:
            self._client = redis.from_url(
                self._redis_url,
                decode_responses=True,
                socket_connect_timeout=REDIS_TIMEOUT_MS / 1000,
                socket_timeout=REDIS_TIMEOUT_MS / 1000,
            )
            self._client.ping()
            self._available = True
            logger.info("Redis cache available")
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- Redis client raises diverse connection/auth/protocol errors; all suppressed to keep Redis optional
            logger.warning("Redis unavailable: %s", e)
            self._available = False
            self._client = None

    def _maybe_reconnect(self) -> None:
        """Re-probe Redis if down and backoff window has elapsed.

        Called lazily from read methods when _available is False.
        Bounded to one attempt per _RECONNECT_BACKOFF_S seconds.
        """
        now = time.monotonic()
        if now - self._last_reconnect_attempt < _RECONNECT_BACKOFF_S:
            return
        self._last_reconnect_attempt = now
        previously_available = self._available
        self._attempt_connect()
        if self._available and not previously_available:
            logger.info("Redis reconnected after recovery")
            self._consecutive_errors = 0

    def _record_error(self) -> None:
        """Track consecutive Redis query failures.

        After _MAX_CONSECUTIVE_ERRORS failures, marks Redis unavailable so
        subsequent reads skip the 75ms timeout until _maybe_reconnect() fires.
        """
        if not hasattr(self, "_consecutive_errors"):
            self._consecutive_errors = 0
        self._consecutive_errors += 1
        if self._consecutive_errors >= _MAX_CONSECUTIVE_ERRORS:
            logger.warning(
                "Redis: %d consecutive errors — marking unavailable until reconnect",
                self._consecutive_errors,
            )
            self._available = False
            self._consecutive_errors = 0

    def _record_success(self) -> None:
        """Reset consecutive error budget after a successful Redis operation."""
        if not hasattr(self, "_consecutive_errors"):
            self._consecutive_errors = 0
        if self._consecutive_errors:
            self._consecutive_errors = 0

    @staticmethod
    def _strip_empty_sentinel(values: set[str]) -> set[str]:
        """Remove the empty-set sentinel from a Redis set payload."""
        return {value for value in values if value != _EMPTY_SET_SENTINEL}

    @staticmethod
    def _hset_mapping(target: Any, key: str, mapping: dict[str, Any]) -> None:
        """Write a hash mapping using Redis-3-compatible single-field HSETs."""
        for field, value in mapping.items():
            target.hset(key, field, f"{_HASH_JSON_PREFIX}{json.dumps(value)}")

    @staticmethod
    def _decode_hash_mapping(raw: dict[str, Any]) -> dict[str, Any]:
        """Decode JSON hash values while tolerating legacy plain-string cache entries."""
        decoded: dict[str, Any] = {}
        for field, value in raw.items():
            if isinstance(value, str) and value.startswith(_HASH_JSON_PREFIX):
                try:
                    decoded[field] = json.loads(value[len(_HASH_JSON_PREFIX) :])
                    continue
                except ValueError:
                    pass
            decoded[field] = value
        return decoded

    def health(self) -> tuple[str, dict[str, Any]]:
        """Return Redis health status."""
        if not self._available or not self._client:
            return "unavailable", {"reason": "not connected"}

        try:
            info = self._client.info()
            return "healthy", {
                "version": info.get("redis_version"),
                "used_memory_human": info.get("used_memory_human"),
            }
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- Redis info() can fail with varied transport/server errors; degraded status is the safe response
            return "degraded", {"reason": str(e)}

    def _key(self, base: str, adg_snapshot_id: str) -> str:
        """Generate versioned cache key."""
        return f"adg:{self._cache_version}:{adg_snapshot_id}:{base}"

    def get_node(self, node_id: str, adg_snapshot_id: str) -> ADGNode | None:
        """Try Redis first, return None on miss or timeout."""
        if not self._available:
            self._maybe_reconnect()
        if not self._available:
            return None

        try:
            key = self._key(f"node:{node_id}", adg_snapshot_id)
            data = self._client.hgetall(key)
            self._record_success()
            if data:
                return ADGNode(**self._decode_hash_mapping(data))
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- Redis client raises varied transport/timeout errors; all are non-fatal cache misses
            logger.debug("Redis get_node miss: %s", e)
            self._record_error()

        return None

    def set_node(self, node: ADGNode, adg_snapshot_id: str) -> None:
        """Cache node in Redis."""
        if not self._available:
            return

        try:
            key = self._key(f"node:{node.id}", adg_snapshot_id)
            mapping = node.model_dump()
            self._hset_mapping(self._client, key, mapping)
            self._record_success()
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- Redis write failure is non-fatal; cache backfill is best-effort
            logger.debug("Redis set_node failed: %s", e)
            self._record_error()

    def get_edge_fanout(self, src_id: str, relation_type: str, adg_snapshot_id: str) -> list[ADGEdge] | None:
        """Try Redis for edges. Returns None on cache miss, empty list if no edges exist."""
        if not self._available:
            self._maybe_reconnect()
        if not self._available:
            return None

        try:
            key = self._key(f"edge:{src_id}:{relation_type}", adg_snapshot_id)
            if not self._client.exists(key):
                return None  # Cache miss - key doesn't exist

            edge_ids = self._strip_empty_sentinel(self._client.smembers(key))
            self._record_success()
            if not edge_ids:
                return []  # Cache hit, but no edges

            edges = []
            for eid in edge_ids:
                detail_key = self._key(f"edge_detail:{eid}", adg_snapshot_id)
                detail = self._client.hgetall(detail_key)
                if detail:
                    edges.append(ADGEdge(**self._decode_hash_mapping(detail)))
            if len(edges) != len(edge_ids):
                return None  # partial: some edge_detail hashes missing — force SQLite fallback
            return edges
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- Redis client raises varied transport/timeout/serialization errors; all are non-fatal cache misses
            logger.debug("Redis get_edge_fanout miss: %s", e)
            self._record_error()

        return None

    def set_edge_fanout(
        self, src_id: str, relation_type: str, edges: list[ADGEdge], adg_snapshot_id: str
    ) -> None:
        """Cache edges in Redis."""
        if not self._available:
            return

        try:
            key = self._key(f"edge:{src_id}:{relation_type}", adg_snapshot_id)
            with self._client.pipeline(transaction=False) as pipe:
                pipe.delete(key)
                if not edges:
                    pipe.sadd(key, _EMPTY_SET_SENTINEL)
                for edge in edges:
                    detail_key = self._key(f"edge_detail:{edge.id}", adg_snapshot_id)
                    mapping = edge.model_dump()
                    self._hset_mapping(pipe, detail_key, mapping)
                    pipe.sadd(key, edge.id)
                pipe.execute()
            self._record_success()
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- Redis write failure is non-fatal; cache backfill is best-effort
            logger.debug("Redis set_edge_fanout failed: %s", e)
            self._record_error()

    def get_edge_fanin(self, tgt_id: str, relation_type: str, adg_snapshot_id: str) -> list[ADGEdge] | None:
        """Try Redis for fanin edges. Returns None on cache miss, list on hit (may be empty)."""
        if not self._available:
            self._maybe_reconnect()
        if not self._available:
            return None

        try:
            key = self._key(f"fanin:{tgt_id}:{relation_type}", adg_snapshot_id)

            if not self._client.exists(key):
                return None  # Cache miss -- key not present

            edge_ids = self._strip_empty_sentinel(self._client.smembers(key))
            self._record_success()
            if not edge_ids:
                return []  # Cache hit, no incoming edges for this relation

            edges = []
            for eid in edge_ids:
                detail_key = self._key(f"edge_detail:{eid}", adg_snapshot_id)
                detail = self._client.hgetall(detail_key)
                if detail:
                    edges.append(ADGEdge(**self._decode_hash_mapping(detail)))
            if len(edges) != len(edge_ids):
                return None  # partial: some edge_detail hashes missing — force SQLite fallback
            return edges
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- Redis client raises varied transport/timeout/serialization errors; all are non-fatal cache misses
            logger.debug("Redis get_edge_fanin miss: %s", e)
            self._record_error()

        return None

    def set_edge_fanin(
        self, tgt_id: str, relation_type: str, edges: list[ADGEdge], adg_snapshot_id: str
    ) -> None:
        """Cache fanin edges in Redis (lazy backfill -- key pattern: fanin:<tgt_id>:<rel>)."""
        if not self._available:
            return

        try:
            key = self._key(f"fanin:{tgt_id}:{relation_type}", adg_snapshot_id)
            with self._client.pipeline(transaction=False) as pipe:
                pipe.delete(key)
                if not edges:
                    pipe.sadd(key, _EMPTY_SET_SENTINEL)
                for edge in edges:
                    detail_key = self._key(f"edge_detail:{edge.id}", adg_snapshot_id)
                    mapping = edge.model_dump()
                    self._hset_mapping(pipe, detail_key, mapping)
                    pipe.sadd(key, edge.id)
                pipe.execute()
            self._record_success()
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- Redis write failure is non-fatal; cache backfill is best-effort
            logger.debug("Redis set_edge_fanin failed: %s", e)
            self._record_error()

    def get_nodes_by_file(self, file_path: str, adg_snapshot_id: str) -> list[ADGNode] | None:
        """Try Redis for file-path->nodes list. Returns None on cache miss."""
        if not self._available:
            self._maybe_reconnect()
        if not self._available:
            return None
        try:
            path_hash = hashlib.sha1(file_path.encode("utf-8")).hexdigest()[:16]
            key = self._key(f"file_nodes:{path_hash}", adg_snapshot_id)
            raw = self._client.get(key)
            if raw is None:
                return None
            self._record_success()
            return [ADGNode(**n) for n in json.loads(raw)]
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- Redis raises varied transport/deserialization errors; miss is non-fatal
            logger.debug("Redis get_nodes_by_file miss: %s", e)
            self._record_error()
        return None

    def set_nodes_by_file(self, file_path: str, nodes: list[ADGNode], adg_snapshot_id: str) -> None:
        """Cache file-path->nodes list in Redis as JSON string."""
        if not self._available:
            return
        try:
            path_hash = hashlib.sha1(file_path.encode("utf-8")).hexdigest()[:16]
            key = self._key(f"file_nodes:{path_hash}", adg_snapshot_id)
            payload = [{k: str(v) for k, v in n.model_dump().items() if v is not None} for n in nodes]
            self._client.set(key, json.dumps(payload))
            self._record_success()
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- Redis write failure is non-fatal; backfill is best-effort
            logger.debug("Redis set_nodes_by_file failed: %s", e)
            self._record_error()

    def get_nodes_by_layer(self, layer: str, adg_snapshot_id: str) -> list[ADGNode] | None:
        """Try Redis for layer->nodes list. Returns None on cache miss."""
        if not self._available:
            self._maybe_reconnect()
        if not self._available:
            return None
        try:
            key = self._key(f"layer_nodes:{layer}", adg_snapshot_id)
            raw = self._client.get(key)
            if raw is None:
                return None
            self._record_success()
            return [ADGNode(**n) for n in json.loads(raw)]
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- Redis raises varied transport/deserialization errors; miss is non-fatal
            logger.debug("Redis get_nodes_by_layer miss: %s", e)
            self._record_error()
        return None

    def set_nodes_by_layer(self, layer: str, nodes: list[ADGNode], adg_snapshot_id: str) -> None:
        """Cache layer->nodes list in Redis as JSON string (key: layer_nodes:{layer})."""
        if not self._available:
            return
        try:
            key = self._key(f"layer_nodes:{layer}", adg_snapshot_id)
            payload = [{k: str(v) for k, v in n.model_dump().items() if v is not None} for n in nodes]
            self._client.set(key, json.dumps(payload))
            self._record_success()
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- Redis write failure is non-fatal; backfill is best-effort
            logger.debug("Redis set_nodes_by_layer failed: %s", e)
            self._record_error()

    def clear_snapshot(self, adg_snapshot_id: str) -> None:
        """Clear all cache entries for a snapshot."""
        if not self._available:
            return

        try:
            pattern = self._key("*", adg_snapshot_id)
            cursor = 0
            while True:
                cursor, keys = self._client.scan(cursor=cursor, match=pattern, count=100)
                if keys:
                    self._client.delete(*keys)
                if cursor == 0:
                    break
            self._record_success()
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            RuntimeError,
        ) as e:  # guardian: allow-broad-exception -- Redis scan/delete raises varied errors; clear_snapshot is best-effort cleanup, never blocks caller
            logger.warning("Redis clear_snapshot failed: %s", e)
            self._record_error()

    def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            try:
                self._client.close()
                logger.info("Redis connection closed")
            except (
                OSError,
                ValueError,
                TypeError,
                KeyError,
                AttributeError,
                RuntimeError,
            ) as e:  # guardian: allow-log-and-swallow -- teardown/cleanup context -- swallow is conventional in resource-release paths
                logger.error("Error closing Redis connection: %s", e)
            finally:
                self._client = None
                self._available = False
