"""Regression coverage for executive_summary lane sentence and ledger contracts."""

from __future__ import annotations

from apps_rg.runtime.sections.executive_summary_lane import (
    normalize_executive_summary_llm_output,
    reconcile_claim_ledger_to_sentence_count,
)
from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences


def test_executive_summary_lane_keeps_split_resume_and_claim_ledger_in_sync() -> None:
    parsed = {
        "executive_summary": (
            "First sentence establishes the context. "
            "Second sentence keeps the pace. "
            "The operating model keeps release cadence steady, enabling the team to prove policy "
            "controls without slowing delivery. "
            "Fourth sentence closes the middle. "
            "Fifth sentence closes the arc."
        ),
        "claim_ledger_emitted": [
            {"claim_text": "First sentence establishes the context.", "source_fact_ids": ["fact_1"]},
            {"claim_text": "Second sentence keeps the pace.", "source_fact_ids": ["fact_2"]},
            {
                "claim_text": "The operating model keeps release cadence steady.",
                "source_fact_ids": ["fact_3"],
            },
            {
                "claim_text": "Fourth sentence closes the middle.",
                "source_fact_ids": ["fact_4"],
            },
            {
                "claim_text": "Fifth sentence closes the arc.",
                "source_fact_ids": ["fact_5", "fact_5_metric_1234"],
                "support_class": "FACT_ONLY",
            },
        ],
        "change_log": [],
        "self_check": {},
    }
    runtime_selected_fact_plan = {
        "section_id": "executive_summary",
        "required_fact_ids": ["fact_1", "fact_2", "fact_3", "fact_4", "fact_5"],
    }

    normalized = normalize_executive_summary_llm_output(parsed, runtime_selected_fact_plan)
    reconcile_claim_ledger_to_sentence_count(normalized)

    assert split_sentences(normalized["resume_display_text"]) == [
        "First sentence establishes the context.",
        "Second sentence keeps the pace.",
        "The operating model keeps release cadence steady.",
        "That capability enables the team to prove policy controls without slowing delivery.",
        "Fourth sentence closes the middle.",
        "Fifth sentence closes the arc.",
    ]
    assert normalized["selected_fact_plan"] == runtime_selected_fact_plan
    assert len(normalized["claim_ledger"]) == 6
    assert normalized["claim_ledger"][-1]["deterministic_split_continuation"] is True
    assert normalized["claim_ledger"][-1]["source_fact_ids"] == ["fact_5", "fact_5_metric_1234"]

