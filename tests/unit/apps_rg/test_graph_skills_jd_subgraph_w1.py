"""W1: JD subgraph monotonic boost + rationale contract tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.fact_inventory.track_weighted_graph_expansion import resolve_career_track_weights
from apps_rg.runtime.graph_selection_rationale import (
    emit_graph_selection_rationale,
    extract_jd_keyword_hits,
    jd_track_weight_delta,
    reject_jd_only_skill_admission,
)

REPO = Path(__file__).resolve().parents[3]
BROWN_JD = (
    REPO / "apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt"
).read_text(encoding="utf-8")


def test_jd_keyword_hits_brown_it_strategy() -> None:
    hits = extract_jd_keyword_hits(BROWN_JD)
    tracks = {h["track_id"] for h in hits}
    assert "track_data_tech_cloud_ml" in tracks
    assert "track_genai_agentic" in tracks


def test_jd_boost_monotonic_track_weights_brown_role_family() -> None:
    role_family_key = "INSURANCE_BROKERAGE_IT_INNOVATION"
    audit = jd_track_weight_delta(role_family_key=role_family_key, jd_text=BROWN_JD)
    assert audit["jd_boost_monotonic"] is True
    for track in audit["jd_boosted_tracks"]:
        assert audit["weight_deltas"][track] >= -1e-9
    with_jd = audit["weights_with_jd"]
    without = audit["weights_without_jd"]
    assert with_jd["track_genai_agentic"] >= without["track_genai_agentic"]
    assert with_jd["track_data_tech_cloud_ml"] >= without["track_data_tech_cloud_ml"]


def test_resolve_career_track_weights_it_strategy_bump() -> None:
    base = resolve_career_track_weights(
        role_family_key="INSURANCE_BROKERAGE_IT_INNOVATION",
        jd_text="",
    )
    boosted = resolve_career_track_weights(
        role_family_key="INSURANCE_BROKERAGE_IT_INNOVATION",
        jd_text="enterprise architecture IT strategy innovation data platforms AI",
    )
    assert boosted["track_data_tech_cloud_ml"] >= base["track_data_tech_cloud_ml"]


def test_neg1_rejects_jd_only_skill_without_fact_links() -> None:
    row = reject_jd_only_skill_admission(
        skill_id="jd_inferred_skill",
        jd_text=BROWN_JD,
        fact_id_links=[],
    )
    assert row["admitted"] is False
    assert row["reason_code"] == "jd_only_or_empty_fact_id_links"


def test_emit_rationale_fixture_executive_summary() -> None:
    payload = emit_graph_selection_rationale(
        section_id="executive_summary",
        target_company="Brown & Brown",
        target_role="SVP IT Strategy & Innovation",
        jd_text=BROWN_JD,
        briefing_text="",
        repo_root=REPO,
    )
    assert payload["schema"] == "graph_selection_rationale_v1"
    assert payload["jd_subgraph_policy"]["jd_used_as_proof"] is False
    assert payload["jd_subgraph_policy"]["jd_shapes_ranking_only"] is True
    assert payload["track_weight_audit"]["jd_boost_monotonic"] is True
    assert payload["neg1_all_selected_skills_have_fact_links"] is True
