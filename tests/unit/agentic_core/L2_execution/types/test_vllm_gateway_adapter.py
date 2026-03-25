"""
PHASE 3.1 WAVE 1 tests — VLLMGatewayAdapter seam unit tests.

Tests the adapter directly without importing SovereignLLMGateway.
Proves the seam is reachable and correct under unit_min_deps.

Validates:
- Adapter routes to Gemini on token budget exceed
- Adapter routes locally on clean path
- Adapter routes to Gemini on queue full
- Adapter routes to Gemini on breaker open
- record_local_failure increments breaker
- record_local_success resets breaker
- emit_seam_proof returns expected marker
- SEAM_PROOF_MARKER is present and correct
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_vllm_gateway_adapter")
# REMOVED: _emit_applies_guardrail("p0", "test_vllm_gateway_adapter", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_vllm_gateway_adapter", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_vllm_gateway_adapter", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_vllm_gateway_adapter")
# REMOVED: emit_determinism_digest("p0", "test_vllm_gateway_adapter")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_vllm_gateway_adapter", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_vllm_gateway_adapter", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_vllm_gateway_adapter", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_vllm_gateway_adapter", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_vllm_gateway_adapter", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_vllm_gateway_adapter", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_vllm_gateway_adapter", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_vllm_gateway_adapter", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_vllm_gateway_adapter", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_vllm_gateway_adapter", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_vllm_gateway_adapter", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_vllm_gateway_adapter", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_vllm_gateway_adapter", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_vllm_gateway_adapter", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_vllm_gateway_adapter", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_vllm_gateway_adapter", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_vllm_gateway_adapter", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_vllm_gateway_adapter", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_vllm_gateway_adapter", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_vllm_gateway_adapter", "exec_snapshot_link")

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
)
from agentic_core.L2_execution.types.vllm_gateway_adapter_types import (
    SEAM_PROOF_MARKER,
    VLLMGatewayAdapter,
    emit_seam_proof,
    reset_singletons,
)
from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
    VLLMCircuitBreakerRegistry,
    VLLMQueueController,
)
from agentic_core.L2_execution.types.vllm_serving_profile_types import (
    LOCAL_FAST_7B_MAX_MODEL_LEN,
)
from agentic_core.L2_execution.types.vllm_token_budget_types import (
    GEMINI_25_PRO_MODEL_ID,
    SAFETY_MARGIN_TOKENS,
    TASK_CLASS_OUTPUT_CAPS,
    TaskClass,
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

# REMOVED: _emit_emits_metric_event("test_vllm_gateway_adapter", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_vllm_gateway_adapter", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_vllm_gateway_adapter", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_vllm_gateway_adapter", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_vllm_gateway_adapter", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_vllm_gateway_adapter", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_vllm_gateway_adapter", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_vllm_gateway_adapter", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_vllm_gateway_adapter", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_vllm_gateway_adapter", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_vllm_gateway_adapter", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_vllm_gateway_adapter", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_vllm_gateway_adapter", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_vllm_gateway_adapter", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_vllm_gateway_adapter", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_vllm_gateway_adapter", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_vllm_gateway_adapter", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_vllm_gateway_adapter", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_vllm_gateway_adapter", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_vllm_gateway_adapter", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_vllm_gateway_adapter", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_vllm_gateway_adapter", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_vllm_gateway_adapter", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_vllm_gateway_adapter", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_vllm_gateway_adapter", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_vllm_gateway_adapter", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_vllm_gateway_adapter", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_vllm_gateway_adapter", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_vllm_gateway_adapter", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_vllm_gateway_adapter", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_vllm_gateway_adapter", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_vllm_gateway_adapter", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_vllm_gateway_adapter", "write_through")
# REMOVED: _emit_writes_through("p1", "test_vllm_gateway_adapter", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_vllm_gateway_adapter", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_vllm_gateway_adapter", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_vllm_gateway_adapter", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_vllm_gateway_adapter", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_vllm_gateway_adapter", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_vllm_gateway_adapter", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_vllm_gateway_adapter", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_vllm_gateway_adapter", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_vllm_gateway_adapter", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_vllm_gateway_adapter", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_vllm_gateway_adapter", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_vllm_gateway_adapter", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_vllm_gateway_adapter", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_vllm_gateway_adapter", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_vllm_gateway_adapter")
# REMOVED: _emit_gated_by_confidence("p1", "test_vllm_gateway_adapter", "confidence_gate")

SHORT_PROMPT = "x" * 30
TASK = TaskClass.PATCH_SUGGESTION.value

_CAP = TASK_CLASS_OUTPUT_CAPS[TASK]
_AVAILABLE = LOCAL_FAST_7B_MAX_MODEL_LEN - SAFETY_MARGIN_TOKENS - _CAP
OVER_BUDGET_PROMPT = "a" * ((_AVAILABLE + 10) * 3)


def fresh_adapter() -> VLLMGatewayAdapter:
    return VLLMGatewayAdapter(
        queue=VLLMQueueController(),
        registry=VLLMCircuitBreakerRegistry(),
    )


# ---------------------------------------------------------------------------
# Seam proof
# ---------------------------------------------------------------------------


def test_seam_proof_marker_present():
    assert "SovereignLLMGateway" in SEAM_PROOF_MARKER
    assert "evaluate_gateway_call" in SEAM_PROOF_MARKER


def test_emit_seam_proof_returns_marker():
    assert emit_seam_proof() == SEAM_PROOF_MARKER


# ---------------------------------------------------------------------------
# Local success path
# ---------------------------------------------------------------------------


def test_adapter_local_success_no_gemini():
    adapter = fresh_adapter()
    result = adapter.evaluate(SHORT_PROMPT, TASK, "low")
    assert not result.route_to_gemini
    assert result.local_request is not None


def test_adapter_local_success_explicit_max_tokens():
    adapter = fresh_adapter()
    result = adapter.evaluate(SHORT_PROMPT, TASK, "low")
    assert result.local_request is not None
    assert result.local_request.max_tokens == _CAP


def test_adapter_local_success_profile_max_model_len():
    adapter = fresh_adapter()
    result = adapter.evaluate(SHORT_PROMPT, TASK, "low")
    assert result.local_request is not None
    assert result.local_request.max_model_len == LOCAL_FAST_7B_MAX_MODEL_LEN


def test_adapter_local_success_telemetry_failure_type_none():
    adapter = fresh_adapter()
    result = adapter.evaluate(SHORT_PROMPT, TASK, "low")
    assert result.telemetry.failure_type is None


# ---------------------------------------------------------------------------
# Token budget exceed → Gemini
# ---------------------------------------------------------------------------


def test_adapter_token_budget_exceed_routes_gemini():
    adapter = fresh_adapter()
    result = adapter.evaluate(OVER_BUDGET_PROMPT, TASK, "low")
    assert result.route_to_gemini
    assert result.local_request is None


def test_adapter_token_budget_exceed_failure_type():
    adapter = fresh_adapter()
    result = adapter.evaluate(OVER_BUDGET_PROMPT, TASK, "low")
    assert result.telemetry.failure_type == VLLMFailureType.TOKEN_BUDGET_EXCEEDED.value


def test_adapter_token_budget_exceed_provider_gemini():
    adapter = fresh_adapter()
    result = adapter.evaluate(OVER_BUDGET_PROMPT, TASK, "low")
    assert result.telemetry.provider_selected == GEMINI_25_PRO_MODEL_ID


# ---------------------------------------------------------------------------
# Queue full → Gemini
# ---------------------------------------------------------------------------


def test_adapter_queue_full_routes_gemini():
    q = VLLMQueueController()
    for _ in range(MAX_QUEUE_DEPTH):
        q.acquire()
    adapter = VLLMGatewayAdapter(queue=q, registry=VLLMCircuitBreakerRegistry())
    result = adapter.evaluate(SHORT_PROMPT, TASK, "low")
    assert result.route_to_gemini
    assert result.telemetry.failure_type == VLLMFailureType.QUEUE_OVERFLOW.value


# ---------------------------------------------------------------------------
# Breaker open → Gemini
# ---------------------------------------------------------------------------


def test_adapter_breaker_open_routes_gemini():
    adapter = fresh_adapter()
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        adapter.record_local_failure("low")
    result = adapter.evaluate(SHORT_PROMPT, TASK, "low")
    assert result.route_to_gemini
    assert result.telemetry.failure_type == VLLMFailureType.CIRCUIT_BREAKER_OPEN.value


def test_adapter_record_local_failure_increments_breaker():
    adapter = fresh_adapter()
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        adapter.record_local_failure("low")
    assert adapter.registry.is_open("local_fast")


def test_adapter_record_local_success_resets_breaker():
    adapter = fresh_adapter()
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        adapter.record_local_failure("low")
    adapter.record_local_success("low")
    assert not adapter.registry.is_open("local_fast")


# ---------------------------------------------------------------------------
# reset_singletons (module-level state)
# ---------------------------------------------------------------------------


def test_reset_singletons_clears_state():
    reset_singletons()
    # After reset, a fresh adapter using defaults should work cleanly
    from agentic_core.L2_execution.types.vllm_gateway_adapter_types import (
        _get_default_queue,
        _get_default_registry,
    )

    q = _get_default_queue()
    r = _get_default_registry()
    assert q.depth == 0
    assert not r.is_open("local_fast")
    reset_singletons()
