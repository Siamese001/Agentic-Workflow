"""One-off debug: C0.3 skills graph SQLite usage for exec_summary run."""

from __future__ import annotations

from pathlib import Path

from agentic_core.L4_state.adapters.sqlite3_adapter import Connection, Row
from apps_rg.fact_inventory.augmented_skills_graph_sqlite import open_graph_sqlite

REPO = Path(__file__).resolve().parents[2]
DB = REPO / "artifacts/apps_rg/fact_inventory/augmented_skills_graph.sqlite"
ROLE_FAMILY = "INSURANCE_BROKERAGE_IT_INNOVATION"
SECTION = "executive_summary"
FACT_IDS = [
    "fact_governance_003",
    "fact_certs_001",
    "fact_quant_hpc_003",
    "fact_engineering_platform_001",
    "fact_exec_002",
    "fact_engineering_platform_006",
    "fact_solutions_002",
    "fact_revenue_ops_001",
    "fact_quant_hpc_001",
]

# Skill nodes bound in run receipt (from c0_evidence_room_receipt c03.bindings)
BOUND_SKILLS = sorted(
    {
        "skill_agent_to_human_handoff_design",
        "skill_approval_gated_workflow_design",
        "skill_capital_regulatory_capital",
        "skill_exit_disposition_governance",
        "skill_fail_closed_gate_semantics",
        "skill_instruction_data_boundary_design",
        "skill_learning_firewall_controls",
        "skill_metadata_acl_freshness_filtering",
        "skill_no_bypass_proof_controls",
        "skill_no_direct_write_runtime_design",
        "skill_policy_bound_runtime_design",
        "skill_risk_and_hitl_route_posture",
        "skill_sr_basel_ccar_lineage_regulatory",
        "skill_static_governance_drift_detection",
        "skill_x1_x2_x3_exit_control",
        "skill_actuarial_fsa_fellowship",
        "skill_capital_capital_modeling",
        "skill_derivatives_derivatives_pricing",
        "skill_greeks_hedging_multi_greek_hedging",
        "skill_agentic_control_plane_design",
        "skill_app_overlay_runtime_binding",
        "skill_app_specific_runtime_overlay_design",
        "skill_authority_ordered_prompt_packaging",
        "skill_bounded_agent_execution",
        "skill_dense_sparse_exact_retrieval_design",
        "skill_deterministic_route_selection",
        "skill_governed_agentic_systems_architecture",
        "skill_graph_aware_relationship_grounding",
        "skill_layered_runtime_spine_design",
        "skill_managed_workflow_orchestration",
        "skill_replayable_runtime_design",
        "skill_reusable_ai_ip_design",
        "skill_route_contract_design",
        "skill_route_replay_and_idempotency_design",
        "skill_runtime_gate_mesh_design",
        "skill_sandboxed_execution_design",
        "skill_side_effect_bounded_action_design",
        "skill_sr_cloud_data_platform_engineering",
        "skill_agentic_platform_productization",
        "skill_p2_tech_reusable_accelerators",
        "skill_reusable_agentic_platform_architecture",
        "skill_ai_platform_commercialization",
        "skill_enterprise_workflow_adoption",
        "skill_p2_tech_reference_architecture",
        "skill_sr_w12_industry_reference_architecture",
        "skill_p2_gtm_discovery_qualification",
        "skill_revops_salesforce_pipeline_analytics",
    }
)


def _open_debug_connection(*, db_path: Path = DB) -> Connection:
    """Open this legacy diagnostic through the governed read-only graph adapter."""
    conn = open_graph_sqlite(repo_root=REPO, db_path=db_path, read_only=True)
    conn.row_factory = Row
    return conn


