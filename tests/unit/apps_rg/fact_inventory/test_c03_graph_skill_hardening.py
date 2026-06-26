# apps-test-model: APP CONTRACT

from apps_rg.fact_inventory.c03_graph_skill_hardening import (
    build_graph_index,
    harden_c03_graph_expansion,
    infer_metric_bucket,
    traverse_between_nodes,
)


def _graph():
    return {
        "graph_metadata": {"schema_version": "test"},
        "skill_rows": [
            {"skill_id": "skill_agent_runtime", "pillar": "pillar_agentic", "activation_status": "ACTIVE", "fact_id_links": ["fact_latency"], "allowed_phrases": ["agent runtime latency"]},
            {"skill_id": "skill_governance", "pillar": "pillar_agentic", "activation_status": "ACTIVE", "fact_id_links": ["fact_risk"], "allowed_phrases": ["AI governance controls"]},
            {"skill_id": "skill_adoption", "pillar": "pillar_enablement", "activation_status": "ACTIVE", "fact_id_links": ["fact_adoption"], "allowed_phrases": ["field adoption"]},
            {"skill_id": "skill_revenue", "pillar": "pillar_gtm", "activation_status": "ACTIVE", "fact_id_links": ["fact_revenue"], "allowed_phrases": ["partner revenue"]},
            {"skill_id": "skill_quality", "pillar": "pillar_quality", "activation_status": "ACTIVE", "fact_id_links": ["fact_quality"], "allowed_phrases": ["model quality"]},
        ],
        "graph_edges": [
            {"edge_type": "career_track_contains_pillar", "source_node_id": "track_genai_agentic", "target_node_id": "pillar_agentic"},
            {"edge_type": "career_track_contains_pillar", "source_node_id": "track_data_tech_cloud_ml", "target_node_id": "pillar_gtm"},
            {"edge_type": "skill_supported_by_fact", "source_node_id": "skill_agent_runtime", "target_node_id": "fact_latency"},
            {"edge_type": "skill_supported_by_fact", "source_node_id": "skill_governance", "target_node_id": "fact_risk"},
            {"edge_type": "skill_supported_by_fact", "source_node_id": "skill_adoption", "target_node_id": "fact_adoption"},
            {"edge_type": "skill_supported_by_fact", "source_node_id": "skill_revenue", "target_node_id": "fact_revenue"},
            {"edge_type": "skill_supported_by_fact", "source_node_id": "skill_quality", "target_node_id": "fact_quality"},
        ],
    }


def test_metric_bucket_is_not_single_generic_bucket():
    assert infer_metric_bucket("30% latency reduction") == "latency_performance"
    assert infer_metric_bucket("$10M annual renewals") == "revenue_growth"
    assert infer_metric_bucket("audit-ready governance controls") == "risk_governance"


def test_reverse_traversal_binds_fact_to_skill():
    idx = build_graph_index(_graph())
    paths = traverse_between_nodes(idx, "fact_latency", ["skill_agent_runtime"], reverse=True)
    assert paths
    assert paths[0][0]["direction"] == "reverse"


def test_hardened_expansion_adds_receipts_and_guardrails():
    expansion = {
        "schema": "track_weighted_graph_expansion_v1",
        "tracks_with_facts": ["track_genai_agentic", "track_data_tech_cloud_ml"],
        "selected_skills": [
            {"skill_id": "skill_agent_runtime"},
            {"skill_id": "skill_governance"},
            {"skill_id": "skill_adoption"},
            {"skill_id": "skill_revenue"},
            {"skill_id": "skill_quality"},
        ],
        "selected_facts": [
            {"fact_id": "fact_latency", "skill_id": "skill_agent_runtime", "claim_text": "30% latency reduction"},
            {"fact_id": "fact_risk", "skill_id": "skill_governance", "claim_text": "audit-ready governance controls"},
            {"fact_id": "fact_adoption", "skill_id": "skill_adoption", "claim_text": "45% self-service adoption improvement"},
            {"fact_id": "fact_revenue", "skill_id": "skill_revenue", "claim_text": "$10M annual renewals"},
            {"fact_id": "fact_quality", "skill_id": "skill_quality", "claim_text": "20% model accuracy improvement"},
        ],
    }
    hardened = harden_c03_graph_expansion(expansion, _graph())
    assert hardened["c03_graph_traversal_depth_max"] == 4
    assert hardened["c03_reverse_deep_paths"]
    assert hardened["c03_frontier_receipt"]["frontier_size_by_depth"]
    assert hardened["c03_metric_heterogeneity_receipt"]["metric_bucket_count"] >= 5
