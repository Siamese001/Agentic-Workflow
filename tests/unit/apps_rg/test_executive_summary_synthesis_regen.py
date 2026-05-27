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


def test_build_synthesis_repair_user_includes_conflation_guidance() -> None:
    msg = _build_synthesis_repair_user(
        "cross_fact_display_conflation:platform_and_governance",
        attempt_index=1,
        prior_word_count=80,
        prior_ledger_rows=5,
    )
    assert "fact_governance_003" in msg
    assert "Led/Successfully/Also/Built" in msg


def test_shape_failure_count_increases_with_more_issues() -> None:
    bad = {
        "resume_display_text": "I am bad. Short. Short.",
        "claim_ledger": [],
    }
    n = _shape_failure_count(bad["resume_display_text"], bad, selected_facts=[])
    assert n >= 2


def test_synthesis_repair_sentence_count_note_fires_on_5_sentences() -> None:
    """sentence_count_note must fire when reject reason names wrong sentence count."""
    reject = (
        "resume_display_text must have exactly 6 sentences; found 5 "
        "(legacy 4–5 and 5–6 bands retired)"
    )
    msg = _build_synthesis_repair_user(
        reject,
        attempt_index=0,
        prior_word_count=85,
        prior_ledger_rows=5,
    )
    assert "SENTENCE COUNT HARD FAIL" in msg, (
        "sentence_count_note must fire when reject reason reports found 5 sentences"
    )
    assert "EXACTLY 6" in msg or "exactly 6" in msg, (
        "sentence_count_note must state EXACTLY 6"
    )
    assert "use 5" not in msg.lower(), (
        "No ambiguous 'use 5' guidance when sentence count failed — gate requires exactly 6"
    )


def test_synthesis_repair_evidence_weave_fires_on_sentences_blob() -> None:
    """utilization_note must fire when 'sentences' appears in reject reason."""
    reject = "Output has 5 sentences; executive synthesis requires exactly 6 sentences"
    msg = _build_synthesis_repair_user(
        reject,
        attempt_index=0,
        prior_word_count=85,
        prior_ledger_rows=5,
    )
    assert "EVIDENCE_WEAVE" in msg, (
        "utilization_note must fire when reject reason contains 'sentences'"
    )
    # Ensure the ambiguous fallback is gone
    assert "use 5 when the pool is tighter" not in msg, (
        "Ambiguous 'use 5 when the pool is tighter' must be removed — gate requires exactly 6"
    )


def test_synthesis_repair_no_ambiguous_fallback_when_count_fails() -> None:
    """'Prefer 6 ... use 5 when tighter' phrase must not appear in any sentence-count failure."""
    for reject in [
        "resume_display_text must have exactly 6 sentences; found 4 (legacy 4–5 and 5–6 bands retired)",
        "Output has 5 sentences; executive synthesis requires exactly 6 sentences",
    ]:
        msg = _build_synthesis_repair_user(
            reject,
            attempt_index=1,
            prior_word_count=90,
            prior_ledger_rows=5,
        )
        assert "use 5 when the pool is tighter" not in msg, (
            f"Ambiguous fallback must be absent for reject: {reject!r}"
        )
