"""Graph Projection Backend — Read-only adapter over `adg_graph_<ts>.sqlite`.

This backend provides graph-native query access to the derived projection artifact
produced by `tools/generate/graph_projection.py`. It is intentionally read-only and
never touches the canonical `adg_indexed_<ts>.sqlite`.

Staleness contract
------------------
On every connection open, `proj_meta.source_artifact_digest` is compared against
`canonical.meta.artifact_digest`. If they differ, the backend is marked stale and
all query methods return `None` or `[]` without raising. Callers receive an explicit
`is_stale()` signal via the public API.

Availability contract
---------------------
If no `adg_graph_*.sqlite` file exists in the ADG artifacts directory, the backend
is marked unavailable. All query methods return `None` or `[]` without raising.

This backend fills the `SQLiteBackend._init_graph_store()` stub seam (Increment 3).
It is wired into `SQLiteBackend` only in Increment 3 — this file is self-contained.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any

from tools.adg.shared_modules.path_resolver import get_adg_dir

logger = logging.getLogger(__name__)

_PROJ_QUERY_TIMEOUT = 5.0
_PROJ_FILE_GLOB = "adg_graph_*.sqlite"
_CANONICAL_FILE_GLOB = "adg_indexed_*.sqlite"


class GraphProjectionBackend:
    """Read-only adapter over `adg_graph_<ts>.sqlite`.

    Discovers the latest projection file on construction, verifies its lineage
    against the canonical artifact, and exposes graph-native query methods that
    go beyond what SQL-based Phase A-E materialized views can provide.

    Thread safety: not thread-safe. Use one instance per thread or protect with a lock.
    """

    _conn: sqlite3.Connection | None
    _proj_path: Path | None
    _available: bool
    _stale: bool
    _source_artifact_digest: str
    _proj_node_count: int
    _proj_schema_version: str

    def __init__(self, canonical_sqlite_path: Path | None = None) -> None:
        """Discover and connect to the latest projection sqlite.

        Args:
            canonical_sqlite_path: Path to the canonical `adg_indexed_<ts>.sqlite`.
                                   If None, the latest canonical file is auto-discovered
                                   from the ADG artifacts directory.
        """
        self._conn = None
        self._proj_path = None
        self._available = False
        self._stale = False
        self._source_artifact_digest = ""
        self._proj_node_count = 0
        self._proj_schema_version = ""

        self._connect(canonical_sqlite_path)

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    def _connect(self, canonical_sqlite_path: Path | None) -> None:
        """Discover projection file, open connection, run staleness check."""
        adg_dir = _resolve_adg_dir()

        proj_files = sorted(f for f in adg_dir.glob(_PROJ_FILE_GLOB) if not f.name.endswith(".tmp"))
        if not proj_files:
            logger.debug(
                "GraphProjectionBackend: no %s found in %s — unavailable",
                _PROJ_FILE_GLOB,
                adg_dir,
            )
            return

        self._proj_path = proj_files[-1]

        try:
            self._conn = sqlite3.connect(
                str(self._proj_path),
                timeout=_PROJ_QUERY_TIMEOUT,
            )
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA query_only = ON")
        except sqlite3.Error as exc:
            logger.debug(
                "GraphProjectionBackend: could not open %s: %s — unavailable",
                self._proj_path.name,
                exc,
            )
            self._conn = None
            return

        if not self._tables_present():
            logger.debug(
                "GraphProjectionBackend: %s is missing expected proj_* tables — unavailable",
                self._proj_path.name,
            )
            self._conn.close()
            self._conn = None
            return

        self._load_meta()
        self._check_staleness(canonical_sqlite_path, adg_dir)

        self._available = True
        logger.debug(
            "GraphProjectionBackend: connected to %s (stale=%s)",
            self._proj_path.name,
            self._stale,
        )

    def _tables_present(self) -> bool:
        """Return True if all required proj_* tables exist."""
        conn = self._conn  # local alias — Mypy can narrow locals, not class attrs
        if conn is None:
            return False
        required = {
            "proj_meta",
            "proj_nodes",
            "proj_centrality",
            "proj_scc",
            "proj_violations",
            "proj_reachability",
            "proj_diff",
        }
        try:
            existing = {
                row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            }
            return required.issubset(existing)
        except sqlite3.Error:
            return False

    def _load_meta(self) -> None:
        """Read proj_meta fields needed for status and staleness check."""
        conn = self._conn  # local alias — Mypy can narrow locals, not class attrs
        if conn is None:
            return
        try:
            rows = conn.execute("SELECT key, value FROM proj_meta").fetchall()
            meta: dict[str, str] = {r["key"]: r["value"] for r in rows}
            self._source_artifact_digest = meta.get("source_artifact_digest", "")
            self._proj_schema_version = meta.get("schema_version", "")
            self._proj_node_count = int(meta.get("node_count", "0"))
        except (sqlite3.Error, ValueError):
            pass

    def _check_staleness(
        self,
        canonical_sqlite_path: Path | None,
        adg_dir: Path,
    ) -> None:
        """Mark stale if proj source_artifact_digest ≠ canonical artifact_digest."""
        canonical_path = canonical_sqlite_path
        if canonical_path is None or not canonical_path.exists():
            canon_files = sorted(adg_dir.glob(_CANONICAL_FILE_GLOB))
            canonical_path = canon_files[-1] if canon_files else None

        if canonical_path is None or not canonical_path.exists():
            logger.debug(
                "GraphProjectionBackend: no canonical sqlite found for staleness check — "
                "treating projection as stale"
            )
            self._stale = True
            return

        try:
            canon_conn = sqlite3.connect(str(canonical_path), timeout=_PROJ_QUERY_TIMEOUT)
            canon_conn.row_factory = sqlite3.Row
            row = canon_conn.execute("SELECT value FROM meta WHERE key = 'artifact_digest'").fetchone()
            canon_conn.close()
        except sqlite3.Error as exc:
            logger.debug(
                "GraphProjectionBackend: could not read canonical meta (%s) — treating projection as stale",
                exc,
            )
            self._stale = True
            return

        canonical_digest = row["value"] if row else ""
        if not canonical_digest or not self._source_artifact_digest:
            self._stale = True
            return

        self._stale = self._source_artifact_digest != canonical_digest
        if self._stale:
            logger.debug(
                "GraphProjectionBackend: stale — projection digest %s…  canonical digest %s…",
                self._source_artifact_digest[:12],
                canonical_digest[:12],
            )

    # ------------------------------------------------------------------
    # Public availability and staleness signals
    # ------------------------------------------------------------------

    def is_available(self) -> bool:
        """Return True if a projection file was found and opened successfully.

        A stale projection is still considered available — callers should
        check `is_stale()` separately if they require freshness guarantees.
        Returns False only when no projection file exists or it could not be opened.
        """
        return self._available

    def is_stale(self) -> bool:
        """Return True if the projection's source_artifact_digest ≠ canonical artifact_digest.

        A stale projection contains metrics computed from an older canonical run.
        Query methods return results even when stale — the `get_status()` response
        carries `stale=True` so callers can surface it in logs or MCP metadata.
        """
        return self._stale

    # ------------------------------------------------------------------
    # Query methods
    # ------------------------------------------------------------------

    def get_centrality(self, adg_name: str) -> dict[str, Any] | None:
        """Return centrality metrics for a single node by adg_name.

        Returns None if the backend is unavailable, the node is not in the
        projection, or any sqlite error occurs.

        Return shape (when found):
            {
                "adg_name": str,
                "fan_in": int,
                "fan_out": int,
                "import_fan_in": int,
                "import_fan_out": int,
                "betweenness_approx": float,
                "reverse_dep_score": float,
                "blast_radius_direct": int,
                "blast_radius_2hop": int,
                "bridge_score": float,
                "bridge_type": str,
                "snapshot_id": str,
                "derived_from": str,   # source_artifact_digest[:16]
                "stale": bool,
            }
        """
        if not self._available or self._conn is None:
            return None

        try:
            row = self._conn.execute(
                "SELECT * FROM proj_centrality WHERE adg_name = ?",
                (adg_name,),
            ).fetchone()
        except sqlite3.Error as exc:
            logger.debug("GraphProjectionBackend.get_centrality failed: %s", exc)
            return None

        if row is None:
            return None

        result = dict(row)
        result["derived_from"] = self._source_artifact_digest[:16]
        result["stale"] = self._stale
        return result

    def get_blast_radius(self, adg_name: str, hops: int = 2) -> dict[str, Any]:
        """Return blast-radius summary for a node.

        Always returns a dict — empty counts when unavailable or node not found.
        For hops=1, returns blast_radius_direct from proj_centrality.
        For hops=2+, also returns blast_radius_2hop and proj_reachability row count.

        Return shape:
            {
                "adg_name": str,
                "blast_radius_direct": int,
                "blast_radius_2hop": int,
                "reachability_rows": int,   # rows in proj_reachability for this seed
                "hops_requested": int,
                "derived_from": str,
                "stale": bool,
                "available": bool,
            }
        """
        base: dict[str, Any] = {
            "adg_name": adg_name,
            "blast_radius_direct": 0,
            "blast_radius_2hop": 0,
            "reachability_rows": 0,
            "hops_requested": hops,
            "derived_from": self._source_artifact_digest[:16],
            "stale": self._stale,
            "available": self._available,
        }

        if not self._available or self._conn is None:
            return base

        try:
            row = self._conn.execute(
                "SELECT blast_radius_direct, blast_radius_2hop FROM proj_centrality WHERE adg_name = ?",
                (adg_name,),
            ).fetchone()
        except sqlite3.Error as exc:
            logger.debug("GraphProjectionBackend.get_blast_radius centrality query failed: %s", exc)
            return base

        if row:
            base["blast_radius_direct"] = row["blast_radius_direct"]
            base["blast_radius_2hop"] = row["blast_radius_2hop"]

        if hops >= 2:
            try:
                count_row = self._conn.execute(
                    "SELECT COUNT(*) AS cnt FROM proj_reachability WHERE src_adg_name = ?",
                    (adg_name,),
                ).fetchone()
                base["reachability_rows"] = count_row["cnt"] if count_row else 0
            except sqlite3.Error as exc:
                logger.debug("GraphProjectionBackend.get_blast_radius reachability query failed: %s", exc)

        return base

    def get_scc(self, adg_name: str) -> dict[str, Any] | None:
        """Return SCC membership for a node.

        Returns None if the backend is unavailable, the node is not in any
        non-trivial SCC, or any sqlite error occurs. A None return for a given
        node means it is in a trivial SCC (size=1) — architecturally positive.

        Return shape (when found):
            {
                "adg_name": str,
                "scc_id": str,
                "scc_size": int,
                "scc_type": str,
                "scc_risk_score": float,
                "members": [str, ...],   # all adg_names in the same SCC
                "snapshot_id": str,
                "derived_from": str,
                "stale": bool,
            }
        """
        if not self._available or self._conn is None:
            return None

        try:
            row = self._conn.execute(
                "SELECT scc_id, scc_size, scc_type, scc_risk_score, snapshot_id "
                "FROM proj_scc WHERE adg_name = ?",
                (adg_name,),
            ).fetchone()
        except sqlite3.Error as exc:
            logger.debug("GraphProjectionBackend.get_scc failed: %s", exc)
            return None

        if row is None:
            return None

        scc_id = row["scc_id"]

        try:
            member_rows = self._conn.execute(
                "SELECT adg_name FROM proj_scc WHERE scc_id = ? ORDER BY adg_name",
                (scc_id,),
            ).fetchall()
            members = [r["adg_name"] for r in member_rows]
        except sqlite3.Error as exc:
            logger.debug("GraphProjectionBackend.get_scc members query failed: %s", exc)
            members = [adg_name]

        return {
            "adg_name": adg_name,
            "scc_id": scc_id,
            "scc_size": row["scc_size"],
            "scc_type": row["scc_type"],
            "scc_risk_score": row["scc_risk_score"],
            "members": members,
            "snapshot_id": row["snapshot_id"],
            "derived_from": self._source_artifact_digest[:16],
            "stale": self._stale,
        }

    def get_violations_with_impact(
        self,
        layer: str | None = None,
        severity: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Return violations joined with blast-radius impact.

        Filters by layer prefix on `adg_name_from` and/or `severity`.
        Returns [] if backend is unavailable or any sqlite error occurs.

        Return shape (each item):
            {
                "adg_name_from": str,
                "adg_name_to": str,
                "relation_type": str,
                "edge_kind": str,
                "source_file": str,
                "line_no": int,
                "severity": str,
                "violation_class": str,
                "disposition": str,
                "category": str,
                "blast_radius_direct": int,
                "snapshot_id": str,
                "derived_from": str,
                "stale": bool,
            }
        """
        if not self._available or self._conn is None:
            return []

        conditions: list[str] = []
        params: list[Any] = []

        if layer is not None:
            conditions.append("adg_name_from LIKE ?")
            params.append(f"ADG::Module::{layer.rstrip('/')}%")

        if severity is not None:
            conditions.append("severity = ?")
            params.append(severity.upper())

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(limit)

        sql = (
            f"SELECT adg_name_from, adg_name_to, relation_type, edge_kind, "
            f"source_file, line_no, severity, violation_class, disposition, "
            f"category, blast_radius_direct, snapshot_id "
            f"FROM proj_violations {where_clause} "
            f"ORDER BY blast_radius_direct DESC, severity DESC "
            f"LIMIT ?"
        )

        try:
            rows = self._conn.execute(sql, params).fetchall()
        except sqlite3.Error as exc:
            logger.debug("GraphProjectionBackend.get_violations_with_impact failed: %s", exc)
            return []

        result = []
        for row in rows:
            item = dict(row)
            item["derived_from"] = self._source_artifact_digest[:16]
            item["stale"] = self._stale
            result.append(item)

        return result

    def get_status(self) -> dict[str, Any]:
        """Return backend availability, staleness, and projection metadata.

        Always returns a dict — never raises.

        Return shape:
            {
                "available": bool,
                "stale": bool,
                "projection_path": str | None,
                "source_artifact_digest": str,
                "proj_schema_version": str,
                "node_count": int,
            }
        """
        return {
            "available": self._available,
            "stale": self._stale,
            "projection_path": str(self._proj_path) if self._proj_path else None,
            "source_artifact_digest": self._source_artifact_digest,
            "proj_schema_version": self._proj_schema_version,
            "node_count": self._proj_node_count,
        }

    def get_diff(
        self,
        metric: str | None = None,
        direction: str | None = None,
        layer: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Return cross-run metric deltas from proj_diff.

        Filters to changed rows only (direction != 'unchanged') unless
        direction is explicitly passed. Returns [] if unavailable.

        Args:
            metric:    One of fan_in, fan_out, blast_radius_direct, blast_radius_2hop.
                       None = all metrics.
            direction: 'increased', 'decreased', 'unchanged', or None (changed only).
            layer:     Layer prefix filter (e.g. 'L0', 'L3').
            limit:     Maximum rows to return (default 100).

        Return shape (each item):
            {
                "adg_name": str,
                "metric": str,
                "prev_value": float,
                "curr_value": float,
                "delta": float,
                "delta_pct": float,
                "direction": str,
                "layer": str,
                "prev_snapshot_id": str,
                "curr_snapshot_id": str,
                "derived_from": str,
                "stale": bool,
            }
        """
        if not self._available or self._conn is None:
            return []

        conditions: list[str] = []
        params: list[Any] = []

        if direction is not None:
            conditions.append("direction = ?")
            params.append(direction)
        else:
            conditions.append("direction != 'unchanged'")

        if metric is not None:
            conditions.append("metric = ?")
            params.append(metric)

        if layer is not None:
            conditions.append("layer = ?")
            params.append(layer)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(limit)

        sql = (
            f"SELECT adg_name, metric, prev_value, curr_value, delta, delta_pct, "
            f"direction, layer, prev_snapshot_id, curr_snapshot_id "
            f"FROM proj_diff {where} "
            f"ORDER BY ABS(delta) DESC "
            f"LIMIT ?"
        )

        try:
            rows = self._conn.execute(sql, params).fetchall()
        except sqlite3.Error as exc:
            logger.debug("GraphProjectionBackend.get_diff failed: %s", exc)
            return []

        result = []
        for row in rows:
            item = dict(row)
            item["derived_from"] = self._source_artifact_digest[:16]
            item["stale"] = self._stale
            result.append(item)
        return result

    def get_top_bridges(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return the top bridge/chokepoint nodes by bridge_score descending.

        Bridge nodes are critical connectors whose removal would fragment the
        dependency graph. Returns [] if unavailable or no bridge data exists.

        Return shape (each item):
            {
                "adg_name": str,
                "bridge_score": float,
                "bridge_type": str,
                "fan_in": int,
                "fan_out": int,
                "blast_radius_direct": int,
                "layer": str,
                "derived_from": str,
                "stale": bool,
            }
        """
        if not self._available or self._conn is None:
            return []

        try:
            rows = self._conn.execute(
                "SELECT c.adg_name, c.bridge_score, c.bridge_type, "
                "c.fan_in, c.fan_out, c.blast_radius_direct, n.layer "
                "FROM proj_centrality c "
                "JOIN proj_nodes n ON c.adg_name = n.adg_name "
                "WHERE c.bridge_score > 0 "
                "ORDER BY c.bridge_score DESC "
                "LIMIT ?",
                (limit,),
            ).fetchall()
        except sqlite3.Error as exc:
            logger.debug("GraphProjectionBackend.get_top_bridges failed: %s", exc)
            return []

        result = []
        for row in rows:
            item = dict(row)
            item["derived_from"] = self._source_artifact_digest[:16]
            item["stale"] = self._stale
            result.append(item)
        return result

    def get_top_regressions(
        self,
        metric: str = "blast_radius_direct",
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Return the top regressions (largest increases) from proj_diff.

        Args:
            metric: Metric to rank by (default: blast_radius_direct).
            limit:  Maximum rows (default 20).

        Return shape (each item):
            {
                "adg_name": str,
                "metric": str,
                "prev_value": float,
                "curr_value": float,
                "delta": float,
                "delta_pct": float,
                "layer": str,
                "derived_from": str,
                "stale": bool,
            }
        """
        if not self._available or self._conn is None:
            return []

        try:
            rows = self._conn.execute(
                "SELECT adg_name, metric, prev_value, curr_value, delta, delta_pct, layer "
                "FROM proj_diff "
                "WHERE metric = ? AND direction = 'increased' "
                "ORDER BY delta DESC "
                "LIMIT ?",
                (metric, limit),
            ).fetchall()
        except sqlite3.Error as exc:
            logger.debug("GraphProjectionBackend.get_top_regressions failed: %s", exc)
            return []

        result = []
        for row in rows:
            item = dict(row)
            item["derived_from"] = self._source_artifact_digest[:16]
            item["stale"] = self._stale
            result.append(item)
        return result

    def get_reachability(
        self,
        src_adg_name: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Return proj_reachability rows for a given seed module.

        These represent nodes reachable from src_adg_name within the hop
        budget used at build time (_REACHABILITY_MAX_HOPS).

        Returns [] if unavailable or the node is not a reachability seed.

        Return shape (each item):
            {
                "src_adg_name": str,
                "dst_adg_name": str,
                "hop_count": int,
                "path_weight": float,
                "derived_from": str,
                "stale": bool,
            }
        """
        if not self._available or self._conn is None:
            return []

        try:
            rows = self._conn.execute(
                "SELECT src_adg_name, dst_adg_name, hop_count, path_weight "
                "FROM proj_reachability WHERE src_adg_name = ? "
                "ORDER BY hop_count ASC, dst_adg_name ASC "
                "LIMIT ?",
                (src_adg_name, limit),
            ).fetchall()
        except sqlite3.Error as exc:
            logger.debug("GraphProjectionBackend.get_reachability failed: %s", exc)
            return []

        result = []
        for row in rows:
            item = dict(row)
            item["derived_from"] = self._source_artifact_digest[:16]
            item["stale"] = self._stale
            result.append(item)
        return result

    # ------------------------------------------------------------------
    # Resource lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the SQLite connection and release the file handle."""
        if self._conn is not None:
            try:
                self._conn.close()
            except sqlite3.Error as exc:
                logger.debug("GraphProjectionBackend.close error: %s", exc)
            finally:
                self._conn = None
        self._available = False

    def __enter__(self) -> "GraphProjectionBackend":
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self.close()


# ------------------------------------------------------------------
# Module-level helper
# ------------------------------------------------------------------


def _resolve_adg_dir() -> Path:
    """Return the ADG artifacts directory, falling back gracefully if unavailable."""
    try:
        return get_adg_dir()
    except (RuntimeError, OSError):
        return Path("artifacts") / "adg"
