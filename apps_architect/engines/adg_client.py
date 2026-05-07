"""ADG client — direct SQLite wrapper for ADG snapshot queries.

Plan: ``.windsurf/plans/apps-architect-pattern-hardening-d7e4f9.md`` W2.P1.

Uses direct SQLite access to the latest ADG snapshot per constitutional §28.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ADG_DIR = _REPO_ROOT / "artifacts" / "adg"


def _latest_snapshot() -> Path | None:
    if not _ADG_DIR.exists():
        return None
    snapshots = sorted(
        _ADG_DIR.glob("adg_indexed_*.sqlite"),
        key=lambda p: p.stat().st_mtime, reverse=True,
    )
    return snapshots[0] if snapshots else None


class ADGClient:
    """Read-only ADG snapshot client with lazy connection."""

    def __init__(self, snapshot_path: str | Path | None = None) -> None:
        self._snapshot_path: Path | None = (
            Path(snapshot_path) if snapshot_path else _latest_snapshot()
        )
        self._conn: sqlite3.Connection | None = None

    @property
    def snapshot_path(self) -> Path | None:
        return self._snapshot_path

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            if self._snapshot_path is None:
                raise FileNotFoundError("No ADG snapshot available")
            self._conn = sqlite3.connect(str(self._snapshot_path))
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def health(self) -> dict[str, Any]:
        try:
            path = self._snapshot_path
            if path is None or not path.exists():
                return {"status": "unhealthy", "reason": "no_snapshot"}
            self.conn.execute("SELECT 1 FROM nodes LIMIT 1")
            return {"status": "healthy", "snapshot": str(path)}
        except Exception as exc:
            return {"status": "unhealthy", "reason": str(exc)}

    def mv_hotspot_centrality(self, limit: int = 50) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM mv_hotspot_centrality ORDER BY degree_centrality DESC, fan_in DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]

    def nodes_by_layer(self, layer: str, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM nodes WHERE layer=? LIMIT ?", (layer, limit)
        ).fetchall()
        return [dict(r) for r in rows]

    def nodes_by_file(self, file_path: str, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM nodes WHERE resolved_path LIKE ? LIMIT ?",
            (f"%{file_path}%", limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def edge_fanin(self, tgt_id: str, relation_type: str, limit: int = 30) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT e.*, n.adg_name AS src_name, n.layer AS src_layer FROM edges e "
            "JOIN nodes n ON n.id=e.src_id WHERE e.dst_id=? AND e.relation_type=? LIMIT ?",
            (tgt_id, relation_type, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def edge_fanout(self, src_id: str, relation_type: str, limit: int = 30) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT e.*, n.adg_name AS dst_name, n.layer AS dst_layer FROM edges e "
            "JOIN nodes n ON n.id=e.dst_id WHERE e.src_id=? AND e.relation_type=? LIMIT ?",
            (src_id, relation_type, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def violations(self, limit: int = 100) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM edges WHERE edge_kind='violation' LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def p_view_query(self, view_name: str, limit: int = 100) -> list[dict[str, Any]]:
        valid = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='view' AND name=?", (view_name,)
        ).fetchone()
        if not valid:
            return []
        rows = self.conn.execute(
            f"SELECT * FROM [{view_name}] LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    def node_count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]

    def edge_count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]

    def layer_summary(self) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT layer, COUNT(*) AS cnt FROM nodes WHERE layer!='' GROUP BY layer ORDER BY layer"
        ).fetchall()
        return [dict(r) for r in rows]

    def cross_layer_edges(self, from_layer: str, to_layer: str, limit: int = 50) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT e.*, s.adg_name AS src_name, s.layer AS src_layer, "
            "d.adg_name AS dst_name, d.layer AS dst_layer "
            "FROM edges e JOIN nodes s ON s.id=e.src_id JOIN nodes d ON d.id=e.dst_id "
            "WHERE s.layer=? AND d.layer=? AND e.relation_type='imports' LIMIT ?",
            (from_layer, to_layer, limit),
        ).fetchall()
        return [dict(r) for r in rows]


__all__ = ["ADGClient"]
