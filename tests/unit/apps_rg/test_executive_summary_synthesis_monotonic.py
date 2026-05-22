"""Unit tests: synthesis regen monotonic acceptance."""

from __future__ import annotations

from apps_rg.runtime.sections.executive_summary_synthesis_monotonic import (
    evaluate_synthesis_regen_monotonicity,
)


def _parsed(text: str, ledger_rows: int = 4, fact_prefix: str = "fact_") -> dict:
    ledger = [
        {
            "claim_text": f"claim {i}",
            "source_fact_ids": [f"{fact_prefix}{i:03d}"],
        }
        for i in range(ledger_rows)
    ]
    return {"resume_display_text": text, "claim_ledger": ledger}


def test_monotonic_rejects_word_shrink_without_sentence_repair() -> None:
    prior = _parsed(
        "One two three four five six seven eight. "
        "Two two three four five six seven eight. "
        "Three two three four five six seven eight. "
        "Four two three four five six seven eight."
    )
    post = _parsed(
        "Short one. Short two. Short three. Short four."
    )
    ok, detail = evaluate_synthesis_regen_monotonicity(
        prior_parsed=prior,
        prior_reject_reason="Executive summary meta or filler scaffolding",
        new_parsed=post,
    )
    assert ok is False
    assert detail["rejection_reasons"]


def test_monotonic_allows_shrink_when_prior_failed_sentence_count() -> None:
    prior = _parsed("One. Two. Three.")
    post = _parsed(
        "One two three four five six seven eight. "
        "Two two three four five six seven eight. "
        "Three two three four five six seven eight. "
        "Four two three four five six seven eight."
    )
    ok, _ = evaluate_synthesis_regen_monotonicity(
        prior_parsed=prior,
        prior_reject_reason="resume_display_text must have 4-5 sentences; found 3",
        new_parsed=post,
    )
    assert ok is True


def test_monotonic_waives_shrink_when_ledger_rows_gain_on_utilization_repair() -> None:
    prior = _parsed(
        ("Word " * 100) + "end. " + ("Two " * 20) + "end. " + ("Three " * 20) + "end. " + ("Four " * 20) + "end.",
        ledger_rows=4,
    )
    post = _parsed(
        ("Alpha " * 15) + "end. " + ("Beta " * 15) + "end. " + ("Gamma " * 15) + "end. " + ("Delta " * 15) + "end.",
        ledger_rows=5,
        fact_prefix="fact_alt_",
    )
    ok, detail = evaluate_synthesis_regen_monotonicity(
        prior_parsed=prior,
        prior_reject_reason="claim_ledger_rows_4_with_pool_7_need_at_least_5",
        new_parsed=post,
    )
    assert ok is True
    assert detail.get("shrink_waived") is True


def test_monotonic_rejects_ledger_row_regression() -> None:
    text = (
        "One two three four five six seven eight. "
        "Two two three four five six seven eight. "
        "Three two three four five six seven eight. "
        "Four two three four five six seven eight."
    )
    prior = _parsed(text, ledger_rows=5)
    post = _parsed(text, ledger_rows=3)
    ok, detail = evaluate_synthesis_regen_monotonicity(
        prior_parsed=prior,
        prior_reject_reason="meta filler",
        new_parsed=post,
    )
    assert ok is False
    assert "claim_ledger_row_count_regressed" in detail["rejection_reasons"][0]
