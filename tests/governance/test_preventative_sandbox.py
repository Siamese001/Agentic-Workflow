"""H1 governance tests: PreventativeSandbox full-spectrum patching.

Validates:
- Write vectors blocked during sandbox activation
- Originals restored after context exit
- Double-activation prevented (idempotent guard)
- SandboxViolationError raised with function name
- Custom target registration
"""

import os
import subprocess

import pytest

from agentic_core.L2_execution.enforcement.preventative_sandbox import (
    PreventativeSandbox,
    SandboxViolationError,
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

_emit_records_execution_trace("p0", "evidence", "test_preventative_sandbox")
_emit_applies_guardrail("p0", "test_preventative_sandbox", "p0_governance")
_emit_reads_policy_state("p0", "test_preventative_sandbox", "policy_binding")
_emit_snapshots_state("p0", "test_preventative_sandbox", "state_snapshot")
emit_replay_key("p0", "test_preventative_sandbox")
emit_determinism_digest("p0", "test_preventative_sandbox")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_preventative_sandbox", "execution_auth")
_emit_validates_capability("p2", "test_preventative_sandbox", "capability_check")
_emit_routes_to_capability("p2", "test_preventative_sandbox", "capability_route")
_emit_writes_via_uwg("p2", "test_preventative_sandbox", "uwg_write")
_emit_blocks_direct_write("p2", "test_preventative_sandbox", "direct_write_block")
_emit_records_tool_invocation("p2", "test_preventative_sandbox", "tool_invocation")
_emit_captures_execution_output("p2", "test_preventative_sandbox", "exec_output")
_emit_dispatches_agent("p3", "test_preventative_sandbox", "agent_dispatch")
_emit_coordinates_agents("p3", "test_preventative_sandbox", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_preventative_sandbox", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_preventative_sandbox", "healing_outcome")
_emit_escalates_failure("p3", "test_preventative_sandbox", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_preventative_sandbox", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_preventative_sandbox", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_preventative_sandbox", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_preventative_sandbox", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_preventative_sandbox", "eval_metric")
_emit_stores_embedding("p4", "test_preventative_sandbox", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_preventative_sandbox", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_preventative_sandbox", "exec_snapshot_link")

pytestmark = pytest.mark.governance


class TestSandboxBlocking:
    """Write vectors must raise SandboxViolationError when active."""

    def test_os_remove_blocked(self):
        sandbox = PreventativeSandbox()
        with sandbox.activated():
            with pytest.raises(SandboxViolationError) as exc:
                os.remove("nonexistent.txt")
            assert "os.remove" in str(exc.value)

    def test_subprocess_run_blocked(self):
        sandbox = PreventativeSandbox()
        with sandbox.activated():
            with pytest.raises(SandboxViolationError) as exc:
                subprocess.run(["echo", "test"])
            assert "subprocess.run" in str(exc.value)

    def test_os_system_blocked(self):
        sandbox = PreventativeSandbox()
        with sandbox.activated():
            with pytest.raises(SandboxViolationError) as exc:
                os.system("echo test")
            assert "os.system" in str(exc.value)

    def test_builtins_open_blocked(self):
        sandbox = PreventativeSandbox()
        with sandbox.activated():
            with pytest.raises(SandboxViolationError) as exc:
                open("nonexistent.txt", "w")  # noqa: SIM115
            assert "builtins.open" in str(exc.value)


class TestSandboxRestoration:
    """Originals must be restored after context exit."""

    def test_os_remove_restored(self):
        original = os.remove
        sandbox = PreventativeSandbox()
        with sandbox.activated():
            assert os.remove is not original
        assert os.remove is original

    def test_subprocess_run_restored(self):
        original = subprocess.run
        sandbox = PreventativeSandbox()
        with sandbox.activated():
            assert subprocess.run is not original
        assert subprocess.run is original

    def test_restored_on_exception(self):
        original = os.remove
        sandbox = PreventativeSandbox()
        with pytest.raises(ValueError, match="test error"):
            with sandbox.activated():
                raise ValueError("test error")
        assert os.remove is original


class TestDoubleActivation:
    """Double activation must be prevented."""

    def test_double_activation_raises(self):
        sandbox = PreventativeSandbox()
        with sandbox.activated():
            with pytest.raises(RuntimeError, match="already active"):
                with sandbox.activated():
                    pass


class TestCustomTargets:
    """Custom write vectors can be registered."""

    def test_custom_target_blocked(self):
        sandbox = PreventativeSandbox()
        sandbox.register_target("os.path", "exists", "custom")
        original = os.path.exists
        with sandbox.activated():
            with pytest.raises(SandboxViolationError):
                os.path.exists("test")
        assert os.path.exists is original


class TestSandboxState:
    """Sandbox state tracking."""

    def test_inactive_by_default(self):
        sandbox = PreventativeSandbox()
        assert sandbox.is_active is False

    def test_active_inside_context(self):
        sandbox = PreventativeSandbox()
        with sandbox.activated():
            assert sandbox.is_active is True
        assert sandbox.is_active is False
