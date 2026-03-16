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

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
