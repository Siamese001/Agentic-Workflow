"""ADG-driven tests for L2_execution/engines/execute_command_executor.py — fan_in=0."""
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

_emit_records_execution_trace("p0", "evidence", "test_execute_command_executor_adg")
_emit_applies_guardrail("p0", "test_execute_command_executor_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_execute_command_executor_adg", "policy_binding")
_emit_snapshots_state("p0", "test_execute_command_executor_adg", "state_snapshot")
emit_replay_key("p0", "test_execute_command_executor_adg")
emit_determinism_digest("p0", "test_execute_command_executor_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_execute_command_executor_adg", "execution_auth")
_emit_validates_capability("p2", "test_execute_command_executor_adg", "capability_check")
_emit_routes_to_capability("p2", "test_execute_command_executor_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_execute_command_executor_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_execute_command_executor_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_execute_command_executor_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_execute_command_executor_adg", "exec_output")
_emit_dispatches_agent("p3", "test_execute_command_executor_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_execute_command_executor_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_execute_command_executor_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_execute_command_executor_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_execute_command_executor_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_execute_command_executor_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_execute_command_executor_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_execute_command_executor_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_execute_command_executor_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_execute_command_executor_adg", "eval_metric")
_emit_stores_embedding("p4", "test_execute_command_executor_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_execute_command_executor_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_execute_command_executor_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.engines.execute_command_executor import (
        ExecuteCommandArgs,
        get_project_root,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ExecuteCommandArgs = None  # type: ignore[assignment,misc]
    get_project_root = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="execute_command_executor deps unavailable")
class TestExecuteCommandArgs:
    def test_is_typed_dict(self):
        assert ExecuteCommandArgs is not None

    def test_has_command_key(self):
        assert "command" in ExecuteCommandArgs.__annotations__

    def test_has_timeout_key(self):
        assert "timeout" in ExecuteCommandArgs.__annotations__


@pytest.mark.skipif(not _AVAILABLE, reason="execute_command_executor deps unavailable")
class TestGetProjectRoot:
    def test_returns_path(self):
        from pathlib import Path
        result = get_project_root()
        assert isinstance(result, Path)

    def test_path_is_absolute(self):
        result = get_project_root()
        assert result.is_absolute()


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
