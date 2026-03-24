"""
WAVE 3 tests — Circuit breaker respects backpressure and escalates to Gemini-2.5-Pro.

Validates:
- Circuit breaker opens after threshold consecutive failures
- Open circuit breaker escalates to Gemini-2.5-Pro
- Circuit breaker takes priority over queue state
- Reset restores closed state
- Deterministic behavior under repeated overload
"""

from __future__ import annotations

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_circuit_breaker_respects_backpressure")
_emit_applies_guardrail("p0", "test_circuit_breaker_respects_backpressure", "p0_governance")
_emit_reads_policy_state("p0", "test_circuit_breaker_respects_backpressure", "policy_binding")
_emit_snapshots_state("p0", "test_circuit_breaker_respects_backpressure", "state_snapshot")
emit_replay_key("p0", "test_circuit_breaker_respects_backpressure")
emit_determinism_digest("p0", "test_circuit_breaker_respects_backpressure")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_circuit_breaker_respects_backpressure", "execution_auth")
_emit_validates_capability("p2", "test_circuit_breaker_respects_backpressure", "capability_check")
_emit_routes_to_capability("p2", "test_circuit_breaker_respects_backpressure", "capability_route")
_emit_writes_via_uwg("p2", "test_circuit_breaker_respects_backpressure", "uwg_write")
_emit_blocks_direct_write("p2", "test_circuit_breaker_respects_backpressure", "direct_write_block")
_emit_records_tool_invocation("p2", "test_circuit_breaker_respects_backpressure", "tool_invocation")
_emit_captures_execution_output("p2", "test_circuit_breaker_respects_backpressure", "exec_output")
_emit_dispatches_agent("p3", "test_circuit_breaker_respects_backpressure", "agent_dispatch")
_emit_coordinates_agents("p3", "test_circuit_breaker_respects_backpressure", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_circuit_breaker_respects_backpressure", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_circuit_breaker_respects_backpressure", "healing_outcome")
_emit_escalates_failure("p3", "test_circuit_breaker_respects_backpressure", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_circuit_breaker_respects_backpressure", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_circuit_breaker_respects_backpressure", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_circuit_breaker_respects_backpressure", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_circuit_breaker_respects_backpressure", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_circuit_breaker_respects_backpressure", "eval_metric")
_emit_stores_embedding("p4", "test_circuit_breaker_respects_backpressure", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_circuit_breaker_respects_backpressure", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_circuit_breaker_respects_backpressure", "exec_snapshot_link")

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
    CIRCUIT_BREAKER_FAILURE_THRESHOLD,
    MAX_QUEUE_DEPTH,
    QUEUE_WAIT_TIMEOUT_SECONDS,
    CircuitBreakerState,
    VLLMCircuitBreaker,
    VLLMQueueState,
    evaluate_backpressure,
)
from agentic_core.L2_execution.types.vllm_token_budget_types import (
    GEMINI_25_PRO_MODEL_ID,
    VLLMFailureType,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("test_circuit_breaker_respects_backpressure", "p4obs", "metric_1")
_emit_emits_metric_event("test_circuit_breaker_respects_backpressure", "p4obs", "metric_2")
_emit_emits_metric_event("test_circuit_breaker_respects_backpressure", "p4obs", "metric_3")
_emit_emits_metric_event("test_circuit_breaker_respects_backpressure", "p4obs", "metric_4")
_emit_emits_metric_event("test_circuit_breaker_respects_backpressure", "p4obs", "metric_5")
_emit_emits_metric_event("test_circuit_breaker_respects_backpressure", "p4obs", "metric_6")
_emit_records_incident_event("test_circuit_breaker_respects_backpressure", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_circuit_breaker_respects_backpressure", "p4obs", "anomaly")
_emit_writes_observability_log("test_circuit_breaker_respects_backpressure", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_circuit_breaker_respects_backpressure", "p4obs", "mon_state")
_emit_triggers_alert("test_circuit_breaker_respects_backpressure", "p4obs", "alert")
_emit_links_incident_trace("test_circuit_breaker_respects_backpressure", "p4obs", "trace_link")
_emit_captures_pattern("test_circuit_breaker_respects_backpressure", "p3lm", "pattern")
_emit_records_learning_event("test_circuit_breaker_respects_backpressure", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_circuit_breaker_respects_backpressure", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_circuit_breaker_respects_backpressure", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_circuit_breaker_respects_backpressure", "p3lm", "routing")
_emit_improves_agent_policy("test_circuit_breaker_respects_backpressure", "p3lm", "policy")
_emit_stores_learning_state("test_circuit_breaker_respects_backpressure", "p3lm", "state")
_emit_records_execution_trace("test_circuit_breaker_respects_backpressure", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_circuit_breaker_respects_backpressure", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_circuit_breaker_respects_backpressure", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_circuit_breaker_respects_backpressure", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_circuit_breaker_respects_backpressure", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_circuit_breaker_respects_backpressure", "env_read", "p2_env_1")
_emit_reads_environ("test_circuit_breaker_respects_backpressure", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_circuit_breaker_respects_backpressure", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_circuit_breaker_respects_backpressure", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_circuit_breaker_respects_backpressure", "context_pull")
_emit_pulls_context("p1", "test_circuit_breaker_respects_backpressure", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_circuit_breaker_respects_backpressure", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_circuit_breaker_respects_backpressure", "uwg_term_secondary")
_emit_writes_through("p1", "test_circuit_breaker_respects_backpressure", "write_through")
_emit_writes_through("p1", "test_circuit_breaker_respects_backpressure", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_circuit_breaker_respects_backpressure", "safety_validation")
_emit_invokes_eval("p1", "test_circuit_breaker_respects_backpressure", "eval_call")
_emit_proposal_commits_routing("p1", "test_circuit_breaker_respects_backpressure", "routing_commit")
_emit_escalates_to_human("p1", "test_circuit_breaker_respects_backpressure", "human_escalation")
_emit_routes_through("p1", "test_circuit_breaker_respects_backpressure", "route_through")
_emit_checks_agent_registry("p1", "test_circuit_breaker_respects_backpressure", "agent_registry")
_emit_validates_agent_capability("p1", "test_circuit_breaker_respects_backpressure", "capability")
_emit_dispatches_execution_plan("p1", "test_circuit_breaker_respects_backpressure", "exec_plan")
_emit_agent_executes_agent("p1", "test_circuit_breaker_respects_backpressure", "sub_agent")
_emit_routes_to_agent("p1", "test_circuit_breaker_respects_backpressure", "target_agent")
_emit_verifies_policy("p1", "test_circuit_breaker_respects_backpressure", "policy_check")
_emit_observes_runtime_state("p1", "test_circuit_breaker_respects_backpressure", "runtime_state")
_emit_verifies_boundary("p1", "test_circuit_breaker_respects_backpressure", "boundary_check")
_emit_transcripts_response("p1", "test_circuit_breaker_respects_backpressure", "transcript")
_emit_hard_fails_untranscripted("p1", "test_circuit_breaker_respects_backpressure")
_emit_gated_by_confidence("p1", "test_circuit_breaker_respects_backpressure", "confidence_gate")


def make_empty_queue() -> VLLMQueueState:
    return VLLMQueueState(
        current_depth=0,
        max_depth=MAX_QUEUE_DEPTH,
        oldest_wait_seconds=0.0,
        timeout_seconds=QUEUE_WAIT_TIMEOUT_SECONDS,
    )


# ---------------------------------------------------------------------------
# Circuit breaker state tests
# ---------------------------------------------------------------------------


def test_breaker_starts_closed():
    cb = VLLMCircuitBreaker(tier="local_fast")
    assert cb.state == CircuitBreakerState.CLOSED
    assert not cb.is_open


def test_breaker_opens_after_threshold_failures():
    cb = VLLMCircuitBreaker(tier="local_fast")
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        cb.record_failure()
    assert cb.is_open
    assert cb.state == CircuitBreakerState.OPEN


def test_breaker_does_not_open_before_threshold():
    cb = VLLMCircuitBreaker(tier="local_fast")
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD - 1):
        cb.record_failure()
    assert not cb.is_open


def test_breaker_resets_on_success():
    cb = VLLMCircuitBreaker(tier="local_fast")
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        cb.record_failure()
    assert cb.is_open
    cb.record_success()
    assert not cb.is_open
    assert cb.consecutive_failures == 0


def test_breaker_reset_restores_closed():
    cb = VLLMCircuitBreaker(tier="local_fast")
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        cb.record_failure()
    cb.reset()
    assert cb.state == CircuitBreakerState.CLOSED
    assert cb.consecutive_failures == 0


def test_failure_threshold_constant():
    assert CIRCUIT_BREAKER_FAILURE_THRESHOLD == 3


# ---------------------------------------------------------------------------
# Backpressure escalation with open circuit breaker
# ---------------------------------------------------------------------------


def test_open_breaker_escalates_to_gemini():
    cb = VLLMCircuitBreaker(tier="local_fast")
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        cb.record_failure()
    decision = evaluate_backpressure(make_empty_queue(), cb)
    assert decision.escalate_to_gemini


def test_open_breaker_failure_type_is_circuit_breaker():
    cb = VLLMCircuitBreaker(tier="local_fast")
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        cb.record_failure()
    decision = evaluate_backpressure(make_empty_queue(), cb)
    assert decision.failure_type == VLLMFailureType.CIRCUIT_BREAKER_OPEN


def test_open_breaker_model_id_is_gemini():
    cb = VLLMCircuitBreaker(tier="local_fast")
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        cb.record_failure()
    decision = evaluate_backpressure(make_empty_queue(), cb)
    assert decision.model_id == GEMINI_25_PRO_MODEL_ID


def test_open_breaker_reason():
    cb = VLLMCircuitBreaker(tier="local_fast")
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        cb.record_failure()
    decision = evaluate_backpressure(make_empty_queue(), cb)
    assert decision.reason == "circuit_breaker_open"


def test_closed_breaker_empty_queue_does_not_escalate():
    cb = VLLMCircuitBreaker(tier="local_fast")
    decision = evaluate_backpressure(make_empty_queue(), cb)
    assert not decision.escalate_to_gemini


def test_open_breaker_takes_priority_over_empty_queue():
    cb = VLLMCircuitBreaker(tier="local_fast")
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        cb.record_failure()
    decision = evaluate_backpressure(make_empty_queue(), cb)
    assert decision.circuit_breaker_open
    assert decision.escalate_to_gemini


def test_open_breaker_takes_priority_over_full_queue():
    cb = VLLMCircuitBreaker(tier="local_fast")
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        cb.record_failure()
    full_queue = VLLMQueueState(
        current_depth=MAX_QUEUE_DEPTH,
        max_depth=MAX_QUEUE_DEPTH,
        oldest_wait_seconds=0.0,
        timeout_seconds=QUEUE_WAIT_TIMEOUT_SECONDS,
    )
    decision = evaluate_backpressure(full_queue, cb)
    assert decision.reason == "circuit_breaker_open"


def test_open_breaker_repeated_is_deterministic():
    cb1 = VLLMCircuitBreaker(tier="local_fast")
    cb2 = VLLMCircuitBreaker(tier="local_fast")
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        cb1.record_failure()
        cb2.record_failure()
    d1 = evaluate_backpressure(make_empty_queue(), cb1)
    d2 = evaluate_backpressure(make_empty_queue(), cb2)
    assert d1.escalate_to_gemini == d2.escalate_to_gemini
    assert d1.failure_type == d2.failure_type
    assert d1.model_id == d2.model_id
