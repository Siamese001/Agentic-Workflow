"""InsurTech/EY role lanes use graph bundle proof, not base-resume bullets.

The base resume is retained as an identity spine only. Claim evidence for these lanes must come
from role_episode_bundle_id values (reb_insurtech_* / reb_ey_*).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.section_graph_skills_proof_pool import (
    _ROLE_EPISODE_BASE_RESUME_NEEDLES,
    _SECTION_MIN_FACTS,
    _base_resume_role_episode_plan,
    _role_episode_bundle_plan,
)

REPO = Path(__file__).resolve().parents[3]


def test_base_resume_role_episode_planner_is_deprecated() -> None:
    assert _ROLE_EPISODE_BASE_RESUME_NEEDLES == {}
    assert _base_resume_role_episode_plan(
        "insurtech_bullets", needles=("insurtech",), limit=3, repo_root=REPO
    ) is None
    assert _base_resume_role_episode_plan(
        "ey_bullets", needles=("ernst", "young"), limit=3, repo_root=REPO
    ) is None


@pytest.mark.parametrize(
    "section,expected_prefix,forbidden_prefix",
    [
        ("insurtech_bullets", "reb_insurtech_", "bul_insurtech_"),
        ("insurtech_narrative", "reb_insurtech_", "bul_insurtech_"),
        ("ey_bullets", "reb_ey_", "bul_ey_"),
        ("ey_narrative", "reb_ey_", "bul_ey_"),
    ],
)
def test_role_episode_bundle_plan_uses_graph_ids(section, expected_prefix, forbidden_prefix) -> None:
    result = _role_episode_bundle_plan(
        section_id=section,
        repo_root=REPO,
        limit=_SECTION_MIN_FACTS[section],
    )
    assert result is not None, f"{section} graph bundle planner returned None"
    plan, ordered, allowed = result
    facts = plan["facts"]
    assert len(facts) == _SECTION_MIN_FACTS[section]
    assert len(ordered) == len(facts)
    assert set(ordered) == allowed
    assert plan["selection_method"] == f"augmented_skills_graph_{section}_role_episode_bundle"
    assert plan["role_episode_bundle_fallback"] is True
    for f in facts:
        fact_id = str(f["fact_id"])
        assert fact_id.startswith(expected_prefix), fact_id
        assert not fact_id.startswith(forbidden_prefix), fact_id
        assert f["source_fact_ids"] == [fact_id]
        assert f["role_episode_bundle_id"] == fact_id
        assert f["srfs_verification_status"] == "GRAPH_ROLE_EPISODE_BUNDLE"
        assert f["claim_text"].strip()


def test_planner_not_applied_to_ibm_or_unify() -> None:
    assert "ibm_bullets" not in _ROLE_EPISODE_BASE_RESUME_NEEDLES
    assert "unify_bullets" not in _ROLE_EPISODE_BASE_RESUME_NEEDLES


def test_end_to_end_proof_pool_nonempty_for_all_four_lanes() -> None:
    """Full proof resolution: insurtech/ey bullets+narrative use graph bundle ids."""
    from types import SimpleNamespace

    from apps_rg.runtime.c0.section_proof_loader import load_section_proof_for_lane

    args = SimpleNamespace(
        provider="external_claude", temperature=0.3, x1d_judges="", mock_judges=True,
        allow_test_mock_judges=True, allow_non_allow_exit_zero=True,
        target_title="VP Global Head of Agentic AI Solutions", target_company="AIG",
        target_role="VP", jd_text="Lead agentic AI platform strategy.",
        briefing="AIG agentic AI.", base_resume_ref="",
    )
    expectations = {
        "insurtech_bullets": ("reb_insurtech_", 12),
        "insurtech_narrative": ("reb_insurtech_", 12),
        "ey_bullets": ("reb_ey_", 5),
        "ey_narrative": ("reb_ey_", 5),
    }
    for sid, (prefix, expected_count) in expectations.items():
        pool, *_ = load_section_proof_for_lane(section_id=sid, args=args, repo_root=REPO)
        facts = (pool.selected_fact_plan or {}).get("facts") or []
        allowed = pool.allowed_fact_ids_ordered or []
        assert len(facts) == expected_count, f"{sid}: expected graph facts, got {len(facts)}"
        assert len(allowed) == expected_count, f"{sid}: expected allowed fact ids, got {len(allowed)}"
        assert pool.base_resume_fallback_used is False
        assert all(str(fid).startswith(prefix) for fid in allowed)
