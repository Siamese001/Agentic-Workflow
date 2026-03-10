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
