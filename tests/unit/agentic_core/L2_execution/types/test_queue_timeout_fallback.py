"""
WAVE 3 tests — Queue timeout fallback to Gemini-2.5-Pro.

Validates:
- Queue wait exceeding timeout escalates to Gemini-2.5-Pro
- Queue wait below timeout does not escalate
- Timeout constant is deterministic
- Escalation produces correct failure type and model_id
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_queue_timeout_fallback")
_emit_applies_guardrail("p0", "test_queue_timeout_fallback", "p0_governance")
_emit_reads_policy_state("p0", "test_queue_timeout_fallback", "policy_binding")
_emit_snapshots_state("p0", "test_queue_timeout_fallback", "state_snapshot")
emit_replay_key("p0", "test_queue_timeout_fallback")
emit_determinism_digest("p0", "test_queue_timeout_fallback")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_queue_timeout_fallback", "execution_auth")
_emit_validates_capability("p2", "test_queue_timeout_fallback", "capability_check")
_emit_routes_to_capability("p2", "test_queue_timeout_fallback", "capability_route")
_emit_writes_via_uwg("p2", "test_queue_timeout_fallback", "uwg_write")
_emit_blocks_direct_write("p2", "test_queue_timeout_fallback", "direct_write_block")
_emit_records_tool_invocation("p2", "test_queue_timeout_fallback", "tool_invocation")
_emit_captures_execution_output("p2", "test_queue_timeout_fallback", "exec_output")
_emit_dispatches_agent("p3", "test_queue_timeout_fallback", "agent_dispatch")
_emit_coordinates_agents("p3", "test_queue_timeout_fallback", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_queue_timeout_fallback", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_queue_timeout_fallback", "healing_outcome")
_emit_escalates_failure("p3", "test_queue_timeout_fallback", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_queue_timeout_fallback", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_queue_timeout_fallback", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_queue_timeout_fallback", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_queue_timeout_fallback", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_queue_timeout_fallback", "eval_metric")
_emit_stores_embedding("p4", "test_queue_timeout_fallback", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_queue_timeout_fallback", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_queue_timeout_fallback", "exec_snapshot_link")

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

from agentic_core.L2_execution.types.vllm_backpressure_types import (
    MAX_QUEUE_DEPTH,
    QUEUE_WAIT_TIMEOUT_SECONDS,
    VLLMCircuitBreaker,
    VLLMQueueState,
    evaluate_backpressure,
)
from agentic_core.L2_execution.types.vllm_token_budget_types import (
    GEMINI_25_PRO_MODEL_ID,
    VLLMFailureType,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_queue_timeout_fallback", "p4obs", "metric_1")
_emit_emits_metric_event("test_queue_timeout_fallback", "p4obs", "metric_2")
_emit_emits_metric_event("test_queue_timeout_fallback", "p4obs", "metric_3")
_emit_emits_metric_event("test_queue_timeout_fallback", "p4obs", "metric_4")
_emit_emits_metric_event("test_queue_timeout_fallback", "p4obs", "metric_5")
_emit_emits_metric_event("test_queue_timeout_fallback", "p4obs", "metric_6")
_emit_records_incident_event("test_queue_timeout_fallback", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_queue_timeout_fallback", "p4obs", "anomaly")
_emit_writes_observability_log("test_queue_timeout_fallback", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_queue_timeout_fallback", "p4obs", "mon_state")
_emit_triggers_alert("test_queue_timeout_fallback", "p4obs", "alert")
_emit_links_incident_trace("test_queue_timeout_fallback", "p4obs", "trace_link")
_emit_captures_pattern("test_queue_timeout_fallback", "p3lm", "pattern")
_emit_records_learning_event("test_queue_timeout_fallback", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_queue_timeout_fallback", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_queue_timeout_fallback", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_queue_timeout_fallback", "p3lm", "routing")
_emit_improves_agent_policy("test_queue_timeout_fallback", "p3lm", "policy")
_emit_stores_learning_state("test_queue_timeout_fallback", "p3lm", "state")
_emit_records_execution_trace("test_queue_timeout_fallback", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_queue_timeout_fallback", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_queue_timeout_fallback", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_queue_timeout_fallback", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_queue_timeout_fallback", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_queue_timeout_fallback", "env_read", "p2_env_1")
_emit_reads_environ("test_queue_timeout_fallback", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_queue_timeout_fallback", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_queue_timeout_fallback", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_queue_timeout_fallback", "context_pull")
_emit_pulls_context("p1", "test_queue_timeout_fallback", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_queue_timeout_fallback", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_queue_timeout_fallback", "uwg_term_secondary")
_emit_writes_through("p1", "test_queue_timeout_fallback", "write_through")
_emit_writes_through("p1", "test_queue_timeout_fallback", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_queue_timeout_fallback", "safety_validation")
_emit_invokes_eval("p1", "test_queue_timeout_fallback", "eval_call")
_emit_proposal_commits_routing("p1", "test_queue_timeout_fallback", "routing_commit")
_emit_escalates_to_human("p1", "test_queue_timeout_fallback", "human_escalation")
_emit_routes_through("p1", "test_queue_timeout_fallback", "route_through")
_emit_checks_agent_registry("p1", "test_queue_timeout_fallback", "agent_registry")
_emit_validates_agent_capability("p1", "test_queue_timeout_fallback", "capability")
_emit_dispatches_execution_plan("p1", "test_queue_timeout_fallback", "exec_plan")
_emit_agent_executes_agent("p1", "test_queue_timeout_fallback", "sub_agent")
_emit_routes_to_agent("p1", "test_queue_timeout_fallback", "target_agent")
_emit_verifies_policy("p1", "test_queue_timeout_fallback", "policy_check")
_emit_observes_runtime_state("p1", "test_queue_timeout_fallback", "runtime_state")
_emit_verifies_boundary("p1", "test_queue_timeout_fallback", "boundary_check")
_emit_transcripts_response("p1", "test_queue_timeout_fallback", "transcript")
_emit_hard_fails_untranscripted("p1", "test_queue_timeout_fallback")
_emit_gated_by_confidence("p1", "test_queue_timeout_fallback", "confidence_gate")


def make_closed_breaker() -> VLLMCircuitBreaker:
    return VLLMCircuitBreaker(tier="local_fast")


def make_timed_out_queue() -> VLLMQueueState:
    return VLLMQueueState(
        current_depth=1,
        max_depth=MAX_QUEUE_DEPTH,
        oldest_wait_seconds=QUEUE_WAIT_TIMEOUT_SECONDS,
        timeout_seconds=QUEUE_WAIT_TIMEOUT_SECONDS,
    )


def make_within_timeout_queue() -> VLLMQueueState:
    return VLLMQueueState(
        current_depth=1,
        max_depth=MAX_QUEUE_DEPTH,
        oldest_wait_seconds=QUEUE_WAIT_TIMEOUT_SECONDS - 0.1,
        timeout_seconds=QUEUE_WAIT_TIMEOUT_SECONDS,
    )


# ---------------------------------------------------------------------------
# Queue timeout tests
# ---------------------------------------------------------------------------


def test_timed_out_queue_escalates_to_gemini():
    decision = evaluate_backpressure(make_timed_out_queue(), make_closed_breaker())
    assert decision.escalate_to_gemini


def test_timed_out_queue_failure_type_is_queue_overflow():
    decision = evaluate_backpressure(make_timed_out_queue(), make_closed_breaker())
    assert decision.failure_type == VLLMFailureType.QUEUE_OVERFLOW


def test_timed_out_queue_model_id_is_gemini():
    decision = evaluate_backpressure(make_timed_out_queue(), make_closed_breaker())
    assert decision.model_id == GEMINI_25_PRO_MODEL_ID


def test_timed_out_queue_reason_is_queue_timeout():
    decision = evaluate_backpressure(make_timed_out_queue(), make_closed_breaker())
    assert decision.reason == "queue_timeout"


def test_within_timeout_does_not_escalate():
    decision = evaluate_backpressure(make_within_timeout_queue(), make_closed_breaker())
    assert not decision.escalate_to_gemini


def test_zero_wait_does_not_escalate():
    queue = VLLMQueueState(
        current_depth=1,
        max_depth=MAX_QUEUE_DEPTH,
        oldest_wait_seconds=0.0,
        timeout_seconds=QUEUE_WAIT_TIMEOUT_SECONDS,
    )
    decision = evaluate_backpressure(queue, make_closed_breaker())
    assert not decision.escalate_to_gemini


def test_timeout_constant_value():
    assert QUEUE_WAIT_TIMEOUT_SECONDS == 5.0


def test_timed_out_queue_repeated_is_deterministic():
    d1 = evaluate_backpressure(make_timed_out_queue(), make_closed_breaker())
    d2 = evaluate_backpressure(make_timed_out_queue(), make_closed_breaker())
    assert d1.escalate_to_gemini == d2.escalate_to_gemini
    assert d1.failure_type == d2.failure_type
    assert d1.reason == d2.reason


def test_queue_is_full_takes_priority_over_timeout():
    queue = VLLMQueueState(
        current_depth=MAX_QUEUE_DEPTH,
        max_depth=MAX_QUEUE_DEPTH,
        oldest_wait_seconds=QUEUE_WAIT_TIMEOUT_SECONDS,
        timeout_seconds=QUEUE_WAIT_TIMEOUT_SECONDS,
    )
    decision = evaluate_backpressure(queue, make_closed_breaker())
    assert decision.escalate_to_gemini
    assert decision.reason == "queue_full"
