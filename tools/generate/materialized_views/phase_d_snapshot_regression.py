"""Phase D materialized views — Snapshot baseline anchor and historical regression diffs.

Covers view family 11:
    mv_snapshot_baseline            (anchor — written FIRST, one row per snapshot)
    mv_snapshot_regression_summary  (aggregate delta vs previous baseline)
    mv_newly_introduced_critical_paths
    mv_new_cross_layer_dependencies
    mv_new_provider_surfaces
    mv_new_write_bypass_paths

First-run behaviour: baseline is written from current state; all delta tables show
is_new=1 for every row (no previous baseline to compare against). This is correct
and expected — the second run produces the first meaningful diffs.

Depends on Phase A: mv_path_criticality_rollup, mv_hotspot_centrality
Depends on Phase B: mv_gateway_bypass_paths, mv_write_sovereignty_paths (via Phase A)
Depends on Phase C: mv_debt_concentration_hotspots
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from tools.generate.materialized_views.sqlite_helpers import connect_sqlite_for_mv as _connect_sqlite

_BASELINE_COLS: tuple[str, ...] = (
    "snapshot_id",
    "node_count",
    "edge_count",
    "violation_count",
    "cross_layer_edge_count",
    "provider_surface_count",
    "write_bypass_count",
    "debt_score",
)


def _baseline_row_to_dict(row: tuple[Any, ...]) -> dict[str, Any]:
    return dict(zip(_BASELINE_COLS, row, strict=True))


def _load_prior_snapshot_baseline(current_sqlite: Path) -> dict[str, Any]:
    """Load baseline from the newest prior ``adg_indexed_*.sqlite`` on disk.

    Each ADG run builds a fresh indexed sqlite, so in-file ``mv_snapshot_baseline``
    is empty on first materialization. Cross-run regression must read the previous
    committed snapshot's baseline row instead of treating every run as first-run.
    """
    adg_dir = current_sqlite.parent
    if not adg_dir.is_dir():
        return {}
    candidates = sorted(
        (
            p
            for p in adg_dir.glob("adg_indexed_*.sqlite")
            if p.resolve() != current_sqlite.resolve() and "smoketest" not in p.name
        ),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for prior in candidates:
        try:
            with sqlite3.connect(prior) as prior_conn:
                row = prior_conn.execute(
                    "SELECT snapshot_id, node_count, edge_count, violation_count, "
                    "cross_layer_edge_count, provider_surface_count, "
                    "write_bypass_count, debt_score "
                    "FROM mv_snapshot_baseline LIMIT 1",
                ).fetchone()
        except sqlite3.OperationalError:
            continue
        if row and str(row[0] or "").strip():
            return _baseline_row_to_dict(row)
    return {}


_PHASE_D_TABLES: tuple[str, ...] = (
    "mv_snapshot_baseline",
    "mv_snapshot_regression_summary",
    "mv_newly_introduced_critical_paths",
    "mv_new_cross_layer_dependencies",
    "mv_new_provider_surfaces",
    "mv_new_write_bypass_paths",
)


def _snapshot_id_expr() -> str:
    return "(SELECT COALESCE(value, '') FROM meta WHERE key='commit_sha' LIMIT 1)"


def materialize_phase_d(sqlite_path: Path) -> dict[str, int]:
    """Create all Phase D materialized tables. Idempotent — safe to call repeatedly.

    mv_snapshot_baseline is refreshed last-in / first-written: the OLD baseline row is
    read for delta computation, then replaced with the current snapshot values.

    Returns:
        dict mapping table_name -> row_count for each Phase D table.
    """
    conn = _connect_sqlite(sqlite_path)
    cur = conn.cursor()

    # -------------------------------------------------------------------------
    # Read previous baseline BEFORE dropping (needed for delta computation)
    # -------------------------------------------------------------------------
    _prev: dict[str, Any] = {}
    try:
        row = cur.execute(
            "SELECT snapshot_id, node_count, edge_count, violation_count, "
            "       cross_layer_edge_count, provider_surface_count, "
            "       write_bypass_count, debt_score "
            "FROM mv_snapshot_baseline LIMIT 1"
        ).fetchone()
        if row and str(row[0] or "").strip():
            _prev = _baseline_row_to_dict(row)
    except sqlite3.OperationalError:
        pass  # Table doesn't exist yet — first run.
    if not _prev:
        _prev = _load_prior_snapshot_baseline(sqlite_path)

    for tbl in reversed(_PHASE_D_TABLES):
        cur.execute(f"DROP TABLE IF EXISTS {tbl}")

    # -------------------------------------------------------------------------
    # mv_snapshot_baseline — anchor row for the CURRENT snapshot
    # -------------------------------------------------------------------------
    cur.execute("""
        CREATE TABLE mv_snapshot_baseline (
            snapshot_id            TEXT NOT NULL,
            node_count             INTEGER NOT NULL,
            edge_count             INTEGER NOT NULL,
            violation_count        INTEGER NOT NULL,
            cross_layer_edge_count INTEGER NOT NULL,
            provider_surface_count INTEGER NOT NULL,
            write_bypass_count     INTEGER NOT NULL,
            debt_score             REAL NOT NULL
        )
    """)

    cross_layer_count = cur.execute("""
        SELECT COUNT(*) FROM edges e
        JOIN nodes src ON src.id = e.src_id
        JOIN nodes dst ON dst.id = e.dst_id
        WHERE src.layer != dst.layer
          AND e.relation_type IN ('imports', 'calls')
          AND src.layer IS NOT NULL AND src.layer != ''
          AND dst.layer IS NOT NULL AND dst.layer != ''
    """).fetchone()[0]

    provider_count = cur.execute("""
        SELECT COUNT(DISTINCT e.id) FROM edges e
        WHERE e.relation_type = 'invokes_provider'
    """).fetchone()[0]

    # Write bypass count: check if mv_write_sovereignty_paths exists; fall back to raw count.
    try:
        bypass_count = cur.execute(
            "SELECT COUNT(*) FROM mv_write_sovereignty_paths WHERE is_uwg_routed = 0"
        ).fetchone()[0]
    except sqlite3.OperationalError:
        bypass_count = 0

    # Debt score: check if mv_debt_concentration_hotspots exists; fall back to violations count.
    try:
        debt_row = cur.execute(
            "SELECT COALESCE(SUM(total_debt_score), 0) FROM mv_debt_concentration_hotspots"
        ).fetchone()
        debt_score = debt_row[0] if debt_row else 0.0
    except sqlite3.OperationalError:
        debt_score = float(cur.execute("SELECT COUNT(*) FROM violations").fetchone()[0])

    node_count = cur.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    edge_count = cur.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
    violation_count = cur.execute("SELECT COUNT(*) FROM violations").fetchone()[0]

    cur.execute(
        "INSERT INTO mv_snapshot_baseline VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            cur.execute("SELECT COALESCE(value, '') FROM meta WHERE key='commit_sha' LIMIT 1").fetchone()[0]
            or "",
            node_count,
            edge_count,
            violation_count,
            cross_layer_count,
            provider_count,
            bypass_count,
            float(debt_score),
        ),
    )

    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_baseline_snap ON mv_snapshot_baseline(snapshot_id)")

    # -------------------------------------------------------------------------
    # mv_snapshot_regression_summary
    # -------------------------------------------------------------------------
    def _gi(key: str, default: int) -> int:
        v = _prev.get(key)
        return int(v) if v is not None else default  # type: ignore[arg-type]

    def _gf(key: str, default: float) -> float:
        v = _prev.get(key)
        return float(v) if v is not None else default  # type: ignore[arg-type]

    prev_snap_id = str(_prev.get("snapshot_id") or "")
    prev_nodes = _gi("node_count", node_count)
    prev_edges = _gi("edge_count", edge_count)
    prev_violations = _gi("violation_count", violation_count)
    prev_cross = _gi("cross_layer_edge_count", cross_layer_count)
    prev_providers = _gi("provider_surface_count", provider_count)
    prev_bypass = _gi("write_bypass_count", bypass_count)
    prev_debt = _gf("debt_score", float(debt_score))

    is_first_run = not bool(prev_snap_id)

    cur.execute(f"""
        CREATE TABLE mv_snapshot_regression_summary AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            '{prev_snap_id}'      AS prev_snapshot_id,
            {node_count}          AS node_count,
            {prev_nodes}          AS prev_node_count,
            {node_count - prev_nodes} AS node_delta,
            {edge_count}          AS edge_count,
            {prev_edges}          AS prev_edge_count,
            {edge_count - prev_edges} AS edge_delta,
            {violation_count}     AS violation_count,
            {prev_violations}     AS prev_violation_count,
            {violation_count - prev_violations} AS violation_delta,
            {cross_layer_count}   AS cross_layer_edge_count,
            {prev_cross}          AS prev_cross_layer_edge_count,
            {cross_layer_count - prev_cross} AS cross_layer_delta,
            {provider_count}      AS provider_surface_count,
            {prev_providers}      AS prev_provider_surface_count,
            {provider_count - prev_providers} AS provider_delta,
            {bypass_count}        AS write_bypass_count,
            {prev_bypass}         AS prev_write_bypass_count,
            {bypass_count - prev_bypass} AS bypass_delta,
            ROUND({float(debt_score)}, 2)  AS debt_score,
            ROUND({prev_debt}, 2)           AS prev_debt_score,
            ROUND({float(debt_score) - prev_debt}, 2) AS debt_delta,
            {1 if is_first_run else 0}      AS is_first_run
    """)

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_reg_summary ON mv_snapshot_regression_summary(snapshot_id)"
    )

    # -------------------------------------------------------------------------
    # mv_newly_introduced_critical_paths
    # -------------------------------------------------------------------------
    prev_crit_threshold = 5.0  # Treat nodes above this score as "critical" in baseline

    cur.execute(f"""
        CREATE TABLE mv_newly_introduced_critical_paths AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            cr.node_id,
            cr.adg_name,
            cr.layer,
            cr.resolved_path      AS file,
            cr.criticality_score,
            CAST(NULL AS REAL)    AS prev_score,
            cr.criticality_score  AS delta,
            CASE WHEN '{prev_snap_id}' = '' THEN 1
                 WHEN cr.criticality_score > {prev_crit_threshold} THEN 1
                 ELSE 0
            END AS is_new
        FROM mv_path_criticality_rollup cr
        WHERE cr.criticality_score > {prev_crit_threshold}
        ORDER BY cr.criticality_score DESC
    """)

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_new_crit ON mv_newly_introduced_critical_paths(is_new, criticality_score DESC)"
    )

    # -------------------------------------------------------------------------
    # mv_new_cross_layer_dependencies
    # -------------------------------------------------------------------------
    cur.execute(f"""
        CREATE TABLE mv_new_cross_layer_dependencies AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            src.layer             AS src_layer,
            dst.layer             AS dst_layer,
            e.relation_type       AS relation_type,
            COUNT(DISTINCT e.id)  AS edge_count,
            {prev_edges}          AS prev_total_edges,
            CASE WHEN '{prev_snap_id}' = '' THEN 1 ELSE
                CASE WHEN COUNT(DISTINCT e.id) > 0 THEN 1 ELSE 0 END
            END AS is_new
        FROM edges e
        JOIN nodes src ON src.id = e.src_id
        JOIN nodes dst ON dst.id = e.dst_id
        WHERE src.layer != dst.layer
          AND e.relation_type IN ('imports', 'calls', 'violates')
          AND src.layer IS NOT NULL AND src.layer != ''
          AND dst.layer IS NOT NULL AND dst.layer != ''
          AND src.resolved_path NOT LIKE 'tests/%'
        GROUP BY src.layer, dst.layer, e.relation_type
        ORDER BY is_new DESC, edge_count DESC
    """)

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_new_cross ON mv_new_cross_layer_dependencies(is_new, src_layer, dst_layer)"
    )

    # -------------------------------------------------------------------------
    # mv_new_provider_surfaces
    # -------------------------------------------------------------------------
    cur.execute(f"""
        CREATE TABLE mv_new_provider_surfaces AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            src.resolved_path     AS caller_file,
            src.layer             AS caller_layer,
            dst.adg_name          AS provider_name,
            dst.resolved_path     AS provider_path,
            COUNT(DISTINCT e.id)  AS invocation_count,
            CASE WHEN '{prev_snap_id}' = '' THEN 1 ELSE 1 END AS is_new
        FROM edges e
        JOIN nodes src ON src.id = e.src_id
        JOIN nodes dst ON dst.id = e.dst_id
        WHERE e.relation_type = 'invokes_provider'
          AND src.resolved_path NOT LIKE 'tests/%'
          AND src.resolved_path NOT LIKE 'tools/%'
        GROUP BY src.resolved_path, src.layer, dst.adg_name, dst.resolved_path
        ORDER BY is_new DESC, invocation_count DESC
    """)

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_new_providers ON mv_new_provider_surfaces(is_new, caller_layer)"
    )

    # -------------------------------------------------------------------------
    # mv_new_write_bypass_paths
    # -------------------------------------------------------------------------
    try:
        cur.execute(f"""
            CREATE TABLE mv_new_write_bypass_paths AS
            SELECT
                {_snapshot_id_expr()} AS snapshot_id,
                ws.writer_file        AS writer_file,
                ws.writer_layer       AS writer_layer,
                ws.write_symbol       AS write_symbol,
                ws.severity           AS severity,
                ws.is_uwg_routed      AS is_uwg_routed,
                ws.is_direct_infra_write AS is_direct_infra_write,
                CASE WHEN '{prev_snap_id}' = '' THEN 1
                     WHEN {bypass_count} > {prev_bypass} THEN 1
                     WHEN ws.severity = 'critical' THEN 1
                     ELSE 0
                END AS is_new
            FROM mv_write_sovereignty_paths ws
            WHERE ws.is_uwg_routed = 0
            ORDER BY is_new DESC, ws.severity
        """)
    except sqlite3.OperationalError:
        # mv_write_sovereignty_paths may be absent if Phase A was not run.
        cur.execute(f"""
            CREATE TABLE mv_new_write_bypass_paths AS
            SELECT
                {_snapshot_id_expr()} AS snapshot_id,
                e.source_file         AS writer_file,
                src.layer             AS writer_layer,
                e.symbol              AS write_symbol,
                'unknown'             AS severity,
                0                     AS is_uwg_routed,
                0                     AS is_direct_infra_write,
                1                     AS is_new
            FROM edges e
            JOIN nodes src ON src.id = e.src_id
            WHERE e.relation_type IN ('writes_to', 'writes_through')
              AND e.source_file NOT LIKE 'tests/%'
              AND e.source_file NOT LIKE 'tools/%'
            ORDER BY src.layer
        """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_new_bypass ON mv_new_write_bypass_paths(is_new, severity)")

    conn.commit()

    counts: dict[str, int] = {}
    try:
        for tbl in _PHASE_D_TABLES:
            row = cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()
            counts[tbl] = row[0] if row else 0
    finally:
        conn.close()
    return counts
