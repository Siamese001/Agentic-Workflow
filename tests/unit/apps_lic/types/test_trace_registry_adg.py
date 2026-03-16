"""ADG-driven tests for apps_lic/types/TraceRegistry.py — fan_in=2.

Contract tests: TraceRegistry init, add/get/clear, persistence-free operation.
"""
from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_trace_registry_adg")
_emit_applies_guardrail("p0", "test_trace_registry_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_trace_registry_adg", "policy_binding")
_emit_snapshots_state("p0", "test_trace_registry_adg", "state_snapshot")
emit_replay_key("p0", "test_trace_registry_adg")
emit_determinism_digest("p0", "test_trace_registry_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_trace_registry_adg", "execution_auth")
_emit_validates_capability("p2", "test_trace_registry_adg", "capability_check")
_emit_routes_to_capability("p2", "test_trace_registry_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_trace_registry_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_trace_registry_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_trace_registry_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_trace_registry_adg", "exec_output")
_emit_dispatches_agent("p3", "test_trace_registry_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_trace_registry_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_trace_registry_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_trace_registry_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_trace_registry_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_trace_registry_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_trace_registry_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_trace_registry_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_trace_registry_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_trace_registry_adg", "eval_metric")
_emit_stores_embedding("p4", "test_trace_registry_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_trace_registry_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_trace_registry_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from apps_lic.types.TraceRegistry import TraceRegistry


class TestTraceRegistryInit:
    def test_creates_without_persistence(self):
        registry = TraceRegistry()
        assert registry is not None

    def test_traces_start_empty(self):
        registry = TraceRegistry()
        assert registry._traces == []

    def test_persistence_path_default_none(self):
        registry = TraceRegistry()
        assert registry.persistence_path is None


class TestTraceRegistryAPI:
    def setup_method(self):
        self.registry = TraceRegistry()

    def test_has_add_trace(self):
        assert hasattr(self.registry, "add_trace")

    def test_has_get_traces(self):
        assert hasattr(self.registry, "get_traces")

    def test_has_clear(self):
        assert hasattr(self.registry, "clear")

    def test_add_trace_increments_count(self):
        initial = len(self.registry._traces)
        self.registry.add_trace(event_type="test_event", details={"step": "init"})
        assert len(self.registry._traces) == initial + 1

    def test_get_traces_returns_list(self):
        self.registry.add_trace(event_type="test_event", details={"step": "init"})
        traces = self.registry.get_traces()
        assert isinstance(traces, list)
        assert len(traces) >= 1

    def test_clear_empties_traces(self):
        self.registry.add_trace(event_type="test_event", details={"step": "init"})
        self.registry.clear()
        assert self.registry._traces == []
