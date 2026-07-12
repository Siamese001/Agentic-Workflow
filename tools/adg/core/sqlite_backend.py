"""SQLite Backend — Canonical ADG source, mandatory, always available.

Provides query access to `adg_indexed_<ts>.sqlite` (canonical CI artifact).
Optionally wires a `GraphProjectionBackend` instance (Increment 3) to serve
pre-computed graph-native metrics from the derived `adg_graph_<ts>.sqlite`.
The graph store is non-critical: construction failure falls back to None and
all canonical query paths remain unaffected.
"""

# W6 ADG consumer mode declaration (per .codex/rules/adg-canonical-invariants.md §6 + agentic_core/adg/artifact/consumer_mode.py).
__adg_consumer_mode__ = "inventory"


import logging
import re
import sqlite3
import threading
from pathlib import Path
from typing import Any

from urllib.parse import quote

from tqdm import tqdm

from tools.adg.core.graph_projection_backend import GraphProjectionBackend
from tools.adg.core.models import ADGEdge, ADGNode
from tools.adg.core.p0_wave_plan import build_p0_remediation_wave_plan
from tools.adg.shared_modules.path_resolver import (
    SnapshotResolution,
    get_adg_dir,
    resolve_snapshot,
)
from tools.adg.shared_modules.snapshot_registry import SnapshotPointerError

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

    def __init__(
        self,
        use_graph_store: bool = True,
        *,
        snapshot_selection: str = "latest",
        allow_unavailable: bool = False,
        verify_pointer_digest: bool = True,
    ):
        """Open an explicitly selected ADG snapshot role.

        Direct callers retain the historical latest default. MCP passes
        certified and allow_unavailable=True so missing certification becomes
        structured health instead of a repair-candidate fallback.
        """
        if snapshot_selection not in {
            "latest",
            "certified",
            "repair",
            "candidate",
        }:
            raise ValueError(
                f"unsupported ADG snapshot selection: {snapshot_selection!r}"
            )
        self._lifecycle_lock = threading.RLock()
        self._conn = None
        self._sqlite_path = None
        self._last_mtime = 0.0
        self._graph_store = None
        self._snapshot_selection = snapshot_selection
        self._allow_unavailable = allow_unavailable
        self._verify_pointer_digest = verify_pointer_digest
        self._snapshot_resolution: SnapshotResolution | None = None
        self._selection_error: str | None = None
        with self._lifecycle_lock:
            self._connect()
            if use_graph_store and self._sqlite_path is not None:
                self._init_graph_store()

    @property
    def snapshot_selection(self) -> str:
        return self._snapshot_selection

    def selected_snapshot_path(self) -> Path | None:
        """Resolve the configured role without cross-role fallback."""
        resolved = resolve_snapshot(
            selection=self._snapshot_selection,
            require_nodes_table=True,
            verify_digest=False,
            strict=False,
        )
        return resolved.path if resolved else None

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
        """Return an open SQLite connection, self-healing on thread-confinement
        errors inherited from a prior reopen() that ran on a different thread.

        Defensive layer for the "SQLite objects created in a thread can only
        be used in that same thread" ProgrammingError. With
        ``check_same_thread=False`` in `_connect()` this error is no longer
        raised by the sqlite3 module itself, but we still guard here because
        (1) older snapshots of this process may hold a pre-fix connection, and
        (2) a future change to a write connection (check_same_thread=True) or
        a different thread-safety level would re-open the failure mode.

        Recovery: ping the connection with a trivial SELECT; on ProgrammingError
        release the lifecycle lock re-entrantly to run reopen() from the
        current thread, then retry the ping once. If that also fails, surface
        the original error — something is structurally wrong (missing file,
        schema corruption) and the caller should see it.
        """
        with self._lifecycle_lock:
            if self._conn is None or self._sqlite_path is None:
                raise RuntimeError(
                    "ADG query unavailable: "
                    + (
                        self._selection_error
                        or f"no {self._snapshot_selection} snapshot"
                    )
                )
            try:
                current_mtime = self._sqlite_path.stat().st_mtime
            except OSError as exc:
                raise RuntimeError("active ADG snapshot disappeared") from exc
            if current_mtime != self._last_mtime:
                raise RuntimeError(
                    "active ADG snapshot changed after selection; reopen required"
                )
            try:
                # Cheap liveness probe — costs one function call and no I/O
                # against the cached sqlite page cache. Detects thread pinning
                # and any other connection-level sickness without a full query.
                self._conn.execute("SELECT 1").fetchone()
                return self._conn
            except sqlite3.ProgrammingError as exc:
                if "thread" not in str(exc).lower():
                    # Some other programming error (e.g., connection closed
                    # mid-query) — not our concern, surface to caller.
                    raise
                logger.warning(
                    "SQLite connection self-heal triggered: %s. Reopening on current thread (tid=%s).",
                    exc,
                    threading.get_ident(),
                )
                # RLock re-entrancy: reopen() re-takes the same lock on the
                # same thread, safe.
                self.reopen()
                if self._conn is None:
                    raise RuntimeError(
                        "SQLiteBackend connection self-heal failed: connection is still None after reopen()"
                    ) from exc
                # One more probe. If it fails, let the caller see it.
                self._conn.execute("SELECT 1").fetchone()
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
        """Establish a read-only connection to the configured snapshot role."""
        try:
            resolved = resolve_snapshot(
                selection=self._snapshot_selection,
                require_nodes_table=True,
                verify_digest=(
                    self._verify_pointer_digest
                    and self._snapshot_selection != "latest"
                ),
                strict=self._snapshot_selection != "latest",
            )
        except SnapshotPointerError as exc:
            resolved = None
            self._selection_error = str(exc)

        if resolved is None:
            self._conn = None
            self._sqlite_path = None
            self._snapshot_resolution = None
            message = self._selection_error or (
                f"No {self._snapshot_selection} ADG snapshot under "
                f"{get_adg_dir()}"
            )
            if self._allow_unavailable:
                return
            raise RuntimeError(message)

        self._snapshot_resolution = resolved
        self._selection_error = None
        self._sqlite_path = resolved.path
        self._last_mtime = resolved.path.stat().st_mtime
        self._conn = sqlite3.connect(
            self._readonly_uri(resolved.path),
            timeout=SQLITE_QUERY_TIMEOUT,
            uri=True,
            check_same_thread=False,
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(
            f"PRAGMA busy_timeout = {int(SQLITE_QUERY_TIMEOUT * 1000)}"
        )
        self._conn.execute("PRAGMA query_only = ON")

    def health(self) -> tuple[str, dict[str, Any]]:
        """Return selection-aware health and materialization provenance."""
        if (
            self._conn is None
            or self._sqlite_path is None
            or not self._sqlite_path.exists()
        ):
            return "unavailable", {
                "snapshot_selection": self._snapshot_selection,
                "selection_error": self._selection_error,
                "materialization": self.get_materialization_status(),
            }

        current_mtime = self._sqlite_path.stat().st_mtime
        is_fresh = current_mtime == self._last_mtime
        selected_path = self.selected_snapshot_path()
        is_stale = selected_path is None or selected_path != self._sqlite_path
        resolution = self._snapshot_resolution
        certified = bool(
            self._snapshot_selection == "certified"
            and resolution is not None
            and resolution.certification_status == "clean"
            and resolution.artifact_status == "certified"
        )
        health_status = (
            "healthy"
            if is_fresh and not is_stale and certified
            else "degraded"
        )
        return health_status, {
            "path": str(self._sqlite_path),
            "mtime": current_mtime,
            "is_fresh": is_fresh,
            "is_stale": is_stale,
            "selected_path": str(selected_path) if selected_path else None,
            "snapshot_selection": self._snapshot_selection,
            "certified": certified,
            "materialization": self.get_materialization_status(),
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

    def _meta_value(self, key: str) -> str | None:
        if self._conn is None:
            return None
        try:
            row = self._require_conn().execute(
                "SELECT value FROM meta WHERE key = ?",
                (key,),
            ).fetchone()
        except (RuntimeError, sqlite3.Error):
            return None
        return str(row[0]) if row and row[0] is not None else None

    def get_status(self) -> dict[str, Any]:
        """Return snapshot status without converting unavailability to zero."""
        if self._conn is None or self._sqlite_path is None:
            return {
                "available": False,
                "timestamp": None,
                "node_count": None,
                "edge_count": None,
                "sqlite_path": None,
                "schema_version": "unknown",
                "artifact_digest": None,
                "snapshot_selection": self._snapshot_selection,
                "certification_status": "unknown",
                "artifact_status": "unknown",
                "certified": False,
                "pointer_path": None,
                "digest_verified": False,
                "selection_error": self._selection_error,
            }

        conn = self._require_conn()
        resolution = self._snapshot_resolution
        certification_status = (
            resolution.certification_status if resolution else "unknown"
        )
        artifact_status = (
            resolution.artifact_status if resolution else "unknown"
        )
        certified = bool(
            self._snapshot_selection == "certified"
            and certification_status == "clean"
            and artifact_status == "certified"
        )
        return {
            "available": True,
            "timestamp": self._sqlite_path.stem.replace(
                "adg_indexed_",
                "",
            ),
            "node_count": conn.execute(
                "SELECT COUNT(*) FROM nodes"
            ).fetchone()[0],
            "edge_count": conn.execute(
                "SELECT COUNT(*) FROM edges"
            ).fetchone()[0],
            "sqlite_path": str(self._sqlite_path),
            "schema_version": self._meta_value("schema_version") or "unknown",
            "artifact_digest": self._meta_value("artifact_digest"),
            "snapshot_selection": self._snapshot_selection,
            "certification_status": certification_status,
            "artifact_status": artifact_status,
            "certified": certified,
            "pointer_path": (
                str(resolution.pointer_path)
                if resolution and resolution.pointer_path
                else None
            ),
            "digest_verified": bool(
                resolution and resolution.digest_verified
            ),
            "selection_error": None,
        }

    def get_materialization_status(self) -> dict[str, Any]:
        """Evaluate the required materialization families fail closed."""
        thresholds = {"mv": 30, "pview": 3, "infra": 1}
        try:
            rows = self._require_conn().execute(
                "SELECT name FROM sqlite_master "
                "WHERE type IN ('table','view') "
                "AND name NOT LIKE 'sqlite_%'"
            ).fetchall()
        except (RuntimeError, sqlite3.Error) as exc:
            return {
                "status": "UNKNOWN",
                "counts": {},
                "thresholds": thresholds,
                "reasons": [str(exc)],
            }

        names = [str(row[0]) for row in rows]
        counts = {
            "mv": sum(name.startswith("mv_") for name in names),
            "pview": sum(name.startswith("v_p") for name in names),
            "infra": sum(
                (
                    "infra" in name.lower()
                    or "wiring" in name.lower()
                )
                and not name.startswith("mv_")
                for name in names
            ),
        }
        reasons = [
            f"{key} count {counts[key]} < {minimum}"
            for key, minimum in thresholds.items()
            if counts[key] < minimum
        ]
        return {
            "status": "FAIL" if reasons else "PASS",
            "counts": counts,
            "thresholds": thresholds,
            "reasons": reasons,
        }

    def get_views_materialized_at(self) -> str | None:
        """Return timestamp only when the full materialization contract passes."""
        materialization = self.get_materialization_status()
        if (
            materialization["status"] == "PASS"
            and self._sqlite_path is not None
        ):
            return self._sqlite_path.stem.replace("adg_indexed_", "")
        return None

    # -----------------------------------------------------------------
    # W3 P3.3 — graph-layer primitives (mv_*, P-views) for §22 consumers
    # -----------------------------------------------------------------

    # Whitelist of canonical semantic relation types (per
    # `.codex/rules/adg-canonical-invariants.md` §3 + ADR-074). Values
    # outside this set are rejected with ValueError so callers cannot
    # smuggle arbitrary relation_type strings into the graph-layer surface.
    SEMANTIC_RELATION_TYPES: tuple[str, ...] = (
        "flows_to",
        "writes_to",
        "reads_from",
        "emits_side_effect",
        "controls_flow",
        "resolves_callsite",
    )

    # Whitelist pattern for P-view names. P-views follow the
    # `v_p<N>_<word>` shape (N ∈ {0,1,2,3}). Any name outside this pattern
    # is rejected to prevent SQL injection via view_name parameter.
    _P_VIEW_NAME_RE = re.compile(r"^v_p[0-3]_[a-z0-9_]+$")

    def get_mv_hotspot_centrality(self, limit: int = 50) -> list[dict[str, Any]]:
        """Top-N rows from ``mv_hotspot_centrality`` ordered by degree centrality.

        Returns rows with columns: snapshot_id, node_id, adg_name, layer,
        resolved_path, fan_in, fan_out, degree, betweenness_approx,
        degree_centrality. Ordered DESC by degree_centrality so the most
        structurally central nodes come first.
        """
        conn = self._require_conn()
        safe_limit = self._normalize_limit(limit, default=50)
        try:
            cur = conn.execute(
                "SELECT * FROM mv_hotspot_centrality "
                "ORDER BY degree_centrality DESC, fan_in DESC LIMIT ?",
                (safe_limit,),
            )
            return [dict(r) for r in cur.fetchall()]
        except sqlite3.OperationalError as exc:
            logger.warning("mv_hotspot_centrality unavailable: %s", exc)
            return []

    def hydrate_mv_hotspot_centrality_ordered(
        self, ordered_node_ids: list[str]
    ) -> list[dict[str, Any]] | None:
        """Return ``mv_hotspot_centrality`` rows for Redis-ranked ``node_id`` strings.

        Preserves Redis ZSET ordering. Returns ``None`` when the MV is missing or
        any ``node_id`` is absent — callers must fall back to a canonical
        SQLite ``ORDER BY`` query because SQLite remains authoritative on row
        material.
        """
        if not ordered_node_ids:
            return []
        conn = self._require_conn()
        try:
            placeholders = ",".join("?" * len(ordered_node_ids))
            cur = conn.execute(
                f"SELECT * FROM mv_hotspot_centrality WHERE node_id IN ({placeholders})",
                ordered_node_ids,
            )
            fetched = [dict(r) for r in cur.fetchall()]
        except sqlite3.OperationalError as exc:
            logger.warning("mv_hotspot_centrality hydrate unavailable: %s", exc)
            return None

        by_nid: dict[str, dict[str, Any]] = {}
        for row in fetched:
            key = str(row["node_id"])
            if key in by_nid:
                return None  # ambiguous duplicate MV rows — treat as mismatch
            by_nid[key] = row

        out: list[dict[str, Any]] = []
        for nid in ordered_node_ids:
            row = by_nid.get(str(nid))
            if row is None:
                return None
            out.append(row)
        return out

    def list_p_views(self) -> list[str]:
        """Return all P-view names present in the snapshot, sorted."""
        conn = self._require_conn()
        cur = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='view' AND name LIKE 'v_p%' ORDER BY name"
        )
        return [r[0] for r in cur.fetchall()]

    def query_p_view(self, view_name: str, limit: int = 100) -> list[dict[str, Any]]:
        """Return up to ``limit`` rows from a P-view.

        ``view_name`` MUST match the canonical P-view pattern
        (``v_p[0-3]_<word>``) and MUST exist in ``sqlite_master``.
        Both checks raise ``ValueError`` to prevent SQL injection through
        the view_name parameter — the SELECT below uses string substitution,
        which is unavoidable for table/view names but safe given the
        whitelist + existence check.
        """
        if not isinstance(view_name, str) or not self._P_VIEW_NAME_RE.match(view_name):
            raise ValueError(
                f"view_name must match v_p[0-3]_<word> pattern; got {view_name!r}"
            )
        safe_limit = self._normalize_limit(limit, default=100)
        conn = self._require_conn()
        # Existence check via parameterized sqlite_master query (no injection).
        exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='view' AND name = ?",
            (view_name,),
        ).fetchone()
        if exists is None:
            raise ValueError(f"P-view {view_name!r} does not exist in snapshot")
        # Safe to interpolate now: name passed both regex + existence check.
        cur = conn.execute(f"SELECT * FROM {view_name} LIMIT ?", (safe_limit,))
        return [dict(r) for r in cur.fetchall()]

    # -----------------------------------------------------------------

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
        """Close SQLite connection and release file handles.

        Serialized via ``_lifecycle_lock`` so a concurrent query from another
        FastMCP worker thread cannot observe a torn-down connection.
        """
        with self._lifecycle_lock:
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
        """Reopen SQLite connection after closing to refresh/release locks lifecycle.

        Serialized via ``_lifecycle_lock``. The new connection is created on
        whichever thread calls reopen() — with ``check_same_thread=False`` in
        `_connect`, it is safe to use from any subsequent caller thread.
        """
        with self._lifecycle_lock:
            self.close()
            self._connect()
            if self._sqlite_path is not None:
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
