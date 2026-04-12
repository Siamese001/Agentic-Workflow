"""ADG Service — Query orchestration with mandatory SQLite + optional Redis."""

import logging
from typing import Any, Callable

from tools.adg.cache.redis_cache import RedisCache
from tools.adg.core.models import ADGResponse, HealthStatus
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

    def __init__(self, redis_url: str | None = "redis://localhost:6379/0"):
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
        redis_query: Callable[[], Any | None],
        sqlite_query: Callable[[], Any],
        cache_set: Callable[[Any], None],
    ) -> tuple[Any, str]:
        """Generic read-through pattern."""
        # Try Redis first
        if self._redis._available:
            try:
                result = redis_query()
                # Treat [] the same as None: an empty cached list is indistinguishable
                # from a cache miss for edge queries, so always fall through to SQLite.
                if result is not None and result != []:
                    return result, "redis"
            except Exception as e:  # guardian: allow-broad-exception -- Redis client can raise varied transport/timeout/serialization errors; all are non-fatal and should fall through to SQLite
                logger.debug(f"Redis query failed: {e}")

        # Fall back to SQLite
        result = sqlite_query()

        # Optionally backfill cache (only if result is valid and non-empty)
        if self._redis._available and result is not None:
            # Validate result before caching (don't cache None or invalid data)
            is_valid = True
            if isinstance(result, list) and not result:
                # Empty list is valid but may not be worth caching
                pass  # Still cache empty results to avoid repeated misses

            if is_valid:
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

    def get_edge_fanout(self, src_id: str, relation_type: str, limit: int = 30) -> ADGResponse:
        """Fetch outgoing edges with read-through."""
        edges, backend = self._query_with_fallback(
            redis_query=lambda: self._redis.get_edge_fanout(
                src_id,
                relation_type,
                self._adg_snapshot_id,
            ),
            sqlite_query=lambda: self._sqlite.get_edge_fanout(src_id, relation_type, limit),
            cache_set=lambda e: self._redis.set_edge_fanout(
                src_id,
                relation_type,
                e,
                self._adg_snapshot_id,
            ),
        )

        # edges is never None from _query_with_fallback (SQLite always returns list)
        # but may be empty list if no edges exist
        return ADGResponse(
            status="ok",
            data={
                "src_id": src_id,
                "relation_type": relation_type,
                "edges": [e.model_dump() for e in edges] if edges else [],
                "count": len(edges) if edges else 0,
            },
            backend_used=backend,
        )

    def get_edge_fanin(self, tgt_id: str, relation_type: str, limit: int = 30) -> ADGResponse:
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
            },
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

    def close(self) -> None:
        """Close all backend connections and release resources."""
        if self._sqlite:
            self._sqlite.close()
        if self._redis:
            self._redis.close()
        logger.info("ADGService closed all connections")

    def reopen(self) -> None:
        """Reopen backend connections after explicit close for lock release workflows."""
        if self._sqlite:
            self._sqlite.reopen()
            # Refresh snapshot ID so Redis cache keys reflect the active snapshot.
            # Without this, Redis lookups after a reload use the stale snapshot ID.
            status = self._sqlite.get_status()
            self._adg_snapshot_id = status["timestamp"]
        logger.info("ADGService reopened SQLite connection")

    def get_projection_status(self) -> ADGResponse:
        """Return graph projection availability, staleness, and metadata."""
        data = self._sqlite.get_projection_status()
        return ADGResponse(
            status="ok",
            data=data,
            backend_used="projection",
        )

    def get_blast_radius(self, node_id: str, hops: int = 2) -> ADGResponse:
        """Return blast-radius summary for a node from the graph projection."""
        data = self._sqlite.get_blast_radius(node_id, hops=hops)
        return ADGResponse(
            status="ok",
            data=data,
            backend_used="projection",
        )

    def get_scc(self, node_id: str) -> ADGResponse:
        """Return SCC membership for a node from the graph projection."""
        data = self._sqlite.get_scc(node_id)
        return ADGResponse(
            status="ok",
            data=data if data is not None else {"adg_name": node_id, "scc": None},
            backend_used="projection",
        )

    def get_violations_with_impact(
        self,
        layer: str | None = None,
        severity: str | None = None,
        limit: int = 100,
    ) -> ADGResponse:
        """Return violations with blast-radius impact from the graph projection."""
        rows = self._sqlite.get_violations_with_impact(layer=layer, severity=severity, limit=limit)
        return ADGResponse(
            status="ok",
            data={"violations": rows, "count": len(rows)},
            backend_used="projection",
        )

    def get_diff(
        self,
        metric: str | None = None,
        direction: str | None = None,
        layer: str | None = None,
        limit: int = 100,
    ) -> ADGResponse:
        """Return cross-run metric deltas from the graph projection."""
        rows = self._sqlite.get_diff(metric=metric, direction=direction, layer=layer, limit=limit)
        return ADGResponse(
            status="ok",
            data={"diff": rows, "count": len(rows)},
            backend_used="projection",
        )

    def get_top_bridges(self, limit: int = 20) -> ADGResponse:
        """Return top bridge/chokepoint nodes from the graph projection."""
        rows = self._sqlite.get_top_bridges(limit=limit)
        return ADGResponse(
            status="ok",
            data={"bridges": rows, "count": len(rows)},
            backend_used="projection",
        )

    def get_top_regressions(
        self,
        metric: str = "blast_radius_direct",
        limit: int = 20,
    ) -> ADGResponse:
        """Return top metric regressions from the graph projection."""
        rows = self._sqlite.get_top_regressions(metric=metric, limit=limit)
        return ADGResponse(
            status="ok",
            data={"regressions": rows, "count": len(rows)},
            backend_used="projection",
        )

    def get_reachability(self, src_adg_name: str, limit: int = 50) -> ADGResponse:
        """Return reachability rows for a seed module from the graph projection."""
        rows = self._sqlite.get_reachability(src_adg_name, limit=limit)
        return ADGResponse(
            status="ok",
            data={"reachability": rows, "count": len(rows), "src": src_adg_name},
            backend_used="projection",
        )

    def find_node(self, name: str, limit: int = 10) -> ADGResponse:
        """Find nodes by exact or prefix adg_name match."""
        nodes = self._sqlite.find_node(name, limit)

        return ADGResponse(
            status="ok",
            data={
                "query": name,
                "nodes": [n.model_dump() for n in nodes],
                "count": len(nodes),
            },
            backend_used="sqlite",
        )
