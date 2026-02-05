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

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states per V10 specification."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject all requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""

    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes in half-open to close
    reset_timeout_seconds: float = 60.0  # Time before half-open
    max_reset_timeout_seconds: float = 600.0  # Max backoff cap
    backoff_multiplier: float = 2.0  # Exponential backoff factor
    half_open_max_calls: int = 3  # Max concurrent calls in half-open
    execution_timeout_seconds: float = 30.0  # Max time a function can run before killed


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


# Global registry with simple lock pattern to prevent deadlock
_breaker_lock = threading.Lock()
_breakers: dict[str, "CircuitBreaker"] = {}


class CircuitBreaker:
    """V10-Compliant Circuit Breaker with Non-Blocking Execution Timeout."""

    def __init__(
        self,
        name: str,
        config: CircuitBreakerConfig | None = None,
    ):
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
                # Reset failure count on success
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
        return (time.time() - self._last_failure_time) >= self._current_reset_timeout

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

    def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state."""
        self._state = CircuitState.HALF_OPEN
        self._success_count = 0
        self._half_open_calls = 0
        self.metrics.state_transitions += 1

    def _transition_to_closed(self) -> None:
        """Transition to CLOSED state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._half_open_calls = 0
        self._current_reset_timeout = self.config.reset_timeout_seconds
        self.metrics.current_backoff = 0.0
        self.metrics.state_transitions += 1

    def get_time_until_retry(self) -> float:
        """Get seconds until retry is allowed (for OPEN state)."""
        if self._state != CircuitState.OPEN:
            return 0.0
        if self._last_failure_time is None:
            return 0.0
        remaining = self._current_reset_timeout - (time.time() - self._last_failure_time)
        return max(0.0, remaining)

    def protect(self, func: Callable) -> Callable:
        """Decorator with non-blocking execution timeout."""

        def wrapper(*args, **kwargs):
            # 1. Check circuit state (fast, minimal lock time)
            if not self.allow_request():
                raise CircuitBreakerOpenError(self.name, self.get_time_until_retry())

            # 2. Run in daemon thread to allow non-blocking timeout
            result_container = {}
            execution_complete = threading.Event()

            def target():
                try:
                    result_container["result"] = func(*args, **kwargs)
                except Exception as e:
                    result_container["exception"] = e
                finally:
                    execution_complete.set()

            # IMPORTANT: daemon=True ensures this thread is killed when main process exits
            t = threading.Thread(target=target)
            t.daemon = True
            t.start()

            # Wait for either completion or timeout
            execution_complete.wait(timeout=self.config.execution_timeout_seconds)

            # 3. Handle result or timeout
            if not execution_complete.is_set():
                # Timeout occurred - record failure without waiting for thread
                error = CircuitBreakerTimeoutError(self.name, self.config.execution_timeout_seconds)
                # Record failure outside of any thread locks
                try:
                    self.record_failure(error)
                except Exception:
                    pass
                raise error

            if "exception" in result_container:
                try:
                    self.record_failure(result_container["exception"])
                except Exception:
                    pass  # Still raise the original exception
                raise result_container["exception"]

            try:
                self.record_success()
            except Exception:
                pass  # Still return the result
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
