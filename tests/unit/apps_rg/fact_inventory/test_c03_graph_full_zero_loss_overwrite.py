from __future__ import annotations

from apps_rg.fact_inventory.apply_c03_graph_full_zero_loss_overwrite import apply_overwrite
from apps_rg.fact_inventory.graph_metric_heterogeneity_policy import (
    explicit_metric_bucket_for_row,
    infer_metric_bucket,
    metric_bucket_for_row,
)
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


def test_explicit_metric_bucket_wins_over_revenue_keyword_collision():
    row = {
        "skill_id": "skill_partner_sales_enablement",
        "metric_bucket": "partner_gtm",
        "allowed_phrases": ["partner sales enablement"],
        "source_snippets": ["Built partner sales motions with hyperscaler alliances."],
    }

    assert explicit_metric_bucket_for_row(row) == "partner_gtm"
    assert metric_bucket_for_row(row) == "partner_gtm"


def test_unknown_explicit_metric_bucket_falls_back_to_inference():
    row = {
        "skill_id": "skill_unknown_bucket",
        "metric_bucket": "not_a_known_bucket",
        "allowed_phrases": ["cost automation and savings"],
    }

    assert explicit_metric_bucket_for_row(row) is None
    assert metric_bucket_for_row(row) == "cost_efficiency"


def test_metric_bucket_inference_does_not_match_substrings():
    assert infer_metric_bucket("insurance carrier architecture") == "general_business_outcome"
    assert infer_metric_bucket("ARR growth and renewal motion") == "revenue_growth"
    assert infer_metric_bucket("pre-sales solution architecture") == "revenue_growth"
    assert infer_metric_bucket("agentic runtime route contract") == "platform_scale"
