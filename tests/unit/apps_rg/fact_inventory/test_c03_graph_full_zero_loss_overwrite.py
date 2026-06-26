from __future__ import annotations

# apps-test-model: APP CONTRACT

from apps_rg.fact_inventory.apply_c03_graph_full_zero_loss_overwrite import apply_overwrite
from apps_rg.fact_inventory.validate_c03_graph_hardening import validate_c03_graph_hardening_payload


def _base_payload():
    return {
        "metadata": {"w4a_hardened": True},
        "support_levels": ["DIRECT_FROM_RESUME_ARCHIVE", "INTERNAL_ONLY"],
        "visibility_rules": ["internal_runtime_only", "internal_runtime_and_resume_when_fact_backed"],
        "activation_statuses": ["ACTIVE_CONFIRMED"],
        "pillars": [],
        "skill_rows": [],
        "actuarial_career_matrix": {},
        "partner_gtm_matrix": {},
        "role_family_projection_profiles": {},
        "validation_rules": {},
        "graph_metadata": {},
        "graph_layers": [],
        "graph_nodes": [
            {
                "node_id": "existing_node",
                "node_type": "capability_domain",
                "label": "Existing",
                "description": "Existing node retained.",
                "support_level": "INTERNAL_ONLY",
                "visibility_rule": "internal_runtime_only",
                "activation_status": "ACTIVE_CONFIRMED",
                "evidence_risk": "LOW",
                "source_refs": [],
                "projection_behavior": "existing",
                "external_claim_policy": "internal_only",
            }
        ],
        "graph_edges": [
            {
                "edge_id": "existing_edge",
                "edge_type": "capability_domain_contains_skill",
                "source_node_id": "existing_node",
                "target_node_id": "existing_skill",
                "rationale": "Existing edge retained.",
                "projection_behavior": "existing",
                "external_claim_policy": "internal_only",
                "validation_status": "ACTIVE_CONFIRMED",
            }
        ],
        "external_claim_policies": [],
        "agentic_runtime_matrix": {},
        "agentic_capability_domains": [],
        "graph_validation_rules": {},
        "resume_generation_policy": {},
    }


def test_apply_overwrite_is_append_only_and_idempotent():
    payload = _base_payload()
    first = apply_overwrite(payload)
    second = apply_overwrite(payload)
    assert first["before"]["graph_nodes"] == 1
    assert first["after"]["graph_nodes"] > first["before"]["graph_nodes"]
    assert second["added_nodes"] == []
    assert second["added_skills"] == []
    assert second["added_edges"] == []
    assert any(n["node_id"] == "existing_node" for n in payload["graph_nodes"])
    assert any(e["edge_id"] == "existing_edge" for e in payload["graph_edges"])


def test_validation_passes_after_overwrite():
    payload = _base_payload()
    apply_overwrite(payload)
    receipt = validate_c03_graph_hardening_payload(payload)
    assert receipt["status"] == "PASS"
