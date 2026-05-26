"""Judge regen loop helpers — thread advance + resume parse."""

from __future__ import annotations

import json

from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    _finding_contradicts_soft_fail,
    collect_judge_remediation_delta_lines,
)
from apps_rg.runtime.sections.executive_summary_judge_regen_loop import (
    advance_regen_thread_for_next_cycle,
    resume_display_text_from_regen_messages,
)


def test_finding_contradicts_soft_fail_filters_pass_noise() -> None:
    judge = {
        "provider_status": "MODEL_BACKED_FAIL",
        "pass": False,
        "evaluator_mode": "MODEL_BACKED",
    }
    assert _finding_contradicts_soft_fail(judge, "All deterministic gates pass; no failures.")
    assert not _finding_contradicts_soft_fail(judge, "S6 forward synthesis is thin.")


def test_collect_delta_lines_prioritizes_edit_budget() -> None:
    judge = {
        "provider_key": "anthropic_claude",
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_FAIL",
        "pass": False,
        "score": 4.0,
        "quality_flags": ["s6_forward_synthesis_slightly_thin"],
        "findings": ["S6 forward synthesis is somewhat thin."],
        "remediation_suggestions": ["Strengthen S6."],
        "dimension_verdicts": {
            "synthesis_quality": {
                "pass": True,
                "severity": "minor",
                "codes": ["s6_thin_recap"],
            },
        },
    }
    lines = collect_judge_remediation_delta_lines(
        [judge],
        unused_fact_ids=[],
        allowed_fact_count=7,
        prior_word_count=120,
        prior_ledger_rows=6,
    )
    joined = "\n".join(lines)
    assert "EDIT_BUDGET" in joined
    assert "S6_forward_synthesis" in joined or "revise S6" in joined


def test_resume_display_text_from_regen_messages() -> None:
    payload = {
        "resume_display_text": "One. Two. Three. Four. Five. Six.",
        "claim_ledger": [],
    }
    messages = [
        {"role": "system", "content": "sys"},
        {"role": "assistant", "content": json.dumps(payload)},
    ]
    assert resume_display_text_from_regen_messages(messages) == payload["resume_display_text"]


def test_advance_regen_thread_for_next_cycle() -> None:
    messages = [{"role": "system", "content": "sys"}]
    raw = json.dumps({"resume_display_text": "A. B. C. D. E. F.", "claim_ledger": []})
    judges = [{"provider_key": "anthropic_claude", "score": 4.2, "pass": True}]
    out_msgs, out_judges = advance_regen_thread_for_next_cycle(
        messages,
        raw_output=raw,
        x1d_judges=judges,
    )
    assert len(out_msgs) == 2
    assert out_msgs[-1]["role"] == "assistant"
    assert out_judges == judges
