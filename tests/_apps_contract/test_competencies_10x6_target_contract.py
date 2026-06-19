"""W0 contract — target state for competencies-graph-8x8-gemini plan.

These tests document the live product constants and defaults after the 8x8
competency selector rollout.
"""
from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
APPS_RG = REPO_ROOT / "apps_rg"

# --- Target constants (W2; variance-class alignment 2026-06: candidate pool 8 -> 8) ---
TARGET_SC_PATH_COUNT = 8
TARGET_FINAL_CATEGORY_COUNT = 8
TARGET_CANDIDATE_CATEGORY_COUNT = 8

# --- Target judge default (W3) ---
TARGET_DEFAULT_X1D_JUDGES = "gemini_pro"


def test_competencies_sc_path_count_matches_candidate_pool() -> None:
    from apps_rg.runtime.reasoning.employment_bullet_pool import COMPETENCIES_SC_PATH_COUNT

    assert COMPETENCIES_SC_PATH_COUNT == TARGET_SC_PATH_COUNT


def test_competencies_emitted_category_count_fixed_at_8() -> None:
    """Competencies now emit 8 graph-backed categories."""
    from apps_rg.runtime.sections.competencies_rigor import (
        MAX_CATEGORY_COUNT,
        MIN_CATEGORY_COUNT,
    )

    assert MIN_CATEGORY_COUNT == TARGET_FINAL_CATEGORY_COUNT
    assert MAX_CATEGORY_COUNT == TARGET_FINAL_CATEGORY_COUNT


def test_competencies_lane_default_x1d_judges_gemini_pro_only() -> None:
    from apps_rg.runtime.sections.competencies_lane_runtime import build_parser

    parser = build_parser()
    action = next(a for a in parser._actions if "--x1d-judges" in (a.option_strings or []))
    assert action.default == TARGET_DEFAULT_X1D_JUDGES


def test_competencies_pool_x1d_judge_rows_exists() -> None:
    """Mirror employment_pool_x1d_judge_rows for competencies (W3)."""
    import apps_rg.runtime.reasoning.employment_bullet_pool as pool

    assert hasattr(pool, "competencies_pool_x1d_judge_rows"), (
        "employment_bullet_pool must expose competencies_pool_x1d_judge_rows "
        "(single gemini_pro pool judge row)"
    )


def test_competency_selector_no_facts_skills_authority_wording() -> None:
    """W1: prompt must not cite facts.skills as verified inventory authority (prohibition text allowed)."""
    path = APPS_RG / "prompt_assembly/templates/competency_selector_v2.yaml"
    text = path.read_text(encoding="utf-8")
    assert "BASE RESUME PARITY" not in text
    assert "verified from canonical JSON (`facts.skills`)" not in text
    assert "Engineering & platform competency rows verified from canonical JSON" not in text
    assert "NOT base-resume facts.skills" in text or "not base-resume facts.skills" in text.lower()


def test_competency_selector_requires_8_candidate_8_emitted_categories() -> None:
    """Competency selector now requires 8 candidate and 8 emitted categories."""
    path = APPS_RG / "prompt_assembly/templates/competency_selector_v2.yaml"
    text = path.read_text(encoding="utf-8")
    assert "graph_8x8" in text
    assert "candidate_category_count" in text
    assert 'value: "8"' in text or "candidate_category_count: 8" in text
    assert "min_items: 8" in text
    assert "max_items: 8" in text
