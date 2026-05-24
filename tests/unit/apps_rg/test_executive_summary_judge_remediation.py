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


def _passing_judge(provider_key: str) -> dict:
    return {
        "provider_key": provider_key,
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_PASS",
        "pass": True,
        "decisive_failure": False,
        "normalized_score": 0.9,
        "normalized_threshold": 0.8,
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


def test_trigger_solitary_severe_soft_fail() -> None:
    judges = [
        _soft_fail_judge(
            "anthropic_claude",
            findings=[
                "Summary reads as stacked bullets; poor ATS alignment to enterprise architecture and IT strategy",
            ],
            score=0.7,
        ),
        _passing_judge("gemini_pro"),
        {
            "provider_key": "openai_chatgpt",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "decisive_failure": True,
            "normalized_score": 0.4,
            "normalized_threshold": 0.8,
        },
    ]
    ok, receipt = evaluate_judge_remediation_trigger(
        judges, runtime_generation_status="REAL_LLM", x2_passed=True
    )
    assert ok is True
    assert receipt.get("trigger_mode") == "solitary_severe_soft_fail"


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
    assert "six-sentence arc" in msg.lower()


def test_trigger_skipped_when_two_judges_already_pass() -> None:
    judges = [
        _passing_judge("anthropic_claude"),
        _passing_judge("openai_gpt"),
        _soft_fail_judge("gemini_pro", findings=["minor synthesis nit"]),
    ]
    ok, receipt = evaluate_judge_remediation_trigger(
        judges, runtime_generation_status="REAL_LLM", x2_passed=True
    )
    assert ok is False
    assert receipt.get("reason") == "two_or_more_judges_already_pass_skip_regen"
    assert receipt.get("model_backed_pass_count") == 2


def test_remediation_user_message_includes_sentence_arc_guidance() -> None:
    plan = {
        "sentence_arc": [
            {"sentence_index": 2, "arc_role": "connective", "guidance": "weave metrics"},
        ],
    }
    msg = build_judge_remediation_user_message(
        x1d_judges=[_soft_fail_judge("anthropic_claude", findings=["weak synthesis"])],
        unused_fact_ids=[],
        allowed_fact_count=6,
        composition_plan=plan,
    )
    assert "six_sentence_arc" in msg
    assert "weave metrics" in msg
    assert "FORBIDDEN PHRASES" in msg


def test_remediation_user_message_includes_dominant_arc_brushstrokes() -> None:
    plan = {
        "dominant_arc": "platform_governance",
        "brushstroke_missing_ids": ["fact_007"],
    }
    msg = build_judge_remediation_user_message(
        x1d_judges=[_soft_fail_judge("anthropic_claude", findings=["weak synthesis"])],
        unused_fact_ids=[],
        allowed_fact_count=6,
        composition_plan=plan,
    )
    assert "COMPOSITION: dominant_arc=platform_governance" in msg
    assert "fact_007" in msg
