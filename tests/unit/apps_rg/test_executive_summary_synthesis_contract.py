"""Unit tests: executive summary SVP synthesis contract SSOT."""

from __future__ import annotations

from apps_rg.runtime.sections.executive_summary_composition import build_sentence_arc
from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    build_judge_remediation_user_message,
    evaluate_judge_remediation_trigger,
)
from apps_rg.runtime.sections.executive_summary_pa import (
    format_strategy_executive_targeting_appendix,
    is_strategy_executive_target_title,
)
from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
    failed_x2_gate_ids,
    gate_ids_from_x2_reject_reason,
    SENTENCE_ARC_SVP_STRATEGY,
    format_strategy_executive_u0_block,
    format_synthesis_repair_directive,
    format_x2_gate_failures_reject_reason,
)


def test_format_x2_gate_failures_reject_reason() -> None:
    rows = [
        {"gate_id": "x2_exec_summary_evidence_utilization", "pass": False, "reason": "thin_sentence"},
        {"gate_id": "x2_other", "pass": True},
    ]
    reason = format_x2_gate_failures_reject_reason(rows)
    assert "evidence_utilization" in reason
    assert "thin_sentence" in reason
    assert failed_x2_gate_ids(rows) == frozenset({"x2_exec_summary_evidence_utilization"})
    assert "x2_exec_summary_evidence_utilization" in gate_ids_from_x2_reject_reason(reason)


def test_strategy_title_detects_brown_brown_svp() -> None:
    assert is_strategy_executive_target_title("SVP IT Strategy & Innovation") is True


def test_u0_block_includes_jd_emphasis_and_s3_s6() -> None:
    block = format_strategy_executive_targeting_appendix("SVP IT Strategy & Innovation")
    assert "enterprise architecture" in block.lower()
    assert "S3–S4" in block or "S3-4" in block
    assert "integrative" in block.lower() or "capstone" in block.lower()
    assert block == format_strategy_executive_u0_block(target_title="SVP IT Strategy & Innovation")


def test_sentence_arc_svp_has_six_roles() -> None:
    arc = build_sentence_arc(
        target_role="SVP IT Strategy & Innovation",
        strategy_executive=True,
    )
    assert len(arc) == 6
    roles = [row["arc_role"] for row in arc]
    assert roles == [r["arc_role"] for r in SENTENCE_ARC_SVP_STRATEGY]
    assert "commercial_strategy" in roles
    assert "enterprise_capstone" in roles


def test_synthesis_repair_directive_nonempty_for_strategy() -> None:
    assert "S3" in format_synthesis_repair_directive(strategy_executive=True)
    assert format_synthesis_repair_directive(strategy_executive=False) == ""


def test_judge_remediation_default_mentions_integrative_s6() -> None:
    msg = build_judge_remediation_user_message(
        x1d_judges=[],
        unused_fact_ids=[],
        allowed_fact_count=6,
    )
    assert "integrative" in msg.lower() or "S6" in msg


def test_solitary_severe_triggers_when_two_judges_pass() -> None:
    judges = [
        {
            "provider_key": "anthropic_claude",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "decisive_failure": False,
            "normalized_score": 0.68,
            "normalized_threshold": 0.8,
            "findings": ["bullet-stack synthesis lacks weave; weak IT strategy emphasis"],
            "fail_reasons": [],
            "remediation_suggestions": [],
        },
        {
            "provider_key": "gemini_pro",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "normalized_score": 1.0,
            "normalized_threshold": 0.8,
        },
        {
            "provider_key": "openai_chatgpt",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "normalized_score": 0.88,
            "normalized_threshold": 0.8,
        },
    ]
    ok, receipt = evaluate_judge_remediation_trigger(
        judges, runtime_generation_status="REAL_LLM", x2_passed=True
    )
    assert ok is True
    assert receipt.get("trigger_mode") == "solitary_severe_soft_fail"
