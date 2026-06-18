"""Unit tests for fact-aware ``x2_cross_section_repeated_metric`` gate logic.

Regression (2026-06-11): bare metric string counting made distinct canonical facts
sharing ``40%`` fail aggregation even when each fact appeared in only one section.
"""
from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.aggregation.cross_section_x2 import run_cross_section_x2_gates


def _lane_section(section_id: str, claim_text: str, fact_id: str) -> dict:
    return {
        "section_kind": "generated_lane",
        "section_id": section_id,
        "l2_output_snapshot": {
            "claim_ledger": [
                {"claim_text": claim_text, "source_fact_ids": [fact_id]},
            ],
            "resume_display_text": claim_text,
        },
    }


def _repeated_metric_gate(sections: list[dict]):
    gates, *_rest = run_cross_section_x2_gates(
        repo=Path("."),
        final_resume_blob={"sections": sections},
        fingerprint={},
        sealed_index={},
    )
    return next(g for g in gates if g.gate_id == "x2_cross_section_repeated_metric")


def test_distinct_facts_sharing_same_metric_value_passes() -> None:
    """Three sections, three facts, all mentioning 40% — not recycling."""
    sections = [
        _lane_section("executive_summary", "Reduced production errors by 40%.", "fact_exec_001"),
        _lane_section("ibm_bullets", "Cut audit remediation time 40%.", "fact_ibm_002"),
        _lane_section("insurtech_bullets", "Lowered TCO by 40%.", "fact_insurtech_003"),
    ]
    gate = _repeated_metric_gate(sections)
    assert gate.verdict == "PASS"
    assert not gate.observed


def test_same_fact_metric_in_three_sections_fails() -> None:
    """Recycling the same fact's metric into >=3 sections must fail closed."""
    sections = [
        _lane_section("executive_summary", "Achieved 40% error reduction.", "fact_shared_001"),
        _lane_section("ibm_bullets", "Delivered 40% cost savings.", "fact_shared_001"),
        _lane_section("unify_bullets", "Realized 40% efficiency gains.", "fact_shared_001"),
    ]
    gate = _repeated_metric_gate(sections)
    assert gate.verdict == "FAIL"
    assert gate.observed
    assert any("40%" in key for key in gate.observed)


def test_same_fact_metric_in_two_sections_passes() -> None:
    sections = [
        _lane_section("executive_summary", "Reduced errors by 40%.", "fact_shared_001"),
        _lane_section("ibm_bullets", "Cut costs 40%.", "fact_shared_001"),
    ]
    gate = _repeated_metric_gate(sections)
    assert gate.verdict == "PASS"
