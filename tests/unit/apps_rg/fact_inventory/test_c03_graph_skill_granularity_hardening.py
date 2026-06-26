from __future__ import annotations

# apps-test-model: APP CONTRACT

import copy
import json
from pathlib import Path

from apps_rg.fact_inventory.apply_c03_graph_skill_granularity_hardening import apply_hardening, validate_zero_loss
from apps_rg.fact_inventory.validate_c03_graph_skill_granularity import validate_graph
from apps_rg.runtime.graph.graph_metric_diversity_policy import rank_with_metric_diversity, build_metric_diversity_receipt


def _catalog() -> dict:
    path = Path("apps_rg/fact_inventory/c03_graph_skill_granularity_catalog.json")
    return json.loads(path.read_text(encoding="utf-8"))


def _minimal_graph() -> dict:
    return {
        "graph_metadata": {"schema_version": "test"},
        "graph_nodes": [
            {"node_id": "track_genai_agentic", "node_type": "career_track"},
            {"node_id": "track_data_tech_cloud_ml", "node_type": "career_track"},
            {"node_id": "track_actuarial_risk_derivatives", "node_type": "career_track"},
        ],
        "graph_edges": [],
        "skill_rows": [
            {
                "skill_id": "existing_skill_latency",
                "allowed_phrases": ["latency optimization"],
                "pillar": "latency",
                "fact_id_links": ["fact_existing_latency_001"],
                "activation_status": "ACTIVE",
            }
        ],
    }


def test_apply_hardening_is_zero_loss_and_idempotent() -> None:
    before = _minimal_graph()
    first = apply_hardening(copy.deepcopy(before), _catalog())["graph"]
    errors = validate_zero_loss(before, first)
    assert errors == []
    second = apply_hardening(copy.deepcopy(first), _catalog())["graph"]
    assert len(second["graph_nodes"]) == len(first["graph_nodes"])
    assert len(second["graph_edges"]) == len(first["graph_edges"])
    assert len(second["skill_rows"]) == len(first["skill_rows"])


def test_validate_graph_requires_metric_diversity_policy() -> None:
    hardened = apply_hardening(_minimal_graph(), _catalog())["graph"]
    assert validate_graph(hardened) == []


def test_apply_hardening_emits_full_w4a_shape_fields() -> None:
    hardened = apply_hardening(_minimal_graph(), _catalog())["graph"]
    required_node_fields = {
        "node_id",
        "node_type",
        "label",
        "description",
        "support_level",
        "visibility_rule",
        "activation_status",
        "evidence_risk",
        "source_refs",
        "projection_behavior",
        "external_claim_policy",
    }
    required_edge_fields = {
        "edge_id",
        "edge_type",
        "source_node_id",
        "target_node_id",
        "rationale",
        "projection_behavior",
        "external_claim_policy",
        "validation_status",
    }
    required_skill_row_fields = {
        "skill_id",
        "fact_id_links",
        "pillar",
        "subpillar",
        "career_stage",
        "source_resume_files",
        "source_snippets",
        "user_confirmed",
        "support_level",
        "role_family_weights",
        "allowed_phrases",
        "forbidden_phrases",
        "allowed_sections",
        "visibility_rule",
        "evidence_risk",
        "activation_status",
        "human_confirmation_required",
    }
    added_nodes = [n for n in hardened["graph_nodes"] if n.get("hardening_wave") == "C03_GRAPH_SKILL_GRANULARITY_V1"]
    added_edges = [e for e in hardened["graph_edges"] if e.get("hardening_wave") == "C03_GRAPH_SKILL_GRANULARITY_V1"]
    added_skill_rows = [
        row for row in hardened["skill_rows"] if row.get("hardening_wave") == "C03_GRAPH_SKILL_GRANULARITY_V1"
    ]
    assert added_nodes
    assert added_edges
    assert added_skill_rows
    assert all(required_node_fields <= set(node) for node in added_nodes)
    assert all(required_edge_fields <= set(edge) for edge in added_edges)
    assert all(required_skill_row_fields <= set(row) for row in added_skill_rows)
    assert all(row["support_level"] == "INTERNAL_ONLY" for row in added_skill_rows)
    assert all(row["activation_status"] == "ACTIVE_CONFIRMED" for row in added_skill_rows)


def test_metric_diversity_ranking_penalizes_repeated_buckets() -> None:
    candidates = [
        {"skill_id": "a", "metric_bucket": "latency", "score": 1.0},
        {"skill_id": "b", "metric_bucket": "risk_control", "score": 0.95},
    ]
    ranked = rank_with_metric_diversity(candidates, already_selected=[{"metric_bucket": "latency"}])
    assert ranked[0]["skill_id"] == "b"
    receipt = build_metric_diversity_receipt(ranked)
    assert receipt["distinct_metric_bucket_count"] == 2
