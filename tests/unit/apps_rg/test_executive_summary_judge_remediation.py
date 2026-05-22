"""Unit tests: judge remediation trigger and repair user message."""

from __future__ import annotations

from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    build_judge_remediation_user_message,
    evaluate_judge_remediation_trigger,
)


def _soft_fail_judge(provider_key: str, *, findings: list[str], score: float = 0.5) -> dict:
    return {
        "provider_key": provider_key,
        "provider_name": provider_key,
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_FAIL",
        "pass": False,
        "decisive_failure": False,
        "normalized_score": score,
        "normalized_threshold": 0.8,
        "findings": findings,
        "fail_reasons": [],
        "remediation_suggestions": [],
    }


def test_trigger_quorum_two_judges_shared_synthesis_tag() -> None:
    judges = [
        _soft_fail_judge("anthropic_claude", findings=["bullet-stack synthesis lacks weave"]),
        _soft_fail_judge("openai_gpt", findings=["paragraph reads as stacked bullets"]),
        {
            "provider_key": "gemini_pro",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "normalized_score": 0.95,
            "normalized_threshold": 0.8,
        },
    ]
    ok, receipt = evaluate_judge_remediation_trigger(
        judges, runtime_generation_status="REAL_LLM", x2_passed=True
    )
    assert ok is True
    assert receipt.get("trigger_mode") == "quorum_soft_fail"


def test_trigger_skipped_when_x2_not_passed() -> None:
    ok, receipt = evaluate_judge_remediation_trigger(
        [], runtime_generation_status="REAL_LLM", x2_passed=False
    )
    assert ok is False
    assert receipt.get("reason") == "requires_real_llm_and_x2_pass"


def test_remediation_user_message_lists_unused_facts() -> None:
    msg = build_judge_remediation_user_message(
        x1d_judges=[_soft_fail_judge("anthropic_claude", findings=["weak synthesis"])],
        unused_fact_ids=["fact_003", "fact_004"],
        allowed_fact_count=8,
    )
    assert "Unused allowed facts" in msg
    assert "fact_003" in msg
    assert "prefer 5" in msg.lower()
