"""SQLite Backend — Canonical ADG source, mandatory, always available.

Provides query access to `adg_indexed_<ts>.sqlite` (canonical CI artifact).
Optionally wires a `GraphProjectionBackend` instance (Increment 3) to serve
pre-computed graph-native metrics from the derived `adg_graph_<ts>.sqlite`.
The graph store is non-critical: construction failure falls back to None and
all canonical query paths remain unaffected.
"""

import logging
import sqlite3
import threading
from pathlib import Path
from typing import Any

from urllib.parse import quote

from tqdm import tqdm

from tools.adg.core.graph_projection_backend import GraphProjectionBackend
from tools.adg.core.models import ADGEdge, ADGNode
from tools.adg.core.p0_wave_plan import build_p0_remediation_wave_plan
from tools.adg.shared_modules.path_resolver import get_adg_dir, latest_sqlite

logger = logging.getLogger(__name__)

# Query timeout in seconds
SQLITE_QUERY_TIMEOUT = 5.0
_MAX_QUERY_LIMIT = 1000
_MAX_TRAVERSAL_DEPTH = 10


class SQLiteBackend:
    """Canonical ADG backend using SQLite as source of truth.

    Enhanced with optional GraphProjectionBackend for graph-native operations.
    """

    _conn: sqlite3.Connection | None = None
    _sqlite_path: Path | None = None
    _last_mtime: float = 0.0
    _graph_store: Any = None  # Optional GraphProjectionBackend instance
    # Serializes connection lifecycle (connect / close / reopen / self-heal) and
    # any explicit multi-statement transaction. Per SQLite docs, an sqlite3
    # connection compiled with THREADSAFE=1 (CPython default) is internally
    # serialized for individual statements, so routine reads do NOT need this
    # lock. We take the lock only on lifecycle events and on the self-heal
    # retry path so a pathological reconnect cannot race with a concurrent
    # query from another FastMCP worker thread.
    # Ref: https://www.sqlite.org/threadsafe.html "Serialized" mode
    # Ref: https://ricardoanderegg.com/posts/python-sqlite-thread-safety/
    _lifecycle_lock: threading.RLock

    def __init__(self, use_graph_store: bool = True):
        self._connect()
        if use_graph_store:
            self._init_graph_store()

    @staticmethod
    def _normalize_limit(limit: int, default: int) -> int:
        """Clamp caller-provided LIMIT values to a safe positive range."""
        if limit <= 0:
            return default
        return min(limit, _MAX_QUERY_LIMIT)

    @staticmethod
    def _normalize_depth(max_depth: int) -> int:
        """Clamp traversal depth so callers cannot trigger unbounded graph walks."""
        if max_depth <= 0:
            return 1
        return min(max_depth, _MAX_TRAVERSAL_DEPTH)

    @staticmethod
    def _readonly_uri(path: Path) -> str:
        """Build a cross-platform SQLite URI that enforces read-only mode."""
        return f"file:{quote(str(path.resolve()))}?mode=ro"

    def _require_conn(self) -> sqlite3.Connection:
        """Return an open SQLite connection or raise a clear lifecycle error."""
        if self._conn is None:
            raise RuntimeError("SQLiteBackend connection is closed")
        return self._conn

    def _init_graph_store(self) -> None:
        """Initialize GraphProjectionBackend for graph-native operations.

        Discovers the latest adg_graph_<ts>.sqlite and wires it as the
        graph store. Falls back to None if the projection is absent or
        cannot be opened — all canonical query paths remain unaffected.
        """
        try:
            self._graph_store = GraphProjectionBackend(
                canonical_sqlite_path=self._sqlite_path,
            )
        except Exception as exc:  # guardian: allow-broad-exception -- GraphProjectionBackend init can fail for many environmental reasons (missing file, sqlite error, bad schema); all are non-fatal and must not block SQLiteBackend construction
            logger.debug("GraphProjectionBackend initialization failed: %s", exc)
            self._graph_store = None

    def _connect(self) -> None:
        """Establish read-only connection to latest SQLite file."""
        sqlite_file = latest_sqlite()
        if sqlite_file is None:
            raise RuntimeError("No ADG SQLite file found")

        self._sqlite_path = sqlite_file
        self._last_mtime = self._sqlite_path.stat().st_mtime
        self._conn = sqlite3.connect(
            self._readonly_uri(self._sqlite_path),
            timeout=SQLITE_QUERY_TIMEOUT,
            uri=True,
            # check_same_thread=False is safe here because the connection is
            # opened mode=ro with PRAGMA query_only=ON (set below). Required
            # because adg_reopen_connections() currently creates the connection
            # on a ThreadPoolExecutor worker (runtime.py reopen_connections W1.2
            # bounded-timeout wrapper) while subsequent query handlers run on
            # the FastMCP event-loop thread — without this flag, every query
            # after a reopen() raises "SQLite objects created in a thread can
            # only be used in that same thread" and the server goes dark until
            # full restart. See RCA 2026-04-24 (plan
            # mcp-destructive-gate-preflight-e9a14b deferred-scope item,
            # Notion ADR + W1-P1 row).
            check_same_thread=False,
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(f"PRAGMA busy_timeout = {int(SQLITE_QUERY_TIMEOUT * 1000)}")
        self._conn.execute("PRAGMA query_only = ON")

    def health(self) -> tuple[str, dict[str, Any]]:
        """Return health status and metadata."""
        if not self._sqlite_path or not self._sqlite_path.exists():
            return "unavailable", {}

        current_mtime = self._sqlite_path.stat().st_mtime
        is_fresh = current_mtime == self._last_mtime

        # Check if current snapshot is stale (newer file exists)
        latest_path = latest_sqlite()
        is_stale = latest_path is not None and latest_path != self._sqlite_path

        return "healthy", {
            "path": str(self._sqlite_path),
            "mtime": current_mtime,
            "is_fresh": is_fresh,
            "is_stale": is_stale,
            "latest_path": str(latest_path) if latest_path else None,
        }

    @staticmethod
    def _row_to_edge(row) -> ADGEdge:
        """Convert a SQLite row to ADGEdge, coercing ids to str."""
        data = dict(row)
        for key in ("id", "src_id", "dst_id"):
            if key in data and data[key] is not None:
                data[key] = str(data[key])
        return ADGEdge(**data)

    @staticmethod
    def _row_to_node(row) -> ADGNode:
        """Convert a SQLite row to ADGNode, coercing id to str."""
        data = dict(row)
        data["id"] = str(data["id"])
        return ADGNode(**data)

    def get_node(self, node_id: str) -> ADGNode | None:
        """Fetch node by ID from SQLite."""
        conn = self._require_conn()
        cur = conn.execute(
            "SELECT * FROM nodes WHERE id = ?",
            (node_id,),
        )
        row = cur.fetchone()
        if row:
            return self._row_to_node(row)
        return None

    def get_nodes_by_layer(self, layer: str, limit: int = 100) -> list[ADGNode]:
        """Fetch nodes by layer."""
        conn = self._require_conn()
        safe_limit = self._normalize_limit(limit, default=100)
        cur = conn.execute(
            "SELECT * FROM nodes WHERE layer = ? LIMIT ?",
            (layer, safe_limit),
        )
        return [self._row_to_node(row) for row in cur.fetchall()]

    def get_nodes_by_file(self, file_path: str, limit: int = 100) -> list[ADGNode]:
        """Fetch nodes by file path.

        Tries exact match first (index-friendly), then suffix LIKE match as fallback.
        The leading-wildcard LIKE used previously caused full-table scans and false matches.
        """
        conn = self._require_conn()
        safe_limit = self._normalize_limit(limit, default=100)

        # 1. Exact match — uses idx_nodes_resolved_path if present
        cur = conn.execute(
            "SELECT * FROM nodes WHERE resolved_path = ? LIMIT ?",
            (file_path, safe_limit),
        )
        rows = cur.fetchall()
        if rows:
            return [self._row_to_node(r) for r in rows]

        # 2. Suffix LIKE fallback — still scans, but only after exact-match miss.
        cur = conn.execute(
            "SELECT * FROM nodes WHERE resolved_path LIKE ? LIMIT ?",
            (f"%{file_path}", safe_limit),
        )
        return [self._row_to_node(r) for r in cur.fetchall()]

    def find_node(self, name: str, limit: int = 10) -> list[ADGNode]:
        """Find nodes by exact adg_name or adg_name prefix match.

        Enables human-readable name resolution without knowing the integer node ID.
        Returns exact matches first, then prefix matches if no exact hit.
        """
        conn = self._require_conn()
        safe_limit = self._normalize_limit(limit, default=10)

        # 1. Exact adg_name match
        cur = conn.execute(
            "SELECT * FROM nodes WHERE adg_name = ? LIMIT ?",
            (name, safe_limit),
        )
        rows = cur.fetchall()
        if rows:
            return [self._row_to_node(r) for r in rows]

        # 2. Prefix match on adg_name
        cur = conn.execute(
            "SELECT * FROM nodes WHERE adg_name LIKE ? LIMIT ?",
            (f"{name}%", safe_limit),
        )
        return [self._row_to_node(r) for r in cur.fetchall()]

    def get_edge_fanout(self, src_id: str, relation_type: str, limit: int = 30) -> list[ADGEdge]:
        """Fetch outgoing edges."""
        conn = self._require_conn()
        safe_limit = self._normalize_limit(limit, default=30)
        cur = conn.execute(
            """SELECT id, src_id, dst_id, relation_type, edge_kind,
                      source_file, line_no, symbol
               FROM edges WHERE src_id = ? AND relation_type = ? LIMIT ?""",
            (src_id, relation_type, safe_limit),
        )
        return [self._row_to_edge(row) for row in cur.fetchall()]

    def get_edge_fanin(self, tgt_id: str, relation_type: str, limit: int = 30) -> list[ADGEdge]:
        """Fetch incoming edges."""
        conn = self._require_conn()
        safe_limit = self._normalize_limit(limit, default=30)
        cur = conn.execute(
            """SELECT id, src_id, dst_id, relation_type, edge_kind,
                      source_file, line_no, symbol
               FROM edges WHERE dst_id = ? AND relation_type = ? LIMIT ?""",
            (tgt_id, relation_type, safe_limit),
        )
        return [self._row_to_edge(row) for row in cur.fetchall()]

    def get_status(self) -> dict[str, Any]:
        """Get ADG snapshot status."""
        conn = self._require_conn()
        if self._sqlite_path is None:
            raise RuntimeError("SQLiteBackend path is unavailable")

        nodes = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
        edges = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]

        return {
            "timestamp": self._sqlite_path.stem.replace("adg_indexed_", ""),
            "node_count": nodes,
            "edge_count": edges,
            "sqlite_path": str(self._sqlite_path),
        }

    def get_violations(self, limit: int = 100) -> list[dict[str, Any]]:
        """Fetch anti-pattern violations."""
        conn = self._require_conn()
        safe_limit = self._normalize_limit(limit, default=100)
        try:
            cur = conn.execute(
                # Include both relation types: 'violates' (layer boundary breaks) and
                # 'antipattern' (code-level anti-pattern instances, ~8800 rows in practice).
                """SELECT id, source_file, relation_type, symbol, line_no
                   FROM edges WHERE relation_type IN ('violates', 'antipattern') LIMIT ?""",
                (safe_limit,),
            )
            return [dict(row) for row in cur.fetchall()]
        except sqlite3.Error as exc:
            # Table or column may not exist
            logger.debug("get_violations query failed: %s", exc)
            return []

    def close(self) -> None:
        """Close SQLite connection and release file handles."""
        if self._conn:
            try:
                self._conn.close()
                logger.info("Closed SQLite connection to %s", self._sqlite_path)
            except Exception as exc:  # guardian: allow-log-and-swallow -- teardown/cleanup context -- swallow is conventional in resource-release paths
                logger.error("Error closing SQLite connection: %s", exc)
            finally:
                self._conn = None

        graph_store = self._graph_store
        if graph_store is not None and hasattr(graph_store, "close"):
            try:
                graph_store.close()
            except Exception as exc:  # guardian: allow-broad-exception -- optional graph store teardown must not block backend shutdown
                logger.debug("Error closing graph projection backend: %s", exc)
        self._graph_store = None

    def reopen(self) -> None:
        """Reopen SQLite connection after closing to refresh/release locks lifecycle."""
        self.close()
        self._connect()
        self._init_graph_store()
        logger.info("Reopened SQLite connection to %s", self._sqlite_path)

    # Graph-native methods that delegate to GraphProjectionBackend when available

    def get_centrality(self, node_id: str) -> float:
        """Get centrality score for a node using graph store if available.

        When GraphProjectionBackend is active, returns blast_radius_direct as
        the scalar centrality proxy (fan-in count, closest to the SQL fallback
        which counts total edges touching the node). Returns a float in all cases.
        """
        if self._graph_store:
            proj = self._graph_store.get_centrality(node_id)
            if isinstance(proj, dict):
                return float(proj.get("blast_radius_direct", 0))
            if isinstance(proj, (int, float)):
                return float(proj)

        conn = self._require_conn()
        # Fallback: degree centrality from direct edge count
        cur = conn.execute(
            "SELECT COUNT(*) FROM edges WHERE src_id = ? OR dst_id = ?",
            (node_id, node_id),
        )
        return float(cur.fetchone()[0])

    def get_projection_status(self) -> dict[str, Any]:
        """Return graph projection availability, staleness, and metadata.

        Always returns a dict — never raises. Returns available=False if the
        projection backend is not wired or is unavailable.
        """
        if self._graph_store:
            return self._graph_store.get_status()
        return {
            "available": False,
            "stale": False,
            "projection_path": None,
            "source_artifact_digest": "",
            "proj_schema_version": "",
            "node_count": 0,
        }

    def get_blast_radius(self, node_id: str, hops: int = 2) -> dict[str, Any]:
        """Return blast-radius summary from the graph projection for a node.

        Delegates to GraphProjectionBackend.get_blast_radius(). Always returns
        a dict — empty counts when projection is unavailable.
        """
        if self._graph_store:
            return self._graph_store.get_blast_radius(node_id, hops=hops)
        return {
            "adg_name": node_id,
            "blast_radius_direct": 0,
            "blast_radius_2hop": 0,
            "reachability_rows": 0,
            "hops_requested": hops,
            "derived_from": "",
            "stale": False,
            "available": False,
        }

    def get_scc(self, node_id: str) -> dict[str, Any] | None:
        """Return SCC membership for a node from the graph projection.

        Returns None if projection unavailable or node is in a trivial SCC.
        """
        if self._graph_store:
            return self._graph_store.get_scc(node_id)
        return None

    def get_violations_with_impact(
        self,
        layer: str | None = None,
        severity: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Return violations with blast-radius impact from the graph projection.

        Delegates to GraphProjectionBackend.get_violations_with_impact().
        Returns [] if projection is unavailable.
        """
        if self._graph_store:
            return self._graph_store.get_violations_with_impact(layer=layer, severity=severity, limit=limit)
        return []

    def get_p0_remediation_wave_plan(self, limit: int = 100) -> dict[str, Any]:
        """Return a wave-based P0 remediation plan from the canonical SQLite snapshot."""
        if self._sqlite_path is None:
            raise RuntimeError("No ADG SQLite snapshot available for P0 remediation planning")
        safe_limit = self._normalize_limit(limit, default=100)
        return build_p0_remediation_wave_plan(self._sqlite_path, limit=safe_limit)

    def get_diff(
        self,
        metric: str | None = None,
        direction: str | None = None,
        layer: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Return cross-run metric deltas from the graph projection.

        Delegates to GraphProjectionBackend.get_diff(). Returns [] if unavailable.
        """
        if self._graph_store:
            return self._graph_store.get_diff(metric=metric, direction=direction, layer=layer, limit=limit)
        return []

    def get_top_bridges(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return top bridge/chokepoint nodes by bridge_score from the projection.

        Returns [] if projection is unavailable.
        """
        if self._graph_store:
            return self._graph_store.get_top_bridges(limit=limit)
        return []

    def get_top_regressions(
        self,
        metric: str = "blast_radius_direct",
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Return top metric regressions (largest increases) from the projection.

        Returns [] if projection is unavailable.
        """
        if self._graph_store:
            return self._graph_store.get_top_regressions(metric=metric, limit=limit)
        return []

    def get_reachability(self, src_adg_name: str, limit: int = 50) -> list[dict[str, Any]]:
        """Return proj_reachability rows for a seed module from the projection.

        Returns [] if projection is unavailable or node is not a seed.
        """
        if self._graph_store:
            return self._graph_store.get_reachability(src_adg_name, limit=limit)
        return []

    def traverse(self, start_id: str, max_depth: int = 2, relation_types: list[str] | None = None) -> list:
        """Traverse graph from start node using graph store if available."""
        if self._graph_store and hasattr(self._graph_store, "traverse"):
            return self._graph_store.traverse(start_id, max_depth, relation_types)
        # Fallback: simple BFS using SQL
        return self._traverse_sql(start_id, max_depth, relation_types)

    def _traverse_sql(self, start_id: str, max_depth: int, relation_types: list[str] | None) -> list:
        """Fallback SQL-based traversal when graph store unavailable."""
        conn = self._require_conn()
        safe_depth = self._normalize_depth(max_depth)
        paths = []
        visited = {start_id}
        current_level = [(start_id, [])]  # (node_id, path)

        for depth in tqdm(range(safe_depth), desc="traverse-depth", leave=False, disable=True):
            next_level = []
            for node_id, path in tqdm(current_level, desc="traverse-level", leave=False, disable=True):
                # Get neighbors
                query = "SELECT dst_id FROM edges WHERE src_id = ?"
                params: list[Any] = [node_id]
                if relation_types:
                    placeholders = ",".join(["?" for _ in relation_types])
                    query += f" AND relation_type IN ({placeholders})"
                    params.extend(relation_types)

                cur = conn.execute(query, params)
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
