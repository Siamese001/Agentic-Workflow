"""Unit tests: x2_exec_summary_evidence_utilization structural gate."""

from __future__ import annotations

from apps_rg.runtime.validators.executive_summary_x2 import (
    check_exec_summary_evidence_utilization,
    collect_unused_allowed_fact_ids,
)


def _facts(n: int) -> list[dict]:
    return [{"fact_id": f"fact_{i:03d}", "claim_text": f"claim {i}"} for i in range(n)]


def test_utilization_fails_thin_four_sentence_with_large_pool() -> None:
    text = (
        "Short one. "
        "Short two. "
        "Short three. "
        "Short four."
    )
    parsed = {
        "claim_ledger": [
            {"claim_text": "a", "source_fact_ids": ["fact_001"]},
            {"claim_text": "b", "source_fact_ids": ["fact_002"]},
            {"claim_text": "c", "source_fact_ids": ["fact_003"]},
            {"claim_text": "d", "source_fact_ids": ["fact_004"]},
        ],
        "self_check": {},
    }
    ok, reason = check_exec_summary_evidence_utilization(
        text, parsed, selected_facts=_facts(6)
    )
    assert ok is False
    assert reason is not None and "sentence_0" in reason


def test_utilization_passes_when_pool_excused() -> None:
    text = "Short one. Short two. Short three. Short four."
    parsed = {
        "claim_ledger": [{"claim_text": "a", "source_fact_ids": ["fact_001"]}],
        "self_check": {
            "selected_fact_pool_too_small": True,
            "selected_fact_pool_too_small_reason": "fixture",
        },
    }
    ok, reason = check_exec_summary_evidence_utilization(
        text, parsed, selected_facts=_facts(8)
    )
    assert ok is True
    assert reason is not None and "excused" in reason


def test_collect_unused_allowed_fact_ids() -> None:
    ledger = [
        {"claim_text": "a", "source_fact_ids": ["fact_001"]},
        {"claim_text": "b", "source_fact_ids": ["fact_002"]},
    ]
    unused = collect_unused_allowed_fact_ids(ledger, {"fact_001", "fact_002", "fact_003"})
    assert unused == ["fact_003"]
