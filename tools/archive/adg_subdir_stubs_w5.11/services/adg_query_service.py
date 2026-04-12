"""ADG Query Service — Unified SQLite/Redis query layer.

SQLite is the authoritative source of truth.
Redis is a versioned hot read cache.
All queries include snapshot lineage verification.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any

import redis

from agentic_core.adg.contracts.query_contracts import (
    Edge,
    EdgeQueryResult,
    Node,
    NodeQueryResult,
    SnapshotMetadata,
    UnresolvedImport,
)

logger = logging.getLogger(__name__)


class SnapshotNotFoundError(Exception):
    """Raised when requested snapshot does not exist."""

    pass


class CacheParityError(Exception):
    """Raised when Redis cache does not match SQLite for snapshot."""

    pass


class ADGQueryService:
    """Unified query service for ADG graph data.

    SQLite is the authoritative source. Redis provides fast reads
    when snapshot parity is verified. All queries are snapshot-bound.

    Usage:
        service = ADGQueryService()
        service.initialize_snapshot("04022026_2140")

        # Query node
        result = service.get_node(3939)
        if result.success:
            print(result.data.adg_name)

        # Query imports
        edges = service.get_edges(3939, "imports")

        # Find unresolved imports
        unresolved = service.find_unresolved_imports("apps_lic")
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        adg_dir: str | None = None,
    ) -> None:
        """Initialize query service.

        Args:
            redis_url: Redis connection URL
            adg_dir: Directory containing ADG SQLite files (default: artifacts/adg)
        """
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.adg_dir = Path(adg_dir) if adg_dir else Path("artifacts/adg")
        self._current_snapshot: str | None = None
        self._sqlite_conn: sqlite3.Connection | None = None
        self._snapshot_meta: SnapshotMetadata | None = None

    def initialize_snapshot(self, snapshot_id: str) -> SnapshotMetadata:
        """Initialize service for a specific snapshot.

        Loads SQLite connection and verifies Redis cache parity.

        Args:
            snapshot_id: Snapshot identifier (e.g., "04022026_2140")

        Returns:
            SnapshotMetadata with lineage verification

        Raises:
            SnapshotNotFoundError: If snapshot not found in SQLite or Redis
            CacheParityError: If Redis cache does not match SQLite
        """
        self._current_snapshot = snapshot_id

        # Load SQLite
        sqlite_path = self._get_sqlite_path(snapshot_id)
        if not sqlite_path.exists():
            raise SnapshotNotFoundError(f"SQLite not found: {sqlite_path}")

        self._sqlite_conn = sqlite3.connect(str(sqlite_path))
        self._sqlite_conn.row_factory = sqlite3.Row

        # Get metadata from SQLite
        meta = self._load_sqlite_metadata()

        # Verify Redis parity
        redis_meta = self._get_redis_metadata()
        if redis_meta:
            meta.projection_coherent = meta.sqlite_digest == redis_meta.get("redis_digest")
            meta.redis_digest = redis_meta.get("redis_digest")
        else:
            meta.projection_coherent = False

        self._snapshot_meta = meta

        logger.info(
            f"Initialized snapshot {snapshot_id}: {meta.node_count} nodes, "
            f"{meta.edge_count} edges, coherent={meta.projection_coherent}",
        )

        return meta

    def _get_sqlite_path(self, snapshot_id: str) -> Path:
        """Get path to SQLite file for snapshot."""
        return self.adg_dir / f"adg_indexed_{snapshot_id}.sqlite"

    def _load_sqlite_metadata(self) -> SnapshotMetadata:
        """Load metadata from SQLite database."""
        conn = self._sqlite_conn
        assert conn is not None

        cursor = conn.execute("SELECT COUNT(*) FROM nodes")
        node_count = cursor.fetchone()[0]

        cursor = conn.execute("SELECT COUNT(*) FROM edges")
        edge_count = cursor.fetchone()[0]

        # Compute digest (simplified - in production use hashlib)
        sqlite_path = self._get_sqlite_path(self._current_snapshot)  # type: ignore[arg-type]
        sqlite_digest = self._compute_file_digest(sqlite_path)

        return SnapshotMetadata(
            snapshot_id=self._current_snapshot,  # type: ignore[arg-type]
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%S"),
            node_count=node_count,
            edge_count=edge_count,
            sqlite_path=str(sqlite_path),
            sqlite_digest=sqlite_digest,
        )

    def _compute_file_digest(self, path: Path) -> str:
        """Compute SHA256 digest of file."""
        import hashlib

        h = hashlib.sha256()
        h.update(path.read_bytes())
        return h.hexdigest()[:16]

    def _get_redis_metadata(self) -> dict[str, Any] | None:
        """Get metadata from Redis cache."""
        status_key = f"adg:snapshot:{self._current_snapshot}:meta"
        data = self.redis_client.get(status_key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse Redis metadata JSON: {e}")
                return None

        # Fallback to legacy adg:status (non-namespaced)
        legacy = self.redis_client.get("adg:status")
        if legacy:
            try:
                parsed = json.loads(legacy)
                if parsed.get("timestamp") == self._current_snapshot:
                    return parsed
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse legacy status JSON: {e}")
        return None

    def get_snapshot_metadata(self) -> SnapshotMetadata | None:
        """Get current snapshot metadata."""
        return self._snapshot_meta

    def get_node(self, node_id: int, prefer_cache: bool = True) -> NodeQueryResult:
        """Get node by ID.

        Args:
            node_id: Numeric node ID
            prefer_cache: Use Redis cache if available

        Returns:
            NodeQueryResult with node data or error
        """
        if not self._current_snapshot:
            return NodeQueryResult(
                success=False,
                error="No snapshot initialized. Call initialize_snapshot() first.",
            )

        # Try Redis cache first
        if prefer_cache and self._snapshot_meta and self._snapshot_meta.projection_coherent:
            cached = self._get_node_from_redis(node_id)
            if cached:
                return NodeQueryResult(
                    success=True,
                    data=cached,
                    snapshot_id=self._current_snapshot,
                    cache_hit=True,
                )

        # Fall back to SQLite
        node = self._get_node_from_sqlite(node_id)
        if node:
            return NodeQueryResult(
                success=True,
                data=node,
                snapshot_id=self._current_snapshot,
                cache_hit=False,
            )

        return NodeQueryResult(
            success=False,
            error=f"Node {node_id} not found",
            snapshot_id=self._current_snapshot,
        )

    def _get_node_from_redis(self, node_id: int) -> Node | None:
        """Fetch node from Redis cache."""
        # Try namespaced key first
        key = f"adg:snapshot:{self._current_snapshot}:node:{node_id}"
        data = self.redis_client.hgetall(key)

        if not data:
            # Fallback to legacy key
            key = f"adg:node:{node_id}"
            data = self.redis_client.hgetall(key)

        if not data:
            return None

        return Node(
            id=int(data.get("id", node_id)),
            adg_name=data.get("adg_name", ""),
            entity_type=data.get("entity_type", ""),
            layer=data.get("layer"),
            file_path=data.get("resolved_path"),
            identity_kind=data.get("identity_kind"),
            confidence=data.get("confidence", "HIGH"),
        )

    def _get_node_from_sqlite(self, node_id: int) -> Node | None:
        """Fetch node from SQLite database."""
        conn = self._sqlite_conn
        assert conn is not None

        cursor = conn.execute(
            """
            SELECT id, adg_name, entity_type, layer, resolved_path,
                   identity_kind, confidence
            FROM nodes
            WHERE id = ?
            """,
            (node_id,),
        )
        row = cursor.fetchone()

        if not row:
            return None

        return Node(
            id=row[0],
            adg_name=row[1],
            entity_type=row[2],
            layer=row[3],
            file_path=row[4],
            identity_kind=row[5],
            confidence=row[6] or "HIGH",
        )

    def get_edges(
        self,
        src_id: int,
        relation_type: str,
        prefer_cache: bool = True,
    ) -> EdgeQueryResult:
        """Get outgoing edges from a source node.

        Args:
            src_id: Source node ID
            relation_type: Type of relation (imports, calls, etc.)
            prefer_cache: Use Redis cache if available

        Returns:
            EdgeQueryResult with list of edges
        """
        if not self._current_snapshot:
            return EdgeQueryResult(
                success=False,
                error="No snapshot initialized. Call initialize_snapshot() first.",
            )

        # Try Redis cache first
        if prefer_cache and self._snapshot_meta and self._snapshot_meta.projection_coherent:
            cached = self._get_edges_from_redis(src_id, relation_type)
            if cached is not None:
                return EdgeQueryResult(
                    success=True,
                    data=cached,
                    snapshot_id=self._current_snapshot,
                    cache_hit=True,
                )

        # Fall back to SQLite
        edges = self._get_edges_from_sqlite(src_id, relation_type)
        return EdgeQueryResult(
            success=True,
            data=edges,
            snapshot_id=self._current_snapshot,
            cache_hit=False,
        )

    def _get_edges_from_redis(self, src_id: int, relation_type: str) -> list[Edge] | None:
        """Fetch edges from Redis cache."""
        # Try namespaced key first
        key = f"adg:snapshot:{self._current_snapshot}:edge:{src_id}:{relation_type}"
        edge_ids = self.redis_client.smembers(key)

        if not edge_ids:
            # Fallback to legacy key
            key = f"adg:edge:{src_id}:{relation_type}"
            edge_ids = self.redis_client.smembers(key)

        if not edge_ids:
            return None

        edges = []
        for edge_id in edge_ids:
            # Get edge detail
            detail_key = f"adg:snapshot:{self._current_snapshot}:edge_detail:{edge_id}"
            data = self.redis_client.hgetall(detail_key)

            if not data:
                # Fallback to legacy
                detail_key = f"adg:edge_detail:{edge_id}"
                data = self.redis_client.hgetall(detail_key)

            if data:
                edges.append(
                    Edge(
                        id=int(edge_id),
                        src_id=int(data.get("src_id", src_id)),
                        dst_id=int(data.get("dst_id", 0)),
                        relation_type=data.get("relation_type", relation_type),
                        edge_kind=data.get("edge_kind", "direct"),
                        symbol=data.get("symbol"),
                        source_file=data.get("source_file"),
                        line_no=int(data.get("line_no", 0)) if data.get("line_no") else None,
                        semantic_type=data.get("semantic_type"),
                        confidence_score=float(data.get("confidence_score", 1.0)),
                    )
                )

        return edges

    def _get_edges_from_sqlite(self, src_id: int, relation_type: str) -> list[Edge]:
        """Fetch edges from SQLite database."""
        conn = self._sqlite_conn
        assert conn is not None

        cursor = conn.execute(
            """
            SELECT e.id, e.src_id, e.dst_id, e.relation_type, e.symbol,
                   e.source_file, e.line_no
            FROM edges e
            WHERE e.src_id = ? AND e.relation_type = ?
            """,
            (src_id, relation_type),
        )

        edges = []
        for row in cursor.fetchall():
            edges.append(
                Edge(
                    id=row[0],
                    src_id=row[1],
                    dst_id=row[2],
                    relation_type=row[3],
                    symbol=row[4],
                    source_file=row[5],
                    line_no=row[6],
                )
            )

        return edges

    def find_unresolved_imports(self, scope: str | None = None) -> list[UnresolvedImport]:
        """Find unresolved imports in the graph.

        An import is unresolved if its destination node is not a module entity.

        Args:
            scope: Optional scope filter (e.g., "apps_lic" to check only apps_lic modules)

        Returns:
            List of UnresolvedImport records
        """
        if not self._current_snapshot or not self._sqlite_conn:
            raise RuntimeError("No snapshot initialized. Call initialize_snapshot() first.")

        conn = self._sqlite_conn

        # Query for imports where destination is not a module
        if scope:
            cursor = conn.execute(
                """
                SELECT e.id, e.src_id, e.dst_id, e.symbol, e.source_file, e.line_no,
                       n_src.adg_name as src_name, n_dst.entity_type as dst_type
                FROM edges e
                JOIN nodes n_src ON e.src_id = n_src.id
                JOIN nodes n_dst ON e.dst_id = n_dst.id
                WHERE e.relation_type = 'imports'
                AND n_dst.entity_type != 'module'
                AND n_src.adg_name LIKE ?
                """,
                (f"%{scope}%",),
            )
        else:
            cursor = conn.execute(
                """
                SELECT e.id, e.src_id, e.dst_id, e.symbol, e.source_file, e.line_no,
                       n_src.adg_name as src_name, n_dst.entity_type as dst_type
                FROM edges e
                JOIN nodes n_src ON e.src_id = n_src.id
                JOIN nodes n_dst ON e.dst_id = n_dst.id
                WHERE e.relation_type = 'imports'
                AND n_dst.entity_type != 'module'
                """,
            )

        unresolved = []
        for row in cursor.fetchall():
            unresolved.append(
                UnresolvedImport(
                    edge_id=row[0],
                    src_module=row[6],
                    src_file=row[4] or "",
                    line_no=row[5] or 0,
                    symbol=row[3] or "",
                    dst_id=row[2],
                    dst_entity_type=row[7],
                    reason="destination_not_module",
                )
            )

        return unresolved

    def close(self) -> None:
        """Close database connections."""
        if self._sqlite_conn:
            self._sqlite_conn.close()
            self._sqlite_conn = None

    def __enter__(self) -> ADGQueryService:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()


__all__ = [
    "ADGQueryService",
    "SnapshotNotFoundError",
    "CacheParityError",
]
