"""ADG-driven tests for runtime/execution_trace.py — fan_in=1."""
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

_emit_applies_guardrail("p0", "test_execution_trace_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_execution_trace_adg", "policy_binding")
_emit_snapshots_state("p0", "test_execution_trace_adg", "state_snapshot")
emit_replay_key("p0", "test_execution_trace_adg")
emit_determinism_digest("p0", "test_execution_trace_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_execution_trace_adg", "execution_auth")
_emit_validates_capability("p2", "test_execution_trace_adg", "capability_check")
_emit_routes_to_capability("p2", "test_execution_trace_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_execution_trace_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_execution_trace_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_execution_trace_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_execution_trace_adg", "exec_output")
_emit_dispatches_agent("p3", "test_execution_trace_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_execution_trace_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_execution_trace_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_execution_trace_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_execution_trace_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_execution_trace_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_execution_trace_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_execution_trace_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_execution_trace_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_execution_trace_adg", "eval_metric")
_emit_stores_embedding("p4", "test_execution_trace_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_execution_trace_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_execution_trace_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.runtime.execution_trace import ExecutionTrace, ExecutionTraceManager


class TestExecutionTrace:
    def test_creates(self):
        trace = ExecutionTrace(
            trace_id="trace-abc",
            plan_hash="phash",
            policy_hash="pohash",
            determinism_digest="ddig",
            hierarchy_hash="hhash",
            metadata={},
        )
        assert trace.trace_id == "trace-abc"

    def test_is_frozen(self):
        trace = ExecutionTrace(
            trace_id="t",
            plan_hash="p",
            policy_hash="po",
            determinism_digest="d",
            hierarchy_hash="h",
            metadata={},
        )
        with pytest.raises(Exception):
            trace.trace_id = "modified"


class TestExecutionTraceManager:
    def test_creates(self):
        manager = ExecutionTraceManager()
        assert manager is not None

    def test_start_trace_returns_str(self):
        manager = ExecutionTraceManager()
        trace_id = manager.start_trace(
            plan_hash="p",
            policy_hash="po",
            hierarchy_hash="h",
        )
        assert isinstance(trace_id, str)
        assert len(trace_id) > 0

    def test_has_active_trace_after_start(self):
        manager = ExecutionTraceManager()
        manager.start_trace(plan_hash="p", policy_hash="po", hierarchy_hash="h")
        assert manager._active_trace is not None
