"""Circuit Breaker.

State machine with CLOSED/OPEN/HALF_OPEN states for fault tolerance.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    half_open_max_calls: int = 3
    success_threshold: int = 2


class CircuitBreaker:
    """Circuit breaker for fault tolerance.

    The CircuitBreaker implements a state machine that prevents
    cascading failures by rejecting requests when a service is
    experiencing high error rates.
    """

    def __init__(
        self,
        name: str,
        config: CircuitBreakerConfig | None = None,
    ):
        """Initialize the circuit breaker.

        Args:
            name: Circuit breaker name
            config: Optional configuration
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()

        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: float | None = None
        self._half_open_calls = 0

        log.info(f"CircuitBreaker '{name}' initialized")

    @property
    def state(self) -> CircuitState:
        """Current circuit state."""
        return self._state

    def can_execute(self) -> bool:
        """Check if execution is allowed.

        Returns:
            True if circuit allows execution
        """
        trace_id = f"cb_{self.name}_{int(time.time())}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "CircuitBreaker.can_execute"
        )

        if self._state == CircuitState.CLOSED:
            return True

        if self._state == CircuitState.OPEN:
            # Check if recovery timeout passed
            if self._last_failure_time and \
               time.time() - self._last_failure_time >= self.config.recovery_timeout:
                self._transition_to(CircuitState.HALF_OPEN)
                return True
            return False

        if self._state == CircuitState.HALF_OPEN:
            return self._half_open_calls < self.config.half_open_max_calls

        return False

    def record_success(self) -> None:
        """Record a successful execution."""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            self._half_open_calls += 1

            if self._success_count >= self.config.success_threshold:
                self._transition_to(CircuitState.CLOSED)
                self._reset_counts()
        else:
            self._failure_count = 0

    def record_failure(self) -> None:
        """Record a failed execution."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            self._half_open_calls += 1
            self._transition_to(CircuitState.OPEN)
        elif self._state == CircuitState.CLOSED:
            if self._failure_count >= self.config.failure_threshold:
                self._transition_to(CircuitState.OPEN)

        trace_id = f"cb_failure_{self.name}_{int(time.time())}"
        _emit_records_telemetry_event(
            trace_id,
            "CircuitBreaker",
            f"{self.name}_failure_{self._state.value}"
        )

    def execute(self, fn: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection.

        Args:
            fn: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpen: If circuit is open
            Exception: If function raises
        """
        if not self.can_execute():
            raise CircuitBreakerOpen(f"Circuit '{self.name}' is OPEN")

        try:
            result = fn(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        old_state = self._state
        self._state = new_state

        log.info(f"Circuit '{self.name}' transitioned: {old_state.value} -> {new_state.value}")

        trace_id = f"cb_transition_{self.name}_{int(time.time())}"
        _emit_records_telemetry_event(
            trace_id,
            "CircuitBreaker",
            f"{self.name}_transition_{old_state.value}_to_{new_state.value}"
        )

    def _reset_counts(self) -> None:
        """Reset failure and success counts."""
        self._failure_count = 0
        self._success_count = 0
        self._half_open_calls = 0

    def get_stats(self) -> dict[str, Any]:
        """Get circuit breaker statistics.

        Returns:
            Dictionary with stats
        """
        return {
            "name": self.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "failure_threshold": self.config.failure_threshold,
        }


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""
    pass


# Global registry
_circuit_breakers: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str) -> CircuitBreaker:
    """Get or create a circuit breaker."""
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name)
    return _circuit_breakers[name]
