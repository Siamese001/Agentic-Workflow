from __future__ import annotations

from apps_rg.runtime.sections import ibm_narrative_lane_defaults as defaults


def test_ibm_narrative_lane_defaults_are_provider_neutral_and_large_enough() -> None:
    assert defaults.LANE_KEY == "ibm_narrative"
    assert defaults.PROMPT_ID == "ibm_position_narrative_dispatch_v1"
    assert defaults.NARRATIVE_TEMP_DEFAULT == 0.45
    assert defaults.NARRATIVE_MAX_OUTPUT_TOKENS == 4000
    assert defaults.TARGET_TITLE_DEFAULT
    assert defaults.TARGET_COMPANY_DEFAULT
    assert defaults.JD_TEXT_DEFAULT.strip()
    assert defaults.BRIEFING_DEFAULT.strip()


def test_find_repo_root_returns_repo_with_apps_rg_base_resume() -> None:
    root = defaults._find_repo_root()

    assert root.is_dir()
    assert (root / "apps_rg" / "resume" / "base").exists()
