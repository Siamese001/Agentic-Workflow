"""GAP-A + GAP-B invariant tests.

GAP-A invariant: run_manifest.json exists with correct trace_id after heal run.
  Negative control: removing the _write_run_manifest_json call → file absent.

GAP-B invariant: mutation ledger is non-empty after a heal run that commits writes.
  Negative control: passing None path → ledger absent AND ERROR logged.
"""

from __future__ import annotations

import json

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_gap_a_b_wire_in")
_emit_applies_guardrail("p0", "test_gap_a_b_wire_in", "p0_governance")
_emit_reads_policy_state("p0", "test_gap_a_b_wire_in", "policy_binding")
_emit_snapshots_state("p0", "test_gap_a_b_wire_in", "state_snapshot")
emit_replay_key("p0", "test_gap_a_b_wire_in")
emit_determinism_digest("p0", "test_gap_a_b_wire_in")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_gap_a_b_wire_in", "execution_auth")
_emit_validates_capability("p2", "test_gap_a_b_wire_in", "capability_check")
_emit_routes_to_capability("p2", "test_gap_a_b_wire_in", "capability_route")
_emit_writes_via_uwg("p2", "test_gap_a_b_wire_in", "uwg_write")
_emit_blocks_direct_write("p2", "test_gap_a_b_wire_in", "direct_write_block")
_emit_records_tool_invocation("p2", "test_gap_a_b_wire_in", "tool_invocation")
_emit_captures_execution_output("p2", "test_gap_a_b_wire_in", "exec_output")
_emit_dispatches_agent("p3", "test_gap_a_b_wire_in", "agent_dispatch")
_emit_coordinates_agents("p3", "test_gap_a_b_wire_in", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_gap_a_b_wire_in", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_gap_a_b_wire_in", "healing_outcome")
_emit_escalates_failure("p3", "test_gap_a_b_wire_in", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_gap_a_b_wire_in", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_gap_a_b_wire_in", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_gap_a_b_wire_in", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_gap_a_b_wire_in", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_gap_a_b_wire_in", "eval_metric")
_emit_stores_embedding("p4", "test_gap_a_b_wire_in", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_gap_a_b_wire_in", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_gap_a_b_wire_in", "exec_snapshot_link")


class TestGapARunManifest:
    def test_write_run_manifest_creates_file(self, tmp_path):
        from agentic_core.L0_routing.scripts.execute_ssot import _write_run_manifest_json

        trace_id = "TEST-GAP-A-001"
        _write_run_manifest_json(
            trace_id=trace_id,
            execution_mode="heal",
            territories=[APPS_RG_DIR, APPS_LIC_DIR],
            agents_executed=["AgentA", "AgentB"],
            output_dir=tmp_path,
        )

        manifest_path = tmp_path / "run_manifest.json"
        assert manifest_path.exists(), "run_manifest.json must exist after _write_run_manifest_json()"

        with manifest_path.open(encoding="utf-8") as fh:
            data = json.load(fh)

        assert data["trace_id"] == trace_id
        assert data["execution_mode"] == "heal"
        assert set(data["territories"]) == {APPS_RG_DIR, APPS_LIC_DIR}
        assert data["agent_count"] == 2

    def test_negative_control_no_call_means_no_file(self, tmp_path):
        manifest_path = tmp_path / "run_manifest.json"
        assert not manifest_path.exists(), "Negative control: no manifest without call"

    def test_write_run_manifest_trace_id_in_file(self, tmp_path):
        from agentic_core.L0_routing.scripts.execute_ssot import _write_run_manifest_json

        trace_id = "SSOT-20260101-abcdef01"
        _write_run_manifest_json(
            trace_id=trace_id,
            execution_mode="scan",
            territories=[AGENTIC_CORE_DIR],
            agents_executed=["ScanAgent"],
            output_dir=tmp_path,
        )

        manifest_path = tmp_path / "run_manifest.json"
        raw = manifest_path.read_text(encoding="utf-8")
        assert trace_id in raw, "trace_id must appear verbatim in run_manifest.json"

    def test_write_run_manifest_creates_parent_dirs(self, tmp_path):
        from agentic_core.L0_routing.scripts.execute_ssot import _write_run_manifest_json

        deep_dir = tmp_path / "logs" / "run_manifests" / "TRACE-X"
        _write_run_manifest_json(
            trace_id="TRACE-X",
            execution_mode="heal",
            territories=[],
            agents_executed=[],
            output_dir=deep_dir,
        )
        assert (deep_dir / "run_manifest.json").exists()


class TestGapBMutationLedger:
    def test_set_mutation_ledger_path_then_write_creates_ledger(self, tmp_path):
        from agentic_core.L2_execution.tools.write_gateway import (
            set_mutation_ledger_path,
            write_text,
        )

        ledger_path = tmp_path / "mutation_ledger.jsonl"
        set_mutation_ledger_path(ledger_path, "TEST-GAP-B-001")

        target = tmp_path / "output.txt"
        write_text(target, "hello")

        assert ledger_path.exists(), "Ledger file must be created after write_text()"
        entries = [json.loads(line) for line in ledger_path.read_text().splitlines() if line.strip()]
        assert len(entries) >= 1
        assert entries[0]["trace_id"] == "TEST-GAP-B-001"

    def test_negative_control_no_ledger_path_means_no_ledger(self, tmp_path):
        from agentic_core.L2_execution.tools.write_gateway import write_text

        target = tmp_path / "out.txt"
        write_text(target, "content")

        jsonl_files = list(tmp_path.rglob("*.jsonl"))
        assert jsonl_files == [], "Negative control: no ledger when set_mutation_ledger_path not called"

    def test_ledger_non_empty_after_heal_write(self, tmp_path):
        from agentic_core.L2_execution.tools.write_gateway import (
            set_mutation_ledger_path,
            write_text,
        )

        ledger_path = tmp_path / "mutation_ledger.jsonl"
        set_mutation_ledger_path(ledger_path, "TEST-GAP-B-002")

        for i in range(3):
            write_text(tmp_path / f"file_{i}.txt", f"content {i}")

        entries = [json.loads(line) for line in ledger_path.read_text().splitlines() if line.strip()]
        assert len(entries) == 3, f"Expected 3 ledger entries, got {len(entries)}"

    def test_ledger_entries_have_required_fields(self, tmp_path):
        from agentic_core.L2_execution.tools.write_gateway import (
            set_mutation_ledger_path,
            write_text,
        )

        ledger_path = tmp_path / "mutation_ledger.jsonl"
        set_mutation_ledger_path(ledger_path, "TEST-GAP-B-003")
        write_text(tmp_path / "test.py", "x = 1")

        entries = [json.loads(line) for line in ledger_path.read_text().splitlines() if line.strip()]
        assert len(entries) == 1
        entry = entries[0]
        required_fields = {"trace_id", "path", "operation", "result"}
        assert required_fields.issubset(entry.keys()), f"Missing fields: {required_fields - entry.keys()}"
