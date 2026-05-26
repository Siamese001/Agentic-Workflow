"""W3 — incremental regen anchor + delta line helpers."""

from __future__ import annotations

from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    collect_judge_remediation_delta_lines,
)
from apps_rg.runtime.sections.executive_summary_regen_incremental import (
    collect_prior_attempt_incremental_delta_lines,
    filter_verbatim_feedback_for_prior_attempt,
    summarize_prior_attempt_sentence_lines,
)


def _dim_fail(dim: str) -> dict:
    return {"pass": False, "severity": "major", "codes": ["test"]}


def test_summarize_prior_attempt_sentence_lines() -> None:
    baseline = "A. B. C. D. E. F."
    prior = "A. B changed. C. D. E. F."
    lines = summarize_prior_attempt_sentence_lines(
        baseline_resume_display_text=baseline,
        prior_attempt_resume_display_text=prior,
    )
    assert any(line.startswith("S2:") for line in lines)


def test_collect_prior_attempt_incremental_delta_lines() -> None:
    judges = [
        {
            "provider_key": "gemini_pro",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "dimension_verdicts": {"resume_voice": _dim_fail("resume_voice")},
            "findings": ["Formulaic connective cadence S2-S5."],
        },
    ]
    prior_judges = [
        {
            "provider_key": "gemini_pro",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "dimension_verdicts": {"resume_voice": _dim_fail("resume_voice")},
            "findings": ["Additionally opener in S3."],
        },
    ]
    lines = collect_prior_attempt_incremental_delta_lines(
        baseline_resume_display_text="S1. S2. S3. S4. S5. S6.",
        prior_attempt_resume_display_text="S1. S2 revised. S3. S4. S5. S6.",
        prior_cycle_judges=prior_judges,
        current_x1d_judges=judges,
    )
    assert any(ln.startswith("PRIOR_ATTEMPT_SUMMARY:") for ln in lines)
    assert any("STILL_FAILING_AFTER_PRIOR_ATTEMPT" in ln for ln in lines)


def test_filter_verbatim_feedback_drops_addressed_connective() -> None:
    lines = [
        "JUDGE_DELTA_SOURCE provider_key=gemini_pro provider_name=gemini_pro",
        "- gemini_pro finding: Additionally/Furthermore openers in S2-S5.",
    ]
    filtered = filter_verbatim_feedback_for_prior_attempt(
        lines,
        prior_attempt_resume_display_text="From the platform view, one arc. Against risk, two. On delivery, three.",
    )
    assert not any("Additionally" in ln for ln in filtered)


def test_collect_delta_lines_includes_incremental_section() -> None:
    judge = {
        "provider_key": "anthropic_claude",
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_FAIL",
        "pass": False,
        "findings": ["S5 thin bridge."],
        "dimension_verdicts": {"executive_signal": _dim_fail("executive_signal")},
    }
    lines = collect_judge_remediation_delta_lines(
        [judge],
        unused_fact_ids=[],
        allowed_fact_count=6,
        prior_word_count=100,
        prior_ledger_rows=5,
        baseline_resume_display_text="Scratch one. Two. Three. Four. Five. Six.",
        prior_attempt_resume_display_text="Scratch one. Two changed. Three. Four. Five. Six.",
        prior_cycle_judges=[judge],
    )
    joined = "\n".join(lines)
    assert "PRIOR_ATTEMPT_SUMMARY" in joined
