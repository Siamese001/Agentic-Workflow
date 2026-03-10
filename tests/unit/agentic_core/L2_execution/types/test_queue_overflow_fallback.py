"""
WAVE 3 tests — Queue overflow fallback to Gemini-2.5-Pro.

Validates:
- Full queue immediately escalates to Gemini-2.5-Pro
- Partial queue does not escalate
- Escalation produces correct failure type and model_id
- Deterministic behavior under repeated overload
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


def make_closed_breaker() -> VLLMCircuitBreaker:
    return VLLMCircuitBreaker(tier="local_fast")


def make_full_queue() -> VLLMQueueState:
    return VLLMQueueState(
        current_depth=MAX_QUEUE_DEPTH,
        max_depth=MAX_QUEUE_DEPTH,
        oldest_wait_seconds=0.0,
        timeout_seconds=QUEUE_WAIT_TIMEOUT_SECONDS,
    )


def make_partial_queue(depth: int = 2) -> VLLMQueueState:
    return VLLMQueueState(
        current_depth=depth,
        max_depth=MAX_QUEUE_DEPTH,
        oldest_wait_seconds=0.0,
        timeout_seconds=QUEUE_WAIT_TIMEOUT_SECONDS,
    )


# ---------------------------------------------------------------------------
# Queue overflow tests
# ---------------------------------------------------------------------------


def test_full_queue_escalates_to_gemini():
    decision = evaluate_backpressure(make_full_queue(), make_closed_breaker())
    assert decision.escalate_to_gemini


def test_full_queue_failure_type_is_queue_overflow():
    decision = evaluate_backpressure(make_full_queue(), make_closed_breaker())
    assert decision.failure_type == VLLMFailureType.QUEUE_OVERFLOW


def test_full_queue_model_id_is_gemini():
    decision = evaluate_backpressure(make_full_queue(), make_closed_breaker())
    assert decision.model_id == GEMINI_25_PRO_MODEL_ID


def test_full_queue_reason_is_queue_full():
    decision = evaluate_backpressure(make_full_queue(), make_closed_breaker())
    assert decision.reason == "queue_full"


def test_partial_queue_does_not_escalate():
    decision = evaluate_backpressure(make_partial_queue(2), make_closed_breaker())
    assert not decision.escalate_to_gemini


def test_empty_queue_does_not_escalate():
    queue = VLLMQueueState(
        current_depth=0,
        max_depth=MAX_QUEUE_DEPTH,
        oldest_wait_seconds=0.0,
        timeout_seconds=QUEUE_WAIT_TIMEOUT_SECONDS,
    )
    decision = evaluate_backpressure(queue, make_closed_breaker())
    assert not decision.escalate_to_gemini


def test_queue_at_max_minus_one_does_not_escalate():
    queue = VLLMQueueState(
        current_depth=MAX_QUEUE_DEPTH - 1,
        max_depth=MAX_QUEUE_DEPTH,
        oldest_wait_seconds=0.0,
        timeout_seconds=QUEUE_WAIT_TIMEOUT_SECONDS,
    )
    decision = evaluate_backpressure(queue, make_closed_breaker())
    assert not decision.escalate_to_gemini


def test_queue_depth_recorded_in_decision():
    decision = evaluate_backpressure(make_full_queue(), make_closed_breaker())
    assert decision.queue_depth == MAX_QUEUE_DEPTH


def test_max_queue_depth_constant():
    assert MAX_QUEUE_DEPTH == 8


def test_full_queue_repeated_is_deterministic():
    d1 = evaluate_backpressure(make_full_queue(), make_closed_breaker())
    d2 = evaluate_backpressure(make_full_queue(), make_closed_breaker())
    assert d1.escalate_to_gemini == d2.escalate_to_gemini
    assert d1.failure_type == d2.failure_type
    assert d1.model_id == d2.model_id
