"""W5 — per-cycle regen artifacts and convergence guard."""

from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.sections.executive_summary_regen_observability import (
    REGEN_STOPPED_REASON_CONVERGED,
    finalize_regen_cycle_observability,
    persist_regen_cycle_artifacts,
)


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
