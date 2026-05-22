"""Unit tests: synthesis regen bounds and repair prompts."""

from __future__ import annotations

import os

from apps_rg.runtime.sections.executive_summary_lane import (
    _build_synthesis_repair_user,
    _regen_candidate_preferred,
    _shape_failure_count,
)
from apps_rg.runtime.sections.executive_summary_repair_policy import (
    SYNTHESIS_REGEN_MAX_ATTEMPTS,
    synthesis_regen_max_attempts,
)


def test_synthesis_regen_max_attempts_default_is_two(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_SYNTHESIS_REGEN_MAX_ATTEMPTS", raising=False)
    assert synthesis_regen_max_attempts() == SYNTHESIS_REGEN_MAX_ATTEMPTS == 2


def test_synthesis_regen_max_attempts_env_clamped(monkeypatch) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_SYNTHESIS_REGEN_MAX_ATTEMPTS", "9")
    assert synthesis_regen_max_attempts() == 3
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_SYNTHESIS_REGEN_MAX_ATTEMPTS", "1")
    assert synthesis_regen_max_attempts() == 1


def test_repair_user_includes_evidence_weave_and_anti_shrink() -> None:
    msg = _build_synthesis_repair_user(
        "claim_ledger_rows_4_with_pool_7_need_at_least_5; sentence 0: mechanism_inventory:6_terms",
        attempt_index=0,
        prior_word_count=102,
        prior_ledger_rows=4,
        last_monotonicity_rejected=True,
    )
    assert "EVIDENCE_WEAVE" in msg
    assert "MECHANISM_CONTROL" in msg
    assert "PRIOR REGEN SHRANK" in msg
    assert "102" in msg


def test_regen_candidate_preferred_rejects_mono_rejected_shrink_with_lower_fail_count() -> None:
    assert (
        _regen_candidate_preferred(
            new_fail_count=1,
            new_ledger_rows=4,
            new_word_count=62,
            best_fail_count=2,
            best_ledger_rows=5,
            best_word_count=81,
            monotonicity_accepted=False,
        )
        is False
    )


def test_regen_candidate_preferred_accepts_mono_ok_weave_gain() -> None:
    assert (
        _regen_candidate_preferred(
            new_fail_count=2,
            new_ledger_rows=5,
            new_word_count=81,
            best_fail_count=4,
            best_ledger_rows=4,
            best_word_count=74,
            monotonicity_accepted=True,
        )
        is True
    )


def test_shape_failure_count_increases_with_more_issues() -> None:
    bad = {
        "resume_display_text": "I am bad. Short. Short.",
        "claim_ledger": [],
    }
    n = _shape_failure_count(bad["resume_display_text"], bad, selected_facts=[])
    assert n >= 2
