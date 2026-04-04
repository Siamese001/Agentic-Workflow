"""ADG Service — Query orchestration with mandatory SQLite + optional Redis."""
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

from tools.adg.cache.redis_cache import RedisCache
from tools.adg.core.models import ADGEdge, ADGNode, ADGResponse, HealthStatus
from tools.adg.core.sqlite_backend import SQLiteBackend

logger = logging.getLogger(__name__)


class ADGService:
    """
    Unified ADG query service.

    Architecture:
    - SQLiteBackend = mandatory canonical source
    - RedisCache = optional accelerator only

    Query contract:
    1. Try Redis with 75ms timeout
    2. On any failure, go straight to SQLite
    3. Return same payload shape regardless of backend
    4. Include backend_used in metadata
    """

    _sqlite: SQLiteBackend
    _redis: RedisCache
    _adg_snapshot_id: str

    def __init__(self, redis_url: Optional[str] = "redis://localhost:6379/0"):
        # SQLite is mandatory — fail fast if unavailable
        self._sqlite = SQLiteBackend()

        # Get snapshot ID from SQLite
        status = self._sqlite.get_status()
        self._adg_snapshot_id = status["timestamp"]

        # Redis is optional — gracefully degrade
        self._redis = RedisCache(redis_url)

    def health(self) -> HealthStatus:
        """Return comprehensive health status."""
        sqlite_status, sqlite_meta = self._sqlite.health()
        redis_status, redis_meta = self._redis.health()

        mode = "full" if redis_status == "healthy" else "sqlite_only"
        cache_hit_capable = redis_status == "healthy"

        return HealthStatus(
            mode=mode,
            sqlite=sqlite_status,
            redis=redis_status,
            cache_hit_capable=cache_hit_capable,
            schema_version="1.0",
            adg_snapshot_id=self._adg_snapshot_id,
        )

    def _query_with_fallback(
        self,
        redis_query: Callable[[], Optional[Any]],
        sqlite_query: Callable[[], Any],
        cache_set: Callable[[Any], None]
    ) -> Tuple[Any, str]:
        """Generic read-through pattern."""
        # Try Redis first
        if self._redis._available:
            try:
                result = redis_query()
                if result is not None:
                    return result, "redis"
            except Exception as e:
                logger.debug(f"Redis query failed: {e}")

        # Fall back to SQLite
        result = sqlite_query()

        # Optionally backfill cache
        if self._redis._available and result is not None:
            try:
                cache_set(result)
            except Exception as e:
                logger.debug(f"Cache backfill failed: {e}")

        return result, "sqlite"

    def get_node(self, node_id: str) -> ADGResponse:
        """Fetch node with read-through semantics."""
        node, backend = self._query_with_fallback(
            redis_query=lambda: self._redis.get_node(node_id, self._adg_snapshot_id),
            sqlite_query=lambda: self._sqlite.get_node(node_id),
            cache_set=lambda n: self._redis.set_node(n, self._adg_snapshot_id),
        )

        if node is None:
            return ADGResponse(
                status="error",
                data={"message": f"Node {node_id} not found"},
                backend_used=backend,
            )

        return ADGResponse(
            status="ok",
            data=node.model_dump(),
            backend_used=backend,
        )

    def get_nodes_by_layer(self, layer: str, limit: int = 100) -> ADGResponse:
        """Fetch nodes by layer (Redis not cached for list queries)."""
        nodes = self._sqlite.get_nodes_by_layer(layer, limit)

        return ADGResponse(
            status="ok",
            data={
                "layer": layer,
                "nodes": [n.model_dump() for n in nodes],
                "count": len(nodes),
            },
            backend_used="sqlite",
        )

    def get_nodes_by_file(self, file_path: str, limit: int = 100) -> ADGResponse:
        """Fetch nodes by file path."""
        nodes = self._sqlite.get_nodes_by_file(file_path, limit)

        return ADGResponse(
            status="ok",
            data={
                "file_path": file_path,
                "nodes": [n.model_dump() for n in nodes],
                "count": len(nodes),
            },
            backend_used="sqlite",
        )

    def get_edge_fanout(self, src_id: str, relation_type: str,
                       limit: int = 30) -> ADGResponse:
        """Fetch outgoing edges with read-through."""
        edges, backend = self._query_with_fallback(
            redis_query=lambda: self._redis.get_edge_fanout(
                src_id, relation_type, self._adg_snapshot_id
            ),
            sqlite_query=lambda: self._sqlite.get_edge_fanout(src_id, relation_type, limit),
            cache_set=lambda e: self._redis.set_edge_fanout(
                src_id, relation_type, e, self._adg_snapshot_id
            ),
        )

        if edges is None:
            edges = []

        return ADGResponse(
            status="ok",
            data={
                "src_id": src_id,
                "relation_type": relation_type,
                "edges": [e.model_dump() for e in edges],
                "count": len(edges),
            },
            backend_used=backend,
        )

    def get_edge_fanin(self, tgt_id: str, relation_type: str,
                      limit: int = 30) -> ADGResponse:
        """Fetch incoming edges (SQLite only for now)."""
        edges = self._sqlite.get_edge_fanin(tgt_id, relation_type, limit)

        return ADGResponse(
            status="ok",
            data={
                "tgt_id": tgt_id,
                "relation_type": relation_type,
                "edges": [e.model_dump() for e in edges],
                "count": len(edges),
            },
            backend_used="sqlite",
        )

    def get_status(self) -> ADGResponse:
        """Get ADG snapshot status."""
        status = self._sqlite.get_status()

        return ADGResponse(
            status="ok",
            data=status,
            backend_used="sqlite",
            cache_meta={
                "is_fresh": True,
                "timestamp": status["timestamp"],
                "node_count": status["node_count"],
                "edge_count": status["edge_count"],
            }
        )

    def get_violations(self, limit: int = 100) -> ADGResponse:
        """Get anti-pattern violations."""
        violations = self._sqlite.get_violations(limit)

        return ADGResponse(
            status="ok",
            data={
                "violations": violations,
                "count": len(violations),
            },
            backend_used="sqlite",
        )
