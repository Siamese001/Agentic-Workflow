"""Token-budget packing for judge-regen delta lines (verbatim feedback)."""

from __future__ import annotations

from agentic_core.L2_execution.regen.delta_shape_guard import estimate_token_count
from agentic_core.L2_execution.regen.prompt_lock import format_regen_delta_user_turn
from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    collect_judge_remediation_delta_lines,
)
from apps_rg.runtime.sections.executive_summary_repair_policy import judge_regen_max_delta_tokens


def _three_judge_soft_fail_panel() -> list[dict]:
    long = (
        "Sentences 2-5 read as a sequential achievement bullet stack rather than integrated "
        "SVP-level strategic narrative with weak connective tissue and thin forward synthesis."
    )
    return [
        {
            "provider_key": "anthropic_claude",
            "provider_name": "Anthropic Claude",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "decisive_failure": False,
            "normalized_score": 0.68,
            "normalized_threshold": 0.8,
            "findings": [long],
            "fail_reasons": ["Achievement bullet-stack pattern undermines SVP synthesis"],
            "remediation_suggestions": [
                "Reframe the opening thesis as enterprise-wide IT strategy and innovation leadership.",
                "Replace S2-S5 bullet stack with connective narrative across platform and governance.",
            ],
            "rationale": "Prose is ledger-backed but reads as stacked wins, not one arc.",
            "dimension_verdicts": {
                "executive_signal": {"pass": False, "severity": "major", "codes": ["bullet_stack"]},
                "synthesis_quality": {"pass": False, "severity": "major", "codes": ["thin_S6"]},
            },
        },
        {
            "provider_key": "openai_chatgpt",
            "provider_name": "OpenAI ChatGPT",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "decisive_failure": False,
            "normalized_score": 0.72,
            "normalized_threshold": 0.8,
            "findings": ["S6 capstone is generic and does not project enterprise architecture themes."],
            "remediation_suggestions": [
                "Strengthen S6 with forward enterprise IT direction from allowed facts only.",
            ],
            "dimension_verdicts": {
                "synthesis_quality": {"pass": False, "severity": "major", "codes": ["thin_recap"]},
            },
        },
        {
            "provider_key": "gemini_pro",
            "provider_name": "Gemini Pro",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "normalized_score": 0.95,
            "normalized_threshold": 0.8,
        },
    ]


def test_verbatim_feedback_present_for_all_soft_fails() -> None:
    lines = collect_judge_remediation_delta_lines(
        _three_judge_soft_fail_panel(),
        unused_fact_ids=[],
        allowed_fact_count=8,
        prior_word_count=120,
        prior_ledger_rows=6,
        compact=True,
    )
    joined = "\n".join(lines)
    assert "JUDGE_DELTA_SOURCE provider_key=anthropic_claude" in joined
    assert "JUDGE_DELTA_SOURCE provider_key=openai_chatgpt" in joined
    assert "enterprise-wide IT strategy" in joined
    assert "Strengthen S6 with forward enterprise IT" in joined
    assert "gemini_pro" not in joined or "JUDGE_DELTA_SOURCE provider_key=gemini_pro" not in joined


def test_token_pack_drops_guards_before_truncating_judge_text(monkeypatch) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_REGEN_MAX_DELTA_TOKENS", "512")
    lines = collect_judge_remediation_delta_lines(
        _three_judge_soft_fail_panel(),
        unused_fact_ids=[],
        allowed_fact_count=8,
        prior_word_count=120,
        prior_ledger_rows=6,
        compact=True,
    )
    joined = "\n".join(lines)
    assert "Anthropic Claude remediation:" in joined
    assert "OpenAI ChatGPT remediation:" in joined
    assert "bullet-stack pattern" in joined
    user_turn = format_regen_delta_user_turn(tuple(lines))
    assert estimate_token_count(user_turn) <= 512 + 80
    if "CONNECTIVE_TISSUE:" not in joined:
        assert estimate_token_count(user_turn) > 400


def test_higher_token_cap_retains_connective_guard(monkeypatch) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_REGEN_MAX_DELTA_TOKENS", "768")
    assert judge_regen_max_delta_tokens() == 768
    lines = collect_judge_remediation_delta_lines(
        _three_judge_soft_fail_panel(),
        unused_fact_ids=[],
        allowed_fact_count=8,
        prior_word_count=120,
        prior_ledger_rows=6,
        compact=True,
    )
    joined = "\n".join(lines)
    assert "CONNECTIVE_TISSUE:" in joined
    user_turn = format_regen_delta_user_turn(tuple(lines))
    assert estimate_token_count(user_turn) <= 768 + 80
