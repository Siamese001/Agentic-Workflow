"""Judge-regen delta lines: verbatim soft-failed feedback (no env token truncation)."""

from __future__ import annotations

from agentic_core.L2_execution.regen.prompt_lock import format_regen_delta_user_turn
from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    REGEN_DELTA_SECTION_ORDER,
    _flatten_delta_sections,
    collect_judge_remediation_delta_lines,
)
from apps_rg.runtime.sections.executive_summary_regen_observability import (
    pack_judge_feedback_with_stats,
)


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


def test_regen_delta_section_order_constant() -> None:
    assert REGEN_DELTA_SECTION_ORDER == (
        "dimension",
        "judge_feedback",
        "floors",
        "guards",
    )


def test_flatten_delta_sections_preserves_pack_order() -> None:
    sections = {
        "dimension": ["- DIM_A"],
        "judge_feedback": ["- JUDGE_A", "- JUDGE_B"],
        "floors": ["- FLOOR_A"],
        "guards": ["- GUARD_A", "- GUARD_B"],
    }
    packed = _flatten_delta_sections(sections)
    assert packed == ["- DIM_A", "- JUDGE_A", "- JUDGE_B", "- FLOOR_A", "- GUARD_A", "- GUARD_B"]


def test_compact_delta_lines_follow_dimension_before_verbatim_judges() -> None:
    lines = collect_judge_remediation_delta_lines(
        _three_judge_soft_fail_panel(),
        unused_fact_ids=[],
        allowed_fact_count=8,
        prior_word_count=120,
        prior_ledger_rows=6,
        compact=True,
    )
    edit_budget_idx = next(i for i, ln in enumerate(lines) if "EDIT_BUDGET" in ln)
    first_judge_idx = next(i for i, ln in enumerate(lines) if "JUDGE_DELTA_SOURCE" in ln)
    connective_idx = next(i for i, ln in enumerate(lines) if "CONNECTIVE_TISSUE:" in ln)
    assert edit_budget_idx < first_judge_idx < connective_idx


def test_pack_judge_feedback_with_stats_never_drops_lines() -> None:
    sections = {
        "judge_feedback": [f"- judge-line-{i}" for i in range(12)],
        "dimension": ["- dim"],
        "floors": [],
        "guards": [],
    }
    packed, stats = pack_judge_feedback_with_stats(sections)
    assert stats["judge_feedback_lines_dropped"] == 0
    assert stats["judge_feedback_lines_included"] == 12
    assert len(packed) == 13


def test_regen_delta_user_turn_excludes_anchor_draft() -> None:
    anchor_snippet = "UNIQUE_ANCHOR_SENTENCE_ZZZ_12345 not in delta"
    lines = collect_judge_remediation_delta_lines(
        _three_judge_soft_fail_panel(),
        unused_fact_ids=[],
        allowed_fact_count=8,
        prior_word_count=120,
        prior_ledger_rows=6,
        compact=True,
    )
    user_turn = format_regen_delta_user_turn(tuple(lines))
    assert anchor_snippet not in user_turn
    assert "REGEN_DELTA_v1" in user_turn
    assert "PROMPT_LOCK" in user_turn


def test_compact_delta_includes_connective_guard() -> None:
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
    assert "CONNECTIVE_TISSUE:" in joined
    user_turn = format_regen_delta_user_turn(tuple(lines))
    assert "REGEN_DELTA" in user_turn
