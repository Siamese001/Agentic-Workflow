from __future__ import annotations

from apps_rg.runtime.section_repair_lane_integration import (
    finalize_lane_product_quality,
    record_deterministic_rewrite,
    record_mechanical,
    record_parse_json_retry,
    record_regen_llm,
    snapshot_lane_x2,
    start_lane_repair_ledger,
)
from apps_rg.runtime.section_repair_ledger import load_ledger


def test_lane_repair_integration_records_repairs_and_x2_snapshots(tmp_path) -> None:
    start_lane_repair_ledger(tmp_path, section_id="headline", run_id="run_wave2")
    record_parse_json_retry(tmp_path, reason="invalid json")
    record_mechanical(tmp_path, operation="trim_whitespace", reason="normalization")
    snapshot_lane_x2(tmp_path, [{"gate_id": "x2_shape", "pass": False}])

    ledger = load_ledger(tmp_path)

    assert ledger is not None
    assert ledger["section_id"] == "headline"
    assert ledger["run_id"] == "run_wave2"
    assert [r["operation"] for r in ledger["repairs"]] == [
        "parse_json_retry",
        "trim_whitespace",
    ]
    assert ledger["x2_runs"][0]["failed_gate_ids"] == ["x2_shape"]
    assert ledger["attempt_1_x2_failed"] is True


def test_finalize_lane_product_quality_marks_counted_regen_authoritative(tmp_path) -> None:
    start_lane_repair_ledger(tmp_path, section_id="executive_summary", run_id="run_wave2")
    record_regen_llm(
        tmp_path,
        operation="regen_after_x2",
        reason="x2 repair required",
        replaced_l2=True,
    )
    l2_output: dict[str, object] = {}

    status, reason = finalize_lane_product_quality(
        tmp_path,
        runtime_generation_status="REAL_LLM",
        x2_gates=[{"gate_id": "x2_shape", "pass": True}],
        pass_reason="all gates passed",
        l2_output=l2_output,
        regen_authoritative_on_x2_pass=True,
    )
    ledger = load_ledger(tmp_path)

    assert status == "PASS"
    assert reason == "all gates passed"
    assert ledger is not None
    assert ledger["authoritative_attempt_number"] == 2
    assert l2_output["product_quality_status"] == "PASS"
    assert l2_output["section_repair_ledger"] == "section_repair_ledger.json"


def test_unauthorized_deterministic_rewrite_keeps_product_fail_closed(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_TEST_HARNESS", raising=False)
    monkeypatch.delenv("APPS_RG_ALLOW_PRODUCT_SHORTCUTS", raising=False)

    start_lane_repair_ledger(tmp_path, section_id="competencies", run_id="run_wave2")
    record_deterministic_rewrite(
        tmp_path,
        operation="silent_claim_rewrite",
        reason="should block pass",
    )

    status, reason = finalize_lane_product_quality(
        tmp_path,
        runtime_generation_status="REAL_LLM",
        x2_gates=[{"gate_id": "x2_shape", "pass": True}],
        pass_reason="all gates passed",
    )

    assert status == "FAIL"
    assert "deterministic_rewrite_without_counted_regen" in reason
