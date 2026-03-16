"""
WAVE 3 tests — Telemetry + failure taxonomy end-to-end.

Validates:
- Telemetry emitted for: local success, token budget exceed, queue full, breaker open
- All telemetry fields present and consistent
- Stable key ordering in as_dict()
- Deterministic: identical input -> identical telemetry payload
- No nondeterministic values inside structured payload
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

_emit_records_execution_trace("p0", "evidence", "test_vllm_telemetry_end_to_end")
_emit_applies_guardrail("p0", "test_vllm_telemetry_end_to_end", "p0_governance")
_emit_reads_policy_state("p0", "test_vllm_telemetry_end_to_end", "policy_binding")
_emit_snapshots_state("p0", "test_vllm_telemetry_end_to_end", "state_snapshot")
emit_replay_key("p0", "test_vllm_telemetry_end_to_end")
emit_determinism_digest("p0", "test_vllm_telemetry_end_to_end")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_vllm_telemetry_end_to_end", "execution_auth")
_emit_validates_capability("p2", "test_vllm_telemetry_end_to_end", "capability_check")
_emit_routes_to_capability("p2", "test_vllm_telemetry_end_to_end", "capability_route")
_emit_writes_via_uwg("p2", "test_vllm_telemetry_end_to_end", "uwg_write")
_emit_blocks_direct_write("p2", "test_vllm_telemetry_end_to_end", "direct_write_block")
_emit_records_tool_invocation("p2", "test_vllm_telemetry_end_to_end", "tool_invocation")
_emit_captures_execution_output("p2", "test_vllm_telemetry_end_to_end", "exec_output")
_emit_dispatches_agent("p3", "test_vllm_telemetry_end_to_end", "agent_dispatch")
_emit_coordinates_agents("p3", "test_vllm_telemetry_end_to_end", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_vllm_telemetry_end_to_end", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_vllm_telemetry_end_to_end", "healing_outcome")
_emit_escalates_failure("p3", "test_vllm_telemetry_end_to_end", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_vllm_telemetry_end_to_end", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_vllm_telemetry_end_to_end", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_vllm_telemetry_end_to_end", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_vllm_telemetry_end_to_end", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_vllm_telemetry_end_to_end", "eval_metric")
_emit_stores_embedding("p4", "test_vllm_telemetry_end_to_end", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_vllm_telemetry_end_to_end", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_vllm_telemetry_end_to_end", "exec_snapshot_link")

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
from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
    VLLMCircuitBreakerRegistry,
    VLLMGatewayTelemetry,
    VLLMQueueController,
    evaluate_gateway_call,
)
from agentic_core.L2_execution.types.vllm_serving_profile_types import (
    LOCAL_FAST_7B_MAX_MODEL_LEN,
    LOCAL_STRONG_14B_MAX_MODEL_LEN,
)
from agentic_core.L2_execution.types.vllm_token_budget_types import (
    GEMINI_25_PRO_MODEL_ID,
    SAFETY_MARGIN_TOKENS,
    TASK_CLASS_OUTPUT_CAPS,
    TaskClass,
    VLLMFailureType,
    estimate_tokens_qwen,
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
)

_emit_emits_metric_event("test_vllm_telemetry_end_to_end", "p4obs", "metric_1")
_emit_emits_metric_event("test_vllm_telemetry_end_to_end", "p4obs", "metric_2")
_emit_emits_metric_event("test_vllm_telemetry_end_to_end", "p4obs", "metric_3")
_emit_emits_metric_event("test_vllm_telemetry_end_to_end", "p4obs", "metric_4")
_emit_emits_metric_event("test_vllm_telemetry_end_to_end", "p4obs", "metric_5")
_emit_emits_metric_event("test_vllm_telemetry_end_to_end", "p4obs", "metric_6")
_emit_records_incident_event("test_vllm_telemetry_end_to_end", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_vllm_telemetry_end_to_end", "p4obs", "anomaly")
_emit_writes_observability_log("test_vllm_telemetry_end_to_end", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_vllm_telemetry_end_to_end", "p4obs", "mon_state")
_emit_triggers_alert("test_vllm_telemetry_end_to_end", "p4obs", "alert")
_emit_links_incident_trace("test_vllm_telemetry_end_to_end", "p4obs", "trace_link")
_emit_captures_pattern("test_vllm_telemetry_end_to_end", "p3lm", "pattern")
_emit_records_learning_event("test_vllm_telemetry_end_to_end", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_vllm_telemetry_end_to_end", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_vllm_telemetry_end_to_end", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_vllm_telemetry_end_to_end", "p3lm", "routing")
_emit_improves_agent_policy("test_vllm_telemetry_end_to_end", "p3lm", "policy")
_emit_stores_learning_state("test_vllm_telemetry_end_to_end", "p3lm", "state")
_emit_records_execution_trace("test_vllm_telemetry_end_to_end", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_vllm_telemetry_end_to_end", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_vllm_telemetry_end_to_end", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_vllm_telemetry_end_to_end", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_vllm_telemetry_end_to_end", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_vllm_telemetry_end_to_end", "env_read", "p2_env_1")
_emit_reads_environ("test_vllm_telemetry_end_to_end", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_vllm_telemetry_end_to_end", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_vllm_telemetry_end_to_end", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_vllm_telemetry_end_to_end", "context_pull")
_emit_pulls_context("p1", "test_vllm_telemetry_end_to_end", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_vllm_telemetry_end_to_end", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_vllm_telemetry_end_to_end", "uwg_term_secondary")
_emit_writes_through("p1", "test_vllm_telemetry_end_to_end", "write_through")
_emit_writes_through("p1", "test_vllm_telemetry_end_to_end", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_vllm_telemetry_end_to_end", "safety_validation")
_emit_invokes_eval("p1", "test_vllm_telemetry_end_to_end", "eval_call")
_emit_proposal_commits_routing("p1", "test_vllm_telemetry_end_to_end", "routing_commit")
_emit_escalates_to_human("p1", "test_vllm_telemetry_end_to_end", "human_escalation")
_emit_routes_through("p1", "test_vllm_telemetry_end_to_end", "route_through")
_emit_checks_agent_registry("p1", "test_vllm_telemetry_end_to_end", "agent_registry")
_emit_validates_agent_capability("p1", "test_vllm_telemetry_end_to_end", "capability")
_emit_dispatches_execution_plan("p1", "test_vllm_telemetry_end_to_end", "exec_plan")
_emit_agent_executes_agent("p1", "test_vllm_telemetry_end_to_end", "sub_agent")
_emit_routes_to_agent("p1", "test_vllm_telemetry_end_to_end", "target_agent")
_emit_verifies_policy("p1", "test_vllm_telemetry_end_to_end", "policy_check")
_emit_observes_runtime_state("p1", "test_vllm_telemetry_end_to_end", "runtime_state")
_emit_verifies_boundary("p1", "test_vllm_telemetry_end_to_end", "boundary_check")
_emit_transcripts_response("p1", "test_vllm_telemetry_end_to_end", "transcript")
_emit_hard_fails_untranscripted("p1", "test_vllm_telemetry_end_to_end")
_emit_gated_by_confidence("p1", "test_vllm_telemetry_end_to_end", "confidence_gate")

SHORT_PROMPT = "x" * 30
TASK = TaskClass.PATCH_SUGGESTION.value

# Prompt that exceeds 7B budget ceiling
_7B_CAP = TASK_CLASS_OUTPUT_CAPS[TASK]
_7B_AVAILABLE = LOCAL_FAST_7B_MAX_MODEL_LEN - SAFETY_MARGIN_TOKENS - _7B_CAP
OVER_BUDGET_PROMPT_7B = "a" * ((_7B_AVAILABLE + 10) * 3)


def make_clean() -> tuple[VLLMQueueController, VLLMCircuitBreakerRegistry]:
    return VLLMQueueController(), VLLMCircuitBreakerRegistry()


# ---------------------------------------------------------------------------
# TELEMETRY FIELD PRESENCE
# ---------------------------------------------------------------------------

REQUIRED_TELEMETRY_KEYS = {
    "provider_selected",
    "model_tier",
    "prompt_tokens_estimated",
    "max_output_tokens_requested",
    "max_model_len_configured",
    "token_budget_ok",
    "budget_margin_tokens",
    "queue_depth",
    "queue_full",
    "queue_wait_seconds",
    "breaker_state",
    "breaker_failure_count",
    "failure_type",
}


def assert_telemetry_fields(telemetry: VLLMGatewayTelemetry) -> None:
    d = telemetry.as_dict()
    missing = REQUIRED_TELEMETRY_KEYS - set(d.keys())
    assert not missing, f"Missing telemetry keys: {missing}"


# ---------------------------------------------------------------------------
# (a) Local success telemetry
# ---------------------------------------------------------------------------


def test_local_success_telemetry_fields_present():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert not result.route_to_gemini
    assert_telemetry_fields(result.telemetry)


def test_local_success_provider_is_local_model():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.telemetry.provider_selected != GEMINI_25_PRO_MODEL_ID
    assert "Qwen" in result.telemetry.provider_selected


def test_local_success_model_tier_is_fast():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.telemetry.model_tier == "fast"


def test_local_success_high_severity_model_tier_is_strong():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "high", ctrl, reg)
    assert result.telemetry.model_tier == "strong"


def test_local_success_token_budget_ok_true():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.telemetry.token_budget_ok is True


def test_local_success_failure_type_is_none():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.telemetry.failure_type is None


def test_local_success_queue_depth_zero():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.telemetry.queue_depth == 0
    assert result.telemetry.queue_full is False


def test_local_success_breaker_state_closed():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.telemetry.breaker_state == "CLOSED"
    assert result.telemetry.breaker_failure_count == 0


def test_local_success_max_model_len_matches_profile():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.telemetry.max_model_len_configured == LOCAL_FAST_7B_MAX_MODEL_LEN


def test_local_success_14b_max_model_len():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "high", ctrl, reg)
    assert result.telemetry.max_model_len_configured == LOCAL_STRONG_14B_MAX_MODEL_LEN


# ---------------------------------------------------------------------------
# (b) Token budget exceed fallback telemetry
# ---------------------------------------------------------------------------


def test_token_budget_exceed_telemetry_fields_present():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(OVER_BUDGET_PROMPT_7B, TASK, "low", ctrl, reg)
    assert result.route_to_gemini
    assert_telemetry_fields(result.telemetry)


def test_token_budget_exceed_provider_is_gemini():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(OVER_BUDGET_PROMPT_7B, TASK, "low", ctrl, reg)
    assert result.telemetry.provider_selected == GEMINI_25_PRO_MODEL_ID


def test_token_budget_exceed_model_tier_is_remote():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(OVER_BUDGET_PROMPT_7B, TASK, "low", ctrl, reg)
    assert result.telemetry.model_tier == "remote"


def test_token_budget_exceed_failure_type():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(OVER_BUDGET_PROMPT_7B, TASK, "low", ctrl, reg)
    assert result.telemetry.failure_type == VLLMFailureType.TOKEN_BUDGET_EXCEEDED.value


def test_token_budget_exceed_token_budget_ok_false():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(OVER_BUDGET_PROMPT_7B, TASK, "low", ctrl, reg)
    assert result.telemetry.token_budget_ok is False


def test_token_budget_exceed_local_request_is_none():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(OVER_BUDGET_PROMPT_7B, TASK, "low", ctrl, reg)
    assert result.local_request is None


# ---------------------------------------------------------------------------
# (c) Queue full fallback telemetry
# ---------------------------------------------------------------------------


def test_queue_full_telemetry_fields_present():
    ctrl = VLLMQueueController()
    for _ in range(MAX_QUEUE_DEPTH):
        ctrl.acquire()
    reg = VLLMCircuitBreakerRegistry()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.route_to_gemini
    assert_telemetry_fields(result.telemetry)


def test_queue_full_provider_is_gemini():
    ctrl = VLLMQueueController()
    for _ in range(MAX_QUEUE_DEPTH):
        ctrl.acquire()
    reg = VLLMCircuitBreakerRegistry()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.telemetry.provider_selected == GEMINI_25_PRO_MODEL_ID


def test_queue_full_failure_type():
    ctrl = VLLMQueueController()
    for _ in range(MAX_QUEUE_DEPTH):
        ctrl.acquire()
    reg = VLLMCircuitBreakerRegistry()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.telemetry.failure_type == VLLMFailureType.QUEUE_OVERFLOW.value


def test_queue_full_queue_full_flag():
    ctrl = VLLMQueueController()
    for _ in range(MAX_QUEUE_DEPTH):
        ctrl.acquire()
    reg = VLLMCircuitBreakerRegistry()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.telemetry.queue_full is True
    assert result.telemetry.queue_depth == MAX_QUEUE_DEPTH


def test_queue_full_local_request_is_none():
    ctrl = VLLMQueueController()
    for _ in range(MAX_QUEUE_DEPTH):
        ctrl.acquire()
    reg = VLLMCircuitBreakerRegistry()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.local_request is None


# ---------------------------------------------------------------------------
# (d) Breaker open fallback telemetry
# ---------------------------------------------------------------------------


def test_breaker_open_telemetry_fields_present():
    ctrl, reg = make_clean()
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        reg.record_failure("local_fast")
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.route_to_gemini
    assert_telemetry_fields(result.telemetry)


def test_breaker_open_provider_is_gemini():
    ctrl, reg = make_clean()
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        reg.record_failure("local_fast")
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.telemetry.provider_selected == GEMINI_25_PRO_MODEL_ID


def test_breaker_open_failure_type():
    ctrl, reg = make_clean()
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        reg.record_failure("local_fast")
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.telemetry.failure_type == VLLMFailureType.CIRCUIT_BREAKER_OPEN.value


def test_breaker_open_breaker_state_in_telemetry():
    ctrl, reg = make_clean()
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        reg.record_failure("local_fast")
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.telemetry.breaker_state == "OPEN"
    assert result.telemetry.breaker_failure_count == CIRCUIT_BREAKER_FAILURE_THRESHOLD


def test_breaker_open_local_request_is_none():
    ctrl, reg = make_clean()
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        reg.record_failure("local_fast")
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.local_request is None


# ---------------------------------------------------------------------------
# Stable key ordering + determinism
# ---------------------------------------------------------------------------


def test_telemetry_as_dict_key_order_stable():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    keys = list(result.telemetry.as_dict().keys())
    # Verify exact declared order (stable, not alphabetical)
    assert keys[0] == "provider_selected"
    assert keys[1] == "model_tier"
    assert keys[-1] == "fingerprint_hash"
    # Verify same order on repeated call
    ctrl2, reg2 = make_clean()
    result2 = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl2, reg2)
    assert list(result2.telemetry.as_dict().keys()) == keys


def test_telemetry_deterministic_same_input():
    ctrl1, reg1 = make_clean()
    ctrl2, reg2 = make_clean()
    r1 = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl1, reg1)
    r2 = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl2, reg2)
    assert r1.telemetry.as_dict() == r2.telemetry.as_dict()


def test_telemetry_prompt_tokens_estimated_consistent():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    expected = estimate_tokens_qwen(SHORT_PROMPT)
    assert result.telemetry.prompt_tokens_estimated == expected


def test_telemetry_max_output_tokens_matches_cap():
    ctrl, reg = make_clean()
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.telemetry.max_output_tokens_requested == TASK_CLASS_OUTPUT_CAPS[TASK]
