"""W2 — composite delta_class when voice + executive_signal/synthesis fail."""

from __future__ import annotations

from typing import Any

import pytest

from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    collect_judge_remediation_delta_lines,
)
from apps_rg.runtime.sections.executive_summary_regen_delta_policy import (
    DELTA_CLASS_DIMENSION_EXECUTIVE_SIGNAL,
    DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE,
    DELTA_CLASS_RESUME_VOICE_HUMANIZE,
    resolve_delta_class,
)


@pytest.fixture(autouse=True)
def _enable_regen_caps(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_REGEN_CAPS", "1")


def _dim_verdict(dim: str, *, passed: bool, major: bool = True) -> dict[str, Any]:
    if passed:
        return {"pass": True, "severity": "none", "codes": []}
    return {
        "pass": False,
        "severity": "major" if major else "minor",
        "codes": ["test_fail"],
    }


def _brown_regen_unblock_panel() -> list[dict[str, Any]]:
    """Pattern from exec_summary_20260526_213359: Gemini voice+synthesis, Anthropic exec+synthesis."""
    base_dims = {
        "factual_support": _dim_verdict("factual_support", passed=True),
        "ats_alignment_without_keyword_stuffing": _dim_verdict(
            "ats_alignment_without_keyword_stuffing", passed=True
        ),
        "anti_overfit": _dim_verdict("anti_overfit", passed=True),
        "evidence_utilization": _dim_verdict("evidence_utilization", passed=True),
        "deterministic_alignment": _dim_verdict("deterministic_alignment", passed=True),
    }
    return [
        {
            "provider_key": "gemini_pro",
            "provider_name": "Gemini Pro",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "score": 3.0,
            "findings": ["Formulaic connective cadence S2-S5; robotic repetition."],
            "remediation_suggestions": ["Vary connective openers across S2-S5."],
            "dimension_verdicts": {
                **base_dims,
                "resume_voice": _dim_verdict("resume_voice", passed=False),
                "synthesis_quality": _dim_verdict("synthesis_quality", passed=False),
                "executive_signal": _dim_verdict("executive_signal", passed=True),
            },
        },
        {
            "provider_key": "anthropic_claude",
            "provider_name": "Anthropic Claude",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "score": 3.5,
            "findings": ["S5 thin bridge without metric; S6 generic forward synthesis."],
            "remediation_suggestions": [
                "Strengthen S5 with FSA/quant outcome; ground S6 in proof."
            ],
            "dimension_verdicts": {
                **base_dims,
                "executive_signal": _dim_verdict("executive_signal", passed=False),
                "synthesis_quality": _dim_verdict("synthesis_quality", passed=False),
                "resume_voice": _dim_verdict("resume_voice", passed=True),
            },
        },
        {
            "provider_key": "openai_chatgpt",
            "provider_name": "OpenAI ChatGPT",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "score": 4.3,
        },
    ]


def test_brown_regen_unblock_panel_resolves_composite_delta_class() -> None:
    judges = _brown_regen_unblock_panel()
    assert resolve_delta_class(judges) == DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE


def test_brown_regen_unblock_delta_contains_metric_s5_s6_guidance() -> None:
    lines = collect_judge_remediation_delta_lines(
        _brown_regen_unblock_panel(),
        unused_fact_ids=[],
        allowed_fact_count=6,
        prior_word_count=121,
        prior_ledger_rows=6,
        compact=True,
    )
    joined = "\n".join(lines).lower()
    assert "executive_signal_and_voice_v1" in joined
    assert "dollar/percent" in joined or "metric" in joined
    assert "s5" in joined
    assert "s6" in joined
    assert "connective" in joined
    assert "metric_weave_s3_s5" in joined


def test_voice_only_failure_stays_resume_voice_humanize() -> None:
    judges = [
        {
            "provider_key": "gemini_pro",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "dimension_verdicts": {
                "resume_voice": _dim_verdict("resume_voice", passed=False),
                "executive_signal": _dim_verdict("executive_signal", passed=True),
                "synthesis_quality": _dim_verdict("synthesis_quality", passed=True),
                "factual_support": _dim_verdict("factual_support", passed=True),
                "ats_alignment_without_keyword_stuffing": _dim_verdict(
                    "ats_alignment_without_keyword_stuffing", passed=True
                ),
                "anti_overfit": _dim_verdict("anti_overfit", passed=True),
                "evidence_utilization": _dim_verdict("evidence_utilization", passed=True),
                "deterministic_alignment": _dim_verdict("deterministic_alignment", passed=True),
            },
        },
    ]
    assert resolve_delta_class(judges) == DELTA_CLASS_RESUME_VOICE_HUMANIZE


def test_executive_signal_only_stays_dimension_executive_signal() -> None:
    judges = [
        {
            "provider_key": "anthropic_claude",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "dimension_verdicts": {
                "executive_signal": _dim_verdict("executive_signal", passed=False),
                "resume_voice": _dim_verdict("resume_voice", passed=True),
                "synthesis_quality": _dim_verdict("synthesis_quality", passed=True),
                "factual_support": _dim_verdict("factual_support", passed=True),
                "ats_alignment_without_keyword_stuffing": _dim_verdict(
                    "ats_alignment_without_keyword_stuffing", passed=True
                ),
                "anti_overfit": _dim_verdict("anti_overfit", passed=True),
                "evidence_utilization": _dim_verdict("evidence_utilization", passed=True),
                "deterministic_alignment": _dim_verdict("deterministic_alignment", passed=True),
            },
        },
    ]
    assert resolve_delta_class(judges) == DELTA_CLASS_DIMENSION_EXECUTIVE_SIGNAL
