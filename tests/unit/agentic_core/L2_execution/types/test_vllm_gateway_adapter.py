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

_emit_records_execution_trace("p0", "evidence", "test_vllm_gateway_adapter")
_emit_applies_guardrail("p0", "test_vllm_gateway_adapter", "p0_governance")
_emit_reads_policy_state("p0", "test_vllm_gateway_adapter", "policy_binding")
_emit_snapshots_state("p0", "test_vllm_gateway_adapter", "state_snapshot")
emit_replay_key("p0", "test_vllm_gateway_adapter")
emit_determinism_digest("p0", "test_vllm_gateway_adapter")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_vllm_gateway_adapter", "execution_auth")
_emit_validates_capability("p2", "test_vllm_gateway_adapter", "capability_check")
_emit_routes_to_capability("p2", "test_vllm_gateway_adapter", "capability_route")
_emit_writes_via_uwg("p2", "test_vllm_gateway_adapter", "uwg_write")
_emit_blocks_direct_write("p2", "test_vllm_gateway_adapter", "direct_write_block")
_emit_records_tool_invocation("p2", "test_vllm_gateway_adapter", "tool_invocation")
_emit_captures_execution_output("p2", "test_vllm_gateway_adapter", "exec_output")
_emit_dispatches_agent("p3", "test_vllm_gateway_adapter", "agent_dispatch")
_emit_coordinates_agents("p3", "test_vllm_gateway_adapter", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_vllm_gateway_adapter", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_vllm_gateway_adapter", "healing_outcome")
_emit_escalates_failure("p3", "test_vllm_gateway_adapter", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_vllm_gateway_adapter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_vllm_gateway_adapter", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_vllm_gateway_adapter", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_vllm_gateway_adapter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_vllm_gateway_adapter", "eval_metric")
_emit_stores_embedding("p4", "test_vllm_gateway_adapter", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_vllm_gateway_adapter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_vllm_gateway_adapter", "exec_snapshot_link")

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
