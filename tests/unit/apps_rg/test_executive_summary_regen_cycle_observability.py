"""W5 — per-cycle regen artifacts and convergence guard."""

from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.sections.executive_summary_regen_observability import (
    REGEN_STOPPED_REASON_CONVERGED,
    REGEN_STOPPED_REASON_X2_STUCK,
    X2_GATE_CLAIM_FIELD_MAPS,
    detect_x2_stuck_same_failure,
    finalize_regen_cycle_observability,
    persist_regen_cycle_artifacts,
    regen_failure_signature,
    x2_failed_row_indexes_from_gates,
)


def _brown_claim_gate_failure(*, rows: tuple[int, ...] = (1, 5)) -> dict:
    row_text = ", ".join(f"row_{idx}" for idx in rows)
    return {
        "gate_id": X2_GATE_CLAIM_FIELD_MAPS,
        "pass": False,
        "failure_reason": f"ledger claim not materialized in resume_display_text: {row_text}",
        "observed_value": f"ledger claim not materialized in resume_display_text: {row_text}",
    }


def test_persist_regen_cycle_artifacts_writes_cycle_files(tmp_path: Path) -> None:
    receipt = {"regen_output_hash": "hash_cycle_1", "accepted": False}
    x2 = [{"gate_id": "x2_exec_summary_six_sentences", "pass": True}]
    paths = persist_regen_cycle_artifacts(
        tmp_path,
        1,
        judge_remediation_receipt=receipt,
        x2_gates=x2,
    )
    assert (tmp_path / "judge_remediation_receipt_cycle_1.json").is_file()
    assert (tmp_path / "x2_gate_outputs_post_regen_cycle_1.json").is_file()
    assert "judge_remediation_receipt_cycle" in paths


def test_finalize_regen_cycle_observability_two_cycles_distinct_hashes(tmp_path: Path) -> None:
    cycles_receipt: dict = {"cycles": []}
    record1 = {"cycle": 1, "draft_parse_ok": True}
    prior, stop1 = finalize_regen_cycle_observability(
        cycles_receipt,
        record1,
        cycle_index=0,
        artifact_dir=tmp_path,
        judge_remediation_receipt={"regen_output_hash": "aaa111"},
        x2_gates=[{"gate_id": "x2_a", "pass": False}],
        prior_regen_output_hash=None,
    )
    assert stop1 is None
    assert len(cycles_receipt["cycles"]) == 1
    assert (tmp_path / "judge_remediation_receipt_cycle_1.json").is_file()
    assert (tmp_path / "x2_gate_outputs_post_regen_cycle_1.json").is_file()

    record2 = {"cycle": 2, "draft_parse_ok": True}
    _, stop2 = finalize_regen_cycle_observability(
        cycles_receipt,
        record2,
        cycle_index=1,
        artifact_dir=tmp_path,
        judge_remediation_receipt={"regen_output_hash": "bbb222"},
        prior_regen_output_hash=prior,
    )
    assert stop2 is None
    assert (tmp_path / "judge_remediation_receipt_cycle_2.json").is_file()


def test_finalize_regen_cycle_convergence_on_identical_hash(tmp_path: Path) -> None:
    cycles_receipt: dict = {"cycles": []}
    same_hash = "deadbeef" * 8
    finalize_regen_cycle_observability(
        cycles_receipt,
        {"cycle": 1},
        cycle_index=0,
        artifact_dir=tmp_path,
        judge_remediation_receipt={"regen_output_hash": same_hash},
        prior_regen_output_hash=None,
    )
    _, stop = finalize_regen_cycle_observability(
        cycles_receipt,
        {"cycle": 2},
        cycle_index=1,
        artifact_dir=tmp_path,
        judge_remediation_receipt={"regen_output_hash": same_hash},
        prior_regen_output_hash=same_hash,
    )
    assert stop == REGEN_STOPPED_REASON_CONVERGED
    assert cycles_receipt["stopped_reason"] == REGEN_STOPPED_REASON_CONVERGED
    assert cycles_receipt["cycles"][-1].get("regen_converged") is True


def test_x2_failed_row_indexes_from_gates_parses_brown_shape() -> None:
    gate = _brown_claim_gate_failure(rows=(1, 5))
    assert x2_failed_row_indexes_from_gates([gate]) == (1, 5)


def test_regen_failure_signature_includes_gate_ids_and_rows() -> None:
    sig = regen_failure_signature(x2_gates=[_brown_claim_gate_failure()])
    assert sig == ((X2_GATE_CLAIM_FIELD_MAPS,), (1, 5))


