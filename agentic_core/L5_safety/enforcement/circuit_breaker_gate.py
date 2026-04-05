"""
Circuit Breaker - V10 Compliant Implementation (FIXED).

Updates:
- Removed ThreadPoolExecutor Context Manager (caused hangs on timeout).
- Implemented non-blocking 'threading.Thread' logic for Execution Timeouts.
- Ensures main thread returns immediately upon timeout, even if worker hangs.

References:
- V10 Diagram: "Fix Rejected with Exponential Backoff + Escalation + Circuit Breaker"
- Human Review Gate: "Retry up to N → escalate"
"""

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
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

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
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
    _emit_writes_through,
)

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states per V10 specification."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""

    failure_threshold: int = 5
    success_threshold: int = 2
    reset_timeout_seconds: float = 60.0
    max_reset_timeout_seconds: float = 600.0
    backoff_multiplier: float = 2.0
    half_open_max_calls: int = 3
    execution_timeout_seconds: float = 30.0


@dataclass
class CircuitBreakerMetrics:
    """Metrics for observability dashboard."""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    timed_out_calls: int = 0
    state_transitions: int = 0
    last_failure_time: float | None = None
    last_success_time: float | None = None
    current_backoff: float = 0.0


class CircuitBreakerOpenError(Exception):
    """Raised when circuit is open and rejecting calls."""

    def __init__(self, breaker_name: str, time_until_retry: float):
        self.breaker_name = breaker_name
        self.time_until_retry = time_until_retry
        super().__init__(
            f"Circuit breaker '{breaker_name}' is OPEN. Retry in {time_until_retry:.1f} seconds."
        )


class CircuitBreakerTimeoutError(Exception):
    """Raised when execution exceeds the configured timeout."""

    def __init__(self, breaker_name: str, timeout: float):
        self.breaker_name = breaker_name
        self.timeout = timeout
        super().__init__(f"Circuit breaker '{breaker_name}' execution timed out after {timeout}s")


_breaker_lock = threading.Lock()
_breakers: dict[str, "CircuitBreaker"] = {}