def main() -> None:
    conn = _open_debug_connection()
    cur = conn.cursor()

    meta = cur.execute(
        "SELECT graph_version, ledger_hash, graph_count_summary, authority_status FROM graph_metadata LIMIT 1"
    ).fetchone()
    print("=== graph_metadata ===")
    print(dict(meta) if meta else "MISSING")

    prof = cur.execute(
        """
        SELECT role_family_id, projection_role_family_key, track_weight_profile
        FROM role_family_projection
        WHERE role_family_id = ? OR projection_role_family_key = ?
        LIMIT 1
        """,
        (ROLE_FAMILY, ROLE_FAMILY),
    ).fetchone()
    print("\n=== role_family_projection ===")
    print(dict(prof) if prof else "NOT FOUND")

    ph = ",".join("?" * len(FACT_IDS))
    links = cur.execute(
        f"""
        SELECT skill_id, fact_id, support_level, claim_eligibility, external_eligible
        FROM skill_fact_links
        WHERE fact_id IN ({ph})
        ORDER BY fact_id, claim_eligibility DESC, skill_id
        """,
        tuple(FACT_IDS),
    ).fetchall()
    print(f"\n=== skill_fact_links for run facts ({len(links)} rows) ===")
    by_fact: dict[str, list] = {}
    for r in links:
        by_fact.setdefault(r["fact_id"], []).append(dict(r))
    for fid in FACT_IDS:
        rows = by_fact.get(fid, [])
        print(f"\n{fid}: {len(rows)} links")
        for row in rows:
            used = row["skill_id"] in BOUND_SKILLS
            mark = "USED" if used else "not_in_binding"
            print(f"  [{mark}] {row['skill_id']} claim_elig={row['claim_eligibility']}")

    sk_ph = ",".join("?" * len(BOUND_SKILLS))

    edge_types = [
        r[0] for r in cur.execute("SELECT DISTINCT edge_type FROM graph_edges ORDER BY 1 LIMIT 30").fetchall()
    ]
    print("\n=== distinct edge_type (sample) ===", edge_types)

    edges = cur.execute(
        f"""
        SELECT edge_id, source_node_id, target_node_id, edge_type, weight
        FROM graph_edges
        WHERE target_node_id IN ({ph})
          AND source_node_id IN ({sk_ph})
        ORDER BY target_node_id, source_node_id
        """,
        (*FACT_IDS, *BOUND_SKILLS),
    ).fetchall()
    print(f"\n=== graph_edges skill->fact for bound skills ({len(edges)} rows) ===")
    for r in edges:
        used = r["source_node_id"] in BOUND_SKILLS
        mark = "USED" if used else "extra"
        print(f"  [{mark}] {r['edge_id']}: {r['source_node_id']} -> {r['target_node_id']}")

    skills = cur.execute(
        f"""
        SELECT node_id, label, support_level, activation_status, external_eligible
        FROM graph_nodes
        WHERE node_type = 'skill' AND node_id IN ({sk_ph})
        ORDER BY node_id
        """,
        tuple(BOUND_SKILLS),
    ).fetchall()
    print(f"\n=== graph_nodes (skill) for bound refs ({len(skills)}/{len(BOUND_SKILLS)}) ===")
    for r in skills[:5]:
        print(" ", dict(r))
    if len(skills) > 5:
        print(f"  ... +{len(skills) - 5} more")

    emp = cur.execute(
        """
        SELECT edge_id, source_node_id, target_node_id, edge_type
        FROM graph_edges
        WHERE edge_type = 'employment_hosts'
          AND target_node_id IN (
            'fact_certs_001','fact_engineering_platform_001','fact_governance_003','fact_quant_hpc_003'
          )
        ORDER BY edge_id
        """
    ).fetchall()
    print(f"\n=== employment_hosts edges in expansion ({len(emp)}) ===")
    for r in emp:
        print(f"  {r['edge_id']}: {r['source_node_id']} -> {r['target_node_id']}")

    bridge = cur.execute(
        """
        SELECT edge_id, source_node_id, target_node_id, edge_type
        FROM graph_edges
        WHERE edge_type IN ('pillar_phase_bridge','pillar_section_eligibility','career_track_contains_pillar')
        LIMIT 15
        """
    ).fetchall()
    print(f"\n=== bridge edge sample ({len(bridge)} shown max 15) ===")
    for r in bridge:
        print(f"  {r['edge_type']}: {r['source_node_id']} -> {r['target_node_id']}")

    conn.close()


if __name__ == "__main__":
    main()
