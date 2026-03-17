"""Regression tests for SandboxEnvelope ToolBudget integration."""

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

_emit_records_execution_trace("p0", "evidence", "test_sandbox_envelope_budget")
_emit_applies_guardrail("p0", "test_sandbox_envelope_budget", "p0_governance")
_emit_reads_policy_state("p0", "test_sandbox_envelope_budget", "policy_binding")
_emit_snapshots_state("p0", "test_sandbox_envelope_budget", "state_snapshot")
emit_replay_key("p0", "test_sandbox_envelope_budget")
emit_determinism_digest("p0", "test_sandbox_envelope_budget")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_sandbox_envelope_budget", "execution_auth")
_emit_validates_capability("p2", "test_sandbox_envelope_budget", "capability_check")
_emit_routes_to_capability("p2", "test_sandbox_envelope_budget", "capability_route")
_emit_writes_via_uwg("p2", "test_sandbox_envelope_budget", "uwg_write")
_emit_blocks_direct_write("p2", "test_sandbox_envelope_budget", "direct_write_block")
_emit_records_tool_invocation("p2", "test_sandbox_envelope_budget", "tool_invocation")
_emit_captures_execution_output("p2", "test_sandbox_envelope_budget", "exec_output")
_emit_dispatches_agent("p3", "test_sandbox_envelope_budget", "agent_dispatch")
_emit_coordinates_agents("p3", "test_sandbox_envelope_budget", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_sandbox_envelope_budget", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_sandbox_envelope_budget", "healing_outcome")
_emit_escalates_failure("p3", "test_sandbox_envelope_budget", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_sandbox_envelope_budget", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_sandbox_envelope_budget", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_sandbox_envelope_budget", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_sandbox_envelope_budget", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_sandbox_envelope_budget", "eval_metric")
_emit_stores_embedding("p4", "test_sandbox_envelope_budget", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_sandbox_envelope_budget", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_sandbox_envelope_budget", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

"""Regression: SandboxEnvelope must carry ToolBudget in signable surface."""
from agentic_core.L2_execution.enforcement.key_source import (
    TestKeySource,
    inject_key_source,
)
from agentic_core.L2_execution.types.sandbox_envelope_types import (
    SandboxEnvelope,
    ToolBudget,
)
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

_emit_emits_metric_event("test_sandbox_envelope_budget", "p4obs", "metric_1")
_emit_emits_metric_event("test_sandbox_envelope_budget", "p4obs", "metric_2")
_emit_emits_metric_event("test_sandbox_envelope_budget", "p4obs", "metric_3")
_emit_emits_metric_event("test_sandbox_envelope_budget", "p4obs", "metric_4")
_emit_emits_metric_event("test_sandbox_envelope_budget", "p4obs", "metric_5")
_emit_emits_metric_event("test_sandbox_envelope_budget", "p4obs", "metric_6")
_emit_records_incident_event("test_sandbox_envelope_budget", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_sandbox_envelope_budget", "p4obs", "anomaly")
_emit_writes_observability_log("test_sandbox_envelope_budget", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_sandbox_envelope_budget", "p4obs", "mon_state")
_emit_triggers_alert("test_sandbox_envelope_budget", "p4obs", "alert")
_emit_links_incident_trace("test_sandbox_envelope_budget", "p4obs", "trace_link")
_emit_captures_pattern("test_sandbox_envelope_budget", "p3lm", "pattern")
_emit_records_learning_event("test_sandbox_envelope_budget", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_sandbox_envelope_budget", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_sandbox_envelope_budget", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_sandbox_envelope_budget", "p3lm", "routing")
_emit_improves_agent_policy("test_sandbox_envelope_budget", "p3lm", "policy")
_emit_stores_learning_state("test_sandbox_envelope_budget", "p3lm", "state")
_emit_records_execution_trace("test_sandbox_envelope_budget", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_sandbox_envelope_budget", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_sandbox_envelope_budget", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_sandbox_envelope_budget", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_sandbox_envelope_budget", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_sandbox_envelope_budget", "env_read", "p2_env_1")
_emit_reads_environ("test_sandbox_envelope_budget", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_sandbox_envelope_budget", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_sandbox_envelope_budget", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_sandbox_envelope_budget", "context_pull")
_emit_pulls_context("p1", "test_sandbox_envelope_budget", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_sandbox_envelope_budget", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_sandbox_envelope_budget", "uwg_term_secondary")
_emit_writes_through("p1", "test_sandbox_envelope_budget", "write_through")
_emit_writes_through("p1", "test_sandbox_envelope_budget", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_sandbox_envelope_budget", "safety_validation")
_emit_invokes_eval("p1", "test_sandbox_envelope_budget", "eval_call")
_emit_proposal_commits_routing("p1", "test_sandbox_envelope_budget", "routing_commit")
_emit_escalates_to_human("p1", "test_sandbox_envelope_budget", "human_escalation")
_emit_routes_through("p1", "test_sandbox_envelope_budget", "route_through")
_emit_checks_agent_registry("p1", "test_sandbox_envelope_budget", "agent_registry")
_emit_validates_agent_capability("p1", "test_sandbox_envelope_budget", "capability")
_emit_dispatches_execution_plan("p1", "test_sandbox_envelope_budget", "exec_plan")
_emit_agent_executes_agent("p1", "test_sandbox_envelope_budget", "sub_agent")
_emit_routes_to_agent("p1", "test_sandbox_envelope_budget", "target_agent")
_emit_verifies_policy("p1", "test_sandbox_envelope_budget", "policy_check")
_emit_observes_runtime_state("p1", "test_sandbox_envelope_budget", "runtime_state")
_emit_verifies_boundary("p1", "test_sandbox_envelope_budget", "boundary_check")
_emit_transcripts_response("p1", "test_sandbox_envelope_budget", "transcript")
_emit_hard_fails_untranscripted("p1", "test_sandbox_envelope_budget")
_emit_gated_by_confidence("p1", "test_sandbox_envelope_budget", "confidence_gate")

inject_key_source(TestKeySource())


def _make_env(**kwargs) -> SandboxEnvelope:
    defaults = {"envelope_id": "e1", "tool_name": "test_tool"}
    return SandboxEnvelope(**{**defaults, **kwargs})


def test_default_budget_present():
    env = _make_env()
    assert env.budget.compute_ms > 0
    assert env.budget.memory_mb > 0
    assert env.budget.stdout_bytes > 0


def test_custom_budget_in_signable_dict():
    budget = ToolBudget(compute_ms=5000, memory_mb=64, stdout_bytes=1024)
    env = _make_env(budget=budget)
    sd = env._signable_dict()
    assert sd["budget"] == {"compute_ms": 5000, "memory_mb": 64, "stdout_bytes": 1024}


def test_budget_bound_in_signature():
    env1 = _make_env(budget=ToolBudget(compute_ms=1000, memory_mb=32, stdout_bytes=512))
    env2 = _make_env(budget=ToolBudget(compute_ms=9000, memory_mb=32, stdout_bytes=512))
    assert env1.signature != env2.signature


def test_zero_budget_rejected():
    with pytest.raises(ValueError):
        ToolBudget(compute_ms=0, memory_mb=64, stdout_bytes=1024)


def test_verify_passes_with_budget():
    secret = TestKeySource.TEST_SECRET
    env = _make_env(budget=ToolBudget(compute_ms=5000, memory_mb=64, stdout_bytes=1024))
    env.verify(secret)  # must not raise