def test_detect_x2_stuck_same_failure_requires_matching_rows() -> None:
    receipt: dict = {"cycles": []}
    sig_a = ((X2_GATE_CLAIM_FIELD_MAPS,), (1, 5))
    sig_b = ((X2_GATE_CLAIM_FIELD_MAPS,), (2,))
    assert detect_x2_stuck_same_failure(receipt, sig_a) is False
    receipt["cycles"].append(
        {
            "post_regen_x2_failed_gate_ids": [X2_GATE_CLAIM_FIELD_MAPS],
            "post_regen_x2_failed_row_indexes": [1, 5],
        },
    )
    assert detect_x2_stuck_same_failure(receipt, sig_a) is True
    assert detect_x2_stuck_same_failure(receipt, sig_b) is False


def test_finalize_regen_cycle_stuck_same_failure_after_two_cycles(tmp_path: Path) -> None:
    """Brown 230615 pattern: distinct hashes, same X2 gate + rows → early exit at cycle 2."""
    cycles_receipt: dict = {"cycles": []}
    x2_fail = [_brown_claim_gate_failure(rows=(1, 5))]

    _, stop1 = finalize_regen_cycle_observability(
        cycles_receipt,
        {"cycle": 1},
        cycle_index=0,
        artifact_dir=tmp_path,
        judge_remediation_receipt={"regen_output_hash": "hash_cycle_1"},
        x2_gates=x2_fail,
        prior_regen_output_hash=None,
    )
    assert stop1 is None
    assert cycles_receipt["cycles"][0]["post_regen_x2_failed_row_indexes"] == [1, 5]

    _, stop2 = finalize_regen_cycle_observability(
        cycles_receipt,
        {"cycle": 2},
        cycle_index=1,
        artifact_dir=tmp_path,
        judge_remediation_receipt={"regen_output_hash": "hash_cycle_2_different"},
        x2_gates=x2_fail,
        prior_regen_output_hash="hash_cycle_1",
    )
    assert stop2 == REGEN_STOPPED_REASON_X2_STUCK
    assert cycles_receipt["stopped_reason"] == REGEN_STOPPED_REASON_X2_STUCK
    assert cycles_receipt["cycles"][-1].get("x2_stuck_same_failure") is True
    lane_stats = cycles_receipt["regen_lane_stats"]
    assert lane_stats["stuck_loop_detected"] is True
    assert lane_stats["stuck_signature"] == {
        "failing_gate_ids": [X2_GATE_CLAIM_FIELD_MAPS],
        "row_indexes": [1, 5],
    }


def test_finalize_regen_cycle_stuck_not_triggered_when_rows_differ(tmp_path: Path) -> None:
    cycles_receipt: dict = {"cycles": []}
    finalize_regen_cycle_observability(
        cycles_receipt,
        {"cycle": 1},
        cycle_index=0,
        artifact_dir=tmp_path,
        judge_remediation_receipt={"regen_output_hash": "aaa"},
        x2_gates=[_brown_claim_gate_failure(rows=(1, 5))],
        prior_regen_output_hash=None,
    )
    _, stop2 = finalize_regen_cycle_observability(
        cycles_receipt,
        {"cycle": 2},
        cycle_index=1,
        artifact_dir=tmp_path,
        judge_remediation_receipt={"regen_output_hash": "bbb"},
        x2_gates=[_brown_claim_gate_failure(rows=(2,))],
        prior_regen_output_hash="aaa",
    )
    assert stop2 is None
    assert cycles_receipt.get("stopped_reason") != REGEN_STOPPED_REASON_X2_STUCK


def test_stuck_precedence_over_hash_convergence(tmp_path: Path) -> None:
    """Same signature twice with identical hash still stops on stuck (checked before converge)."""
    cycles_receipt: dict = {"cycles": []}
    same_hash = "cafebabe" * 8
    x2_fail = [_brown_claim_gate_failure(rows=(1, 5))]
    finalize_regen_cycle_observability(
        cycles_receipt,
        {"cycle": 1},
        cycle_index=0,
        artifact_dir=tmp_path,
        judge_remediation_receipt={"regen_output_hash": same_hash},
        x2_gates=x2_fail,
        prior_regen_output_hash=None,
    )
    _, stop2 = finalize_regen_cycle_observability(
        cycles_receipt,
        {"cycle": 2},
        cycle_index=1,
        artifact_dir=tmp_path,
        judge_remediation_receipt={"regen_output_hash": same_hash},
        x2_gates=x2_fail,
        prior_regen_output_hash=same_hash,
    )
    assert stop2 == REGEN_STOPPED_REASON_X2_STUCK
    assert cycles_receipt["stopped_reason"] == REGEN_STOPPED_REASON_X2_STUCK
