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
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_preventative_sandbox", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_preventative_sandbox", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_preventative_sandbox", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_preventative_sandbox", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_preventative_sandbox", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_preventative_sandbox", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_preventative_sandbox", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_preventative_sandbox", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_preventative_sandbox", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_preventative_sandbox", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_preventative_sandbox", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_preventative_sandbox", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_preventative_sandbox", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_preventative_sandbox", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_preventative_sandbox", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_preventative_sandbox", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_preventative_sandbox", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_preventative_sandbox", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_preventative_sandbox", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_preventative_sandbox", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_preventative_sandbox", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_preventative_sandbox", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_preventative_sandbox", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_preventative_sandbox", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_preventative_sandbox", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_preventative_sandbox", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_preventative_sandbox", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_preventative_sandbox", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_preventative_sandbox")
# REMOVED: _emit_applies_guardrail("p0", "test_preventative_sandbox", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_preventative_sandbox", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_preventative_sandbox", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_preventative_sandbox", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_preventative_sandbox", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_preventative_sandbox", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_preventative_sandbox", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_preventative_sandbox", "write_through")
# REMOVED: _emit_writes_through("p1", "test_preventative_sandbox", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_preventative_sandbox", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_preventative_sandbox", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_preventative_sandbox", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_preventative_sandbox", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_preventative_sandbox", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_preventative_sandbox", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_preventative_sandbox", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_preventative_sandbox", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_preventative_sandbox", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_preventative_sandbox", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_preventative_sandbox", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_preventative_sandbox", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_preventative_sandbox", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_preventative_sandbox", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_preventative_sandbox")
# REMOVED: _emit_gated_by_confidence("p1", "test_preventative_sandbox", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_preventative_sandbox")
# REMOVED: emit_determinism_digest("p0", "test_preventative_sandbox")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_preventative_sandbox", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_preventative_sandbox", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_preventative_sandbox", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_preventative_sandbox", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_preventative_sandbox", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_preventative_sandbox", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_preventative_sandbox", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_preventative_sandbox", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_preventative_sandbox", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_preventative_sandbox", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_preventative_sandbox", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_preventative_sandbox", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_preventative_sandbox", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_preventative_sandbox", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_preventative_sandbox", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_preventative_sandbox", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_preventative_sandbox", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_preventative_sandbox", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_preventative_sandbox", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_preventative_sandbox", "exec_snapshot_link")

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
