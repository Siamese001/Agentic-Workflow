"""Redis Cache — Optional read-through accelerator, non-authoritative."""
import json
import logging
from typing import Any, Dict, List, Optional, Tuple

import redis

from tools.adg.core.models import ADGEdge, ADGNode

logger = logging.getLogger(__name__)

# Strict timeout budget for Redis (ms)
REDIS_TIMEOUT_MS = 75


class RedisCache:
    """Read-through cache with tight timeout budget."""

    _client: Optional[redis.Redis] = None
    _available: bool = False
    _cache_version: str = "v1"  # Bump on schema changes

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self._redis_url = redis_url
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
        except Exception as e:
            logger.warning(f"Redis unavailable: {e}")
            self._available = False
            self._client = None

    def health(self) -> Tuple[str, Dict[str, Any]]:
        """Return Redis health status."""
        if not self._available or not self._client:
            return "unavailable", {"reason": "not connected"}

        try:
            info = self._client.info()
            return "healthy", {
                "version": info.get("redis_version"),
                "used_memory_human": info.get("used_memory_human"),
            }
        except Exception as e:
            return "degraded", {"reason": str(e)}

    def _key(self, base: str, adg_snapshot_id: str) -> str:
        """Generate versioned cache key."""
        return f"adg:{self._cache_version}:{adg_snapshot_id}:{base}"

    def get_node(self, node_id: str, adg_snapshot_id: str) -> Optional[ADGNode]:
        """Try Redis first, return None on miss or timeout."""
        if not self._available:
            return None

        try:
            key = self._key(f"node:{node_id}", adg_snapshot_id)
            data = self._client.hgetall(key)
            if data:
                return ADGNode(**data)
        except Exception as e:
            logger.debug(f"Redis get_node miss: {e}")

        return None

    def set_node(self, node: ADGNode, adg_snapshot_id: str) -> None:
        """Cache node in Redis."""
        if not self._available:
            return

        try:
            key = self._key(f"node:{node.id}", adg_snapshot_id)
            self._client.hset(key, mapping=node.model_dump())
        except Exception as e:
            logger.debug(f"Redis set_node failed: {e}")

    def get_edge_fanout(self, src_id: str, relation_type: str,
                        adg_snapshot_id: str) -> Optional[List[ADGEdge]]:
        """Try Redis for edges."""
        if not self._available:
            return None

        try:
            key = self._key(f"edge:{src_id}:{relation_type}", adg_snapshot_id)
            edge_ids = self._client.smembers(key)
            if not edge_ids:
                return None

            edges = []
            for eid in edge_ids:
                detail_key = self._key(f"edge_detail:{eid}", adg_snapshot_id)
                detail = self._client.hgetall(detail_key)
                if detail:
                    edges.append(ADGEdge(**detail))
            return edges
        except Exception as e:
            logger.debug(f"Redis get_edge_fanout miss: {e}")

        return None

    def set_edge_fanout(self, src_id: str, relation_type: str,
                       edges: List[ADGEdge], adg_snapshot_id: str) -> None:
        """Cache edges in Redis."""
        if not self._available:
            return

        try:
            key = self._key(f"edge:{src_id}:{relation_type}", adg_snapshot_id)
            for edge in edges:
                detail_key = self._key(f"edge_detail:{edge.id}", adg_snapshot_id)
                self._client.hset(detail_key, mapping=edge.model_dump())
                self._client.sadd(key, edge.id)
        except Exception as e:
            logger.debug(f"Redis set_edge_fanout failed: {e}")

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
        except Exception as e:
            logger.warning(f"Redis clear_snapshot failed: {e}")
