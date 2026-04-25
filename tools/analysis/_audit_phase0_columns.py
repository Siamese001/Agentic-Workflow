"""Phase 0/2 ADG audit: column-level introspection for query design."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

DB = Path(r"C:\Git\Agentic-Workflow\artifacts\adg\adg_indexed_04252026_0521.sqlite")
GRAPH = Path(r"C:\Git\Agentic-Workflow\artifacts\adg\adg_graph_04252026_0520.sqlite")

KEY_TABLES = [
    "nodes",
    "edges",
    "violations",
    "overlay_violations",
    "side_effect_calls",
    "config_references",
    "boundary_strings",
    "module_entrypoints",
    "module_origins",
    "external_calls",
    "async_fire_and_forget",
    "mcp_config_servers",
    "mcp_tool_declarations",
    "test_stubs",
    "t_infra_importers",
    "snapshot_metadata",
    "meta",
]
KEY_MVS = [
    "mv_graph_reverse_dependency_hotspots",
    "mv_hotspot_centrality",
    "mv_graph_chokepoint_bridges",
    "mv_graph_critical_path_blast_radius",
    "mv_dependency_cone_risk",
    "mv_path_criticality_rollup",
    "mv_debt_concentration_hotspots",
    "mv_high_fan_in_out_with_defects",
    "mv_authority_boundary_breaches",
    "mv_gateway_bypass_paths",
    "mv_capability_and_egress_gaps",
    "mv_provider_surface_sprawl",
    "mv_new_provider_surfaces",
    "mv_new_write_bypass_paths",
    "mv_write_sovereignty_paths",
    "mv_replay_surface_gaps",
    "mv_determinism_provenance_drift",
    "mv_runtime_spine_gaps",
    "mv_prompt_assembly_wiring_gaps",
    "mv_exit_disposition_coverage",
    "mv_heal_retry_exit_gaps",
    "mv_hitl_reclearance_gaps",
    "mv_trace_replay_eval_gaps",
    "mv_task_contract_gaps",
    "mv_unknown_taxonomy_and_orphans",
    "mv_modified_area_regressions",
    "mv_new_cross_layer_dependencies",
    "mv_repeated_p3_near_critical_paths",
    "mv_exemptions_near_critical_paths",
    "mv_critical_path_segments",
    "mv_handoff_witness_tiers",
    "mv_cross_cutting_witness_tiers",
    "mv_manager_sprawl",
    "mv_agent_specialization_overlap",
]
KEY_PVIEWS = [
    "v_p0_apps_direct_infra",
    "v_p0_l0_raw_execution",
    "v_p0_l1_direct_infra",
    "v_p0_l6_mutation",
    "v_p0_provider_bypass",
    "v_p0_write_bypass_uwg",
    "v_p1_ad_hoc_imports",
    "v_p1_mis_layered_infra",
    "v_p1_not_on_spine",
    "v_p1_raw_http_outside_seam",
    "v_p1_zero_caller_infra",
    "v_p2_dormant_ambiguous",
    "v_p2_duplicated_adapters",
    "v_p2_mixed_usage",
    "v_p3_isolated_experimental",
]
GRAPH_TABLES = [
    "proj_nodes",
    "proj_centrality",
    "proj_reachability",
    "proj_violations",
    "proj_diff",
    "proj_meta",
]


def cols(con: sqlite3.Connection, name: str) -> list[str]:
    try:
        return [r[1] for r in con.execute(f"PRAGMA table_info({name})").fetchall()]
    except sqlite3.Error:
        return []


def main() -> int:
    out: dict = {"indexed": {}, "graph": {}}
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    for t in KEY_TABLES + KEY_MVS + KEY_PVIEWS:
        out["indexed"][t] = cols(con, t)
    # snapshot meta sample
    try:
        meta_rows = con.execute("SELECT key, value FROM meta").fetchall()
        out["indexed"]["_meta_kv"] = dict(meta_rows)
    except sqlite3.Error:
        pass
    try:
        snap = con.execute("SELECT * FROM snapshot_metadata LIMIT 6").fetchall()
        out["indexed"]["_snapshot_metadata"] = snap
    except sqlite3.Error:
        pass
    con.close()

    con = sqlite3.connect(f"file:{GRAPH}?mode=ro", uri=True)
    for t in GRAPH_TABLES:
        out["graph"][t] = cols(con, t)
    try:
        meta = con.execute("SELECT * FROM proj_meta").fetchall()
        out["graph"]["_proj_meta"] = meta
    except sqlite3.Error:
        pass
    con.close()
    print(json.dumps(out, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
