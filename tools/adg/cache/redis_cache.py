"""Redis Cache — Optional read-through accelerator, non-authoritative."""

import logging
import time
from typing import Any

import redis

from tools.adg.core.models import ADGEdge, ADGNode

logger = logging.getLogger(__name__)

# Strict timeout budget for Redis (ms)
REDIS_TIMEOUT_MS = 75
# Backoff between reconnect attempts when Redis is down
_RECONNECT_BACKOFF_S: float = 30.0
# Mark Redis unavailable after this many consecutive query failures
_MAX_CONSECUTIVE_ERRORS: int = 5


class RedisCache:
    """Read-through cache with tight timeout budget."""

    _client: redis.Redis | None = None
    _available: bool = False
    _cache_version: str = "v1"  # Bump on schema changes

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self._redis_url = redis_url
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
        except Exception as e:  # guardian: allow-broad-exception -- Redis client raises diverse connection/auth/protocol errors; all suppressed to keep Redis optional
            logger.warning(f"Redis unavailable: {e}")
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
        self._consecutive_errors += 1
        if self._consecutive_errors >= _MAX_CONSECUTIVE_ERRORS:
            logger.warning(
                "Redis: %d consecutive errors — marking unavailable until reconnect",
                self._consecutive_errors,
            )
            self._available = False
            self._consecutive_errors = 0

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
        except Exception as e:  # guardian: allow-broad-exception -- Redis info() can fail with varied transport/server errors; degraded status is the safe response
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
            if data:
                return ADGNode(**data)
        except Exception as e:  # guardian: allow-broad-exception -- Redis client raises varied transport/timeout errors; all are non-fatal cache misses
            logger.debug(f"Redis get_node miss: {e}")
            self._record_error()

        return None

    def set_node(self, node: ADGNode, adg_snapshot_id: str) -> None:
        """Cache node in Redis."""
        if not self._available:
            return

        try:
            key = self._key(f"node:{node.id}", adg_snapshot_id)
            mapping = {k: str(v) for k, v in node.model_dump().items() if v is not None}
            self._client.hmset(key, mapping)
        except Exception as e:
            logger.debug(f"Redis set_node failed: {e}")

    def get_edge_fanout(self, src_id: str, relation_type: str, adg_snapshot_id: str) -> list[ADGEdge] | None:
        """Try Redis for edges. Returns None on cache miss, empty list if no edges exist."""
        if not self._available:
            self._maybe_reconnect()
        if not self._available:
            return None

        try:
            key = self._key(f"edge:{src_id}:{relation_type}", adg_snapshot_id)
            edge_ids = self._client.smembers(key)

            # Check if key exists (distinguish empty set from key not existing)
            if not self._client.exists(key):
                return None  # Cache miss - key doesn't exist

            # Key exists but may be empty (no edges for this relation)
            if not edge_ids:
                return []  # Cache hit, but no edges

            edges = []
            for eid in edge_ids:
                detail_key = self._key(f"edge_detail:{eid}", adg_snapshot_id)
                detail = self._client.hgetall(detail_key)
                if detail:
                    edges.append(ADGEdge(**detail))
            if len(edges) != len(edge_ids):
                return None  # partial: some edge_detail hashes missing — force SQLite fallback
            return edges
        except Exception as e:  # guardian: allow-broad-exception -- Redis client raises varied transport/timeout/serialization errors; all are non-fatal cache misses
            logger.debug(f"Redis get_edge_fanout miss: {e}")
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
            for edge in edges:
                detail_key = self._key(f"edge_detail:{edge.id}", adg_snapshot_id)
                mapping = {k: str(v) for k, v in edge.model_dump().items() if v is not None}
                self._client.hmset(detail_key, mapping)
                self._client.sadd(key, edge.id)
        except Exception as e:
            logger.debug(f"Redis set_edge_fanout failed: {e}")

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

            edge_ids = self._client.smembers(key)
            if not edge_ids:
                return []  # Cache hit, no incoming edges for this relation

            edges = []
            for eid in edge_ids:
                detail_key = self._key(f"edge_detail:{eid}", adg_snapshot_id)
                detail = self._client.hgetall(detail_key)
                if detail:
                    edges.append(ADGEdge(**detail))
            if len(edges) != len(edge_ids):
                return None  # partial: some edge_detail hashes missing — force SQLite fallback
            return edges
        except Exception as e:  # guardian: allow-broad-exception -- Redis client raises varied transport/timeout/serialization errors; all are non-fatal cache misses
            logger.debug(f"Redis get_edge_fanin miss: {e}")
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
            for edge in edges:
                detail_key = self._key(f"edge_detail:{edge.id}", adg_snapshot_id)
                mapping = {k: str(v) for k, v in edge.model_dump().items() if v is not None}
                self._client.hmset(detail_key, mapping)
                self._client.sadd(key, edge.id)
        except Exception as e:  # guardian: allow-broad-exception -- Redis write failure is non-fatal; cache backfill is best-effort, silent skip is intentional
            logger.debug(f"Redis set_edge_fanin failed: {e}")

    def get_nodes_by_file(self, file_path: str, adg_snapshot_id: str) -> list[ADGNode] | None:
        """Try Redis for file-path->nodes list. Returns None on cache miss."""
        if not self._available:
            self._maybe_reconnect()
        if not self._available:
            return None
        try:
            import hashlib, json

            path_hash = hashlib.sha1(file_path.encode()).hexdigest()[:16]
            key = self._key(f"file_nodes:{path_hash}", adg_snapshot_id)
            raw = self._client.get(key)
            if raw is None:
                return None
            return [ADGNode(**n) for n in json.loads(raw)]
        except Exception as e:  # guardian: allow-broad-exception -- Redis raises varied transport/deserialization errors; miss is non-fatal
            logger.debug(f"Redis get_nodes_by_file miss: {e}")
            self._record_error()
        return None

    def set_nodes_by_file(self, file_path: str, nodes: list[ADGNode], adg_snapshot_id: str) -> None:
        """Cache file-path->nodes list in Redis as JSON string."""
        if not self._available:
            return
        try:
            import hashlib, json

            path_hash = hashlib.sha1(file_path.encode()).hexdigest()[:16]
            key = self._key(f"file_nodes:{path_hash}", adg_snapshot_id)
            payload = [{k: str(v) for k, v in n.model_dump().items() if v is not None} for n in nodes]
            self._client.set(key, json.dumps(payload))
        except Exception as e:  # guardian: allow-broad-exception -- Redis write failure is non-fatal; backfill is best-effort
            logger.debug(f"Redis set_nodes_by_file failed: {e}")

    def get_nodes_by_layer(self, layer: str, adg_snapshot_id: str) -> list[ADGNode] | None:
        """Try Redis for layer->nodes list. Returns None on cache miss."""
        if not self._available:
            self._maybe_reconnect()
        if not self._available:
            return None
        try:
            import json

            key = self._key(f"layer_nodes:{layer}", adg_snapshot_id)
            raw = self._client.get(key)
            if raw is None:
                return None
            return [ADGNode(**n) for n in json.loads(raw)]
        except Exception as e:  # guardian: allow-broad-exception -- Redis raises varied transport/deserialization errors; miss is non-fatal
            logger.debug(f"Redis get_nodes_by_layer miss: {e}")
            self._record_error()
        return None

    def set_nodes_by_layer(self, layer: str, nodes: list[ADGNode], adg_snapshot_id: str) -> None:
        """Cache layer->nodes list in Redis as JSON string (key: layer_nodes:{layer})."""
        if not self._available:
            return
        try:
            import json

            key = self._key(f"layer_nodes:{layer}", adg_snapshot_id)
            payload = [{k: str(v) for k, v in n.model_dump().items() if v is not None} for n in nodes]
            self._client.set(key, json.dumps(payload))
        except Exception as e:  # guardian: allow-broad-exception -- Redis write failure is non-fatal; backfill is best-effort
            logger.debug(f"Redis set_nodes_by_layer failed: {e}")

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
        except Exception as e:  # guardian: allow-broad-exception -- Redis scan/delete raises varied errors; clear_snapshot is best-effort cleanup, never blocks caller
            logger.warning(f"Redis clear_snapshot failed: {e}")

    def close(self) -> None:
        """Close Redis connection."""
        if self._client:
            try:
                self._client.close()
                logger.info("Redis connection closed")
            except Exception as e:  # guardian: allow-log-and-swallow -- teardown/cleanup context -- swallow is conventional in resource-release paths
                logger.error(f"Error closing Redis connection: {e}")
            finally:
                self._client = None
                self._available = False
