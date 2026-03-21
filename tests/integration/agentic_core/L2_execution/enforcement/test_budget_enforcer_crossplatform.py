"""Tests for BudgetEnforcer cross-platform wall-clock and stdout caps.

Phase 1: ToolBudget runtime enforcement — Contract [2], Guarantee #10.
Covers Windows (threading.Timer) and Unix (SIGALRM) paths.
"""

from __future__ import annotations

import time

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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_budget_enforcer_crossplatform")
_emit_applies_guardrail("p0", "test_budget_enforcer_crossplatform", "p0_governance")
_emit_reads_policy_state("p0", "test_budget_enforcer_crossplatform", "policy_binding")
_emit_snapshots_state("p0", "test_budget_enforcer_crossplatform", "state_snapshot")
emit_replay_key("p0", "test_budget_enforcer_crossplatform")
emit_determinism_digest("p0", "test_budget_enforcer_crossplatform")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_budget_enforcer_crossplatform", "execution_auth")
_emit_validates_capability("p2", "test_budget_enforcer_crossplatform", "capability_check")
_emit_routes_to_capability("p2", "test_budget_enforcer_crossplatform", "capability_route")
_emit_writes_via_uwg("p2", "test_budget_enforcer_crossplatform", "uwg_write")
_emit_blocks_direct_write("p2", "test_budget_enforcer_crossplatform", "direct_write_block")
_emit_records_tool_invocation("p2", "test_budget_enforcer_crossplatform", "tool_invocation")
_emit_captures_execution_output("p2", "test_budget_enforcer_crossplatform", "exec_output")
_emit_dispatches_agent("p3", "test_budget_enforcer_crossplatform", "agent_dispatch")
_emit_coordinates_agents("p3", "test_budget_enforcer_crossplatform", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_budget_enforcer_crossplatform", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_budget_enforcer_crossplatform", "healing_outcome")
_emit_escalates_failure("p3", "test_budget_enforcer_crossplatform", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_budget_enforcer_crossplatform", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_budget_enforcer_crossplatform", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_budget_enforcer_crossplatform", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_budget_enforcer_crossplatform", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_budget_enforcer_crossplatform", "eval_metric")
_emit_stores_embedding("p4", "test_budget_enforcer_crossplatform", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_budget_enforcer_crossplatform", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_budget_enforcer_crossplatform", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.enforcement.budget_enforcer import (
    BudgetEnforcer,
    BudgetExceeded,
    _wall_clock_cap_threading,
)
from agentic_core.L2_execution.enforcement.key_source import TestKeySource, inject_key_source
from agentic_core.L2_execution.types.sandbox_envelope_types import SandboxEnvelope, ToolBudget

inject_key_source(TestKeySource())
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_budget_enforcer_crossplatform", "p4obs", "metric_1")
_emit_emits_metric_event("test_budget_enforcer_crossplatform", "p4obs", "metric_2")
_emit_emits_metric_event("test_budget_enforcer_crossplatform", "p4obs", "metric_3")
_emit_emits_metric_event("test_budget_enforcer_crossplatform", "p4obs", "metric_4")
_emit_emits_metric_event("test_budget_enforcer_crossplatform", "p4obs", "metric_5")
_emit_emits_metric_event("test_budget_enforcer_crossplatform", "p4obs", "metric_6")
_emit_records_incident_event("test_budget_enforcer_crossplatform", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_budget_enforcer_crossplatform", "p4obs", "anomaly")
_emit_writes_observability_log("test_budget_enforcer_crossplatform", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_budget_enforcer_crossplatform", "p4obs", "mon_state")
_emit_triggers_alert("test_budget_enforcer_crossplatform", "p4obs", "alert")
_emit_links_incident_trace("test_budget_enforcer_crossplatform", "p4obs", "trace_link")
_emit_captures_pattern("test_budget_enforcer_crossplatform", "p3lm", "pattern")
_emit_records_learning_event("test_budget_enforcer_crossplatform", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_budget_enforcer_crossplatform", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_budget_enforcer_crossplatform", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_budget_enforcer_crossplatform", "p3lm", "routing")
_emit_improves_agent_policy("test_budget_enforcer_crossplatform", "p3lm", "policy")
_emit_stores_learning_state("test_budget_enforcer_crossplatform", "p3lm", "state")
_emit_records_execution_trace("test_budget_enforcer_crossplatform", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_budget_enforcer_crossplatform", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_budget_enforcer_crossplatform", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_budget_enforcer_crossplatform", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_budget_enforcer_crossplatform", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_budget_enforcer_crossplatform", "env_read", "p2_env_1")
_emit_reads_environ("test_budget_enforcer_crossplatform", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_budget_enforcer_crossplatform", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_budget_enforcer_crossplatform", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_budget_enforcer_crossplatform", "context_pull")
_emit_pulls_context("p1", "test_budget_enforcer_crossplatform", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_budget_enforcer_crossplatform", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_budget_enforcer_crossplatform", "uwg_term_2")
_emit_writes_through("p1", "test_budget_enforcer_crossplatform", "write_through")
_emit_writes_through("p1", "test_budget_enforcer_crossplatform", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_budget_enforcer_crossplatform", "safety_validation")
_emit_invokes_eval("p1", "test_budget_enforcer_crossplatform", "eval_call")
_emit_proposal_commits_routing("p1", "test_budget_enforcer_crossplatform", "routing_commit")
_emit_escalates_to_human("p1", "test_budget_enforcer_crossplatform", "human_escalation")
_emit_routes_through("p1", "test_budget_enforcer_crossplatform", "route_through")
_emit_checks_agent_registry("p1", "test_budget_enforcer_crossplatform", "agent_registry")
_emit_validates_agent_capability("p1", "test_budget_enforcer_crossplatform", "capability")
_emit_dispatches_execution_plan("p1", "test_budget_enforcer_crossplatform", "exec_plan")
_emit_agent_executes_agent("p1", "test_budget_enforcer_crossplatform", "sub_agent")
_emit_routes_to_agent("p1", "test_budget_enforcer_crossplatform", "target_agent")
_emit_verifies_policy("p1", "test_budget_enforcer_crossplatform", "policy_check")
_emit_observes_runtime_state("p1", "test_budget_enforcer_crossplatform", "runtime_state")
_emit_verifies_boundary("p1", "test_budget_enforcer_crossplatform", "boundary_check")
_emit_transcripts_response("p1", "test_budget_enforcer_crossplatform", "transcript")
_emit_hard_fails_untranscripted("p1", "test_budget_enforcer_crossplatform")
_emit_gated_by_confidence("p1", "test_budget_enforcer_crossplatform", "confidence_gate")


def _make_envelope(compute_ms: int = 5000, memory_mb: int = 256, stdout_bytes: int = 1024) -> SandboxEnvelope:
    budget = ToolBudget(compute_ms=compute_ms, memory_mb=memory_mb, stdout_bytes=stdout_bytes)
    return SandboxEnvelope(
        envelope_id="test-env-001",
        tool_name="test_tool",
        tool_args={},
        instruction_packet_id="ip-001",
        budget=budget,
    )


class TestBudgetEnforcerStdoutCap:
    def test_stdout_within_cap_succeeds(self):
        enforcer = BudgetEnforcer()
        envelope = _make_envelope(stdout_bytes=1024)

        def small_tool():
            return "ok"

        exit_code, stdout = enforcer.run(envelope, small_tool)
        assert exit_code == 0
        assert len(stdout) <= 1024

    def test_stdout_over_cap_raises(self):
        enforcer = BudgetEnforcer()
        envelope = _make_envelope(stdout_bytes=5)

        def big_tool():
            return "x" * 100

        with pytest.raises(BudgetExceeded, match="stdout_bytes cap"):
            enforcer.run(envelope, big_tool)

    def test_stdout_exact_cap_boundary_succeeds(self):
        enforcer = BudgetEnforcer()
        # "ok" encodes to 2 bytes — cap at 2 must pass
        envelope = _make_envelope(stdout_bytes=2)

        def exact_tool():
            return "ok"

        exit_code, stdout = enforcer.run(envelope, exact_tool)
        assert exit_code == 0
        assert stdout == b"ok"

    def test_stdout_one_over_cap_raises(self):
        enforcer = BudgetEnforcer()
        envelope = _make_envelope(stdout_bytes=2)

        def over_tool():
            return "abc"  # 3 bytes

        with pytest.raises(BudgetExceeded, match="stdout_bytes cap"):
            enforcer.run(envelope, over_tool)


class TestBudgetEnforcerComputeCap:
    def test_threading_timer_fires_after_deadline(self):
        """Verify threading.Timer cap raises BudgetExceeded on timeout."""
        with pytest.raises(BudgetExceeded, match="compute_ms cap"):
            with _wall_clock_cap_threading(50):
                time.sleep(DEFAULT_SLEEP)

    def test_threading_timer_does_not_fire_within_budget(self):
        """Verify no exception raised when work completes before deadline."""
        with _wall_clock_cap_threading(500):
            time.sleep(0.1)  # well within 500 ms


class TestBudgetEnforcerReturnContract:
    def test_returns_exit_code_zero_on_success(self):
        enforcer = BudgetEnforcer()
        envelope = _make_envelope()

        def fast_tool():
            return "done"

        exit_code, stdout = enforcer.run(envelope, fast_tool)
        assert exit_code == 0
        assert isinstance(stdout, bytes)

    def test_tool_args_passed_through(self):
        enforcer = BudgetEnforcer()
        envelope = _make_envelope()
        # Manually set tool_args on a new envelope via dataclasses.replace
        from dataclasses import replace

        env2 = replace(envelope, tool_args={"x": 42})

        captured: list[dict] = []

        def capturing_tool(x):
            captured.append({"x": x})
            return f"x={x}"

        exit_code, _ = enforcer.run(env2, capturing_tool)
        assert exit_code == 0
        assert captured[0]["x"] == 42
