from __future__ import annotations

from apps_rg.fact_inventory import run_w14_senior_role_offline_traversal as w14


def test_target_role_and_match_rate_helpers() -> None:
    assert w14._target_role_from_jd("Chief Technology Officer \u2014 Remote\nBody") == (
        "Chief Technology Officer"
    )
    assert w14._target_role_from_jd("A" * 140) == "A" * 120
    assert w14._match_rate([], set()) == 1.0
    assert w14._match_rate(["pillar_a", "pillar_b"], {"pillar_b"}) == 0.5


def test_rank_pillars_sorts_by_count_weight_then_name() -> None:
    ranked = w14._rank_pillars(
        [
            {"pillar": "pillar_a", "weight": 2.0},
            {"pillar": "pillar_b", "weight": 6.0},
            {"pillar": "pillar_a", "weight": 3.0},
            {"pillar": "pillar_b", "weight": 5.0},
            {"pillar": "pillar_c", "weight": 100.0},
        ]
    )

    assert ranked == [
        {"pillar_id": "pillar_b", "skill_hits": 2, "weight_sum": 11.0, "rank": 1},
        {"pillar_id": "pillar_a", "skill_hits": 2, "weight_sum": 5.0, "rank": 2},
        {"pillar_id": "pillar_c", "skill_hits": 1, "weight_sum": 100.0, "rank": 3},
    ]


def test_bridge_families_filter_bridge_edges_and_return_unique_sorted_values() -> None:
    graph = {
        "graph_edges": [
            {
                "edge_type": "pillar_phase_bridge",
                "source_node_id": "pillar_a",
                "target_node_id": "phase_1",
                "bridge_edge_family": "phase_family",
            },
            {
                "edge_type": "pillar_section_eligibility",
                "source_node_id": "section_1",
                "target_node_id": "pillar_a",
                "bridge_edge_family": "section_family",
            },
            {
                "edge_type": "pillar_section_eligibility",
                "source_node_id": "section_2",
                "target_node_id": "pillar_a",
                "bridge_edge_family": "section_family",
            },
            {
                "edge_type": "unrelated",
                "source_node_id": "pillar_a",
                "target_node_id": "phase_2",
                "bridge_edge_family": "ignored_family",
            },
        ]
    }

    assert w14._bridge_families_for_pillars(graph, {"pillar_a"}) == [
        "phase_family",
        "section_family",
    ]


def test_merge_skill_selection_preserves_track_order_and_supplemental_source() -> None:
    merged = w14._merge_skill_selection(
        [
            {"skill_id": "skill_a", "pillar": "pillar_a"},
            {"skill_id": "skill_b", "pillar": "pillar_b", "traversal_source": "track_override"},
        ],
        [
            {"skill_id": "skill_a", "pillar": "pillar_a", "traversal_source": "manifest_supplemental"},
            {"skill_id": "skill_c", "pillar": "pillar_c", "traversal_source": "manifest_supplemental"},
        ],
    )

    assert [row["skill_id"] for row in merged] == ["skill_a", "skill_b", "skill_c"]
    assert merged[0]["traversal_source"] == "track_weighted"
    assert merged[1]["traversal_source"] == "track_override"
    assert merged[2]["traversal_source"] == "manifest_supplemental"


def test_forbidden_violations_catches_excluded_and_non_external_selections() -> None:
    violations = w14._forbidden_violations(
        slug="generic_role",
        selected_external_skills={"skill_excluded", "skill_draft", "skill_blocked_status"},
        rows_by_id={
            "skill_draft": {"support_level": "DRAFT", "activation_status": "ACTIVE"},
            "skill_blocked_status": {"support_level": "SUPPORTED", "activation_status": "BLOCKED"},
        },
        manifest_entry={"excluded_skill_ids": ["skill_excluded"]},
    )

    assert "excluded_skill_in_external_set:skill_excluded" in violations
    assert "non_external_support_in_selection:skill_draft" in violations
    assert "non_external_status_in_selection:skill_blocked_status" in violations


def test_classify_skill_uses_external_and_internal_eligibility(monkeypatch) -> None:
    monkeypatch.setattr(w14, "skill_row_eligible_for_external_claim", lambda row: row.get("external") is True)
    monkeypatch.setattr(w14, "skill_row_eligible_for_internal_ranking", lambda row: row.get("internal") is True)

    assert w14._classify_skill({"support_level": "DRAFT"}) == "blocked_internal_draft"
    assert w14._classify_skill({"external": True, "fact_id_links": ["F1"]}) == "evidence_backed"
    assert w14._classify_skill({"external": True, "fact_id_links": []}) == "directional_snippet_only"
    assert w14._classify_skill({"internal": True}) == "directional_internal_only"
    assert w14._classify_skill({}) == "blocked"
