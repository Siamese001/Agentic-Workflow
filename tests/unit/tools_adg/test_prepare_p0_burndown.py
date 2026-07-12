from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tools.adg import prepare_p0_burndown as planner


def _write_json(path: Path, value: dict) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact(tmp_path: Path, name: str, value: dict) -> dict[str, str]:
    path = tmp_path / name
    return {"path": str(path), "sha256": _write_json(path, value)}


def _fixture(tmp_path: Path) -> tuple[Path, dict, dict]:
    run_id = "07122026_0907"
    snapshot = tmp_path / "adg_indexed_07122026_0907.sqlite"
    snapshot.write_bytes(b"sqlite-fixture")
    snapshot_ref = {"path": str(snapshot), "sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest()}
    gate_results = {
        "gates": [
            {"gate_id": "G_REACH_l0_reachability", "band": "P0", "status": "fail", "classification": "regressed", "violation_count": 3, "baseline_count": 0, "exit_code": 1},
            {"gate_id": "1_critical_path_integrity", "band": "P0", "status": "pass", "classification": "pass", "violation_count": 0, "baseline_count": 0, "exit_code": 0},
            {"gate_id": "tracked_gate_a", "band": "P0", "enforcement": "ratchet", "status": "pass", "classification": "pass", "violation_count": 5, "baseline_count": 5, "exit_code": 0},
            {"gate_id": "tracked_gate_b", "band": "P0", "enforcement": "ratchet", "status": "pass", "classification": "pass", "violation_count": 4, "baseline_count": 4, "exit_code": 0},
        ]
    }
    action_queue = {
        "actions": [
            {"queue_section": "open_blockers", "verdict_cluster": "FIX", "sort_band": "P0", "disposition": "open", "work_priority": "P0", "gate_id": "G_REACH_l0_reachability", "file_path": None},
            {"queue_section": "candidate_blockers", "verdict_cluster": "CANDIDATE_BLOCKER_TRIAGE", "sort_band": "P0", "disposition": "open", "work_priority": "triage", "file_path": "agentic_core/L1_cognition/bridges/u0_to_l1_planning.py"},
            {"queue_section": "candidate_blockers", "verdict_cluster": "CANDIDATE_BLOCKER_TRIAGE", "sort_band": "P0", "disposition": "open", "work_priority": "triage", "file_path": "agentic_core/L1_cognition/c0_context/__init__.py"},
            {"queue_section": "candidate_blockers", "verdict_cluster": "CANDIDATE_BLOCKER_TRIAGE", "sort_band": "P0", "disposition": "open", "work_priority": "triage", "file_path": "agentic_core/L1_cognition/c0_context/contract.py"},
            {"queue_section": "tracked_debt", "disposition": "open", "work_priority": "tracked", "file_path": "tracked/a.py"},
            {"queue_section": "tracked_debt", "disposition": "open", "work_priority": "tracked", "file_path": "tracked/b.py"},
        ]
    }
    artifacts = {
        "snapshot": snapshot_ref,
        "gate_results": _artifact(tmp_path, f"adg_gate_results_{run_id}.json", gate_results),
        "action_queue": _artifact(tmp_path, f"adg_action_queue_{run_id}.json", action_queue),
        "burndown_report": _artifact(tmp_path, f"adg_burndown_report_{run_id}.md", {"report": "p0"}),
        "burndown_table": _artifact(tmp_path, f"adg_burndown_table_{run_id}.json", {"p0": 1}),
        "generation_manifest": _artifact(tmp_path, f"adg_generation_manifest_{run_id}.json", {"snapshot": str(snapshot)}),
        "gate_manifest": _artifact(tmp_path, f"adg_gate_invocation_manifest_{run_id}.json", {"snapshot": str(snapshot)}),
    }
    handoff = {
        "schema_version": planner.REPAIR_HANDOFF_SCHEMA_VERSION,
        "adg_run_id": run_id,
        "repair_handoff": {"artifacts": artifacts, "legacy_counts": {"P0_FIX": 1, "P0_WAVE": 3, "P0_TRACKED_BACKLOG": 2}},
    }
    handoff_path = tmp_path / f"adg_repair_handoff_{run_id}.json"
    handoff_path.write_text(json.dumps(handoff, sort_keys=True), encoding="utf-8")
    receipt = {
        "schema_version": planner.RECEIPT_SCHEMA_VERSION,
        "artifact_status": "repair_ready",
        "artifact_status_source": "direct",
        "adg_run_id": run_id,
        "repair_handoff": handoff["repair_handoff"],
    }
    receipt_path = tmp_path / f"adg_audit_pipeline_receipt_{run_id}.json"
    receipt_path.write_text(json.dumps(receipt, sort_keys=True), encoding="utf-8")
    pointer = {
        "schema_version": planner.REPAIR_HANDOFF_POINTER_SCHEMA_VERSION,
        "adg_run_id": run_id,
        "handoff_path": str(handoff_path),
        "handoff_sha256": hashlib.sha256(handoff_path.read_bytes()).hexdigest(),
        "receipt_path": str(receipt_path),
        "receipt_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
    }
    pointer_path = tmp_path / "adg_repair_handoff_latest.json"
    pointer_path.write_text(json.dumps(pointer, sort_keys=True), encoding="utf-8")
    return pointer_path, receipt, handoff


def test_fresh_plan_binds_exact_receipt_artifacts_and_p0_buckets(tmp_path, monkeypatch):
    pointer_path, receipt, _handoff = _fixture(tmp_path)
    monkeypatch.setattr(planner, "validate_repair_handoff_pointer", lambda _path: (receipt, {}, []))
    monkeypatch.setattr(
        planner.p0_wave_plan,
        "build_p0_remediation_wave_plan",
        lambda _path, limit: {"schema_version": "1.0", "generated_via": "adg_mcp_sqlite", "plan_required": True, "summary": {"total_p0_issues": 1}, "top_files": [], "waves": []},
    )

    json_path, markdown_path, plan = planner.create_p0_execution_plan(pointer_path, output_dir=tmp_path / "plans")

    assert json_path.is_file()
    assert markdown_path.is_file()
    assert plan["schema_version"] == planner.PLAN_SCHEMA_VERSION
    assert plan["p0_counts"] == {"P0_FIX": 1, "P0_WAVE": 3, "P0_TRACKED_BACKLOG": 2}
    assert plan["handoff"]["receipt"]["sha256"] == json.loads((tmp_path / "adg_repair_handoff_latest.json").read_text())["receipt_sha256"]
    assert plan["provenance"]["backend"] == "degraded_sqlite"
    assert "DEGRADED_FALLBACK:" in plan["provenance"]["fallback_reason"]


def test_fresh_plan_rejects_action_queue_count_drift(tmp_path, monkeypatch):
    pointer_path, receipt, handoff = _fixture(tmp_path)
    handoff["repair_handoff"]["legacy_counts"]["P0_WAVE"] = 2
    handoff_path = Path(json.loads(pointer_path.read_text())["handoff_path"])
    handoff_path.write_text(json.dumps(handoff, sort_keys=True), encoding="utf-8")
    pointer = json.loads(pointer_path.read_text())
    pointer["handoff_sha256"] = hashlib.sha256(handoff_path.read_bytes()).hexdigest()
    receipt["repair_handoff"] = handoff["repair_handoff"]
    receipt_path = Path(pointer["receipt_path"])
    receipt_path.write_text(json.dumps(receipt, sort_keys=True), encoding="utf-8")
    pointer["receipt_sha256"] = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    pointer_path.write_text(json.dumps(pointer, sort_keys=True), encoding="utf-8")
    monkeypatch.setattr(planner, "validate_repair_handoff_pointer", lambda _path: (receipt, {}, []))

    with pytest.raises(planner.P0PlanError, match="P0 count mismatch"):
        planner.create_p0_execution_plan(pointer_path, output_dir=tmp_path / "plans")


def test_p0_automation_requires_fresh_plan_before_edits():
    automation = Path(__file__).parents[3] / ".codex" / "automations" / "adg-p0-blocker-burndown" / "automation.toml"
    text = automation.read_text(encoding="utf-8")

    assert "tools/adg/prepare_p0_burndown.py" in text
    assert "requires_fresh_p0_execution_plan = true" in text
    assert "fresh_plan_schema = \"adg-p0-execution-plan/v1\"" in text
    validator_pos = text.index("python tools/adg/consume_adg_repair_handoff.py")
    plan_pos = text.index("python tools/adg/prepare_p0_burndown.py")
    assert validator_pos < plan_pos < text.index("Do not reuse a prior")
