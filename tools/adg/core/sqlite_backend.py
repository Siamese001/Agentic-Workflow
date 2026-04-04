"""SQLite Backend — Canonical ADG source, mandatory, always available."""
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
    """Canonical ADG backend using SQLite as source of truth."""

    _conn: sqlite3.Connection | None = None
    _sqlite_path: Path | None = None
    _last_mtime: float = 0.0

    def __init__(self):
        self._connect()

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
