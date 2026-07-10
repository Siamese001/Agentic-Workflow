"""apps-test-model: APP CONTRACT."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.fact_inventory.master_skills_arsenal_ledger import load_master_skills_arsenal_ledger
from apps_rg.fact_inventory.track_weighted_graph_expansion import (
    build_track_weighted_expansion,
)
from apps_rg.runtime.graph.graph_skill_concentration_policy import (
    build_graph_skill_concentration_policy,
)
from apps_rg.runtime.sections.graph_role_episode_selector import (
    build_selected_graph_evidence_plan_for_section,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
GRAPH_PATH = REPO_ROOT / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"
INVESCO_JD = REPO_ROOT / "apps_rg/config/targeting/invesco_global_head_advanced_engineering_jd.txt"
INVESCO_BRIEF = REPO_ROOT / "apps_rg/config/targeting/invesco_global_head_advanced_engineering_briefing.md"
ANTHROPIC_JD = REPO_ROOT / "apps_rg/config/targeting/anthropic_manager_applied_ai_architecture_partnerships_jd.txt"
ANTHROPIC_BRIEF = REPO_ROOT / "tests/fixtures/apps_rg/anthropic_manager_applied_ai_architecture_partnerships_briefing.md"
SINGLE_TRACK_FIXTURE = REPO_ROOT / "docs/reports/apps_rg/fixtures/p1_w4_single_track_jd_fixture.json"


@pytest.fixture(scope="module")
def ledger() -> dict:
    return load_master_skills_arsenal_ledger(path=GRAPH_PATH)


@pytest.mark.parametrize(
    "counts, dominant_pct, proposed",
    [
        ({"track_a": 17, "track_b": 2, "track_c": 1}, 85.0, {"track_a": 80.0, "track_b": 12.5, "track_c": 7.5}),
        ({"track_a": 18, "track_b": 1, "track_c": 1}, 90.0, {"track_a": 80.0, "track_b": 10.0, "track_c": 10.0}),
        ({"track_a": 19, "track_b": 1, "track_c": 0}, 95.0, {"track_a": 80.0, "track_b": 12.5, "track_c": 7.5}),
        ({"track_a": 20, "track_b": 0, "track_c": 0}, 100.0, {"track_a": 80.0, "track_b": 10.0, "track_c": 10.0}),
    ],
)
def test_concentration_policy_matrix_hits_and_reallocates_from_over_threshold_percentages(
    counts: dict[str, int],
    dominant_pct: float,
    proposed: dict[str, float],
) -> None:
    policy = build_graph_skill_concentration_policy(
        counts=counts,
        distribution_kind="career_track",
        bucket_ids=("track_a", "track_b", "track_c"),
    )
    assert policy["policy_status"] == "hitl"
    assert policy["dominant_share_pct"] == pytest.approx(dominant_pct)
    assert policy["reallocation_feasible"] is True
    assert policy["rows"][0]["bucket_id"] == "track_a"
    assert policy["rows"][0]["current_share_pct"] == pytest.approx(dominant_pct)
    assert policy["rows"][0]["proposed_share_pct"] == pytest.approx(proposed["track_a"])
    assert policy["rows"][0]["delta_pp"] < 0.0
    assert policy["reallocation_proposal"]["proposed_share_pct_by_bucket"]["track_a"] == pytest.approx(
        proposed["track_a"]
    )
    assert policy["reallocation_proposal"]["proposed_share_pct_by_bucket"]["track_b"] == pytest.approx(
        proposed["track_b"]
    )
    assert policy["reallocation_proposal"]["proposed_share_pct_by_bucket"]["track_c"] == pytest.approx(
        proposed["track_c"]
    )

    hitl = build_graph_skill_concentration_policy(
        counts={"track_a": 20, "track_b": 0, "track_c": 0},
        distribution_kind="career_track",
        bucket_ids=("track_a", "track_b", "track_c"),
    )
    assert hitl["policy_status"] == "hitl"
    assert hitl["dominant_share_pct"] == pytest.approx(100.0)
    assert hitl["rows"][0]["bucket_id"] == "track_a"
    assert hitl["rows"][0]["current_share_pct"] == pytest.approx(100.0)
    assert hitl["rows"][0]["proposed_share_pct"] == pytest.approx(80.0)
    assert hitl["rows"][1]["proposed_share_pct"] == pytest.approx(10.0)
    assert hitl["rows"][2]["proposed_share_pct"] == pytest.approx(10.0)


def test_track_weighted_expansion_policy_flows_through_real_jds(ledger: dict) -> None:
    invesco_jd = INVESCO_JD.read_text(encoding="utf-8")
    invesco_brief = INVESCO_BRIEF.read_text(encoding="utf-8")
    invesco = build_track_weighted_expansion(
        graph=ledger,
        role_family_key="SVP_ENGINEERING_AI_PLATFORM",
        jd_text=invesco_jd,
        briefing_text=invesco_brief,
    )
    invesco_policy = invesco["concentration_policy"]
    assert invesco_policy["distribution_kind"] == "career_track"
    assert invesco_policy["policy_status"] == "ok"
    assert invesco_policy["dominant_bucket_id"] == "track_genai_agentic"
    assert invesco_policy["dominant_share_pct"] == pytest.approx(60.0, abs=0.1)
    assert invesco_policy["rows"][0]["bucket_id"] == "track_genai_agentic"
    assert invesco_policy["rows"][0]["current_share_pct"] == pytest.approx(60.0, abs=0.1)
    assert invesco_policy["rows"][0]["proposed_share_pct"] == pytest.approx(60.0, abs=0.1)

    single_fixture = json.loads(SINGLE_TRACK_FIXTURE.read_text(encoding="utf-8"))
    single = build_track_weighted_expansion(
        graph=ledger,
        role_family_key="QUANT_TRADING",
        jd_text=single_fixture["jd_text"],
        briefing_text="",
        weight_override=single_fixture["weight_override"],
        enforce_hybrid_contract=False,
        min_tracks_with_facts=1,
    )
    single_policy = single["concentration_policy"]
    assert single_policy["policy_status"] == "hitl"
    assert single_policy["dominant_bucket_id"] == "track_actuarial_risk_derivatives"
    assert single_policy["dominant_share_pct"] == pytest.approx(100.0)
    assert single_policy["reallocation_feasible"] is True
    assert single_policy["rows"][0]["proposed_share_pct"] == pytest.approx(80.0)
    assert single_policy["rows"][1]["proposed_share_pct"] == pytest.approx(10.0)
    assert single_policy["rows"][2]["proposed_share_pct"] == pytest.approx(10.0)


@pytest.mark.parametrize("section_id", ["headline", "competencies"])
def test_shared_section_plans_carry_the_same_matrix(section_id: str) -> None:
    jd_text = ANTHROPIC_JD.read_text(encoding="utf-8")
    brief_text = ANTHROPIC_BRIEF.read_text(encoding="utf-8")
    plan, ordered, allowed = build_selected_graph_evidence_plan_for_section(
        repo_root=REPO_ROOT,
        section_id=section_id,
        target_role=jd_text.split("\n", 1)[0],
        jd_text=jd_text,
        briefing_text=brief_text,
    )
    policy = plan["concentration_policy"]
    assert ordered
    assert allowed
    assert policy["distribution_kind"] == "employer_lane"
    assert policy["bucket_ids"] == ["unify", "ibm", "insurtech", "ey"]
    assert len(policy["rows"]) == 4
    assert policy["policy_status"] == "ok"
    assert policy["current_share_pct_by_bucket"]["ey"] >= 0.0
    assert policy["rows"][0]["rank"] == 1
