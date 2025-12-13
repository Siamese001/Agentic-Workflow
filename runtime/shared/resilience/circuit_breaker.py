"""
Circuit Breaker - Prevents cascading failures in distributed systems.

Implements the Circuit Breaker pattern with three states:
- CLOSED: Normal operation, requests pass through
- OPEN: Failures exceeded threshold, requests fail fast
- HALF_OPEN: Testing if service recovered, limited requests allowed
"""

import time
import logging
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker monitoring."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    consecutive_failures: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    state_changed_at: float = field(default_factory=time.time)

    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests

class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    pass

class CircuitBreaker:
    """
    Circuit Breaker implementation for fault tolerance.

    Prevents cascading failures by failing fast when a service is unhealthy.
    """

    def __init__(
        self,
        name: str,
        fail_max: int = 5,
        reset_timeout: int = 60,
        half_open_max_calls: int = 1
    ):
        """Initialize circuit breaker.

        Args:
            name: Circuit breaker name for logging
            fail_max: Number of failures before opening circuit
            reset_timeout: Seconds before attempting recovery (OPEN -> HALF_OPEN)
            half_open_max_calls: Max calls allowed in HALF_OPEN state
        """
        self.name = name
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self.half_open_max_calls = half_open_max_calls

        self._state = CircuitState.CLOSED
        self._stats = CircuitBreakerStats()
        self._half_open_calls = 0

        logger.info(
            f"CircuitBreaker '{name}' initialized: "
            f"fail_max={fail_max}, reset_timeout={reset_timeout}s"
        )

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state

    @property
    def stats(self) -> CircuitBreakerStats:
        """Get circuit breaker statistics."""
        return self._stats

    def is_closed(self) -> bool:
        """Check if circuit is closed (healthy)."""
        return self._state == CircuitState.CLOSED

    def is_open(self) -> bool:
        """Check if circuit is open (failing fast)."""
        return self._state == CircuitState.OPEN

    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing recovery)."""
        return self._state == CircuitState.HALF_OPEN

    def raise_if_open(self) -> None:
        """Raise exception if circuit is open.

        Raises:
            CircuitBreakerError: If circuit is open
        """
        # Check if we should transition from OPEN to HALF_OPEN
        if self._state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Failing fast to prevent cascading failures."
                )

        # Check if we've exceeded half-open call limit
        if self._state == CircuitState.HALF_OPEN:
            if self._half_open_calls >= self.half_open_max_calls:
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' is HALF_OPEN. "
                    f"Max test calls ({self.half_open_max_calls}) exceeded."
                )

    def record_success(self) -> None:
        """Record a successful operation."""
        self._stats.total_requests += 1
        self._stats.successful_requests += 1
        self._stats.consecutive_failures = 0
        self._stats.last_success_time = time.time()

        # Transition based on current state
        if self._state == CircuitState.HALF_OPEN:
            # Success in HALF_OPEN means service recovered
            self._transition_to_closed()
            logger.info(
                f"CircuitBreaker '{self.name}': Service recovered, "
                f"transitioning to CLOSED"
            )
        elif self._state == CircuitState.OPEN:
            # This shouldn't happen, but handle gracefully
            logger.warning(
                f"CircuitBreaker '{self.name}': "
                f"Success recorded while OPEN (unexpected)"
            )

    def record_failure(self) -> None:
        """Record a failed operation."""
        self._stats.total_requests += 1
        self._stats.failed_requests += 1
        self._stats.consecutive_failures += 1
        self._stats.last_failure_time = time.time()

        # Check if we should open the circuit
        if self._state == CircuitState.CLOSED:
            if self._stats.consecutive_failures >= self.fail_max:
                self._transition_to_open()
                logger.error(
                    f"CircuitBreaker '{self.name}': "
                    f"Threshold exceeded ({self.fail_max} failures), "
                    f"transitioning to OPEN"
                )

        elif self._state == CircuitState.HALF_OPEN:
            # Failure in HALF_OPEN means service still unhealthy
            self._transition_to_open()
            logger.warning(
                f"CircuitBreaker '{self.name}': "
                f"Test call failed, returning to OPEN"
            )

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self._stats.last_failure_time is None:
            return False

        time_since_failure = time.time() - self._stats.last_failure_time
        return time_since_failure >= self.reset_timeout

    def _transition_to_closed(self) -> None:
        """Transition to CLOSED state."""
        self._state = CircuitState.CLOSED
        self._stats.consecutive_failures = 0
        self._stats.state_changed_at = time.time()
        self._half_open_calls = 0

    def _transition_to_open(self) -> None:
        """Transition to OPEN state."""
        self._state = CircuitState.OPEN
        self._stats.state_changed_at = time.time()
        self._half_open_calls = 0

    def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state."""
        self._state = CircuitState.HALF_OPEN
        self._stats.state_changed_at = time.time()
        self._half_open_calls = 0

        logger.info(
            f"CircuitBreaker '{self.name}': "
            f"Attempting recovery, transitioning to HALF_OPEN"
        )

    def reset(self) -> None:
        """Manually reset circuit breaker to CLOSED state."""
        logger.info(f"CircuitBreaker '{self.name}': Manual reset to CLOSED")
        self._transition_to_closed()

    def get_status(self) -> dict:
        """Get detailed status information.

        Returns:
            Status dictionary with state and statistics
        """
        return {
            "name": self.name,
            "state": self._state.value,
            "stats": {
                "total_requests": self._stats.total_requests,
                "successful_requests": self._stats.successful_requests,
                "failed_requests": self._stats.failed_requests,
                "consecutive_failures": self._stats.consecutive_failures,
                "success_rate": self._stats.success_rate(),
                "last_failure_time": self._stats.last_failure_time,
                "last_success_time": self._stats.last_success_time,
                "state_changed_at": self._stats.state_changed_at
            },
            "config": {
                "fail_max": self.fail_max,
                "reset_timeout": self.reset_timeout,
                "half_open_max_calls": self.half_open_max_calls
            }
        }
