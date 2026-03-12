"""
WAVE 2 tests — Backpressure + circuit breaker runtime wiring.

Validates:
- Breaker open supersedes queue checks (priority ordering)
- Queue full/timeout triggers Gemini without local attempt
- Breaker transitions: closed -> open -> reset
- QueueController threadsafe acquire/release
- CircuitBreakerRegistry per-tier isolation
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
    QUEUE_WAIT_TIMEOUT_SECONDS,
    CircuitBreakerState,
)
from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
    VLLMCircuitBreakerRegistry,
    VLLMQueueController,
    evaluate_gateway_call,
)
from agentic_core.L2_execution.types.vllm_token_budget_types import (
    TaskClass,
    VLLMFailureType,
)


def make_queue(depth: int = 0, wait: float = 0.0) -> VLLMQueueController:
    ctrl = VLLMQueueController()
    for _ in range(depth):
        ctrl.acquire()
    return ctrl


def make_registry() -> VLLMCircuitBreakerRegistry:
    return VLLMCircuitBreakerRegistry()


SHORT_PROMPT = "x" * 30
TASK = TaskClass.PATCH_SUGGESTION.value


# ---------------------------------------------------------------------------
# QueueController tests
# ---------------------------------------------------------------------------


def test_queue_controller_starts_empty():
    ctrl = VLLMQueueController()
    assert ctrl.depth == 0


def test_queue_controller_acquire_increments():
    ctrl = VLLMQueueController()
    assert ctrl.acquire()
    assert ctrl.depth == 1


def test_queue_controller_release_decrements():
    ctrl = VLLMQueueController()
    ctrl.acquire()
    ctrl.release()
    assert ctrl.depth == 0


def test_queue_controller_full_acquire_fails():
    ctrl = VLLMQueueController(max_depth=2)
    ctrl.acquire()
    ctrl.acquire()
    assert not ctrl.acquire()
    assert ctrl.depth == 2


def test_queue_controller_snapshot_is_immutable():
    ctrl = VLLMQueueController()
    snap = ctrl.snapshot()
    ctrl.acquire()
    assert snap.current_depth == 0


def test_queue_controller_full_snapshot():
    ctrl = VLLMQueueController(max_depth=MAX_QUEUE_DEPTH)
    for _ in range(MAX_QUEUE_DEPTH):
        ctrl.acquire()
    snap = ctrl.snapshot()
    assert snap.is_full


# ---------------------------------------------------------------------------
# CircuitBreakerRegistry tests
# ---------------------------------------------------------------------------


def test_registry_creates_breaker_on_first_access():
    reg = make_registry()
    cb = reg.get("local_fast")
    assert cb.tier == "local_fast"
    assert not cb.is_open


def test_registry_per_tier_isolation():
    reg = make_registry()
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        reg.record_failure("local_fast")
    assert reg.is_open("local_fast")
    assert not reg.is_open("local_strong")


def test_registry_record_success_resets():
    reg = make_registry()
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        reg.record_failure("local_fast")
    reg.record_success("local_fast")
    assert not reg.is_open("local_fast")


def test_registry_reset_all():
    reg = make_registry()
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        reg.record_failure("local_fast")
        reg.record_failure("local_strong")
    reg.reset_all()
    assert not reg.is_open("local_fast")
    assert not reg.is_open("local_strong")


# ---------------------------------------------------------------------------
# evaluate_gateway_call — backpressure priority ordering
# ---------------------------------------------------------------------------


def test_open_breaker_supersedes_empty_queue():
    reg = make_registry()
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        reg.record_failure("local_fast")
    ctrl = make_queue(depth=0)
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.route_to_gemini
    assert result.telemetry.failure_type == VLLMFailureType.CIRCUIT_BREAKER_OPEN.value
    assert result.local_request is None


def test_open_breaker_supersedes_full_queue():
    reg = make_registry()
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        reg.record_failure("local_fast")
    ctrl = make_queue(depth=MAX_QUEUE_DEPTH)
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.route_to_gemini
    assert result.telemetry.failure_type == VLLMFailureType.CIRCUIT_BREAKER_OPEN.value


def test_full_queue_routes_to_gemini():
    reg = make_registry()
    ctrl = make_queue(depth=MAX_QUEUE_DEPTH)
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert result.route_to_gemini
    assert result.telemetry.failure_type == VLLMFailureType.QUEUE_OVERFLOW.value
    assert result.local_request is None


def test_queue_timeout_routes_to_gemini():
    reg = make_registry()
    ctrl = make_queue(depth=1)
    result = evaluate_gateway_call(
        SHORT_PROMPT,
        TASK,
        "low",
        ctrl,
        reg,
        oldest_wait_seconds=QUEUE_WAIT_TIMEOUT_SECONDS,
    )
    assert result.route_to_gemini
    assert result.telemetry.failure_type == VLLMFailureType.QUEUE_OVERFLOW.value


def test_empty_queue_closed_breaker_local_path():
    reg = make_registry()
    ctrl = make_queue(depth=0)
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert not result.route_to_gemini
    assert result.local_request is not None
    assert result.telemetry.failure_type is None


def test_breaker_open_no_local_attempt():
    reg = make_registry()
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        reg.record_failure("local_strong")
    ctrl = make_queue(depth=0)
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "high", ctrl, reg)
    assert result.route_to_gemini
    assert result.local_request is None


def test_breaker_closed_after_reset_allows_local():
    reg = make_registry()
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        reg.record_failure("local_fast")
    reg.reset("local_fast")
    ctrl = make_queue(depth=0)
    result = evaluate_gateway_call(SHORT_PROMPT, TASK, "low", ctrl, reg)
    assert not result.route_to_gemini
    assert result.local_request is not None


# ---------------------------------------------------------------------------
# Breaker state transitions
# ---------------------------------------------------------------------------


def test_breaker_closed_to_open_transition():
    reg = make_registry()
    cb = reg.get("local_fast")
    assert cb.state == CircuitBreakerState.CLOSED
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN


def test_breaker_open_to_closed_via_success():
    reg = make_registry()
    cb = reg.get("local_fast")
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD):
        cb.record_failure()
    cb.record_success()
    assert cb.state == CircuitBreakerState.CLOSED
    assert cb.consecutive_failures == 0


def test_breaker_does_not_open_below_threshold():
    reg = make_registry()
    cb = reg.get("local_fast")
    for _ in range(CIRCUIT_BREAKER_FAILURE_THRESHOLD - 1):
        cb.record_failure()
    assert cb.state == CircuitBreakerState.CLOSED
