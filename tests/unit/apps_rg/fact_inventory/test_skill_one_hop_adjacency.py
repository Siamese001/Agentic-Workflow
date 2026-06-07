"""Unit tests for C03 1-hop skill adjacency in augmented_skills_graph projection."""
from __future__ import annotations

from apps_rg.fact_inventory.augmented_skills_graph import (
    _build_skill_one_hop_adjacency_index,
    build_verified_skill_inventory_projection,
)


def _synthetic_graph() -> dict:
    return {
        "skill_rows": [
            {"skill_id": "skill_a", "allowed_sections": ["competencies"], "activation_status": "ACTIVE",
             "support_level": "DERIVED_SUPPORTED", "fact_id_links": ["fact_a"], "allowed_phrases": ["a"]},
            {"skill_id": "skill_b", "allowed_sections": ["competencies"], "activation_status": "ACTIVE",
             "support_level": "DERIVED_SUPPORTED", "fact_id_links": ["fact_b"], "allowed_phrases": ["b"]},
            {"skill_id": "skill_c", "allowed_sections": ["competencies"], "activation_status": "ACTIVE",
             "support_level": "DERIVED_SUPPORTED", "fact_id_links": ["fact_c"], "allowed_phrases": ["c"]},
            {"skill_id": "skill_orphan", "allowed_sections": ["competencies"], "activation_status": "ACTIVE",
             "support_level": "DERIVED_SUPPORTED", "fact_id_links": ["fact_o"], "allowed_phrases": ["o"]},
        ],
        "graph_edges": [
            {
                "edge_type": "capability_domain_contains_skill",
                "source_node_id": "domain_x",
                "target_node_id": "skill_a",
            },
            {
                "edge_type": "capability_domain_contains_skill",
                "source_node_id": "domain_x",
                "target_node_id": "skill_b",
            },
            {
                "edge_type": "capability_domain_contains_skill",
                "source_node_id": "domain_y",
                "target_node_id": "skill_c",
            },
            {
                "edge_type": "unrelated_edge",
                "source_node_id": "domain_x",
                "target_node_id": "skill_c",
            },
        ],
    }


def test_adjacency_co_members_under_shared_domain() -> None:
    idx = _build_skill_one_hop_adjacency_index(_synthetic_graph())
    assert "skill_b" in idx["skill_a"]
    assert "skill_a" in idx["skill_b"]
    assert idx["skill_a"] == sorted(idx["skill_a"])
    assert "skill_a" not in idx["skill_a"]


def test_adjacency_orphan_skill_has_no_neighbors() -> None:
    idx = _build_skill_one_hop_adjacency_index(_synthetic_graph())
    # Orphan skills are omitted from the index when they have no domain co-members.
    assert "skill_orphan" not in idx


def test_adjacency_caps_neighbors_at_five() -> None:
    graph = {
        "skill_rows": [{"skill_id": f"skill_{i}"} for i in range(7)],
        "graph_edges": [
            {
                "edge_type": "capability_domain_contains_skill",
                "source_node_id": "domain_big",
                "target_node_id": f"skill_{i}",
            }
            for i in range(7)
        ],
    }
    idx = _build_skill_one_hop_adjacency_index(graph)
    assert len(idx["skill_0"]) == 5


def test_projection_surfaces_adjacent_skill_ids() -> None:
    proj = build_verified_skill_inventory_projection(
        section_id="competencies",
        graph=_synthetic_graph(),
    )
    skills = (proj.get("verified_skill_inventory_projection") or {}).get("skills") or []
    by_id = {s["skill_id"]: s for s in skills if isinstance(s, dict)}
    assert by_id["skill_a"].get("adjacent_skill_ids") == ["skill_b"]
    assert by_id["skill_orphan"].get("adjacent_skill_ids") == []
