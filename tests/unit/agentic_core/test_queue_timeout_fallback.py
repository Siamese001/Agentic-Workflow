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
