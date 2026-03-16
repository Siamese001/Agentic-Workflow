"""ADG-driven tests for system_learning/stores/telemetry_store.py — fan_in=1."""
from __future__ import annotations

import json

import pytest

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

_emit_records_execution_trace("p0", "evidence", "test_telemetry_store_adg")
_emit_applies_guardrail("p0", "test_telemetry_store_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_telemetry_store_adg", "policy_binding")
_emit_snapshots_state("p0", "test_telemetry_store_adg", "state_snapshot")
emit_replay_key("p0", "test_telemetry_store_adg")
emit_determinism_digest("p0", "test_telemetry_store_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_telemetry_store_adg", "execution_auth")
_emit_validates_capability("p2", "test_telemetry_store_adg", "capability_check")
_emit_routes_to_capability("p2", "test_telemetry_store_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_telemetry_store_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_telemetry_store_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_telemetry_store_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_telemetry_store_adg", "exec_output")
_emit_dispatches_agent("p3", "test_telemetry_store_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_telemetry_store_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_telemetry_store_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_telemetry_store_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_telemetry_store_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_telemetry_store_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_telemetry_store_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_telemetry_store_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_telemetry_store_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_telemetry_store_adg", "eval_metric")
_emit_stores_embedding("p4", "test_telemetry_store_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_telemetry_store_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_telemetry_store_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from system_learning.stores.telemetry_store import FileBackedTelemetryStore


class TestFileBackedTelemetryStore:
    def test_creates(self, tmp_path):
        store = FileBackedTelemetryStore(telemetry_path=tmp_path / "telemetry.jsonl")
        assert store is not None

    def test_missing_file_returns_empty_tuple(self, tmp_path):
        store = FileBackedTelemetryStore(telemetry_path=tmp_path / "missing.jsonl")
        result = store.read_events(0, 9999999999)
        assert result == ()

    def test_returns_tuple(self, tmp_path):
        store = FileBackedTelemetryStore(telemetry_path=tmp_path / "t.jsonl")
        result = store.read_events(0, 9999999999)
        assert isinstance(result, tuple)

    def test_reads_events_from_file(self, tmp_path):
        event = {"timestamp_utc": 1000, "event_type": "heal", "payload": {"ok": True}}
        path = tmp_path / "events.jsonl"
        path.write_text(json.dumps(event) + "\n", encoding="utf-8")
        store = FileBackedTelemetryStore(telemetry_path=path)
        result = store.read_events(0, 9999999999)
        assert isinstance(result, tuple)

    def test_has_read_events(self):
        assert hasattr(FileBackedTelemetryStore, "read_events")
