"""W3 (apps-rg-insurtech-ey-unlock-a4c0f0) — InsurTech/EY grounded in own base-resume bullets.

Deterministic, hermetic. Guards that the insurtech/ey lanes source proof from the candidate's
verbatim, in-period base-resume employment bullets (bul_insurtech_* / bul_ey_*) — not the generic
substrate-ledger company-hint fallback — closing the REQUIRED_PROOF_ABSENT / empty-slice gap.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.section_graph_skills_proof_pool import (
    _ROLE_EPISODE_BASE_RESUME_NEEDLES,
    _base_resume_role_episode_plan,
)

REPO = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize(
    "section,needles,expected_ids",
    [
        ("insurtech_bullets", ("insurtech",), {"bul_insurtech_001", "bul_insurtech_002", "bul_insurtech_003"}),
        ("ey_bullets", ("ernst", "young"), {"bul_ey_001", "bul_ey_002", "bul_ey_003"}),
    ],
)
def test_planner_sources_own_base_resume_bullets(section, needles, expected_ids) -> None:
    result = _base_resume_role_episode_plan(section, needles=needles, limit=3, repo_root=REPO)
    assert result is not None, f"{section} planner returned None — base-resume bullets not found"
    plan, ordered, allowed = result
    fact_ids = {str(f["fact_id"]) for f in plan["facts"]}
    assert fact_ids == expected_ids, f"{section} fact ids {fact_ids} != {expected_ids}"
    assert set(ordered) == expected_ids
    assert expected_ids <= allowed
    assert plan["selection_method"] == f"base_resume_employment_{section}"
    # Every fact carries verbatim base-resume claim text and self-referential provenance.
    for f in plan["facts"]:
        assert f["claim_text"].strip(), "empty claim_text"
        assert f["source_fact_ids"] == [f["fact_id"]]
        assert f["srfs_verification_status"] == "BASE_RESUME_CANONICAL"


def test_needles_map_covers_four_role_episode_lanes() -> None:
    assert set(_ROLE_EPISODE_BASE_RESUME_NEEDLES) == {
        "insurtech_bullets",
        "insurtech_narrative",
        "ey_bullets",
        "ey_narrative",
    }


def test_planner_returns_none_for_unknown_employer() -> None:
    assert _base_resume_role_episode_plan(
        "insurtech_bullets", needles=("nonexistent_employer_xyz",), limit=3, repo_root=REPO
    ) is None


def test_planner_not_applied_to_ibm_or_unify() -> None:
    # IBM/Unify keep their dedicated graph-ranked planners; they must NOT be in the base-resume map.
    assert "ibm_bullets" not in _ROLE_EPISODE_BASE_RESUME_NEEDLES
    assert "unify_bullets" not in _ROLE_EPISODE_BASE_RESUME_NEEDLES


def test_end_to_end_proof_pool_nonempty_for_all_four_lanes() -> None:
    """Full proof resolution: insurtech/ey bullets+narrative no longer REQUIRED_PROOF_ABSENT."""
    from types import SimpleNamespace

    from apps_rg.runtime.c0.section_proof_loader import load_section_proof_for_lane

    args = SimpleNamespace(
        provider="external_claude", temperature=0.3, x1d_judges="", mock_judges=True,
        allow_test_mock_judges=True, allow_non_allow_exit_zero=True,
        target_title="VP Global Head of Agentic AI Solutions", target_company="AIG",
        target_role="VP", jd_text="Lead agentic AI platform strategy.",
        briefing="AIG agentic AI.", base_resume_ref="",
    )
    for sid in ("insurtech_bullets", "ey_bullets", "insurtech_narrative", "ey_narrative"):
        pool, *_ = load_section_proof_for_lane(section_id=sid, args=args, repo_root=REPO)
        facts = (pool.selected_fact_plan or {}).get("facts") or []
        allowed = pool.allowed_fact_ids_ordered or []
        assert len(facts) == 3, f"{sid}: expected 3 grounded facts, got {len(facts)}"
        assert len(allowed) == 3, f"{sid}: expected 3 allowed fact ids, got {len(allowed)}"
