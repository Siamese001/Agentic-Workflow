"""W2.0 — exec summary repair stack preserves defect lineage in receipts."""

from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.section_repair_ledger import (
    KIND_REGEN_LLM,
    init_ledger,
    record_repair,
    record_x2_run,
)


def test_repair_receipt_preserves_failure_reason(tmp_path: Path) -> None:
    adir = tmp_path / "exec"
    adir.mkdir()
    init_ledger(adir, section_id="executive_summary", run_id="w2_lineage")
    record_repair(
        adir,
        kind=KIND_REGEN_LLM,
        operation="synthesis_regen",
        reason="x2_exec_summary_sentence_count_6",
        replaced_l2=True,
        detail={"trigger_gate_id": "x2_exec_summary_sentence_count_6", "failure_reason": "sentence_count"},
    )
    record_x2_run(
        adir,
        run_number=1,
        after_l2_source=KIND_REGEN_LLM,
        x2_gates=[{"gate_id": "x2_exec_summary_sentence_count_6", "pass": False}],
    )
    from apps_rg.runtime.section_repair_ledger import load_ledger

    ledger = load_ledger(adir)
    repair = ledger["repairs"][0]
    assert repair.get("reason") == "x2_exec_summary_sentence_count_6"
    assert repair.get("detail", {}).get("failure_reason") == "sentence_count"
    x2_run = ledger["x2_runs"][0]
    assert "x2_exec_summary_sentence_count_6" in x2_run.get("failed_gate_ids", [])


def test_silent_normalization_red_path_missing_reason(tmp_path: Path) -> None:
    adir = tmp_path / "bad"
    adir.mkdir()
    init_ledger(adir, section_id="executive_summary", run_id="bad")
    record_repair(
        adir,
        kind=KIND_REGEN_LLM,
        operation="silent_coerce",
        reason="",
        replaced_l2=True,
    )
    from apps_rg.runtime.section_repair_ledger import load_ledger

    ledger = load_ledger(adir)
    assert not (ledger["repairs"][0].get("reason") or "").strip(), "red-path: empty reason simulates silent normalize"
