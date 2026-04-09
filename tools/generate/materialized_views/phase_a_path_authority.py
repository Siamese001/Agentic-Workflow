"""Phase A materialized views — Critical path, authority/sovereignty, lifecycle, topology seeds.

Covers view families:
    1. Critical path and spine (mv_critical_path_segments, mv_runtime_spine_gaps,
       mv_path_criticality_rollup)
    2. Authority and sovereignty (mv_authority_boundary_breaches, mv_write_sovereignty_paths,
       mv_live_future_mutation_conflicts, mv_hitl_reclearance_gaps)
    3. Lifecycle and phase coverage (mv_l2_phase_coverage, mv_exit_disposition_coverage,
       mv_heal_retry_exit_gaps)
    Partial 8. Determinism seeds (mv_digest_reconciliation, mv_snapshot_integrity_anomalies)
    Partial 10. Topology seeds (mv_hotspot_centrality, mv_unknown_taxonomy_and_orphans)

All tables are physical (DROP + CREATE AS SELECT), idempotent, and snapshot-stamped via
    (SELECT value FROM meta WHERE key='commit_sha') AS snapshot_id
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

_PHASE_A_TABLES: tuple[str, ...] = (
    "mv_critical_path_segments",
    "mv_runtime_spine_gaps",
    "mv_path_criticality_rollup",
    "mv_authority_boundary_breaches",
    "mv_write_sovereignty_paths",
    "mv_live_future_mutation_conflicts",
    "mv_hitl_reclearance_gaps",
    "mv_l2_phase_coverage",
    "mv_exit_disposition_coverage",
    "mv_heal_retry_exit_gaps",
    "mv_digest_reconciliation",
    "mv_snapshot_integrity_anomalies",
    "mv_hotspot_centrality",
    "mv_unknown_taxonomy_and_orphans",
)

_SPINE_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5", "L6", "L_APP", "L_SHARED")

_FORBIDDEN_LAYER_PAIRS = (
    ("L6", "L2"),
    ("L6", "L0"),
    ("L6", "L1"),
    ("L_APP", "L0"),
    ("L_APP", "L1"),
    ("L_APP", "L2"),
)

_UWG_PATH_FRAGMENTS = (
    "UniversalWrite",
    "write_gateway",
    "uwg",
    "mutation_prohibition",
    "durable_write",
)

_L2_PHASE_KEYWORDS: list[tuple[str, str]] = [
    ("pre_audit", "pre_audit"),
    ("discovery", "discovery"),
    ("reconciliation", "reconciliation"),
    ("alignment", "alignment"),
    ("arch_validation", "arch_validation"),
    ("healing", "healing"),
    ("certification", "certification"),
    ("guardrail", "guardrail"),
    ("enforcement", "enforcement"),
    ("execution_gateway", "execution_gateway"),
    ("boundary_validator", "boundary_validator"),
]


def _snapshot_id_expr() -> str:
    return "(SELECT COALESCE(value, '') FROM meta WHERE key='commit_sha' LIMIT 1)"


def _build_forbidden_pairs_clause() -> str:
    pairs = " OR ".join(f"(src.layer = '{s}' AND dst.layer = '{d}')" for s, d in _FORBIDDEN_LAYER_PAIRS)
    return f"({pairs})"


def _build_uwg_path_clause(col: str) -> str:
    frags = " OR ".join(f"{col} LIKE '%{f}%'" for f in _UWG_PATH_FRAGMENTS)
    return f"({frags})"


def _spine_layers_in() -> str:
    return "(" + ", ".join(f"'{l}'" for l in _SPINE_LAYERS) + ")"


def materialize_phase_a(sqlite_path: Path) -> dict[str, int]:
    """Create all Phase A materialized tables. Idempotent — safe to call repeatedly.

    Returns:
        dict mapping table_name -> row_count for each Phase A table.
    """
    conn = sqlite3.connect(str(sqlite_path))
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()

    # Drop in reverse dependency order
    for tbl in reversed(_PHASE_A_TABLES):
        cur.execute(f"DROP TABLE IF EXISTS {tbl}")

    # -------------------------------------------------------------------------
    # Family 1 — Critical path and spine
    # -------------------------------------------------------------------------

    # mv_critical_path_segments
    # Cross-layer edge summary: which layers talk to which layers, and how many edges.
    cur.execute(f"""
        CREATE TABLE mv_critical_path_segments AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            src.layer             AS src_layer,
            dst.layer             AS dst_layer,
            e.relation_type       AS hop_type,
            COUNT(DISTINCT e.id)  AS edge_count,
            COUNT(DISTINCT e.source_file) AS file_count,
            CASE
                WHEN src.layer IN {_spine_layers_in()} AND dst.layer IN {_spine_layers_in()}
                THEN 1 ELSE 0
            END AS both_on_spine
        FROM edges e
        JOIN nodes src ON src.id = e.src_id
        JOIN nodes dst ON dst.id = e.dst_id
        WHERE e.relation_type IN ('imports', 'calls', 'violates')
          AND src.layer IS NOT NULL AND src.layer != ''
          AND dst.layer IS NOT NULL AND dst.layer != ''
          AND src.layer != dst.layer
        GROUP BY src.layer, dst.layer, e.relation_type
        ORDER BY edge_count DESC
    """)

    # mv_runtime_spine_gaps
    # Per-layer: how many modules have zero incoming spine edges (disconnected from spine).
    cur.execute(f"""
        CREATE TABLE mv_runtime_spine_gaps AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.layer               AS layer,
            COUNT(n.id)           AS module_count,
            COUNT(CASE
                WHEN EXISTS (
                    SELECT 1 FROM edges e2
                    JOIN nodes src2 ON src2.id = e2.src_id
                    WHERE e2.dst_id = n.id
                      AND e2.relation_type IN ('imports', 'calls')
                      AND src2.layer IN {_spine_layers_in()}
                ) THEN 1
            END)                  AS connected_count,
            COUNT(n.id) - COUNT(CASE
                WHEN EXISTS (
                    SELECT 1 FROM edges e2
                    JOIN nodes src2 ON src2.id = e2.src_id
                    WHERE e2.dst_id = n.id
                      AND e2.relation_type IN ('imports', 'calls')
                      AND src2.layer IN {_spine_layers_in()}
                ) THEN 1
            END)                  AS gap_count,
            ROUND(
                CAST(
                    COUNT(n.id) - COUNT(CASE
                        WHEN EXISTS (
                            SELECT 1 FROM edges e2
                            JOIN nodes src2 ON src2.id = e2.src_id
                            WHERE e2.dst_id = n.id
                              AND e2.relation_type IN ('imports', 'calls')
                              AND src2.layer IN {_spine_layers_in()}
                        ) THEN 1
                    END)
                AS REAL) / NULLIF(COUNT(n.id), 0) * 100,
                1
            )                     AS gap_pct
        FROM nodes n
        WHERE n.entity_type = 'module'
          AND n.layer IN {_spine_layers_in()}
          AND n.resolved_path NOT LIKE 'tests/%'
          AND n.resolved_path NOT LIKE 'tools/%'
        GROUP BY n.layer
        ORDER BY gap_count DESC
    """)

    # mv_path_criticality_rollup
    # Per-module composite criticality: fan_in, fan_out, violation_count, cross-layer edges.
    cur.execute(f"""
        CREATE TABLE mv_path_criticality_rollup AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.adg_name            AS adg_name,
            n.layer               AS layer,
            n.resolved_path       AS resolved_path,
            COUNT(DISTINCT e_in.id)  AS fan_in,
            COUNT(DISTINCT e_out.id) AS fan_out,
            COALESCE((
                SELECT COUNT(*) FROM violations v
                JOIN edges ev ON ev.id = v.edge_id
                WHERE ev.src_id = n.id
            ), 0)                 AS violation_count,
            COALESCE((
                SELECT COUNT(*) FROM edges ecl
                JOIN nodes ndst ON ndst.id = ecl.dst_id
                WHERE ecl.src_id = n.id
                  AND ecl.relation_type IN ('imports', 'calls')
                  AND ndst.layer != n.layer
            ), 0)                 AS cross_layer_edges,
            ROUND(
                (COUNT(DISTINCT e_in.id) + COUNT(DISTINCT e_out.id)) * 1.0
                + COALESCE((
                    SELECT COUNT(*) FROM violations v
                    JOIN edges ev ON ev.id = v.edge_id
                    WHERE ev.src_id = n.id
                ), 0) * 3.0,
            2)                    AS criticality_score
        FROM nodes n
        LEFT JOIN edges e_in  ON e_in.dst_id  = n.id  AND e_in.relation_type  IN ('imports', 'calls')
        LEFT JOIN edges e_out ON e_out.src_id = n.id  AND e_out.relation_type IN ('imports', 'calls')
        WHERE n.entity_type = 'module'
        GROUP BY n.id
        ORDER BY criticality_score DESC
    """)

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_crit_rollup_snapshot ON mv_path_criticality_rollup(snapshot_id)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_crit_rollup_score ON mv_path_criticality_rollup(criticality_score DESC)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_crit_rollup_layer ON mv_path_criticality_rollup(layer, violation_count DESC)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_spine_gaps_layer ON mv_runtime_spine_gaps(layer, gap_count DESC)"
    )

    # -------------------------------------------------------------------------
    # Family 2 — Authority and sovereignty
    # -------------------------------------------------------------------------

    forbidden_pairs_clause = _build_forbidden_pairs_clause()

    # mv_authority_boundary_breaches
    cur.execute(f"""
        CREATE TABLE mv_authority_boundary_breaches AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            e.id                  AS edge_id,
            src.resolved_path     AS src_file,
            src.layer             AS src_layer,
            dst.resolved_path     AS dst_file,
            dst.layer             AS dst_layer,
            e.relation_type       AS relation_type,
            e.source_file         AS source_file,
            e.line_no             AS line_no,
            CASE
                WHEN e.relation_type = 'violates' THEN 'layer_violation'
                WHEN src.layer = 'L6' THEN 'L6_downstream_mutation'
                WHEN src.layer LIKE 'L_APP' THEN 'L_APP_core_bypass'
                ELSE 'forbidden_cross_layer'
            END AS breach_class
        FROM edges e
        JOIN nodes src ON src.id = e.src_id
        JOIN nodes dst ON dst.id = e.dst_id
        WHERE {forbidden_pairs_clause}
          AND e.relation_type IN ('imports', 'calls', 'violates', 'writes_to', 'writes_through')
        ORDER BY breach_class, src.layer, dst.layer
    """)

    # mv_write_sovereignty_paths
    cur.execute(f"""
        CREATE TABLE mv_write_sovereignty_paths AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            e.id                  AS edge_id,
            src.resolved_path     AS writer_file,
            src.layer             AS writer_layer,
            e.symbol              AS write_symbol,
            e.line_no             AS write_line,
            e.source_file         AS source_file,
            CASE WHEN {_build_uwg_path_clause("src.resolved_path")}
                 THEN 1 ELSE 0 END AS is_uwg_routed,
            CASE WHEN EXISTS (
                SELECT 1 FROM t_infra_importers ti
                WHERE ti.resolved_path = src.resolved_path
            ) THEN 1 ELSE 0 END   AS is_direct_infra_write,
            CASE
                WHEN NOT ({_build_uwg_path_clause("src.resolved_path")})
                     AND EXISTS (
                         SELECT 1 FROM t_infra_importers ti
                         WHERE ti.resolved_path = src.resolved_path
                     ) THEN 'critical'
                WHEN NOT ({_build_uwg_path_clause("src.resolved_path")})
                     THEN 'warning'
                ELSE 'ok'
            END AS severity
        FROM edges e
        JOIN nodes src ON src.id = e.src_id
        WHERE e.relation_type IN ('writes_to', 'writes_through')
          AND src.resolved_path NOT LIKE 'tests/%'
          AND src.resolved_path NOT LIKE 'tools/%'
          AND src.resolved_path NOT LIKE 'ops_scripts/%'
        ORDER BY severity, writer_layer
    """)

    # mv_live_future_mutation_conflicts
    # Files with both live-run writes AND future/snapshot link edges — potential current/future confusion.
    cur.execute(f"""
        CREATE TABLE mv_live_future_mutation_conflicts AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            src.resolved_path     AS file,
            src.layer             AS layer,
            COUNT(DISTINCT CASE WHEN e.relation_type IN ('writes_to', 'writes_through') THEN e.id END) AS live_write_count,
            COUNT(DISTINCT CASE WHEN e.relation_type IN ('links_execution_to_snapshot', 'snapshots_state') THEN e.id END) AS snapshot_link_count,
            CASE
                WHEN COUNT(DISTINCT CASE WHEN e.relation_type IN ('writes_to', 'writes_through') THEN e.id END) > 0
                 AND COUNT(DISTINCT CASE WHEN e.relation_type IN ('links_execution_to_snapshot', 'snapshots_state') THEN e.id END) > 0
                THEN 'live_and_future_write_conflict'
                ELSE 'no_conflict'
            END AS conflict_type
        FROM edges e
        JOIN nodes src ON src.id = e.src_id
        WHERE e.relation_type IN ('writes_to', 'writes_through', 'links_execution_to_snapshot', 'snapshots_state')
          AND src.resolved_path NOT LIKE 'tests/%'
          AND src.resolved_path NOT LIKE 'tools/%'
        GROUP BY src.resolved_path, src.layer
        HAVING live_write_count > 0 AND snapshot_link_count > 0
        ORDER BY live_write_count DESC
    """)

    # mv_hitl_reclearance_gaps
    # Modules with write edges but no applies_guardrail outgoing edge.
    cur.execute(f"""
        CREATE TABLE mv_hitl_reclearance_gaps AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.resolved_path       AS file,
            n.layer               AS layer,
            COALESCE((
                SELECT COUNT(*) FROM edges ew
                WHERE ew.src_id = n.id
                  AND ew.relation_type IN ('writes_to', 'writes_through')
            ), 0)                 AS write_edge_count,
            COALESCE((
                SELECT COUNT(*) FROM edges eg
                WHERE eg.src_id = n.id
                  AND eg.relation_type = 'applies_guardrail'
            ), 0)                 AS guardrail_edge_count,
            CASE
                WHEN COALESCE((
                    SELECT COUNT(*) FROM edges ew
                    WHERE ew.src_id = n.id
                      AND ew.relation_type IN ('writes_to', 'writes_through')
                ), 0) > 0
                 AND COALESCE((
                    SELECT COUNT(*) FROM edges eg
                    WHERE eg.src_id = n.id
                      AND eg.relation_type = 'applies_guardrail'
                ), 0) = 0
                THEN 'write_without_guardrail'
                ELSE 'ok'
            END AS gap_type
        FROM nodes n
        WHERE n.entity_type = 'module'
          AND n.layer IN {_spine_layers_in()}
          AND n.resolved_path NOT LIKE 'tests/%'
          AND n.resolved_path NOT LIKE 'tools/%'
        ORDER BY write_edge_count DESC
    """)

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_auth_breach_layers ON mv_authority_boundary_breaches(src_layer, dst_layer)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_write_sov_severity ON mv_write_sovereignty_paths(severity, is_uwg_routed)"
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_hitl_gap ON mv_hitl_reclearance_gaps(gap_type, layer)")

    # -------------------------------------------------------------------------
    # Family 3 — Lifecycle and phase coverage
    # -------------------------------------------------------------------------

    phase_cases = "\n            ".join(
        f"WHEN n.resolved_path LIKE '%{kw}%' THEN '{label}'" for kw, label in _L2_PHASE_KEYWORDS
    )

    # mv_l2_phase_coverage
    cur.execute(f"""
        CREATE TABLE mv_l2_phase_coverage AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            phase_label,
            COUNT(node_id)         AS node_count,
            MAX(has_entry_edge)    AS has_entry_edge,
            MAX(has_exit_edge)     AS has_exit_edge,
            MAX(covered_by_test)   AS covered_by_test,
            CASE WHEN COUNT(node_id) = 0 THEN 1 ELSE 0 END AS gap_flag
        FROM (
            SELECT
                n.id AS node_id,
                CASE
                    {phase_cases}
                    ELSE 'phase_unknown'
                END AS phase_label,
                CASE WHEN EXISTS (
                    SELECT 1 FROM edges ei WHERE ei.dst_id = n.id
                      AND ei.relation_type IN ('imports', 'calls')
                ) THEN 1 ELSE 0 END AS has_entry_edge,
                CASE WHEN EXISTS (
                    SELECT 1 FROM edges eo WHERE eo.src_id = n.id
                      AND eo.relation_type IN ('routes_to_capability', 'routes_to_agent',
                                               'invokes_eval', 'writes_through')
                ) THEN 1 ELSE 0 END AS has_exit_edge,
                CASE WHEN EXISTS (
                    SELECT 1 FROM edges ec WHERE ec.dst_id = n.id
                      AND ec.relation_type = 'covers'
                ) THEN 1 ELSE 0 END AS covered_by_test
            FROM nodes n
            WHERE n.layer = 'L2'
              AND n.entity_type = 'module'
              AND n.resolved_path NOT LIKE 'tests/%'
        )
        GROUP BY phase_label
        ORDER BY phase_label
    """)

    # mv_exit_disposition_coverage
    cur.execute(f"""
        CREATE TABLE mv_exit_disposition_coverage AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.resolved_path       AS file,
            n.layer               AS layer,
            COALESCE((
                SELECT COUNT(*) FROM edges eo
                WHERE eo.src_id = n.id
                  AND eo.relation_type IN (
                      'routes_to_capability', 'invokes_eval',
                      'writes_through', 'writes_via_uwg',
                      'execution_terminates_at_uwg'
                  )
            ), 0)                 AS outgoing_terminal_count,
            CASE WHEN COALESCE((
                SELECT COUNT(*) FROM edges eo
                WHERE eo.src_id = n.id
                  AND eo.relation_type IN (
                      'routes_to_capability', 'invokes_eval',
                      'writes_through', 'writes_via_uwg',
                      'execution_terminates_at_uwg'
                  )
            ), 0) > 0 THEN 1 ELSE 0 END AS is_terminal_covered,
            CASE WHEN COALESCE((
                SELECT COUNT(*) FROM edges eo
                WHERE eo.src_id = n.id
                  AND eo.relation_type IN (
                      'routes_to_capability', 'invokes_eval',
                      'writes_through', 'writes_via_uwg',
                      'execution_terminates_at_uwg'
                  )
            ), 0) = 0 THEN 'no_exit_disposition'
            ELSE 'ok' END         AS gap_type
        FROM nodes n
        WHERE n.layer IN ('L2', 'L5')
          AND n.entity_type = 'module'
          AND n.resolved_path NOT LIKE 'tests/%'
        ORDER BY is_terminal_covered ASC, layer
    """)

    # mv_heal_retry_exit_gaps
    cur.execute(f"""
        CREATE TABLE mv_heal_retry_exit_gaps AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.resolved_path       AS file,
            n.layer               AS layer,
            CASE WHEN n.resolved_path LIKE '%heal%'
                   OR n.adg_name LIKE '%heal%' THEN 1 ELSE 0 END AS has_heal_keyword,
            CASE WHEN n.resolved_path LIKE '%retry%'
                   OR n.adg_name LIKE '%retry%'
                   OR n.resolved_path LIKE '%rollback%' THEN 1 ELSE 0 END AS has_retry_keyword,
            CASE WHEN EXISTS (
                SELECT 1 FROM edges eo WHERE eo.src_id = n.id
                  AND eo.relation_type IN (
                      'routes_to_capability', 'invokes_eval',
                      'writes_through', 'escalates_failure',
                      'execution_terminates_at_uwg'
                  )
            ) THEN 1 ELSE 0 END   AS has_terminal_exit,
            CASE WHEN (
                    n.resolved_path LIKE '%heal%' OR n.adg_name LIKE '%heal%'
                    OR n.resolved_path LIKE '%retry%' OR n.adg_name LIKE '%retry%'
                )
              AND NOT EXISTS (
                SELECT 1 FROM edges eo WHERE eo.src_id = n.id
                  AND eo.relation_type IN (
                      'routes_to_capability', 'invokes_eval',
                      'writes_through', 'escalates_failure',
                      'execution_terminates_at_uwg'
                  )
            ) THEN 1 ELSE 0 END   AS gap_flag
        FROM nodes n
        WHERE n.entity_type = 'module'
          AND n.layer IN {_spine_layers_in()}
          AND (
            n.resolved_path LIKE '%heal%' OR n.adg_name LIKE '%heal%'
            OR n.resolved_path LIKE '%retry%' OR n.adg_name LIKE '%retry%'
            OR n.resolved_path LIKE '%rollback%'
          )
          AND n.resolved_path NOT LIKE 'tests/%'
        ORDER BY gap_flag DESC
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_l2_phase ON mv_l2_phase_coverage(phase_label, gap_flag)")
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_exit_disp ON mv_exit_disposition_coverage(gap_type, layer)"
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_heal_gap ON mv_heal_retry_exit_gaps(gap_flag, layer)")

    # -------------------------------------------------------------------------
    # Partial Family 8 — Determinism seeds
    # -------------------------------------------------------------------------

    # mv_digest_reconciliation
    # Compare meta-stored counts against actual table counts.
    cur.execute(f"""
        CREATE TABLE mv_digest_reconciliation AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            m.key                 AS meta_key,
            m.value               AS meta_value,
            CASE m.key
                WHEN 'total_nodes' THEN CAST((SELECT COUNT(*) FROM nodes) AS TEXT)
                WHEN 'total_edges' THEN CAST((SELECT COUNT(*) FROM edges) AS TEXT)
                ELSE NULL
            END                   AS cross_check_value,
            CASE
                WHEN m.key NOT IN ('total_nodes', 'total_edges') THEN NULL
                WHEN m.key = 'total_nodes'
                     AND m.value = CAST((SELECT COUNT(*) FROM nodes) AS TEXT) THEN 1
                WHEN m.key = 'total_edges'
                     AND m.value = CAST((SELECT COUNT(*) FROM edges) AS TEXT) THEN 1
                ELSE 0
            END                   AS match_flag
        FROM meta m
        WHERE m.key IN ('total_nodes', 'total_edges', 'commit_sha',
                        'schema_version', 'artifact_digest', 'scanner_digest')
        ORDER BY m.key
    """)

    # mv_snapshot_integrity_anomalies
    cur.execute(f"""
        CREATE TABLE mv_snapshot_integrity_anomalies AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            'null_resolved_path'  AS anomaly_type,
            CAST(n.id AS TEXT)    AS affected_id,
            n.adg_name            AS detail
        FROM nodes n
        WHERE n.resolved_path IS NULL OR n.resolved_path = ''
        UNION ALL
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            'null_layer'          AS anomaly_type,
            CAST(n.id AS TEXT)    AS affected_id,
            n.adg_name            AS detail
        FROM nodes n
        WHERE (n.layer IS NULL OR n.layer = '')
          AND n.identity_kind != 'external_module'
          AND n.entity_type = 'module'
        UNION ALL
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            'dynamic_override'    AS anomaly_type,
            CAST(e.id AS TEXT)    AS affected_id,
            e.source_file || ':' || CAST(e.line_no AS TEXT) AS detail
        FROM edges e
        WHERE e.dynamic_resolution IS NOT NULL
          AND e.dynamic_resolution != ''
          AND e.source_file NOT LIKE 'tests/%'
          AND e.source_file NOT LIKE 'tools/%'
        ORDER BY anomaly_type
    """)

    # -------------------------------------------------------------------------
    # Partial Family 10 — Topology seeds
    # -------------------------------------------------------------------------

    # mv_hotspot_centrality
    cur.execute(f"""
        CREATE TABLE mv_hotspot_centrality AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.adg_name            AS adg_name,
            n.layer               AS layer,
            n.resolved_path       AS resolved_path,
            COUNT(DISTINCT e_in.id)   AS fan_in,
            COUNT(DISTINCT e_out.id)  AS fan_out,
            COUNT(DISTINCT e_in.id) + COUNT(DISTINCT e_out.id) AS degree,
            ROUND(
                CAST(COUNT(DISTINCT e_in.id) AS REAL)
                * CAST(COUNT(DISTINCT e_out.id) AS REAL)
                / NULLIF((SELECT COUNT(*) FROM nodes WHERE entity_type='module'), 0),
            4)                    AS betweenness_approx,
            ROUND(
                CAST(COUNT(DISTINCT e_in.id) AS REAL)
                / NULLIF((SELECT COUNT(*) FROM nodes WHERE entity_type='module'), 0),
            4)                    AS degree_centrality
        FROM nodes n
        LEFT JOIN edges e_in  ON e_in.dst_id  = n.id  AND e_in.relation_type  IN ('imports', 'calls')
        LEFT JOIN edges e_out ON e_out.src_id = n.id  AND e_out.relation_type IN ('imports', 'calls')
        WHERE n.entity_type = 'module'
        GROUP BY n.id
        ORDER BY fan_in DESC
    """)

    # mv_unknown_taxonomy_and_orphans
    cur.execute(f"""
        CREATE TABLE mv_unknown_taxonomy_and_orphans AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.resolved_path       AS file,
            n.layer               AS layer,
            n.identity_kind       AS identity_kind,
            n.entity_type         AS entity_type,
            CASE WHEN n.layer IS NULL OR n.layer = '' THEN 1 ELSE 0 END AS unknown_taxonomy_flag,
            CASE
                WHEN NOT EXISTS (
                    SELECT 1 FROM edges ei WHERE ei.dst_id = n.id
                )
                 AND NOT EXISTS (
                    SELECT 1 FROM edges eo WHERE eo.src_id = n.id
                ) THEN 1
                ELSE 0
            END                   AS orphan_flag
        FROM nodes n
        WHERE n.entity_type = 'module'
          AND n.identity_kind != 'external_module'
          AND n.resolved_path NOT LIKE 'tests/%'
        ORDER BY unknown_taxonomy_flag DESC, orphan_flag DESC
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_hotspot_fi ON mv_hotspot_centrality(fan_in DESC, layer)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_hotspot_snapshot ON mv_hotspot_centrality(snapshot_id)")
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_orphan_flags ON mv_unknown_taxonomy_and_orphans(orphan_flag, unknown_taxonomy_flag)"
    )

    conn.commit()

    counts: dict[str, int] = {}
    try:
        for tbl in _PHASE_A_TABLES:
            row = cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()
            counts[tbl] = row[0] if row else 0
    finally:
        conn.close()
    return counts
