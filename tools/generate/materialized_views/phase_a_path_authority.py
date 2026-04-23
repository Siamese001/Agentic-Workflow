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
    11. Prompt-assembly wiring gaps (mv_prompt_assembly_wiring_gaps)

All tables are physical (DROP + CREATE AS SELECT), idempotent, and snapshot-stamped via
    (SELECT value FROM meta WHERE key='commit_sha') AS snapshot_id
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


def _validate_sqlite_path(sqlite_path: Path) -> Path:
    sqlite_path = sqlite_path.expanduser().resolve()
    if not sqlite_path.exists():
        raise FileNotFoundError(f"ADG SQLite not found: {sqlite_path}")
    if not sqlite_path.is_file():
        raise ValueError(f"ADG SQLite path is not a file: {sqlite_path}")
    return sqlite_path


def _connect_sqlite(sqlite_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(_validate_sqlite_path(sqlite_path)), timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


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
    "mv_prompt_assembly_wiring_gaps",
    "mv_handoff_witness_tiers",
    "mv_cross_cutting_witness_tiers",
    "mv_local_heal_first_breaches",
    "mv_observability_interference_breaches",
)

_SPINE_LAYERS = ("L0", "L1", "L2", "L3", "L4", "L5", "L6")

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
    conn = _connect_sqlite(sqlite_path)
    conn.execute("PRAGMA cache_size = -64000")  # 64MB cache for MV queries
    conn.execute("PRAGMA temp_store = MEMORY")
    cur = conn.cursor()

    # Performance-critical composite indexes for all materialized view phases.
    # Additive (IF NOT EXISTS) — persist in the SQLite and benefit all phases.
    cur.execute("CREATE INDEX IF NOT EXISTS idx_nodes_resolved_path ON nodes(resolved_path)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_nodes_entity_layer ON nodes(entity_type, layer)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_edges_dst_rel ON edges(dst_id, relation_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_edges_src_rel ON edges(src_id, relation_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_edges_source_file ON edges(source_file)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_violations_edge_id ON violations(edge_id)")

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
                    JOIN nodes dst2 ON dst2.id = e2.dst_id
                    JOIN nodes src2 ON src2.id = e2.src_id
                    WHERE dst2.resolved_path = n.resolved_path
                      AND src2.resolved_path != n.resolved_path
                      AND e2.relation_type IN ('imports', 'calls')
                      AND src2.layer IN {_spine_layers_in()}
                ) THEN 1
            END)                  AS connected_count,
            COUNT(n.id) - COUNT(CASE
                WHEN EXISTS (
                    SELECT 1 FROM edges e2
                    JOIN nodes dst2 ON dst2.id = e2.dst_id
                    JOIN nodes src2 ON src2.id = e2.src_id
                    WHERE dst2.resolved_path = n.resolved_path
                      AND src2.resolved_path != n.resolved_path
                      AND e2.relation_type IN ('imports', 'calls')
                      AND src2.layer IN {_spine_layers_in()}
                ) THEN 1
            END)                  AS gap_count,
            ROUND(
                CAST(
                    COUNT(n.id) - COUNT(CASE
                        WHEN EXISTS (
                            SELECT 1 FROM edges e2
                            JOIN nodes dst2 ON dst2.id = e2.dst_id
                            JOIN nodes src2 ON src2.id = e2.src_id
                            WHERE dst2.resolved_path = n.resolved_path
                              AND src2.resolved_path != n.resolved_path
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
          -- Primitive-provider exemption (Author-Gate 2026-04-23):
          -- config/* and types/* subdirectories expose pure constants/Enums/dataclasses
          -- that are legitimately shared across layers. Functional cross-layer calls
          -- (enforcement/*, reasoning/*, orchestration/*) remain flagged.
          AND dst.resolved_path NOT LIKE '%/config/%'
          AND dst.resolved_path NOT LIKE '%/types/%'
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
    # Fix: Aggregate at symbol level first (edges reference symbols, not modules),
    # then roll up to module level via resolved_path.
    cur.execute("DROP TABLE IF EXISTS _t_symbol_inbound")
    cur.execute("DROP TABLE IF EXISTS _t_symbol_outbound")

    # Pre-aggregate inbound edges at symbol level by resolved_path
    cur.execute("""
        CREATE TEMP TABLE _t_symbol_inbound AS
        SELECT
            sym.resolved_path AS file_path,
            COUNT(DISTINCT e.id) AS fan_in
        FROM edges e
        JOIN nodes sym ON e.dst_id = sym.id
        WHERE e.relation_type IN ('imports', 'calls')
        AND sym.resolved_path IS NOT NULL
        GROUP BY sym.resolved_path
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS _idx_sym_in ON _t_symbol_inbound(file_path)")

    # Pre-aggregate outbound edges at symbol level by resolved_path
    cur.execute("""
        CREATE TEMP TABLE _t_symbol_outbound AS
        SELECT
            sym.resolved_path AS file_path,
            COUNT(DISTINCT e.id) AS fan_out
        FROM edges e
        JOIN nodes sym ON e.src_id = sym.id
        WHERE e.relation_type IN ('imports', 'calls')
        AND sym.resolved_path IS NOT NULL
        GROUP BY sym.resolved_path
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS _idx_sym_out ON _t_symbol_outbound(file_path)")

    cur.execute(f"""
        CREATE TABLE mv_hotspot_centrality AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.adg_name            AS adg_name,
            n.layer               AS layer,
            n.resolved_path       AS resolved_path,
            COALESCE(fi.fan_in, 0)   AS fan_in,
            COALESCE(fo.fan_out, 0)  AS fan_out,
            COALESCE(fi.fan_in, 0) + COALESCE(fo.fan_out, 0) AS degree,
            ROUND(
                CAST(COALESCE(fi.fan_in, 0) AS REAL)
                * CAST(COALESCE(fo.fan_out, 0) AS REAL)
                / NULLIF((SELECT COUNT(*) FROM nodes WHERE entity_type='module'), 0),
            4)                    AS betweenness_approx,
            ROUND(
                CAST(COALESCE(fi.fan_in, 0) AS REAL)
                / NULLIF((SELECT COUNT(*) FROM nodes WHERE entity_type='module'), 0),
            4)                    AS degree_centrality
        FROM nodes n
        LEFT JOIN _t_symbol_inbound fi ON fi.file_path = n.resolved_path
        LEFT JOIN _t_symbol_outbound fo ON fo.file_path = n.resolved_path
        WHERE n.entity_type = 'module'
        GROUP BY n.id
        ORDER BY fan_in DESC
    """)

    cur.execute("DROP TABLE IF EXISTS _t_symbol_inbound")
    cur.execute("DROP TABLE IF EXISTS _t_symbol_outbound")

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

    # -------------------------------------------------------------------------
    # Family 11 — Prompt-assembly runtime wiring gaps
    # -------------------------------------------------------------------------

    # mv_prompt_assembly_wiring_gaps
    # For each module in the prompt-assembly subsystem (dispatcher, bridge, contracts,
    # evidence-contract surface), count live (non-test) callers separately from
    # test-only callers.
    #
    # gap_type = 'disconnected'  =>  module is built and test-covered but has
    #                                zero live runtime callers — the exact
    #                                negative-space pattern that was previously
    #                                undetectable by SC-5 / AP-14 / mv_unknown_taxonomy_and_orphans.
    cur.execute("DROP TABLE IF EXISTS mv_prompt_assembly_wiring_gaps")
    cur.execute(f"""
        CREATE TABLE mv_prompt_assembly_wiring_gaps AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.adg_name            AS target_symbol,
            n.resolved_path       AS target_file,
            n.layer               AS layer,
            COUNT(DISTINCT e.id)  AS total_callers,
            COUNT(DISTINCT CASE
                WHEN c.resolved_path NOT LIKE 'tests/%'
                 AND c.resolved_path NOT LIKE 'test_%'
                THEN e.id END)    AS live_callers,
            COUNT(DISTINCT CASE
                WHEN c.resolved_path LIKE 'tests/%'
                  OR c.resolved_path LIKE 'test_%'
                THEN e.id END)    AS test_callers,
            CASE
                WHEN COUNT(DISTINCT CASE
                    WHEN c.resolved_path NOT LIKE 'tests/%'
                     AND c.resolved_path NOT LIKE 'test_%'
                    THEN e.id END) = 0
                THEN 'disconnected'
                ELSE 'ok'
            END                   AS gap_type
        FROM nodes n
        LEFT JOIN edges e  ON e.dst_id = n.id AND e.relation_type = 'imports'
        LEFT JOIN nodes c  ON c.id = e.src_id
        WHERE n.entity_type = 'module'
          AND n.resolved_path NOT LIKE 'tests/%'
          AND (
              n.resolved_path LIKE 'tools/adg/prompt_assembly/%'
           OR n.resolved_path LIKE '%c0_evidence_contract_types%'
           OR n.resolved_path LIKE '%c0_dispatcher%'
           OR n.resolved_path LIKE '%c0_bridge_adapter%'
          )
        GROUP BY n.id
        ORDER BY live_callers ASC, total_callers DESC
    """)
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_pa_wiring_gap "
        "ON mv_prompt_assembly_wiring_gaps(gap_type, live_callers, test_callers)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_pa_wiring_snapshot ON mv_prompt_assembly_wiring_gaps(snapshot_id)"
    )

    # -------------------------------------------------------------------------
    # Family 12 — Handoff witness tiers (runtime-spine Phase 2)
    # -------------------------------------------------------------------------

    # mv_handoff_witness_tiers
    # For each of the 17 architecture-handoff relation types, classify ADG edges
    # into three witness tiers:
    #   plumbing  — graph_persister.py / lifecycle_trace_contract.py (bootstrap proof)
    #   test      — tests/ prefix (coverage proof)
    #   live_rt   — all other production-code edges (runtime-spine obligation)
    # runtime_orphaned = 1 when extraction is wired and (plumbing OR test) exists
    #                     but live_runtime_witness_count = 0
    cur.execute("DROP TABLE IF EXISTS mv_handoff_witness_tiers")
    cur.execute(f"""
        CREATE TABLE mv_handoff_witness_tiers AS
        WITH handoff_rels AS (
            SELECT 'validates_request'           AS relation_type,
                   'mv_ingress_before_anything'  AS view_name
            UNION ALL SELECT 'produces_plan',            'mv_l1_plan_before_route'
            UNION ALL SELECT 'proposes_route',            'mv_l1_plan_before_route'
            UNION ALL SELECT 'prefilters_scope',          'mv_retrieval_evidence_handoff'
            UNION ALL SELECT 'produces_evidence_contract','mv_retrieval_evidence_handoff'
            UNION ALL SELECT 'packages_prompt_envelope',  'mv_evidence_to_prompt_handoff'
            UNION ALL SELECT 'stamps_execution_packet',   'mv_governed_execution_envelope_continuity'
            UNION ALL SELECT 'propagates_policy_hash',    'mv_governed_execution_envelope_continuity'
            UNION ALL SELECT 'propagates_replay_key',     'mv_governed_execution_envelope_continuity'
            UNION ALL SELECT 'publishes_retrieval_surface','mv_governed_execution_envelope_continuity'
            UNION ALL SELECT 'promotes_future_run_change','mv_governed_execution_envelope_continuity'
            UNION ALL SELECT 'seals_result',              'mv_runtime_exit_continuity'
            UNION ALL SELECT 'chooses_exit_disposition',  'mv_runtime_exit_continuity'
            UNION ALL SELECT 'materializes_hitl_packet',  'mv_runtime_exit_continuity'
            UNION ALL SELECT 'reclears_human_decision',   'mv_runtime_exit_continuity'
            UNION ALL SELECT 'verifies_blast_radius',     'mv_runtime_exit_continuity'
            UNION ALL SELECT 'appends_commit_receipt',    'mv_runtime_exit_continuity'
        ),
        tier_counts AS (
            SELECT
                hr.relation_type,
                hr.view_name,
                COALESCE(SUM(CASE
                    WHEN e.source_file IN (
                        'agentic_core/adg/extraction/graph_persister.py',
                        'agentic_core/runtime/contracts/lifecycle_trace_contract.py'
                    ) THEN 1 ELSE 0 END), 0) AS plumbing_witness_count,
                COALESCE(SUM(CASE
                    WHEN e.source_file LIKE 'tests/%'
                    THEN 1 ELSE 0 END), 0)   AS test_witness_count,
                COALESCE(SUM(CASE
                    WHEN e.source_file NOT IN (
                        'agentic_core/adg/extraction/graph_persister.py',
                        'agentic_core/runtime/contracts/lifecycle_trace_contract.py'
                    ) AND e.source_file NOT LIKE 'tests/%'
                    THEN 1 ELSE 0 END), 0)   AS live_runtime_witness_count
            FROM handoff_rels hr
            LEFT JOIN edges e ON e.relation_type = hr.relation_type
            GROUP BY hr.relation_type, hr.view_name
        )
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            relation_type,
            view_name,
            plumbing_witness_count,
            test_witness_count,
            live_runtime_witness_count,
            CASE WHEN (plumbing_witness_count + test_witness_count + live_runtime_witness_count) = 0
                 THEN 1 ELSE 0 END AS zero_witness_count,
            CASE WHEN (plumbing_witness_count > 0 OR test_witness_count > 0)
                  AND live_runtime_witness_count = 0
                 THEN 1 ELSE 0 END AS built_plus_test_or_plumbing_covered_plus_runtime_orphaned,
            CASE WHEN (plumbing_witness_count + test_witness_count + live_runtime_witness_count) > 0
                  AND (plumbing_witness_count > 0 OR test_witness_count > 0)
                  AND live_runtime_witness_count = 0
                 THEN 1 ELSE 0 END AS runtime_orphaned
        FROM tier_counts
        ORDER BY view_name, relation_type
    """)
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_handoff_witness_rt_orphaned"
        " ON mv_handoff_witness_tiers(runtime_orphaned, view_name)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_handoff_witness_snapshot ON mv_handoff_witness_tiers(snapshot_id)"
    )

    # -------------------------------------------------------------------------
    # Family 13 — Cross-cutting witness tiers (all architectural obligation families)
    # -------------------------------------------------------------------------

    # mv_cross_cutting_witness_tiers
    # Same witness-tier model as mv_handoff_witness_tiers but covering all 13
    # cross-cutting architectural obligation families:
    #
    #   1.  capability_egress_chokepoint       — capability token + egress route proof
    #   2.  local_heal_first                   — local healer dispatches before escalation
    #   3.  heal_retry_under_blueprint         — orchestrator retries under same blueprint
    #   4.  exit_hitl_envelope_continuity      — exit packet sealed + HITL cleared
    #   5.  hitl_freeze_materialize_reclear    — context frozen before HITL, recleared after
    #   6.  commit_uwg_envelope_continuity     — blast-radius checked + receipt appended
    #   7.  uwg_full_commit_chain              — full UWG validation + durable commit
    #   8.  no_direct_write_live_planes        — writes route through UWG, no bypass
    #   9.  replay_envelope_continuity         — RNG/time sealed + replay key emitted
    #   10. observability_non_interference     — observability reads only, no side-effects
    #   11. future_run_only_promotion          — promotion gated + committed via DPO
    #   12. offline_publication_before_runtime — surface published offline before runtime reads
    #   13. retrieval_surface_integrity        — retrieval indexed, guardrailed, routed
    #
    # Tier semantics identical to mv_handoff_witness_tiers:
    #   plumbing  — graph_persister.py + lifecycle_trace_contract.py (bootstrap proof)
    #   test      — tests/* prefix (coverage proof)
    #   live_rt   — all other production-code edges (runtime-spine obligation)
    cur.execute("DROP TABLE IF EXISTS mv_cross_cutting_witness_tiers")
    cur.execute(f"""
        CREATE TABLE mv_cross_cutting_witness_tiers AS
        WITH cross_cutting_rels AS (
            -- 1. capability_egress_chokepoint
            SELECT 'capability_egress_chokepoint'  AS family_name,
                   'routes_to_capability'           AS relation_type
            UNION ALL SELECT 'capability_egress_chokepoint', 'issues_capability_token'
            UNION ALL SELECT 'capability_egress_chokepoint', 'has_capability'
            UNION ALL SELECT 'capability_egress_chokepoint', 'validates_agent_capability'
            -- 2. local_heal_first
            UNION ALL SELECT 'local_heal_first',             'dispatches_healing_run'
            UNION ALL SELECT 'local_heal_first',             'confirms_heal'
            UNION ALL SELECT 'local_heal_first',             'aborts_heal'
            -- 3. heal_retry_under_blueprint
            UNION ALL SELECT 'heal_retry_under_blueprint',   'orchestrates_healing'
            UNION ALL SELECT 'heal_retry_under_blueprint',   'heals'
            -- 4. exit_hitl_envelope_continuity
            UNION ALL SELECT 'exit_hitl_envelope_continuity', 'seals_result'
            UNION ALL SELECT 'exit_hitl_envelope_continuity', 'chooses_exit_disposition'
            UNION ALL SELECT 'exit_hitl_envelope_continuity', 'materializes_hitl_packet'
            UNION ALL SELECT 'exit_hitl_envelope_continuity', 'reclears_human_decision'
            -- 5. hitl_freeze_materialize_reclear
            UNION ALL SELECT 'hitl_freeze_materialize_reclear', 'freezes_context'
            UNION ALL SELECT 'hitl_freeze_materialize_reclear', 'escalates_to_human'
            UNION ALL SELECT 'hitl_freeze_materialize_reclear', 'awaits_approval'
            UNION ALL SELECT 'hitl_freeze_materialize_reclear', 'requires_human_review'
            UNION ALL SELECT 'hitl_freeze_materialize_reclear', 'learns_from_decision'
            -- 6. commit_uwg_envelope_continuity
            UNION ALL SELECT 'commit_uwg_envelope_continuity', 'verifies_blast_radius'
            UNION ALL SELECT 'commit_uwg_envelope_continuity', 'appends_commit_receipt'
            UNION ALL SELECT 'commit_uwg_envelope_continuity', 'commits_mutation'
            UNION ALL SELECT 'commit_uwg_envelope_continuity', 'distributes_mutation'
            -- 7. uwg_full_commit_chain
            UNION ALL SELECT 'uwg_full_commit_chain',         'validates_uwg_intent'
            UNION ALL SELECT 'uwg_full_commit_chain',         'checks_policy_hash_at_uwg'
            UNION ALL SELECT 'uwg_full_commit_chain',         'validates_blast_radius_at_uwg'
            UNION ALL SELECT 'uwg_full_commit_chain',         'performs_durable_commit'
            UNION ALL SELECT 'uwg_full_commit_chain',         'applies_hmac_seal'
            UNION ALL SELECT 'uwg_full_commit_chain',         'packages_execution_trace'
            UNION ALL SELECT 'uwg_full_commit_chain',         'appends_hash_chain'
            -- 8. no_direct_write_live_planes
            UNION ALL SELECT 'no_direct_write_live_planes',   'routes_through_uwg'
            UNION ALL SELECT 'no_direct_write_live_planes',   'bypasses_uwg'
            UNION ALL SELECT 'no_direct_write_live_planes',   'execution_terminates_at_uwg'
            -- 9. replay_envelope_continuity
            UNION ALL SELECT 'replay_envelope_continuity',    'guards_replay'
            UNION ALL SELECT 'replay_envelope_continuity',    'seeds_rng'
            UNION ALL SELECT 'replay_envelope_continuity',    'patches_time'
            UNION ALL SELECT 'replay_envelope_continuity',    'emits_replay_key'
            UNION ALL SELECT 'replay_envelope_continuity',    'compares_proof'
            UNION ALL SELECT 'replay_envelope_continuity',    'emits_determinism_digest'
            -- 10. observability_non_interference
            UNION ALL SELECT 'observability_non_interference', 'observes_policy_state'
            UNION ALL SELECT 'observability_non_interference', 'observes_runtime_state'
            UNION ALL SELECT 'observability_non_interference', 'snapshots_state'
            UNION ALL SELECT 'observability_non_interference', 'intercepts_io'
            UNION ALL SELECT 'observability_non_interference', 'transcripts_response'
            UNION ALL SELECT 'observability_non_interference', 'hard_fails_untranscripted'
            -- 11. future_run_only_promotion
            UNION ALL SELECT 'future_run_only_promotion',     'promotes_future_run_change'
            UNION ALL SELECT 'future_run_only_promotion',     'gates_promotion'
            UNION ALL SELECT 'future_run_only_promotion',     'commits_optimization'
            UNION ALL SELECT 'future_run_only_promotion',     'builds_dpo_batch'
            -- 12. offline_publication_before_runtime
            UNION ALL SELECT 'offline_publication_before_runtime', 'publishes_retrieval_surface'
            UNION ALL SELECT 'offline_publication_before_runtime', 'reads_materialized_surface'
            UNION ALL SELECT 'offline_publication_before_runtime', 'materializes_read_view'
            -- 13. retrieval_surface_integrity
            UNION ALL SELECT 'retrieval_surface_integrity',   'indexes_for_retrieval'
            UNION ALL SELECT 'retrieval_surface_integrity',   'retrieves_via'
            UNION ALL SELECT 'retrieval_surface_integrity',   'retrieves_from_store'
            UNION ALL SELECT 'retrieval_surface_integrity',   'applies_retrieval_guardrail'
            UNION ALL SELECT 'retrieval_surface_integrity',   'routes_retrieval'
        ),
        tier_counts AS (
            SELECT
                cr.family_name,
                cr.relation_type,
                COALESCE(SUM(CASE
                    WHEN e.source_file IN (
                        'agentic_core/adg/extraction/graph_persister.py',
                        'agentic_core/runtime/contracts/lifecycle_trace_contract.py'
                    ) THEN 1 ELSE 0 END), 0) AS plumbing_witness_count,
                COALESCE(SUM(CASE
                    WHEN e.source_file LIKE 'tests/%'
                    THEN 1 ELSE 0 END), 0)   AS test_witness_count,
                COALESCE(SUM(CASE
                    WHEN e.source_file NOT IN (
                        'agentic_core/adg/extraction/graph_persister.py',
                        'agentic_core/runtime/contracts/lifecycle_trace_contract.py'
                    ) AND e.source_file NOT LIKE 'tests/%'
                    THEN 1 ELSE 0 END), 0)   AS live_runtime_witness_count
            FROM cross_cutting_rels cr
            LEFT JOIN edges e ON e.relation_type = cr.relation_type
            GROUP BY cr.family_name, cr.relation_type
        )
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            family_name,
            relation_type,
            plumbing_witness_count,
            test_witness_count,
            live_runtime_witness_count,
            CASE WHEN (plumbing_witness_count + test_witness_count + live_runtime_witness_count) = 0
                 THEN 1 ELSE 0 END AS zero_witness_count,
            CASE WHEN (plumbing_witness_count > 0 OR test_witness_count > 0)
                  AND live_runtime_witness_count = 0
                 THEN 1 ELSE 0 END AS built_plus_test_or_plumbing_covered_plus_runtime_orphaned,
            CASE WHEN (plumbing_witness_count + test_witness_count + live_runtime_witness_count) > 0
                  AND (plumbing_witness_count > 0 OR test_witness_count > 0)
                  AND live_runtime_witness_count = 0
                 THEN 1 ELSE 0 END AS runtime_orphaned
        FROM tier_counts
        ORDER BY family_name, relation_type
    """)
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_cc_witness_rt_orphaned"
        " ON mv_cross_cutting_witness_tiers(runtime_orphaned, family_name)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_cc_witness_snapshot ON mv_cross_cutting_witness_tiers(snapshot_id)"
    )

    # -------------------------------------------------------------------------
    # Family 14 — Class B breach surfaces (absence/forbidden-path semantics)
    # -------------------------------------------------------------------------

    # mv_local_heal_first_breaches
    # Identifies heal-domain production modules that have escalation edges
    # (escalates_failure, escalates_to_human) but NO local-heal-first relations
    # (dispatches_healing_run, confirms_heal, aborts_heal) in the same source file.
    # Zero rows = no breach (PASSED). Any rows = forbidden path detected.
    cur.execute("DROP TABLE IF EXISTS mv_local_heal_first_breaches")
    cur.execute(f"""
        CREATE TABLE mv_local_heal_first_breaches AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            e.source_file,
            e.relation_type         AS escalation_relation,
            COUNT(DISTINCT e.id)    AS breach_edge_count,
            CASE WHEN EXISTS (
                SELECT 1 FROM edges e2
                WHERE e2.source_file = e.source_file
                  AND e2.relation_type IN (
                      'dispatches_healing_run', 'confirms_heal', 'aborts_heal'
                  )
            ) THEN 0 ELSE 1 END    AS missing_heal_first_in_file
        FROM edges e
        WHERE e.relation_type IN ('escalates_failure', 'escalates_to_human')
          AND e.source_file NOT LIKE 'tests/%'
          AND e.source_file NOT IN (
              'agentic_core/adg/extraction/graph_persister.py',
              'agentic_core/runtime/contracts/lifecycle_trace_contract.py'
          )
          AND (
              e.source_file LIKE '%heal%'
              OR e.source_file LIKE '%retry%'
              OR e.source_file LIKE '%recovery%'
          )
        GROUP BY e.source_file, e.relation_type
        HAVING missing_heal_first_in_file = 1
        ORDER BY breach_edge_count DESC
    """)
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_local_heal_breach"
        " ON mv_local_heal_first_breaches(source_file, escalation_relation)"
    )

    # mv_observability_interference_breaches
    # Identifies production source files that have BOTH observability relations
    # (observes_*, snapshots_state, intercepts_io, transcripts_response,
    #  hard_fails_untranscripted) AND mutation/write relations
    # (commits_mutation, performs_durable_commit, applies_hmac_seal, bypasses_uwg,
    #  routes_through_uwg).
    # Any such file is a forbidden-path breach: observability code with side-effects.
    # Zero rows = no breach (PASSED).
    cur.execute("DROP TABLE IF EXISTS mv_observability_interference_breaches")
    cur.execute(f"""
        CREATE TABLE mv_observability_interference_breaches AS
        SELECT
            {_snapshot_id_expr()}        AS snapshot_id,
            obs_e.source_file,
            COUNT(DISTINCT obs_e.id)     AS observability_edge_count,
            COUNT(DISTINCT mut_e.id)     AS mutation_edge_count
        FROM edges obs_e
        JOIN edges mut_e ON mut_e.source_file = obs_e.source_file
        WHERE obs_e.relation_type IN (
            'observes_policy_state', 'observes_runtime_state', 'snapshots_state',
            'intercepts_io', 'transcripts_response', 'hard_fails_untranscripted'
        )
          AND mut_e.relation_type IN (
            'commits_mutation', 'performs_durable_commit', 'applies_hmac_seal',
            'bypasses_uwg', 'routes_through_uwg'
          )
          AND obs_e.source_file NOT LIKE 'tests/%'
          AND obs_e.source_file NOT IN (
              'agentic_core/adg/extraction/graph_persister.py',
              'agentic_core/runtime/contracts/lifecycle_trace_contract.py'
          )
        GROUP BY obs_e.source_file
        HAVING observability_edge_count > 0 AND mutation_edge_count > 0
        ORDER BY mutation_edge_count DESC
    """)
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_obs_interference"
        " ON mv_observability_interference_breaches(source_file)"
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
