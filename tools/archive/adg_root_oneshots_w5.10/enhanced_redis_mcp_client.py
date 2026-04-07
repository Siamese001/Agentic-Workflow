"""
DEPRECATED — do not use in new code.

Use ADGRedisClient from tools/adg/adg_redis_query.py instead.
That client is the canonical, fail-closed ADG Redis interface and is
integrated with ADGQuerySession for freshness enforcement.

Enhanced Redis MCP Client with HASH and SET support for ADG queries.

This client extends the basic Redis MCP functionality to support:
- HASH operations (hget, hgetall, hkeys, hvals)
- SET operations (smembers, scard)
- ADG-specific query helpers

Fail-closed: ALL methods raise RuntimeError when Redis is unavailable.
NO silent fallbacks. NO returning None on Redis failure.
If Redis is not hot, run: python tools/adg/adg_redis_ingest.py --force
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class EnhancedRedisMCPClient:
    """Enhanced Redis client for ADG cache queries.

    Provides HASH and SET operations needed for ADG cache queries.
    Fail-closed: raises RuntimeError if Redis is unavailable or ADG is not loaded.
    """

    def __init__(self) -> None:
        self._client: Any = None

    def _get_client(self) -> Any:
        """Return a connected Redis client, raising RuntimeError if unavailable."""
        if self._client is None:
            import redis

            try:
                self._client = redis.Redis(
                    host="localhost",
                    port=6379,
                    db=0,
                    decode_responses=True,
                )
                self._client.ping()
                if not self._client.exists("adg:meta"):
                    raise RuntimeError(
                        "ADG Redis cache is not loaded. Run: python tools/adg/adg_redis_ingest.py --force",
                    )
                logger.debug("Redis client connected and ADG cache is hot")
            except redis.RedisError as exc:
                raise RuntimeError(
                    f"Redis unavailable — ADG cache cannot be queried: {exc}. "
                    "Run: python tools/adg/adg_redis_ingest.py --force",
                ) from exc
        return self._client

    def get_string(self, key: str) -> str | None:
        """Get a STRING value from Redis."""
        return self._get_client().get(key)

    def get_hash(self, key: str) -> dict[str, str]:
        """Get a HASH value from Redis. Raises RuntimeError if Redis is unavailable."""
        result = self._get_client().hgetall(key)
        logger.debug(f"Redis HASH get: {key} -> {len(result)} fields")
        return result

    def get_set(self, key: str) -> list[str]:
        """Get a SET value from Redis. Raises RuntimeError if Redis is unavailable."""
        result = list(self._get_client().smembers(key))
        logger.debug(f"Redis SET get: {key} -> {len(result)} members")
        return result

    def get_adg_meta(self) -> dict[str, str] | None:
        """Get ADG metadata hash."""
        return self.get_hash("adg:meta")

    def get_adg_snapshot(self) -> dict[str, Any] | None:
        """Get ADG snapshot (STRING type - works with MCP)."""
        snapshot_str = self.get_string("adg:snapshot")
        if snapshot_str:
            try:
                return json.loads(snapshot_str)
            except json.JSONDecodeError as exc:
                logger.warning(f"Failed to parse ADG snapshot JSON: {exc}")
        return None

    def get_adg_nodes_by_layer(self, layer: str) -> list[str] | None:
        """Get node IDs for a specific layer."""
        return self.get_set(f"adg:nodes:by_layer:{layer}")

    def get_adg_nodes_by_file(self, file_path: str) -> list[str] | None:
        """Get node IDs for a specific file path."""
        return self.get_set(f"adg:nodes:by_file:{file_path}")

    def get_adg_edge_fan_out(self, node_id: str, relation_type: str) -> list[str] | None:
        """Get fan-out edges from a node."""
        return self.get_set(f"adg:edge:{node_id}:{relation_type}")

    def get_adg_edge_fan_in(self, node_id: str, relation_type: str) -> list[str] | None:
        """Get fan-in edges to a node."""
        return self.get_set(f"adg:edge:in:{node_id}:{relation_type}")

    def get_adg_violations(self) -> list[dict[str, Any]]:
        """Get ADG violations list. Raises RuntimeError if Redis is unavailable."""
        violations = self._get_client().lrange("adg:violations", 0, -1)
        return [json.loads(v) for v in violations if v]

    def get_adg_drift_score(self) -> str | None:
        """Get drift score composite."""
        return self.get_string("adg:drift:score")

    def get_adg_drift_subscores(self) -> dict[str, str] | None:
        """Get drift score subscores."""
        return self.get_hash("adg:drift:subscores")

    def get_adg_drift_uncovered(self) -> list[str]:
        """Get uncovered production modules. Raises RuntimeError if Redis is unavailable."""
        return self._get_client().lrange("adg:drift:uncovered", 0, -1)

    def get_adg_drift_orphan_tests(self) -> list[str]:
        """Get orphan/dead test modules. Raises RuntimeError if Redis is unavailable."""
        return self._get_client().lrange("adg:drift:orphan_tests", 0, -1)

    def get_adg_layer_stats(self) -> dict[str, Any]:
        """Get comprehensive ADG layer statistics. Raises RuntimeError if Redis is unavailable."""
        stats: dict[str, Any] = {}
        snapshot = self.get_adg_snapshot()
        if snapshot and "by_layer" in snapshot:
            stats.update(snapshot["by_layer"])
        meta = self.get_adg_meta()
        stats["total_nodes"] = int(meta.get("node_count", 0))
        stats["total_edges"] = int(meta.get("edge_count", 0))
        stats["timestamp"] = meta.get("timestamp", "unknown")
        return stats

    def check_adg_cache_health(self) -> dict[str, Any]:
        """Check ADG cache health. Raises RuntimeError if Redis is unavailable."""
        import time

        client = self._get_client()
        adg_keys = client.keys("adg:*")
        meta = self.get_adg_meta()
        health: dict[str, Any] = {
            "redis_available": True,
            "adg_keys_count": len(adg_keys),
            "adg_meta_available": bool(meta),
            "adg_snapshot_available": client.exists("adg:snapshot") > 0,
            "cache_freshness_hours": None,
        }
        if meta and "ingested_at" in meta:
            try:
                health["cache_freshness_hours"] = (time.time() - float(meta["ingested_at"])) / 3600
            except (ValueError, TypeError):
                pass
        return health

    def query_adg(self, query_type: str, **kwargs) -> Any:
        """Execute an ADG query by type. Raises RuntimeError if Redis is unavailable
        or query_type is unknown.

        Args:
            query_type: One of 'meta', 'snapshot', 'layer_nodes', 'file_nodes',
                        'fan_out', 'fan_in', 'violations', 'drift_score',
                        'drift_subscores', 'drift_uncovered', 'drift_orphan_tests',
                        'layer_stats'.
            **kwargs: Query-specific parameters (layer, file_path, node_id, relation_type).
        """
        query_map = {
            "meta": self.get_adg_meta,
            "snapshot": self.get_adg_snapshot,
            "layer_nodes": lambda: self.get_adg_nodes_by_layer(kwargs["layer"]),
            "file_nodes": lambda: self.get_adg_nodes_by_file(kwargs["file_path"]),
            "fan_out": lambda: self.get_adg_edge_fan_out(kwargs["node_id"], kwargs["relation_type"]),
            "fan_in": lambda: self.get_adg_edge_fan_in(kwargs["node_id"], kwargs["relation_type"]),
            "violations": self.get_adg_violations,
            "drift_score": self.get_adg_drift_score,
            "drift_subscores": self.get_adg_drift_subscores,
            "drift_uncovered": self.get_adg_drift_uncovered,
            "drift_orphan_tests": self.get_adg_drift_orphan_tests,
            "layer_stats": self.get_adg_layer_stats,
        }
        if query_type not in query_map:
            raise RuntimeError(f"Unknown ADG query type: '{query_type}'. Valid types: {sorted(query_map)}")
        return query_map[query_type]()


# Singleton instance for easy access
_enhanced_client: EnhancedRedisMCPClient | None = None


def get_enhanced_redis_client() -> EnhancedRedisMCPClient:
    """Get the singleton enhanced Redis MCP client."""
    global _enhanced_client
    if _enhanced_client is None:
        _enhanced_client = EnhancedRedisMCPClient()
    return _enhanced_client


def reset_enhanced_client() -> None:
    """Reset the singleton client (for testing)."""
    global _enhanced_client
    _enhanced_client = None


if __name__ == "__main__":
    # Demo usage
    client = get_enhanced_redis_client()

    print("=== ADG Cache Health ===")
    health = client.check_adg_cache_health()
    for key, value in health.items():
        print(f"{key}: {value}")

    print("\n=== ADG Metadata ===")
    meta = client.get_adg_meta()
    if meta:
        print(f"Timestamp: {meta.get('timestamp')}")
        print(f"Node count: {meta.get('node_count')}")
        print(f"Edge count: {meta.get('edge_count')}")

    print("\n=== Layer Stats ===")
    stats = client.get_adg_layer_stats()
    for layer, count in stats.items():
        if isinstance(count, int):
            print(f"{layer}: {count}")

    print("\n=== Sample Query: L0 Nodes ===")
    l0_nodes = client.get_adg_nodes_by_layer("L0")
    if l0_nodes:
        print(f"L0 has {len(l0_nodes)} nodes")
        print(f"Sample: {l0_nodes[:3]}")
