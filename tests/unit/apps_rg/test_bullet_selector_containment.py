"""W5 (AIG E2E remediation, E2E-09/E2E-10) — truthful block labels + empty-selection signal.

Deterministic, hermetic. No provider calls. Covers the two shared helpers that contain the
bullet-lane empty-selection failure mode:

1. truthful_block_reason: never says 'provider blocked' when the provider produced REAL_LLM
   output (the E2E-09/10 mislabel).
2. summarize_selector_emptiness: flags an empty selection and records the sub-threshold scores
   so a downstream block is truthful and the < 0.72 selector scores are observable.
"""
from __future__ import annotations

from types import SimpleNamespace

from apps_rg.runtime.reasoning.bullet_lane_generation import (
    SELECTOR_EMPTY_BLOCK_REASON,
    summarize_selector_emptiness,
    truthful_block_reason,
)


def _result(err: str | None) -> SimpleNamespace:
    return SimpleNamespace(exact_provider_error=err)


def test_truthful_reason_uses_exact_provider_error_when_present() -> None:
    assert truthful_block_reason(_result("timeout"), "BLOCKED", "") == "timeout"


def test_truthful_reason_real_llm_never_says_provider_blocked() -> None:
    # Provider produced output -> must NOT claim provider blocked.
    reason = truthful_block_reason(_result(None), "REAL_LLM", "")
    assert reason != "provider blocked"
    assert "selector" in reason or "parse" in reason


def test_truthful_reason_real_llm_preserves_existing_parse_error() -> None:
    assert truthful_block_reason(_result(None), "REAL_LLM", "bad_json") == "bad_json"


def test_truthful_reason_genuine_block_still_says_provider_blocked() -> None:
    assert truthful_block_reason(_result(None), "BLOCKED", "") == "provider blocked"
    assert truthful_block_reason(None, "BLOCKED", "") == "provider blocked"


def test_empty_selection_flagged_with_block_reason_and_scores() -> None:
    pool = SimpleNamespace(selections=[], selection_mode="fallback_empty")
    gate = SimpleNamespace(bullets_in_merged=0)
    out = summarize_selector_emptiness(pool=pool, gate=gate)
    assert out["selector_empty"] is True
    assert out["selector_block_reason"] == SELECTOR_EMPTY_BLOCK_REASON
    assert out["selector_subthreshold_scores"] == []
    assert out["selector_selection_count"] == 0


def test_subthreshold_scores_recorded_when_present() -> None:
    # Selections exist but merged is empty (all below threshold) -> still empty, scores captured.
    pool = SimpleNamespace(
        selections=[{"score": 0.61}, {"score": 0.55}], selection_mode="claude_top_n"
    )
    gate = SimpleNamespace(bullets_in_merged=0)
    out = summarize_selector_emptiness(pool=pool, gate=gate)
    assert out["selector_empty"] is True  # bullets_in_merged == 0
    assert out["selector_subthreshold_scores"] == [0.61, 0.55]
    assert out["selector_block_reason"] == SELECTOR_EMPTY_BLOCK_REASON


def test_nonempty_selection_is_not_flagged_empty() -> None:
    pool = SimpleNamespace(
        selections=[{"score": 0.81}, {"score": 0.79}], selection_mode="claude_top_n"
    )
    gate = SimpleNamespace(bullets_in_merged=6)
    out = summarize_selector_emptiness(pool=pool, gate=gate)
    assert out["selector_empty"] is False
    assert "selector_block_reason" not in out
    assert out["selector_subthreshold_scores"] == [0.81, 0.79]
