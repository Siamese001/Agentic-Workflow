"""W3 — Brown SVP process hardening (operator receipts, escalation, S5 inventory X2)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.sections.executive_summary_operator_reporting import (
    build_regen_escalation_receipt,
    check_exec_summary_s5_no_derivatives_inventory,
    check_self_check_s5_no_derivatives_inventory,
    collect_regen_reasoning_execution_block_rows,
    reasoning_block_rows_from_receipt,
)
from apps_rg.runtime.sections.executive_summary_regen_observability import (
    REGEN_STOPPED_REASON_X2_STUCK,
    detect_x2_stuck_same_failure,
    finalize_regen_cycle_observability,
)
from apps_rg.runtime.sections.executive_summary_synthesis_contract import (
    QUANT_METRIC_DISPLAY_FACT_ID,
)


def _brown_allowed() -> set[str]:
    return {
        "fact_exec_002",
        "fact_engineering_platform_006",
        "fact_governance_003",
        QUANT_METRIC_DISPLAY_FACT_ID,
        "fact_quant_hpc_003",
    }


def test_reasoning_block_rows_extracts_block_ledger() -> None:
    receipt = {
        "aggregate_blocked": True,
        "ledger": [
            {
                "control_name": "self_consistency",
                "downgrade_disposition": "BLOCK",
                "receipt_state": "MISSING",
                "decisive_reason": "reflexion blocked",
                "gap_notes": "",
            },
            {
                "control_name": "other",
                "downgrade_disposition": "WARN",
                "receipt_state": "OK",
                "decisive_reason": "",
                "gap_notes": "",
            },
        ],
    }
    rows = reasoning_block_rows_from_receipt(
        receipt,
        phase="judge_regen",
        artifact_ref="provider_response_judge_regen_cycle01.json",
    )
    assert len(rows) == 1
    assert rows[0]["control_name"] == "self_consistency"


def test_collect_regen_reasoning_blocks_from_artifacts(tmp_path: Path) -> None:
    trace = {
        "reasoning_execution_receipt": {
            "aggregate_blocked": True,
            "ledger": [
                {
                    "control_name": "tot_depth",
                    "downgrade_disposition": "BLOCK",
                    "receipt_state": "MISSING",
                    "decisive_reason": "tot blocked",
                    "gap_notes": "",
                },
            ],
        },
    }
    (tmp_path / "prompt_selection_trace.json").write_text(
        json.dumps(trace),
        encoding="utf-8",
    )
    rows = collect_regen_reasoning_execution_block_rows(tmp_path)
    assert len(rows) == 1
    assert rows[0]["phase"] == "scratch_generation"


def test_regen_escalation_receipt_on_stuck_loop() -> None:
    cycles_receipt = {
        "stopped_reason": REGEN_STOPPED_REASON_X2_STUCK,
        "cycles": [{"cycle": 1}, {"cycle": 2}],
        "stuck_signature": {"failing_gate_ids": ["x2_claim_field_maps_to_display_sentence"]},
    }
    esc = build_regen_escalation_receipt(
        cycles_receipt=cycles_receipt,
        allowed_fact_ids=_brown_allowed(),
    )
    assert esc is not None
    assert esc["recommended_option_id"] == "document_proof_gap"
    option_ids = {o["id"] for o in esc["operator_options"]}
    assert "widen_delta" in option_ids
    assert "document_proof_gap" in option_ids
    assert "stop" in option_ids


def test_finalize_regen_writes_escalation_receipt(tmp_path: Path) -> None:
    cycles_receipt: dict = {
        "cycles": [],
        "allowed_fact_ids": sorted(_brown_allowed()),
    }
    sig = (("x2_claim_field_maps_to_display_sentence",), (3,))
    cycles_receipt["cycles"].append(
        {
            "post_regen_x2_failed_gate_ids": list(sig[0]),
            "post_regen_x2_failed_row_indexes": list(sig[1]),
        },
    )
    cycles_receipt["cycles"].append(
        {
            "post_regen_x2_failed_gate_ids": list(sig[0]),
            "post_regen_x2_failed_row_indexes": list(sig[1]),
        },
    )
    assert detect_x2_stuck_same_failure(cycles_receipt, sig, n_cycles=2) is True

    judge_remediation = {"regen_output_hash": "abc123"}
    _, stopped = finalize_regen_cycle_observability(
        cycles_receipt,
        cycles_receipt["cycles"][-1],
        cycle_index=1,
        artifact_dir=tmp_path,
        judge_remediation_receipt=judge_remediation,
        x2_gates=[{"gate_id": "x2_claim_field_maps_to_display_sentence", "pass": False}],
    )
    assert stopped == REGEN_STOPPED_REASON_X2_STUCK
    assert (tmp_path / "regen_escalation_receipt.json").is_file()
    esc = json.loads((tmp_path / "regen_escalation_receipt.json").read_text(encoding="utf-8"))
    assert esc["schema"] == "executive_summary_regen_escalation_v1"


def test_s5_derivatives_inventory_fails_without_hpc_metric() -> None:
    text = (
        "S1. S2. S3. S4. "
        "Built advanced quantitative foundation through derivatives pricing and multi-Greek hedging. "
        "S6."
    )
    ok, reason = check_exec_summary_s5_no_derivatives_inventory(
        text,
        allowed_fact_ids=_brown_allowed(),
        selected_facts=[
            {
                "fact_id": QUANT_METRIC_DISPLAY_FACT_ID,
                "claim_text": "Shortened stress-test cycles by 40%.",
                "metric_raw": "40%",
            },
        ],
    )
    assert ok is False
    assert reason and "paired_hpc_metric" in reason


def test_s5_derivatives_inventory_passes_with_percent_in_s5() -> None:
    text = (
        "S1. S2. S3. S4. "
        "Derivatives pricing depth supports stress-testing discipline, shortening cycles by 40%. "
        "S6."
    )
    ok, _ = check_exec_summary_s5_no_derivatives_inventory(
        text,
        allowed_fact_ids=_brown_allowed(),
    )
    assert ok is True


def test_self_check_s5_derivatives_inventory_honors_false() -> None:
    parsed = {"self_check": {"s5_no_derivatives_inventory": False}}
    text = (
        "S1. S2. S3. S4. "
        "Quantitative foundation with derivatives pricing only. "
        "S6."
    )
    ok, reason = check_self_check_s5_no_derivatives_inventory(
        parsed,
        text,
        allowed_fact_ids=_brown_allowed(),
    )
    assert ok is False
