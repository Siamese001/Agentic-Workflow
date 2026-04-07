"""SQLite Backend — Canonical ADG source, mandatory, always available.

Enhanced with SQLiteGraphStore for graph-native operations.
"""
import logging
import sqlite3
from pathlib import Path
from typing import Any

from tools.adg.core.models import ADGEdge, ADGNode
from tools.adg.shared_modules.path_resolver import get_adg_dir

logger = logging.getLogger(__name__)

# Query timeout in seconds
SQLITE_QUERY_TIMEOUT = 5.0


class SQLiteBackend:
    """Canonical ADG backend using SQLite as source of truth.

    Enhanced with optional SQLiteGraphStore for graph-native operations.
    """

    _conn: sqlite3.Connection | None = None
    _sqlite_path: Path | None = None
    _last_mtime: float = 0.0
    _graph_store: Any = None  # Optional SQLiteGraphStore instance

    def __init__(self, use_graph_store: bool = True):
        self._connect()
        if use_graph_store:
            self._init_graph_store()

    def _connect(self) -> None:
        """Establish connection to latest SQLite file."""
        adg_dir = get_adg_dir()
        files = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
        if not files:
            raise RuntimeError("No ADG SQLite file found")

        self._sqlite_path = files[-1]
        self._last_mtime = self._sqlite_path.stat().st_mtime
        self._conn = sqlite3.connect(str(self._sqlite_path), timeout=SQLITE_QUERY_TIMEOUT)
        self._conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrency
        self._conn.execute("PRAGMA journal_mode=WAL")

    def health(self) -> tuple[str, dict[str, Any]]:
        """Return health status and metadata."""
        if not self._sqlite_path or not self._sqlite_path.exists():
            return "unavailable", {}

        current_mtime = self._sqlite_path.stat().st_mtime
        is_fresh = current_mtime == self._last_mtime

        return "healthy", {
            "path": str(self._sqlite_path),
            "mtime": current_mtime,
            "is_fresh": is_fresh,
        }

    def get_node(self, node_id: str) -> ADGNode | None:
        """Fetch node by ID from SQLite."""
        cur = self._conn.execute(
            "SELECT * FROM nodes WHERE id = ?", (node_id,)
        )
        row = cur.fetchone()
        if row:
            return ADGNode(**dict(row))
        return None

    def get_nodes_by_layer(self, layer: str, limit: int = 100) -> list[ADGNode]:
        """Fetch nodes by layer."""
        cur = self._conn.execute(
            "SELECT * FROM nodes WHERE layer = ? LIMIT ?",
            (layer, limit)
        )
        return [ADGNode(**dict(row)) for row in cur.fetchall()]

    def get_nodes_by_file(self, file_path: str, limit: int = 100) -> list[ADGNode]:
        """Fetch nodes by file path."""
        cur = self._conn.execute(
            "SELECT * FROM nodes WHERE resolved_path LIKE ? LIMIT ?",
            (f"%{file_path}%", limit)
        )
        return [ADGNode(**dict(row)) for row in cur.fetchall()]

    def get_edge_fanout(self, src_id: str, relation_type: str, limit: int = 30) -> list[ADGEdge]:
        """Fetch outgoing edges."""
        cur = self._conn.execute(
            """SELECT id, src_id, dst_id, relation_type, edge_kind,
                      source_file, line_no, symbol
               FROM edges WHERE src_id = ? AND relation_type = ? LIMIT ?""",
            (src_id, relation_type, limit)
        )
        return [ADGEdge(**dict(row)) for row in cur.fetchall()]

    def get_edge_fanin(self, tgt_id: str, relation_type: str, limit: int = 30) -> list[ADGEdge]:
        """Fetch incoming edges."""
        cur = self._conn.execute(
            """SELECT id, src_id, dst_id, relation_type, edge_kind,
                      source_file, line_no, symbol
               FROM edges WHERE dst_id = ? AND relation_type = ? LIMIT ?""",
            (tgt_id, relation_type, limit)
        )
        return [ADGEdge(**dict(row)) for row in cur.fetchall()]

    def get_status(self) -> dict[str, Any]:
        """Get ADG snapshot status."""
        nodes = self._conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        edges = self._conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]

        return {
            "timestamp": self._sqlite_path.stem.replace("adg_indexed_", ""),
            "node_count": nodes,
            "edge_count": edges,
            "sqlite_path": str(self._sqlite_path),
        }

    def get_violations(self, limit: int = 100) -> list[dict[str, Any]]:
        """Fetch anti-pattern violations."""
        try:
            cur = self._conn.execute(
                """SELECT id, source_file, relation_type, symbol, line_no
                   FROM edges WHERE relation_type = 'violates' LIMIT ?""",
                (limit,)
            )
            return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as e:
            # Table or column may not exist
            logger.debug(f"get_violations query failed: {e}")
            return []

    def close(self) -> None:
        """Close SQLite connection and release file locks."""
        if self._conn:
            try:
                # Checkpoint WAL to release locks before closing
                self._conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                self._conn.close()
                logger.info(f"Closed SQLite connection to {self._sqlite_path}")
            except Exception as e:  # guardian: allow-log-and-swallow -- teardown/cleanup context -- swallow is conventional in resource-release paths
                logger.error(f"Error closing SQLite connection: {e}")
            finally:
                self._conn = None

    def reopen(self) -> None:
        """Reopen SQLite connection after closing to refresh/release locks lifecycle."""
        if self._conn is not None:
            self.close()
        self._connect()
        if self._graph_store is None:
            self._init_graph_store()
        logger.info(f"Reopened SQLite connection to {self._sqlite_path}")

    # Graph-native methods that delegate to SQLiteGraphStore when available

    def get_centrality(self, node_id: str) -> float:
        """Get centrality score for a node using graph store if available."""
        if self._graph_store:
            return self._graph_store.get_centrality(node_id)
        # Fallback: degree centrality from direct edge count
        cur = self._conn.execute(
            "SELECT COUNT(*) FROM edges WHERE src_id = ? OR dst_id = ?",
            (node_id, node_id)
        )
        return float(cur.fetchone()[0])

    def traverse(self, start_id: str, max_depth: int = 2, relation_types: list[str] | None = None) -> list:
        """Traverse graph from start node using graph store if available."""
        if self._graph_store:
            return self._graph_store.traverse(start_id, max_depth, relation_types)
        # Fallback: simple BFS using SQL
        return self._traverse_sql(start_id, max_depth, relation_types)

    def _traverse_sql(self, start_id: str, max_depth: int, relation_types: list[str] | None) -> list:
        """Fallback SQL-based traversal when graph store unavailable."""
        paths = []
        visited = {start_id}
        current_level = [(start_id, [])]  # (node_id, path)

        for depth in range(max_depth):
            next_level = []
            for node_id, path in current_level:
                # Get neighbors
                query = "SELECT dst_id FROM edges WHERE src_id = ?"
                params = [node_id]
                if relation_types:
                    placeholders = ",".join(["?" for _ in relation_types])
                    query += f" AND relation_type IN ({placeholders})"
                    params.extend(relation_types)

                cur = self._conn.execute(query, params)
                for row in cur.fetchall():
                    neighbor_id = row[0]
                    if neighbor_id not in visited:
                        visited.add(neighbor_id)
                        new_path = path + [node_id]
                        paths.append({"path": new_path, "depth": depth + 1})
                        next_level.append((neighbor_id, new_path))
            current_level = next_level
            if not current_level:
                break

        return paths
