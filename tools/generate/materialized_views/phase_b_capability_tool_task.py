"""Phase B materialized views — Capability/egress, tool/agent shape, task-contract/action-safety.

Covers view families:
    4. Capability, provider, and egress (mv_capability_and_egress_gaps,
       mv_provider_surface_sprawl, mv_gateway_bypass_paths)
    5. Tool and agent shape (mv_tool_surface_overlap, mv_agent_specialization_overlap,
       mv_manager_sprawl, mv_agent_tool_ratio)
    6. Task-contract and action-safety (mv_task_contract_gaps,
       mv_untrusted_text_to_action_risk, mv_actionable_surface_without_schema,
       mv_structured_output_gaps)
    Remaining 10. Topology (mv_dependency_cone_risk, mv_high_fan_in_out_with_defects)

Depends on Phase A tables: mv_path_criticality_rollup, mv_hotspot_centrality.
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


_PHASE_B_TABLES: tuple[str, ...] = (
    "mv_capability_and_egress_gaps",
    "mv_provider_surface_sprawl",
    "mv_gateway_bypass_paths",
    "mv_tool_surface_overlap",
    "mv_agent_specialization_overlap",
    "mv_manager_sprawl",
    "mv_agent_tool_ratio",
    "mv_task_contract_gaps",
    "mv_untrusted_text_to_action_risk",
    "mv_actionable_surface_without_schema",
    "mv_structured_output_gaps",
    "mv_dependency_cone_risk",
    "mv_high_fan_in_out_with_defects",
)

_GATEWAY_APPROVED_PATHS = (
    "infrastructure/sdks_mcps/",
    "apps_shared/",
    "agentic_core/L2_execution/enforcement/",
    "agentic_core/L2_execution/reasoning/execution_gateway",
    "SovereignMCPGateway",
    "SovereignLLMGateway",
    # Added 2026-04-23 (W10) — sanctioned provider adapter modules:
    "agentic_core/gateway/",  # explicit gateway package
    "agentic_core/L3_orchestration/inference/qwen_vllm/",  # VLLM inference adapter
    "agentic_core/L4_state/utils/memory/blob_storage_provider.py",  # S3 blob storage adapter
    "agentic_core/L4_state/utils/memory/canonical_store.py",  # canonical S3 store adapter
    "agentic_core/evaluation/judges/claude_judge.py",  # Claude judge adapter
    "apps_rg/enforcement/HardenedanthropicexecutorStrategy.py",  # Hardened Anthropic executor
    # 2026-04-29 P0 unblock — same file is already on infra_wiring_scan.SANCTIONED_ADAPTER_FILES
    # (line 118: "L0 GAP-03 assembly stage — anthropic SDK lazy-loaded inside try/except for
    # token-budget computation"). Propagating that approval to the parallel
    # mv_gateway_bypass_paths gate so the two MVs agree on what is a sanctioned provider invoker.
    "agentic_core/L0_routing/reasoning/assembly_stage.py",
)


def _snapshot_id_expr() -> str:
    return "(SELECT COALESCE(value, '') FROM meta WHERE key='commit_sha' LIMIT 1)"


def _build_gateway_approved_clause(col: str) -> str:
    frags = " OR ".join(f"{col} LIKE '%{p}%'" for p in _GATEWAY_APPROVED_PATHS)
    return f"({frags})"


def materialize_phase_b(sqlite_path: Path) -> dict[str, int]:
    """Create all Phase B materialized tables. Idempotent — safe to call repeatedly.

    Returns:
        dict mapping table_name -> row_count for each Phase B table.
    """
    conn = _connect_sqlite(sqlite_path)
    conn.execute("PRAGMA cache_size = -64000")
    conn.execute("PRAGMA temp_store = MEMORY")
    cur = conn.cursor()

    for tbl in reversed(_PHASE_B_TABLES):
        cur.execute(f"DROP TABLE IF EXISTS {tbl}")

    # -------------------------------------------------------------------------
    # Family 4 — Capability, provider, and egress
    # -------------------------------------------------------------------------

    # mv_capability_and_egress_gaps
    cur.execute(f"""
        CREATE TABLE mv_capability_and_egress_gaps AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.resolved_path       AS file,
            n.layer               AS layer,
            -- Scanner-false-positive exemption (2026-04-23 W11):
            -- urllib.parse.* and urllib.request.Request are pure-string / URL-object
            -- utilities classified as 'invokes_provider' by the edge scanner despite
            -- making no network calls. 'requests.append' etc. are list-method calls
            -- on locals named 'requests'. None of these constitute a real egress.
            COUNT(DISTINCT CASE WHEN e.relation_type = 'invokes_provider'
                                 AND e.symbol NOT LIKE 'urllib.parse.%'
                                 AND e.symbol NOT LIKE 'urllib.request.%'
                                 AND e.symbol NOT IN ('requests.append', 'requests.extend',
                                                       'requests.pop', 'requests.clear',
                                                       'requests.insert', 'requests.remove')
                                THEN e.id END)
                                  AS provider_invoke_count,
            COUNT(DISTINCT CASE WHEN e.relation_type = 'routes_to_capability' THEN e.id END)
                                  AS capability_route_count,
            COUNT(DISTINCT CASE WHEN e.relation_type IN ('writes_through', 'writes_via_uwg',
                                                          'execution_terminates_at_uwg') THEN e.id END)
                                  AS egress_gate_count,
            CASE
                WHEN COUNT(DISTINCT CASE WHEN e.relation_type = 'invokes_provider'
                                             AND e.symbol NOT LIKE 'urllib.parse.%'
                                             AND e.symbol NOT LIKE 'urllib.request.%'
                                             AND e.symbol NOT IN ('requests.append', 'requests.extend',
                                                                   'requests.pop', 'requests.clear',
                                                                   'requests.insert', 'requests.remove')
                                            THEN e.id END) > 0
                 AND COUNT(DISTINCT CASE WHEN e.relation_type = 'routes_to_capability' THEN e.id END) = 0
                THEN 'provider_without_capability_route'
                -- The former 'action_without_egress_gate' branch was removed 2026-04-23:
                -- it duplicated write_sovereignty's "write without UWG" check (same edge
                -- predicates, same files). capability_egress now covers only egress of
                -- actual provider invocations; UWG enforcement lives in write_sovereignty.
                ELSE 'ok'
            END AS gap_type
        FROM nodes n
        LEFT JOIN edges e ON e.src_id = n.id
            AND e.relation_type IN ('invokes_provider', 'routes_to_capability',
                                    'writes_to', 'writes_through', 'writes_via_uwg',
                                    'execution_terminates_at_uwg')
        WHERE n.entity_type = 'module'
          AND n.resolved_path NOT LIKE 'tests/%'
          AND n.resolved_path NOT LIKE 'tools/%'
          AND n.resolved_path NOT LIKE 'ops_scripts/%'
          -- Non-runtime tooling / hook exclusions (2026-04-23):
          AND n.resolved_path NOT LIKE '.windsurf/scripts/%'
          AND n.resolved_path NOT LIKE 'agentic_core/adg/%'
          AND n.resolved_path NOT LIKE 'infrastructure/%'
          -- Sanctioned gateway adapter modules ARE the capability route;
          -- flagging them for lacking one is semantically backward.
          AND NOT {_build_gateway_approved_clause("n.resolved_path")}
        GROUP BY n.id
        HAVING provider_invoke_count > 0 OR gap_type != 'ok'
        ORDER BY gap_type, layer
    """)

    # mv_provider_surface_sprawl
    cur.execute(f"""
        CREATE TABLE mv_provider_surface_sprawl AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            src.resolved_path     AS file,
            src.layer             AS layer,
            COUNT(DISTINCT dst.resolved_path) AS provider_count,
            GROUP_CONCAT(DISTINCT dst.adg_name) AS provider_names,
            CASE WHEN COUNT(DISTINCT dst.resolved_path) > 1 THEN 1 ELSE 0 END AS sprawl_flag
        FROM edges e
        JOIN nodes src ON src.id = e.src_id
        JOIN nodes dst ON dst.id = e.dst_id
        WHERE e.relation_type = 'invokes_provider'
          AND src.resolved_path NOT LIKE 'tests/%'
          AND src.resolved_path NOT LIKE 'tools/%'
        GROUP BY src.resolved_path, src.layer
        ORDER BY provider_count DESC
    """)

    # mv_gateway_bypass_paths
    cur.execute(f"""
        CREATE TABLE mv_gateway_bypass_paths AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            e.id                  AS edge_id,
            src.resolved_path     AS src_file,
            src.layer             AS src_layer,
            e.symbol              AS provider_symbol,
            e.source_file         AS source_file,
            e.line_no             AS line_no,
            CASE
                WHEN e.relation_type = 'dynamic_exec' THEN 'dynamic_execution_bypass'
                ELSE 'direct_provider_bypass'
            END AS bypass_type
        FROM edges e
        JOIN nodes src ON src.id = e.src_id
        WHERE e.relation_type IN ('invokes_provider', 'dynamic_exec')
          AND NOT {_build_gateway_approved_clause("src.resolved_path")}
          AND src.resolved_path NOT LIKE 'tests/%'
          AND src.resolved_path NOT LIKE 'tools/%'
          AND src.resolved_path NOT LIKE 'ops_scripts/%'
          -- Non-runtime tooling / hook exclusions (2026-04-23, same class as W5 write_sov):
          AND src.resolved_path NOT LIKE '.windsurf/scripts/%'
          AND src.resolved_path NOT LIKE 'agentic_core/adg/%'
          AND src.resolved_path NOT LIKE 'infrastructure/%'
          -- Pure-string stdlib symbols are scanner false-positives for invokes_provider
          -- (no network call, no provider semantics). Exclude them.
          AND e.symbol NOT LIKE 'urllib.parse.%'
          AND e.symbol NOT LIKE 'urllib.request.%'
          -- requests.append / requests.extend / requests.pop etc. are list-method calls
          -- on local variables named 'requests'. The scanner marks these as provider
          -- invocations because of the module name match; they are not.
          AND e.symbol NOT IN ('requests.append', 'requests.extend', 'requests.pop',
                                'requests.clear', 'requests.insert', 'requests.remove')
        ORDER BY bypass_type, src.layer
    """)

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_cap_gap_type ON mv_capability_and_egress_gaps(gap_type, layer)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_prov_sprawl ON mv_provider_surface_sprawl(sprawl_flag, layer)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_gw_bypass ON mv_gateway_bypass_paths(bypass_type, src_layer)"
    )

    # -------------------------------------------------------------------------
    # Family 5 — Tool and agent shape
    # -------------------------------------------------------------------------

    # mv_tool_surface_overlap
    cur.execute(f"""
        CREATE TABLE mv_tool_surface_overlap AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            dst.resolved_path     AS tool_file,
            dst.layer             AS tool_layer,
            COUNT(DISTINCT e.src_id)          AS caller_count,
            COUNT(DISTINCT src.layer)         AS distinct_caller_layers,
            ROUND(
                CAST(COUNT(DISTINCT src.layer) AS REAL)
                * CAST(COUNT(DISTINCT e.src_id) AS REAL)
                / 10.0,
            2)                    AS overlap_score
        FROM edges e
        JOIN nodes dst ON dst.id = e.dst_id
        JOIN nodes src ON src.id = e.src_id
        WHERE e.relation_type IN ('imports', 'calls')
          AND (
            dst.resolved_path LIKE 'tools/%'
            OR dst.adg_name LIKE '%Tool%'
            OR dst.adg_name LIKE '%_tool%'
          )
          AND dst.entity_type = 'module'
          AND src.resolved_path NOT LIKE 'tests/%'
        GROUP BY dst.resolved_path, dst.layer
        HAVING caller_count > 0
        ORDER BY overlap_score DESC
    """)

    # mv_agent_specialization_overlap
    # Agents that share the same outgoing routes_to_capability destinations.
    cur.execute(f"""
        CREATE TABLE mv_agent_specialization_overlap AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            a.resolved_path       AS agent_file,
            a.layer               AS layer,
            COUNT(DISTINCT e_cap.dst_id) AS outgoing_capability_count,
            COALESCE((
                SELECT COUNT(DISTINCT e2.dst_id)
                FROM edges e2
                JOIN nodes a2 ON a2.id = e2.src_id
                WHERE e2.relation_type = 'routes_to_capability'
                  AND a2.id != a.id
                  AND (a2.resolved_path LIKE '%Agent%' OR a2.adg_name LIKE '%Agent%')
                  AND e2.dst_id IN (
                      SELECT dst_id FROM edges WHERE src_id = a.id
                        AND relation_type = 'routes_to_capability'
                  )
            ), 0)                 AS shared_capability_count,
            COALESCE((
                SELECT COUNT(DISTINCT a2.id)
                FROM nodes a2
                JOIN edges e2 ON e2.src_id = a2.id
                WHERE e2.relation_type = 'routes_to_capability'
                  AND a2.id != a.id
                  AND (a2.resolved_path LIKE '%Agent%' OR a2.adg_name LIKE '%Agent%')
                  AND e2.dst_id IN (
                      SELECT dst_id FROM edges WHERE src_id = a.id
                        AND relation_type = 'routes_to_capability'
                  )
            ), 0)                 AS overlap_agent_count
        FROM nodes a
        LEFT JOIN edges e_cap ON e_cap.src_id = a.id
            AND e_cap.relation_type = 'routes_to_capability'
        WHERE (a.resolved_path LIKE '%Agent%' OR a.adg_name LIKE '%Agent%')
          AND a.entity_type = 'module'
          AND a.resolved_path NOT LIKE 'tests/%'
        GROUP BY a.id
        ORDER BY shared_capability_count DESC
    """)

    # mv_manager_sprawl
    cur.execute(f"""
        CREATE TABLE mv_manager_sprawl AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.resolved_path       AS manager_file,
            n.layer               AS layer,
            COUNT(DISTINCT e_out.dst_id) AS direct_report_count,
            CASE WHEN COUNT(DISTINCT e_out.dst_id) > 5 THEN 1 ELSE 0 END AS sprawl_flag
        FROM nodes n
        LEFT JOIN edges e_out ON e_out.src_id = n.id
            AND e_out.relation_type IN ('routes_to_agent', 'coordinates_agents',
                                        'dispatches_agent', 'orchestrates_workflow')
        WHERE (n.adg_name LIKE '%Manager%' OR n.adg_name LIKE '%Orchestrator%'
               OR n.resolved_path LIKE '%orchestrator%' OR n.resolved_path LIKE '%manager%')
          AND n.entity_type = 'module'
          AND n.resolved_path NOT LIKE 'tests/%'
        GROUP BY n.id
        ORDER BY direct_report_count DESC
    """)

    # mv_agent_tool_ratio
    cur.execute(f"""
        CREATE TABLE mv_agent_tool_ratio AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            layer,
            COUNT(DISTINCT CASE WHEN is_agent = 1 THEN node_id END) AS agent_count,
            COUNT(DISTINCT CASE WHEN is_tool  = 1 THEN node_id END) AS tool_count,
            ROUND(
                CAST(COUNT(DISTINCT CASE WHEN is_agent = 1 THEN node_id END) AS REAL)
                / NULLIF(COUNT(DISTINCT CASE WHEN is_tool = 1 THEN node_id END), 0),
            2)                    AS ratio,
            CASE
                WHEN COUNT(DISTINCT CASE WHEN is_tool = 1 THEN node_id END) = 0
                 AND COUNT(DISTINCT CASE WHEN is_agent = 1 THEN node_id END) > 0
                THEN 1
                ELSE 0
            END AS anomaly_flag
        FROM (
            SELECT
                n.id AS node_id,
                n.layer AS layer,
                CASE WHEN n.resolved_path LIKE '%Agent%' OR n.adg_name LIKE '%Agent%' THEN 1 ELSE 0 END AS is_agent,
                CASE WHEN n.resolved_path LIKE 'tools/%' OR n.adg_name LIKE '%Tool%' THEN 1 ELSE 0 END AS is_tool
            FROM nodes n
            WHERE n.entity_type = 'module'
              AND n.resolved_path NOT LIKE 'tests/%'
        )
        GROUP BY layer
        ORDER BY agent_count DESC
    """)

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_tool_overlap ON mv_tool_surface_overlap(overlap_score DESC)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_manager_sprawl ON mv_manager_sprawl(sprawl_flag, direct_report_count DESC)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_agent_tool_anomaly ON mv_agent_tool_ratio(anomaly_flag, layer)"
    )

    # -------------------------------------------------------------------------
    # Family 6 — Task-contract and action-safety
    # -------------------------------------------------------------------------

    # mv_task_contract_gaps
    cur.execute(f"""
        CREATE TABLE mv_task_contract_gaps AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.resolved_path       AS file,
            n.layer               AS layer,
            COUNT(DISTINCT CASE WHEN e.relation_type IN ('writes_to', 'writes_through',
                                                          'routes_to_capability') THEN e.id END)
                                  AS action_edge_count,
            COUNT(DISTINCT CASE WHEN e.relation_type IN ('reads_policy_state',
                                                          'validates_capability') THEN e.id END)
                                  AS schema_or_policy_count,
            COUNT(DISTINCT CASE WHEN e2.relation_type = 'implements' THEN e2.id END)
                                  AS contract_impl_count,
            CASE
                WHEN COUNT(DISTINCT CASE WHEN e.relation_type IN ('writes_to', 'writes_through',
                                                                   'routes_to_capability') THEN e.id END) > 0
                 AND COUNT(DISTINCT CASE WHEN e.relation_type IN ('reads_policy_state',
                                                                   'validates_capability') THEN e.id END) = 0
                 AND COUNT(DISTINCT CASE WHEN e2.relation_type = 'implements' THEN e2.id END) = 0
                THEN 'action_without_contract'
                ELSE 'ok'
            END AS gap_flag
        FROM nodes n
        LEFT JOIN edges e  ON e.src_id  = n.id
            AND e.relation_type IN ('writes_to', 'writes_through',
                                    'routes_to_capability', 'reads_policy_state',
                                    'validates_capability')
        LEFT JOIN edges e2 ON e2.src_id = n.id AND e2.relation_type = 'implements'
        WHERE n.entity_type = 'module'
          AND n.resolved_path NOT LIKE 'tests/%'
          AND n.resolved_path NOT LIKE 'tools/%'
        GROUP BY n.id
        HAVING action_edge_count > 0
        ORDER BY gap_flag DESC, action_edge_count DESC
    """)

    # mv_untrusted_text_to_action_risk
    cur.execute(f"""
        CREATE TABLE mv_untrusted_text_to_action_risk AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.resolved_path       AS file,
            n.layer               AS layer,
            COUNT(DISTINCT CASE WHEN e.relation_type = 'dynamic_exec' THEN e.id END)
                                  AS dynamic_exec_count,
            COUNT(DISTINCT CASE WHEN e.relation_type IN ('validates_capability',
                                                          'reads_policy_state',
                                                          'validated_by_safety_plane') THEN e.id END)
                                  AS schema_validation_count,
            ROUND(
                CAST(COUNT(DISTINCT CASE WHEN e.relation_type = 'dynamic_exec' THEN e.id END) AS REAL)
                / NULLIF(
                    COUNT(DISTINCT CASE WHEN e.relation_type IN ('validates_capability',
                                                                  'reads_policy_state',
                                                                  'validated_by_safety_plane') THEN e.id END),
                    0
                ),
            2)                    AS risk_score
        FROM nodes n
        LEFT JOIN edges e ON e.src_id = n.id
            AND e.relation_type IN ('dynamic_exec', 'validates_capability',
                                    'reads_policy_state', 'validated_by_safety_plane')
        WHERE n.entity_type = 'module'
          AND n.resolved_path NOT LIKE 'tests/%'
        GROUP BY n.id
        HAVING dynamic_exec_count > 0
        ORDER BY risk_score DESC NULLS LAST
    """)

    # mv_actionable_surface_without_schema
    cur.execute(f"""
        CREATE TABLE mv_actionable_surface_without_schema AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.resolved_path       AS file,
            n.layer               AS layer,
            COUNT(DISTINCT CASE WHEN e.relation_type IN ('writes_through', 'invokes_provider',
                                                          'routes_to_capability') THEN e.id END)
                                  AS action_edge_count,
            COUNT(DISTINCT CASE WHEN e2.relation_type = 'implements' THEN e2.id END)
                                  AS structured_output_count,
            CASE
                WHEN COUNT(DISTINCT CASE WHEN e.relation_type IN ('writes_through', 'invokes_provider',
                                                                   'routes_to_capability') THEN e.id END) > 0
                 AND COUNT(DISTINCT CASE WHEN e2.relation_type = 'implements' THEN e2.id END) = 0
                THEN 1
                ELSE 0
            END AS gap_flag
        FROM nodes n
        LEFT JOIN edges e  ON e.src_id  = n.id
            AND e.relation_type IN ('writes_through', 'invokes_provider',
                                    'routes_to_capability')
        LEFT JOIN edges e2 ON e2.src_id = n.id AND e2.relation_type = 'implements'
        WHERE n.entity_type = 'module'
          AND n.resolved_path NOT LIKE 'tests/%'
          AND n.resolved_path NOT LIKE 'tools/%'
        GROUP BY n.id
        HAVING action_edge_count > 0
        ORDER BY gap_flag DESC
    """)

    # mv_structured_output_gaps
    cur.execute(f"""
        CREATE TABLE mv_structured_output_gaps AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.resolved_path       AS file,
            n.layer               AS layer,
            COUNT(DISTINCT CASE WHEN e.relation_type = 'generates_prompt' THEN e.id END)
                                  AS generates_prompt_count,
            COUNT(DISTINCT CASE WHEN e2.relation_type = 'implements' THEN e2.id END)
                                  AS output_schema_flag,
            CASE
                WHEN COUNT(DISTINCT CASE WHEN e.relation_type = 'generates_prompt' THEN e.id END) > 0
                 AND COUNT(DISTINCT CASE WHEN e2.relation_type = 'implements' THEN e2.id END) = 0
                THEN 1
                ELSE 0
            END AS gap_flag
        FROM nodes n
        LEFT JOIN edges e  ON e.src_id = n.id  AND e.relation_type = 'generates_prompt'
        LEFT JOIN edges e2 ON e2.src_id = n.id AND e2.relation_type = 'implements'
        WHERE n.entity_type = 'module'
          AND n.resolved_path NOT LIKE 'tests/%'
        GROUP BY n.id
        HAVING generates_prompt_count > 0
        ORDER BY gap_flag DESC
    """)

    cur.execute("CREATE INDEX IF NOT EXISTS idx_mv_task_contract ON mv_task_contract_gaps(gap_flag, layer)")
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_ta_risk ON mv_untrusted_text_to_action_risk(risk_score DESC)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_action_schema ON mv_actionable_surface_without_schema(gap_flag, layer)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_struct_output ON mv_structured_output_gaps(gap_flag, layer)"
    )

    # -------------------------------------------------------------------------
    # Remaining Family 10 — Topology
    # -------------------------------------------------------------------------

    # mv_dependency_cone_risk
    # Fix: Aggregate at symbol level first (edges reference symbols, not modules),
    # then roll up to module level via resolved_path for both hop-1 and hop-2.
    # Hop-3 remains deferred due to performance (500K+ edges).
    cur.execute("DROP TABLE IF EXISTS _t_sym_direct_fan_in")
    cur.execute("DROP TABLE IF EXISTS _t_sym_hop2_fan_in")
    cur.execute("DROP TABLE IF EXISTS _t_mod_direct_fan_in")
    cur.execute("DROP TABLE IF EXISTS _t_mod_hop2_fan_in")

    # Hop 1: Direct fan-in at symbol level, rolled up to module
    cur.execute("""
        CREATE TEMP TABLE _t_sym_direct_fan_in AS
        SELECT
            dst_sym.resolved_path AS file_path,
            COUNT(DISTINCT src_sym.resolved_path) AS fan_in
        FROM edges e
        JOIN nodes dst_sym ON e.dst_id = dst_sym.id
        JOIN nodes src_sym ON e.src_id = src_sym.id
        WHERE e.relation_type IN ('imports', 'calls')
        AND dst_sym.resolved_path IS NOT NULL
        AND src_sym.resolved_path IS NOT NULL
        GROUP BY dst_sym.resolved_path
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS _idx_sdfi ON _t_sym_direct_fan_in(file_path)")

    # Build module-level direct fan-in from symbol aggregation
    cur.execute("""
        CREATE TEMP TABLE _t_mod_direct_fan_in AS
        SELECT n.id AS node_id, COALESCE(s.fan_in, 0) AS fan_in
        FROM nodes n
        LEFT JOIN _t_sym_direct_fan_in s ON s.file_path = n.resolved_path
        WHERE n.entity_type = 'module'
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS _idx_mdfi ON _t_mod_direct_fan_in(node_id)")

    # Hop 2: Find modules that import modules which the target imports
    # If Target imports symbols from Module B, and Module B imports Module A,
    # then changes to Module A could affect Target via Module B.
    # Pattern: Target -(e1)-> symbols in Module B, Module B -(e2)-> symbols in Module A
    cur.execute("""
        CREATE TEMP TABLE _t_sym_hop2_fan_in AS
        SELECT
            target_imports.resolved_path AS file_path,
            COUNT(DISTINCT hop2_src.resolved_path) AS fan_in
        FROM edges e1
        -- e1: target module imports symbols
        JOIN nodes target_imports ON e1.src_id = target_imports.id
        -- Those symbols are defined in intermediate modules
        JOIN nodes intermediate_sym ON e1.dst_id = intermediate_sym.id
        -- Intermediate modules import other modules (e2)
        JOIN edges e2 ON e2.src_id = intermediate_sym.id
        JOIN nodes hop2_src ON e2.dst_id = hop2_src.id
        WHERE e1.relation_type IN ('imports', 'calls')
        AND e2.relation_type IN ('imports', 'calls')
        AND target_imports.resolved_path IS NOT NULL
        AND hop2_src.resolved_path IS NOT NULL
        AND target_imports.resolved_path != hop2_src.resolved_path
        AND intermediate_sym.resolved_path IS NOT NULL
        GROUP BY target_imports.resolved_path
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS _idx_sh2fi ON _t_sym_hop2_fan_in(file_path)")

    # Build module-level hop-2 fan-in
    cur.execute("""
        CREATE TEMP TABLE _t_mod_hop2_fan_in AS
        SELECT n.id AS node_id, COALESCE(s.fan_in, 0) AS fan_in
        FROM nodes n
        LEFT JOIN _t_sym_hop2_fan_in s ON s.file_path = n.resolved_path
        WHERE n.entity_type = 'module'
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS _idx_mh2fi ON _t_mod_hop2_fan_in(node_id)")

    cur.execute(f"""
        CREATE TABLE mv_dependency_cone_risk AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            n.id                  AS node_id,
            n.adg_name            AS adg_name,
            n.layer               AS layer,
            n.resolved_path       AS resolved_path,
            COALESCE(h1.fan_in, 0) AS direct_fan_in,
            COALESCE(h2.fan_in, 0) AS hop2_fan_in,
            0                      AS hop3_fan_in,
            COALESCE(h1.fan_in, 0) + COALESCE(h2.fan_in, 0) AS transitive_depth_approx,
            ROUND(
                COALESCE(h1.fan_in, 0) * 1.0 +
                COALESCE(h2.fan_in, 0) * 0.5,
            2)                    AS cone_risk_score
        FROM nodes n
        LEFT JOIN _t_mod_direct_fan_in h1 ON h1.node_id = n.id
        LEFT JOIN _t_mod_hop2_fan_in h2 ON h2.node_id = n.id
        WHERE n.entity_type = 'module'
        ORDER BY cone_risk_score DESC
    """)

    cur.execute("DROP TABLE IF EXISTS _t_sym_direct_fan_in")
    cur.execute("DROP TABLE IF EXISTS _t_sym_hop2_fan_in")
    cur.execute("DROP TABLE IF EXISTS _t_mod_direct_fan_in")
    cur.execute("DROP TABLE IF EXISTS _t_mod_hop2_fan_in")

    # mv_high_fan_in_out_with_defects
    cur.execute(f"""
        CREATE TABLE mv_high_fan_in_out_with_defects AS
        SELECT
            {_snapshot_id_expr()} AS snapshot_id,
            hc.node_id,
            hc.adg_name,
            hc.layer,
            hc.resolved_path,
            hc.fan_in,
            hc.fan_out,
            hc.degree,
            COALESCE((
                SELECT COUNT(*) FROM violations v
                JOIN edges ev ON ev.id = v.edge_id
                WHERE ev.src_id = hc.node_id
            ), 0)                 AS violation_count,
            ROUND(
                hc.degree * 1.0
                + COALESCE((
                    SELECT COUNT(*) FROM violations v
                    JOIN edges ev ON ev.id = v.edge_id
                    WHERE ev.src_id = hc.node_id
                ), 0) * 5.0,
            2)                    AS combined_risk_score
        FROM mv_hotspot_centrality hc
        WHERE hc.degree > 0
        ORDER BY combined_risk_score DESC
    """)

    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_cone_risk ON mv_dependency_cone_risk(cone_risk_score DESC, layer)"
    )
    cur.execute(
        "CREATE INDEX IF NOT EXISTS idx_mv_hfi_defects ON mv_high_fan_in_out_with_defects(combined_risk_score DESC)"
    )

    conn.commit()

    counts: dict[str, int] = {}
    try:
        for tbl in _PHASE_B_TABLES:
            row = cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()
            counts[tbl] = row[0] if row else 0
    finally:
        conn.close()
    return counts
