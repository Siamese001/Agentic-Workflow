"""Direct contract tests for the executive_summary lane helper surface."""

from __future__ import annotations

from apps_rg.runtime.sections.executive_summary_lane import (
    coerce_resume_display_sentence_count_band,
    normalize_executive_summary_llm_output,
    reconcile_claim_ledger_to_sentence_count,
)
from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences


def _five_sentence_resume() -> str:
    return (
        "First sentence establishes the context. "
        "Second sentence keeps the pace. "
        "The operating model keeps release cadence steady, enabling the team to prove policy "
        "controls without slowing delivery. "
        "Fourth sentence closes the middle. "
        "Fifth sentence closes the arc."
    )


def test_normalize_executive_summary_llm_output_coerces_resume_and_uses_runtime_plan() -> None:
    parsed = {
        "executive_summary": _five_sentence_resume(),
        "claim_ledger_emitted": [{"claim_text": "claimed", "source_fact_ids": ["fact_1"]}],
        "gap_notes": ("not", "a", "list"),
        "change_log": [{"operation": "seed"}],
        "self_check": {"ok": True},
        "source_sensitive_phrase_ledger": ["phrase"],
        "input_payload_hash": "input-hash",
        "output_payload_hash": "output-hash",
        "claim_ledger_hash": "ledger-hash",
        "allowed_fact_ids_hash": "facts-hash",
    }
    runtime_selected_fact_plan = {
        "section_id": "executive_summary",
        "facts": [{"fact_id": "fact_1", "claim_text": "claimed"}],
    }

    normalized = normalize_executive_summary_llm_output(parsed, runtime_selected_fact_plan)

    assert split_sentences(normalized["resume_display_text"]) == [
        "First sentence establishes the context.",
        "Second sentence keeps the pace.",
        "The operating model keeps release cadence steady.",
        "That capability enables the team to prove policy controls without slowing delivery.",
        "Fourth sentence closes the middle.",
        "Fifth sentence closes the arc.",
    ]
    assert normalized["selected_fact_plan"] == runtime_selected_fact_plan
    assert normalized["claim_ledger"] == parsed["claim_ledger_emitted"]
    assert normalized["gap_notes"] == []
    assert normalized["change_log"] == parsed["change_log"]
    assert normalized["self_check"] == parsed["self_check"]
    assert normalized["source_sensitive_phrase_ledger"] == parsed["source_sensitive_phrase_ledger"]
    assert normalized["input_payload_hash"] == "input-hash"
    assert normalized["output_payload_hash"] == "output-hash"
    assert normalized["claim_ledger_hash"] == "ledger-hash"
    assert normalized["allowed_fact_ids_hash"] == "facts-hash"


def test_coerce_resume_display_sentence_count_band_splits_one_compound_sentence() -> None:
    coerced = coerce_resume_display_sentence_count_band(_five_sentence_resume())

    assert split_sentences(coerced) == [
        "First sentence establishes the context.",
        "Second sentence keeps the pace.",
        "The operating model keeps release cadence steady.",
        "That capability enables the team to prove policy controls without slowing delivery.",
        "Fourth sentence closes the middle.",
        "Fifth sentence closes the arc.",
    ]
    assert ".." not in coerced


def test_reconcile_claim_ledger_to_sentence_count_appends_split_sentence_row() -> None:
    parsed = {
        "resume_display_text": coerce_resume_display_sentence_count_band(_five_sentence_resume()),
        "claim_ledger": [
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
    }

    reconcile_claim_ledger_to_sentence_count(parsed)

    ledger = parsed["claim_ledger"]
    assert len(ledger) == 6
    assert ledger[-1] == {
        "claim": "Fifth sentence closes the arc.",
        "claim_text": "Fifth sentence closes the arc.",
        "source_fact_ids": ["fact_5", "fact_5_metric_1234"],
        "support_class": "FACT_ONLY",
        "deterministic_split_continuation": True,
    }