class CircuitBreaker:
    """V10-Compliant Circuit Breaker with Non-Blocking Execution Timeout."""

    def __init__(self, name: str, config: CircuitBreakerConfig | None = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float | None = None
        self._current_reset_timeout = self.config.reset_timeout_seconds
        self._half_open_calls = 0
        self._state_lock = threading.RLock()
        self.metrics = CircuitBreakerMetrics()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        with self._state_lock:
            return self._state

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self.state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (rejecting calls)."""
        return self.state == CircuitState.OPEN

    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing recovery)."""
        return self.state == CircuitState.HALF_OPEN

    def allow_request(self) -> bool:
        """
        Check if a request should be allowed through.

        Returns:
            True if request is allowed, False if circuit is open

        Raises:
            CircuitBreakerOpenError if circuit is open (optional, for detailed info)
        """
        with self._state_lock:
            self.metrics.total_calls += 1
            if self._state == CircuitState.CLOSED:
                return True
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                    return True
                else:
                    self.metrics.rejected_calls += 1
                    return False
            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls < self.config.half_open_max_calls:
                    self._half_open_calls += 1
                    return True
                else:
                    self.metrics.rejected_calls += 1
                    return False
            return False

    def record_success(self) -> None:
        """Record a successful call."""
        with self._state_lock:
            self.metrics.successful_calls += 1
            self.metrics.last_success_time = time.time()
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    self._transition_to_closed()
            elif self._state == CircuitState.CLOSED:
                self._failure_count = 0

    def record_failure(self, error: Exception | None = None) -> None:
        """Record a failed call."""
        with self._state_lock:
            self.metrics.failed_calls += 1
            self.metrics.last_failure_time = time.time()
            self._last_failure_time = time.time()
            if isinstance(error, CircuitBreakerTimeoutError):
                self.metrics.timed_out_calls += 1
            if self._state == CircuitState.HALF_OPEN:
                self._apply_exponential_backoff()
                self._transition_to_open()
            elif self._state == CircuitState.CLOSED:
                self._failure_count += 1
                if self._failure_count >= self.config.failure_threshold:
                    self._transition_to_open()
            logger.warning(f"Circuit breaker '{self.name}' failure: {error}")

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self._last_failure_time is None:
            return True
        return time.time() - self._last_failure_time >= self._current_reset_timeout

    def _apply_exponential_backoff(self) -> None:
        """Increase timeout exponentially."""
        self._current_reset_timeout = min(
            self._current_reset_timeout * self.config.backoff_multiplier,
            self.config.max_reset_timeout_seconds,
        )
        self.metrics.current_backoff = self._current_reset_timeout

    def _transition_to_open(self) -> None:
        """Transition to OPEN state."""
        self._state = CircuitState.OPEN
        self._success_count = 0
        self._half_open_calls = 0
        self.metrics.state_transitions += 1
        self._emit_state_transition_event("OPEN")

    def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state."""
        self._state = CircuitState.HALF_OPEN
        self._success_count = 0
        self._half_open_calls = 0
        self.metrics.state_transitions += 1
        self._emit_state_transition_event("HALF_OPEN")

    def _transition_to_closed(self) -> None:
        """Transition to CLOSED state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._half_open_calls = 0
        self._current_reset_timeout = self.config.reset_timeout_seconds
        self.metrics.current_backoff = 0.0
        self.metrics.state_transitions += 1
        self._emit_state_transition_event("CLOSED")

    def _emit_state_transition_event(self, new_state: str) -> None:
        """Emit circuit breaker state transition to system learning."""
        try:
            from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge
            bridge = get_sl_memory_bridge()
            bridge.persist_circuit_breaker_event(
                breaker_name=self.name,
                old_state="UNKNOWN",  # Could track previous state if needed
                new_state=new_state,
                timestamp_utc=int(time.time() * 1000),
                failure_count=self._failure_count,
                success_count=self._success_count,
                current_backoff=self._current_reset_timeout,
            )
        except (ValueError, TypeError):
            # System learning unavailable - continue without emission
            pass

    def get_time_until_retry(self) -> float:
        """Get seconds until retry is allowed (for OPEN state)."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "CircuitBreaker.get_time_until_retry"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:CircuitBreaker.get_time_until_retry".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if self._state != CircuitState.OPEN:
            return 0.0
        if self._last_failure_time is None:
            return 0.0
        remaining = self._current_reset_timeout - (time.time() - self._last_failure_time)
        return max(0.0, remaining)

    def protect(self, func: Callable) -> Callable:
        """Decorator with non-blocking execution timeout."""

        def wrapper(*args, **kwargs):
            if not self.allow_request():
                raise CircuitBreakerOpenError(self.name, self.get_time_until_retry())
            result_container = {}
            execution_complete = threading.Event()

            def target():
                try:
                    result_container["result"] = func(*args, **kwargs)
                except Exception as e:
                    raise
                    result_container["exception"] = e
                finally:
                    execution_complete.set()

            t = threading.Thread(target=target)
            t.daemon = True
            t.start()
            execution_complete.wait(timeout=self.config.execution_timeout_seconds)
            if not execution_complete.is_set():
                error = CircuitBreakerTimeoutError(self.name, self.config.execution_timeout_seconds)
                try:
                    self.record_failure(error)
                except (AttributeError, TypeError) as e:
                    self.logger.debug(f"Failed to record failure: {e}")
                raise error
            if "exception" in result_container:
                try:
                    self.record_failure(result_container["exception"])
                except (AttributeError, TypeError) as e:
                    self.logger.debug(f"Failed to record failure: {e}")
                raise result_container["exception"]
            try:
                self.record_success()
            except (AttributeError, TypeError) as e:
                self.logger.debug(f"Failed to record success: {e}")
            return result_container["result"]

        wrapper.__name__ = func.__name__
        return wrapper


def get_breaker(name: str, **kwargs) -> "CircuitBreaker":
    """Get or create a circuit breaker by name using deadlock-free pattern."""
    if name not in _breakers:
        with _breaker_lock:
            if name not in _breakers:
                config = CircuitBreakerConfig(**kwargs) if kwargs else None
                _breakers[name] = CircuitBreaker(name, config)
    return _breakers[name]


def get_all_breakers() -> dict[str, "CircuitBreaker"]:
    """Get all registered circuit breakers for dashboard."""
    with _breaker_lock:
        return dict(_breakers)


def reset_registry() -> None:
    """Reset the circuit breaker registry - for testing only."""
    with _breaker_lock:
        _breakers.clear()
