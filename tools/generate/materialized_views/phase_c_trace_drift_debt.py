"""Phase C materialized views — Trace/replay/eval, determinism/provenance, exemption/debt.

Covers view families:
    7. Trace, replay, and eval (mv_trace_replay_eval_gaps, mv_eval_coverage_by_path,
       mv_replay_surface_gaps)
    Remaining 8. Determinism / provenance drift (mv_determinism_provenance_drift,
       mv_graph_vs_report_mismatches)
    9. Exemption, debt, and concentration (mv_exemptions_near_critical_paths,
       mv_modified_area_regressions, mv_repeated_p3_near_critical_paths,
       mv_debt_concentration_hotspots)

Depends on Phase A tables: mv_path_criticality_rollup, mv_hotspot_centrality.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from tools.generate.materialized_views.sqlite_helpers import connect_sqlite_for_mv as _connect_sqlite


_PHASE_C_TABLES: tuple[str, ...] = (
    "mv_trace_replay_eval_gaps",
    "mv_eval_coverage_by_path",
    "mv_replay_surface_gaps",
    "mv_determinism_provenance_drift",
    "mv_graph_vs_report_mismatches",
    "mv_exemptions_near_critical_paths",
    "mv_modified_area_regressions",
    "mv_repeated_p3_near_critical_paths",
    "mv_debt_concentration_hotspots",
)

_ANTIPATTERN_EDGE_KINDS = (
    "silent_exception_swallow",
    "broad_exception_catch",
    "log_and_swallow",
    "return_none_swallow",
)


def _snapshot_id_expr() -> str:
    return "(SELECT COALESCE(value, '') FROM meta WHERE key='commit_sha' LIMIT 1)"


def _antipattern_kinds_in() -> str:
    return "(" + ", ".join(f"'{k}'" for k in _ANTIPATTERN_EDGE_KINDS) + ")"


def materialize_phase_c(sqlite_path: Path) -> dict[str, int]:
    """Create all Phase C materialized tables. Idempotent — safe to call repeatedly.

    Returns:
        dict mapping table_name -> row_count for each Phase C table.
    """
    conn = _connect_sqlite(sqlite_path)
    conn.execute("PRAGMA cache_size = -64000")
    conn.execute("PRAGMA temp_store = MEMORY")
    cur = conn.cursor()

    for tbl in reversed(_PHASE_C_TABLES):
        cur.execute(f"DROP TABLE IF EXISTS {tbl}")

    # -------------------------------------------------------------------------
    # Family 7 — Trace, replay, and eval
    # -------------------------------------------------------------------------

    # mv_trace_replay_eval_gaps
    cur.execute(f"""
        CREATE TABLE mv_trace_replay_eval_gaps AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.resolved_path       AS file,
            n.layer               AS layer,
            CASE WHEN EXISTS (
                SELECT 1 FROM edges et WHERE et.src_id = n.id
                  AND et.relation_type IN ('signs_execution_trace', 'records_execution_trace')
            ) THEN 1 ELSE 0 END   AS has_trace,
            CASE WHEN EXISTS (
                SELECT 1 FROM edges er WHERE er.src_id = n.id
                  AND er.relation_type IN ('links_execution_to_snapshot', 'snapshots_state')
            ) THEN 1 ELSE 0 END   AS has_replay_link,
            CASE WHEN EXISTS (
                SELECT 1 FROM edges ee WHERE ee.src_id = n.id
                  AND ee.relation_type IN ('invokes_eval', 'captures_evaluation_metric',
                                            'invokes_evaluation')
            ) THEN 1 ELSE 0 END   AS has_eval,
            CASE
                WHEN NOT EXISTS (
                    SELECT 1 FROM edges et WHERE et.src_id = n.id
                      AND et.relation_type IN ('signs_execution_trace', 'records_execution_trace')
                ) AND NOT EXISTS (
                    SELECT 1 FROM edges er WHERE er.src_id = n.id
                      AND er.relation_type IN ('links_execution_to_snapshot', 'snapshots_state')
                ) AND NOT EXISTS (
                    SELECT 1 FROM edges ee WHERE ee.src_id = n.id
                      AND ee.relation_type IN ('invokes_eval', 'captures_evaluation_metric',
                                               'invokes_evaluation')
                )
                THEN 'no_trace_replay_eval'
                WHEN NOT EXISTS (
                    SELECT 1 FROM edges et WHERE et.src_id = n.id
                      AND et.relation_type IN ('signs_execution_trace', 'records_execution_trace')
                ) THEN 'no_trace'
                WHEN NOT EXISTS (
                    SELECT 1 FROM edges er WHERE er.src_id = n.id
                      AND er.relation_type IN ('links_execution_to_snapshot', 'snapshots_state')
                ) THEN 'no_replay'
                WHEN NOT EXISTS (
                    SELECT 1 FROM edges ee WHERE ee.src_id = n.id
                      AND ee.relation_type IN ('invokes_eval', 'captures_evaluation_metric',
                                               'invokes_evaluation')
                ) THEN 'no_eval'
                ELSE 'ok'
            END AS gap_type
        FROM nodes n
        WHERE n.entity_type = 'module'
          AND EXISTS (
              SELECT 1 FROM edges ea WHERE ea.src_id = n.id
                AND ea.relation_type IN ('writes_to', 'writes_through', 'routes_to_capability',
                                          'invokes_provider')
          )
          -- Non-runtime code exemptions (2026-04-23 W2 - p1-burndown): trace/replay/eval
          -- edges are produced by the agentic RUNTIME. Paths that execute outside the
          -- runtime (tests, tools, ops scripts, hook scripts, ADG build tooling, low-level
          -- infrastructure) cannot emit runtime telemetry by construction and must not be
          -- flagged for missing it.
          AND n.resolved_path NOT LIKE 'tests/%'
          AND n.resolved_path NOT LIKE 'tools/%'
          AND n.resolved_path NOT LIKE 'ops_scripts/%'
          AND n.resolved_path NOT LIKE '.windsurf/scripts/%'
          AND n.resolved_path NOT LIKE 'agentic_core/adg/%'
          AND n.resolved_path NOT LIKE 'infrastructure/%'
          -- Primitive-provider exemption (config/, types/): hold constants, Enums, and
          -- dataclass definitions only. They cannot emit trace/replay/eval edges because
          -- they do not execute orchestration logic.
          AND n.resolved_path NOT LIKE '%/config/%'
          AND n.resolved_path NOT LIKE '%/types/%'
          AND n.resolved_path NOT LIKE '%_types.py'
        ORDER BY gap_type, layer
    """)

    # mv_eval_coverage_by_path
    cur.execute(f"""
        CREATE TABLE mv_eval_coverage_by_path AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            layer,
            COUNT(DISTINCT node_id)                    AS action_node_count,
            COUNT(DISTINCT CASE WHEN has_eval = 1 THEN node_id END) AS eval_covered_count,
            COUNT(DISTINCT node_id)
                - COUNT(DISTINCT CASE WHEN has_eval = 1 THEN node_id END) AS gap_count,
            ROUND(
                CAST(COUNT(DISTINCT CASE WHEN has_eval = 1 THEN node_id END) AS REAL)
                / NULLIF(COUNT(DISTINCT node_id), 0) * 100,
            1)                    AS coverage_pct
        FROM mv_trace_replay_eval_gaps
        GROUP BY layer
        ORDER BY coverage_pct ASC
    """)

    # mv_replay_surface_gaps
    cur.execute(f"""
        CREATE TABLE mv_replay_surface_gaps AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.resolved_path       AS file,
            n.layer               AS layer,
            COUNT(DISTINCT CASE WHEN e.relation_type IN ('writes_to', 'writes_through') THEN e.id END)
                                  AS mutation_count,
            COUNT(DISTINCT CASE WHEN e.relation_type IN ('links_execution_to_snapshot',
                                                          'snapshots_state') THEN e.id END)
                                  AS replay_link_count,
            CASE WHEN COUNT(DISTINCT CASE WHEN e.relation_type IN ('writes_to', 'writes_through') THEN e.id END) > 0
                  AND COUNT(DISTINCT CASE WHEN e.relation_type IN ('links_execution_to_snapshot',
                                                                    'snapshots_state') THEN e.id END) = 0
                 THEN 1 ELSE 0 END AS gap_flag
        FROM nodes n
        LEFT JOIN edges e ON e.src_id = n.id
            AND e.relation_type IN ('writes_to', 'writes_through',
                                    'links_execution_to_snapshot', 'snapshots_state')
        WHERE n.entity_type = 'module'
          AND n.resolved_path NOT LIKE 'tests/%'
          AND n.resolved_path NOT LIKE 'tools/%'
        GROUP BY n.id
        HAVING mutation_count > 0
        ORDER BY gap_flag DESC, mutation_count DESC
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_trace_gap ON mv_trace_replay_eval_gaps(gap_type, layer)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_eval_cov ON mv_eval_coverage_by_path(coverage_pct ASC)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_replay_gap ON mv_replay_surface_gaps(gap_flag, layer)")

    # -------------------------------------------------------------------------
    # Remaining Family 8 — Determinism / provenance drift
    # -------------------------------------------------------------------------

    # mv_determinism_provenance_drift
    # Pre-compute dynamic resolution counts to avoid OR-join performance issue.
    # Original: LEFT JOIN edges e ON (e.src_id = n.id OR e.dst_id = n.id)
    # Fix: use UNION ALL with separate index-friendly lookups.
    cur.execute("DROP TABLE IF EXISTS _t_dyn_res_counts")
    cur.execute("""
        CREATE TEMP TABLE _t_dyn_res_counts AS
        SELECT node_id, COUNT(DISTINCT edge_id) AS cnt FROM (
            SELECT src_id AS node_id, id AS edge_id FROM edges
            WHERE dynamic_resolution IS NOT NULL AND dynamic_resolution != ''
            UNION ALL
            SELECT dst_id AS node_id, id AS edge_id FROM edges
            WHERE dynamic_resolution IS NOT NULL AND dynamic_resolution != ''
        )
        GROUP BY node_id
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS _idx_drc ON _t_dyn_res_counts(node_id)")

    cur.execute(f"""
        CREATE TABLE mv_determinism_provenance_drift AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.resolved_path       AS file,
            n.layer               AS layer,
            CASE WHEN (SELECT value FROM meta WHERE key='commit_sha' LIMIT 1) IS NOT NULL
                 THEN 1 ELSE 0 END AS has_commit_sha,
            CASE WHEN (SELECT value FROM meta WHERE key='artifact_digest' LIMIT 1) IS NOT NULL
                 THEN 1 ELSE 0 END AS has_artifact_digest,
            CASE WHEN (SELECT value FROM meta WHERE key='scanner_digest' LIMIT 1) IS NOT NULL
                 THEN 1 ELSE 0 END AS has_scanner_digest,
            COALESCE(dr.cnt, 0)   AS dynamic_resolution_count,
            CASE
                WHEN COALESCE(dr.cnt, 0) > 0
                THEN 1 ELSE 0
            END AS drift_flag
        FROM nodes n
        LEFT JOIN _t_dyn_res_counts dr ON dr.node_id = n.id
        WHERE n.entity_type = 'module'
          AND n.resolved_path NOT LIKE 'tests/%'
        ORDER BY dynamic_resolution_count DESC
    """)
    cur.execute("DROP TABLE IF EXISTS _t_dyn_res_counts")

    # mv_graph_vs_report_mismatches
    # Violations whose edge_id has no matching edge row, or edges with no violations row.
    cur.execute(f"""
        CREATE TABLE mv_graph_vs_report_mismatches AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            'orphan_violation'    AS mismatch_type,
            CAST(v.id AS TEXT)    AS ref_id,
            v.file_path           AS file,
            v.category            AS detail,
            1                     AS mismatch_delta
        FROM violations v
        WHERE NOT EXISTS (
            SELECT 1 FROM edges e WHERE e.id = v.edge_id
        )
        UNION ALL
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            'meta_count_mismatch' AS mismatch_type,
            m.key                 AS ref_id,
            ''                    AS file,
            'meta=' || m.value
                || ' actual='
                || CASE m.key
                    WHEN 'total_nodes' THEN CAST((SELECT COUNT(*) FROM nodes) AS TEXT)
                    WHEN 'total_edges' THEN CAST((SELECT COUNT(*) FROM edges) AS TEXT)
                    ELSE '?'
                   END            AS detail,
            ABS(
                CAST(m.value AS INTEGER) - CASE m.key
                    WHEN 'total_nodes' THEN (SELECT COUNT(*) FROM nodes)
                    WHEN 'total_edges' THEN (SELECT COUNT(*) FROM edges)
                    ELSE 0
                END
            )                     AS mismatch_delta
        FROM meta m
        WHERE m.key IN ('total_nodes', 'total_edges')
          AND m.value != CASE m.key
              WHEN 'total_nodes' THEN CAST((SELECT COUNT(*) FROM nodes) AS TEXT)
              WHEN 'total_edges' THEN CAST((SELECT COUNT(*) FROM edges) AS TEXT)
              ELSE m.value
          END
        ORDER BY mismatch_type
    """)

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_drift_flag ON mv_determinism_provenance_drift(drift_flag, layer)"
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_mismatch ON mv_graph_vs_report_mismatches(mismatch_type)")

    # -------------------------------------------------------------------------
    # Family 9 — Exemption, debt, and concentration
    # -------------------------------------------------------------------------

    # mv_exemptions_near_critical_paths
    cur.execute(f"""
        CREATE TABLE mv_exemptions_near_critical_paths AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            e.id                  AS edge_id,
            src.resolved_path     AS file,
            src.layer             AS layer,
            e.edge_kind           AS exemption_kind,
            e.source_file         AS source_file,
            e.line_no             AS line_no,
            COALESCE(cr.criticality_score, 0) AS criticality_score,
            CASE WHEN cr.criticality_score IS NOT NULL
                  AND cr.criticality_score > 5.0
                 THEN 1 ELSE 0 END AS proximity_flag
        FROM edges e
        JOIN nodes src ON src.id = e.src_id
        LEFT JOIN mv_path_criticality_rollup cr ON cr.node_id = src.id
        WHERE e.edge_kind IN {_antipattern_kinds_in()}
          AND src.resolved_path NOT LIKE 'tests/%'
        ORDER BY criticality_score DESC, proximity_flag DESC
    """)

    # mv_modified_area_regressions
    # Files accumulating violations — uses violation count as regression signal.
    # (No cross-snapshot diff here; use Family 11 for delta.)
    cur.execute(f"""
        CREATE TABLE mv_modified_area_regressions AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            v.file_path           AS file,
            n.layer               AS layer,
            v.violation_class     AS violation_class,
            v.severity            AS severity,
            COUNT(DISTINCT v.id)  AS violation_count,
            v.disposition         AS disposition
        FROM violations v
        LEFT JOIN edges ev ON ev.id = v.edge_id
        LEFT JOIN nodes n ON n.id = ev.src_id
        WHERE v.file_path != ''
        GROUP BY v.file_path, n.layer, v.violation_class, v.severity, v.disposition
        ORDER BY violation_count DESC
    """)

    # mv_repeated_p3_near_critical_paths
    cur.execute(f"""
        CREATE TABLE mv_repeated_p3_near_critical_paths AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            src.resolved_path     AS file,
            src.layer             AS layer,
            COUNT(DISTINCT e.id)  AS p3_count,
            COALESCE(cr.criticality_score, 0) AS criticality_score,
            CASE WHEN cr.criticality_score IS NOT NULL
                  AND cr.criticality_score > 5.0
                 THEN 1 ELSE 0 END AS near_critical,
            CASE WHEN COUNT(DISTINCT e.id) > 2 THEN 1 ELSE 0 END AS chronic_flag
        FROM edges e
        JOIN nodes src ON src.id = e.src_id
        LEFT JOIN mv_path_criticality_rollup cr ON cr.node_id = src.id
        WHERE e.edge_kind IN {_antipattern_kinds_in()}
          AND src.resolved_path NOT LIKE 'tests/%'
        GROUP BY src.resolved_path, src.layer
        ORDER BY p3_count DESC, near_critical DESC
    """)

    # mv_debt_concentration_hotspots
    cur.execute(f"""
        CREATE TABLE mv_debt_concentration_hotspots AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            v.file_path           AS file,
            n.layer               AS layer,
            SUM(CASE WHEN v.severity = 'CRITICAL' THEN 1 ELSE 0 END) AS p0_count,
            SUM(CASE WHEN v.severity = 'HIGH'     THEN 1 ELSE 0 END) AS p1_count,
            SUM(CASE WHEN v.severity = 'MEDIUM'   THEN 1 ELSE 0 END) AS p2_count,
            SUM(CASE WHEN v.severity = 'LOW'      THEN 1 ELSE 0 END) AS p3_count,
            COUNT(DISTINCT v.id)                                       AS total_violations,
            ROUND(
                SUM(CASE WHEN v.severity = 'CRITICAL' THEN 1 ELSE 0 END) * 10.0
                + SUM(CASE WHEN v.severity = 'HIGH'   THEN 1 ELSE 0 END) * 5.0
                + SUM(CASE WHEN v.severity = 'MEDIUM' THEN 1 ELSE 0 END) * 2.0
                + SUM(CASE WHEN v.severity = 'LOW'    THEN 1 ELSE 0 END) * 1.0,
            1)                    AS total_debt_score,
            ROW_NUMBER() OVER (ORDER BY
                SUM(CASE WHEN v.severity = 'CRITICAL' THEN 1 ELSE 0 END) * 10.0
                + SUM(CASE WHEN v.severity = 'HIGH'   THEN 1 ELSE 0 END) * 5.0
                + SUM(CASE WHEN v.severity = 'MEDIUM' THEN 1 ELSE 0 END) * 2.0
                + SUM(CASE WHEN v.severity = 'LOW'    THEN 1 ELSE 0 END) * 1.0
            DESC) AS hotspot_rank
        FROM violations v
        LEFT JOIN edges ev ON ev.id = v.edge_id
        LEFT JOIN nodes n ON n.id = ev.src_id
        WHERE v.file_path != ''
        GROUP BY v.file_path, n.layer
        ORDER BY total_debt_score DESC
    """)

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_exempt_crit ON mv_exemptions_near_critical_paths(criticality_score DESC, proximity_flag)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_mod_reg ON mv_modified_area_regressions(violation_count DESC, layer)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_p3_crit ON mv_repeated_p3_near_critical_paths(chronic_flag, near_critical)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_debt_rank ON mv_debt_concentration_hotspots(hotspot_rank, total_debt_score DESC)"
    )

    conn.commit()

    counts: dict[str, int] = {}
    try:
        for tbl in _PHASE_C_TABLES:
            row = cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()
            counts[tbl] = row[0] if row else 0
    finally:
        conn.close()
    return counts
