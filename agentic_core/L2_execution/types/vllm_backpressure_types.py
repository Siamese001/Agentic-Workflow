"""
WAVE 3 — Backpressure + Overload Escalation Enforcement types.

Defines queue policy, circuit breaker state, and overload escalation
invariants for vLLM tiered routing.

No GPU libraries. No torch/vllm imports. L2 purity preserved.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from agentic_core.L2_execution.types.vllm_token_budget_types import (
    GEMINI_25_PRO_MODEL_ID,
    VLLMFailureType,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)

# ---------------------------------------------------------------------------
# WAVE 3.1 — Queue policy constants (deterministic, not env-derived)
# ---------------------------------------------------------------------------

MAX_QUEUE_DEPTH: int = 8
QUEUE_WAIT_TIMEOUT_SECONDS: float = 5.0
CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 3
CIRCUIT_BREAKER_RESET_AFTER_SECONDS: float = 30.0

# ---------------------------------------------------------------------------
# WAVE 3.2 — Queue state dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VLLMQueueState:
    """Immutable snapshot of the vLLM request queue state.

    Used for backpressure decisions. Produced before routing.
    """

    current_depth: int
    max_depth: int
    oldest_wait_seconds: float
    timeout_seconds: float

    @property
    def is_full(self) -> bool:
        return self.current_depth >= self.max_depth

    @property
    def is_timed_out(self) -> bool:
        return self.oldest_wait_seconds >= self.timeout_seconds


# ---------------------------------------------------------------------------
# WAVE 3.3 — Circuit breaker state
# ---------------------------------------------------------------------------


class CircuitBreakerState(str, Enum):
    """Circuit breaker state for local vLLM tier."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


@dataclass
class VLLMCircuitBreaker:
    """Mutable circuit breaker for a single vLLM tier.

    Tracks consecutive failures and opens the circuit when threshold exceeded.
    """

    tier: str
    failure_threshold: int = CIRCUIT_BREAKER_FAILURE_THRESHOLD
    consecutive_failures: int = field(default=0)
    state: CircuitBreakerState = field(default=CircuitBreakerState.CLOSED)

    def record_failure(self) -> None:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "VLLMCircuitBreaker.record_failure")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:VLLMCircuitBreaker.record_failure".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        self.consecutive_failures += 1
        if self.consecutive_failures >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN

    def record_success(self) -> None:
        self.consecutive_failures = 0
        self.state = CircuitBreakerState.CLOSED

    def reset(self) -> None:
        self.consecutive_failures = 0
        self.state = CircuitBreakerState.CLOSED

    @property
    def is_open(self) -> bool:
        return self.state == CircuitBreakerState.OPEN


# ---------------------------------------------------------------------------
# WAVE 3.4 — Backpressure escalation decision
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BackpressureDecision:
    """Immutable backpressure escalation decision.

    Produced when queue or circuit breaker state forces Gemini escalation.
    """

    escalate_to_gemini: bool
    reason: str
    failure_type: VLLMFailureType | None
    model_id: str
    queue_depth: int
    circuit_breaker_open: bool


def evaluate_backpressure(
    queue_state: VLLMQueueState,
    circuit_breaker: VLLMCircuitBreaker,
) -> BackpressureDecision:
    """Evaluate backpressure conditions and produce escalation decision.

    Invariants (in priority order):
        1. Circuit breaker open → Gemini-2.5-Pro immediately
        2. Queue full → Gemini-2.5-Pro immediately
        3. Queue wait timed out → Gemini-2.5-Pro immediately
        4. Otherwise → proceed to local tier

    Gemini-2.5-Pro is always reachable as escalation path.

    Args:
        queue_state: Current queue snapshot.
        circuit_breaker: Current circuit breaker state.

    Returns:
        BackpressureDecision with escalation flag and reason.
    """
    if circuit_breaker.is_open:
        return BackpressureDecision(
            escalate_to_gemini=True,
            reason="circuit_breaker_open",
            failure_type=VLLMFailureType.CIRCUIT_BREAKER_OPEN,
            model_id=GEMINI_25_PRO_MODEL_ID,
            queue_depth=queue_state.current_depth,
            circuit_breaker_open=True,
        )

    if queue_state.is_full:
        return BackpressureDecision(
            escalate_to_gemini=True,
            reason="queue_full",
            failure_type=VLLMFailureType.QUEUE_OVERFLOW,
            model_id=GEMINI_25_PRO_MODEL_ID,
            queue_depth=queue_state.current_depth,
            circuit_breaker_open=False,
        )

    if queue_state.is_timed_out:
        return BackpressureDecision(
            escalate_to_gemini=True,
            reason="queue_timeout",
            failure_type=VLLMFailureType.QUEUE_OVERFLOW,
            model_id=GEMINI_25_PRO_MODEL_ID,
            queue_depth=queue_state.current_depth,
            circuit_breaker_open=False,
        )

    return BackpressureDecision(
        escalate_to_gemini=False,
        reason="ok",
        failure_type=None,
        model_id="",
        queue_depth=queue_state.current_depth,
        circuit_breaker_open=False,
    )


__all__ = [
    "CIRCUIT_BREAKER_FAILURE_THRESHOLD",
    "CIRCUIT_BREAKER_RESET_AFTER_SECONDS",
    "MAX_QUEUE_DEPTH",
    "QUEUE_WAIT_TIMEOUT_SECONDS",
    "BackpressureDecision",
    "CircuitBreakerState",
    "VLLMCircuitBreaker",
    "VLLMQueueState",
    "evaluate_backpressure",
]
