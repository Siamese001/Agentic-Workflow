"""
ADG Redis query helper.

Provides fast, session-persistent lookups against the ADG Redis cache.
All methods return Python dicts/lists. Call adg_redis_query.ping() first
to verify the cache is loaded.

Usage:
    from tools.adg.adg_redis_query import ADGRedisClient
    adg = ADGRedisClient()
    adg.ping()
    meta = adg.meta()
    node = adg.get_node("ADG::Module::apps_shared/types/sovereign_severity_types.py")
    imports = adg.fan_out(node_id, "imports")
    imported_by = adg.fan_in(node_id, "imports")
    violations = adg.violations()
    snap = adg.snapshot()
"""

import json
from typing import Any

import redis


class ADGRedisClient:
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self._r = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def ping(self) -> bool:
        """Verify Redis is up and ADG cache is loaded."""
        self._r.ping()
        loaded = self._r.exists("adg:meta")
        if not loaded:
            raise RuntimeError("ADG Redis cache is not loaded. Run: python tools/adg/adg_redis_ingest.py")
        return True

    def meta(self) -> dict[str, str]:
        """Return ingest metadata (timestamp, counts, digest)."""
        return self._r.hgetall("adg:meta")

    def snapshot(self) -> dict[str, Any]:
        """Return the full ADG snapshot JSON."""
        raw = self._r.get("adg:snapshot")
        return json.loads(raw) if raw else {}

    def get_node(self, node_id: str) -> dict[str, str]:
        """Return a node hash by its ID string."""
        return self._r.hgetall(f"adg:node:{node_id}")

    def nodes_in_file(self, file_path: str) -> set[str]:
        """Return all node IDs defined in a given file path."""
        return self._r.smembers(f"adg:nodes:by_file:{file_path}")

    def nodes_in_layer(self, layer: str) -> set[str]:
        """Return all node IDs belonging to a layer (e.g. 'L0', 'L5')."""
        return self._r.smembers(f"adg:nodes:by_layer:{layer}")

    def fan_out(self, node_id: str, relation: str) -> set[str]:
        """Return all targets of edges (node_id)-[relation]->(*)."""
        return self._r.smembers(f"adg:edge:{node_id}:{relation}")

    def fan_in(self, node_id: str, relation: str) -> set[str]:
        """Return all sources of edges (*)-[relation]->(node_id)."""
        return self._r.smembers(f"adg:edge:in:{node_id}:{relation}")

    def all_edge_relations_from(self, node_id: str) -> list[str]:
        """Return all distinct relation types emanating from node_id."""
        pattern = f"adg:edge:{node_id}:*"
        keys = []
        cursor = 0
        while True:
            cursor, batch = self._r.scan(cursor, match=pattern, count=200)
            keys.extend(batch)
            if cursor == 0:
                break
        prefix = f"adg:edge:{node_id}:"
        return [k[len(prefix) :] for k in keys]

    def violations(self) -> list[dict]:
        """Return all stored layer violations."""
        raw = self._r.lrange("adg:violations", 0, -1)
        return [json.loads(v) for v in raw]

    def is_stale(self, sqlite_mtime: float) -> bool:
        """Return True if the cache was built from an older SQLite file."""
        stored = self._r.hget("adg:meta", "sqlite_mtime")
        if stored is None:
            return True
        return float(stored) < sqlite_mtime
