"""Unit tests: authoritative post-X2 gate snapshot for judge refresh (1745d772)."""

from __future__ import annotations

from apps_rg.runtime.judges.executive_summary_judge_packet import (
    build_deterministic_gate_summary_from_x2_gates,
)


def test_x2_gate_snapshot_skips_malformed_rows_and_uses_observed_value() -> None:
    x2_gates = [
        "not-a-gate",
        {"gate_id": "", "pass": True},
        {
            "gate_id": "x2_exec_summary_no_credential_dump",
            "pass": False,
            "failure_reason": None,
            "observed_value": "aws inventory",
        },
    ]
    summary = build_deterministic_gate_summary_from_x2_gates(x2_gates)
    assert summary["x2_exec_summary_no_credential_dump"]["detail"] == "aws inventory"
    assert summary["x2_exec_summary_no_credential_dump"]["pass"] is False
    assert "x2_exec_summary_sentence_count_6" not in summary


def test_x2_gate_snapshot_empty_list_has_no_product_shape_note() -> None:
    assert build_deterministic_gate_summary_from_x2_gates([]) == {}
