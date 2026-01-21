from __future__ import annotations

"""Circuit Breaker implementation for fault tolerance.

Migrated from archives/legacy_root_folders/tools/runtime_utils.py
Phase 1 - Pillar 8: Tool Ecosystem (Resilience Middleware)
"""

import time
from dataclasses import dataclass
from enum import Enum


class CircuitBreakerState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and rejects requests."""

    def __init__(self, message: str, breaker_name: str):
        super().__init__(message)
        self.breaker_name = breaker_name


@dataclass
class CircuitBreaker:
    """Minimal circuit breaker with CLOSED / OPEN / HALF_OPEN states.

    This is intentionally simple and process-local; higher-level
    orchestration (e.g. batch runner) is responsible for coordinating
    breakers across workers if needed.

    Attributes:
        name: Unique identifier for this circuit breaker
        failure_threshold: Number of failures before opening circuit
        reset_after_s: Seconds to wait before attempting recovery
        half_open_max_calls: Successful calls needed to close circuit
        state: Current state (CLOSED, OPEN, HALF_OPEN)
        failure_count: Current count of consecutive failures
        success_count: Current count of consecutive successes
        opened_at: Timestamp when circuit was opened
    """

    name: str
    failure_threshold: int = 5
    reset_after_s: int = 30
    half_open_max_calls: int = 3

    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    opened_at: float = 0.0

    def can_execute(self) -> bool:
        """Check if execution is allowed based on current state.

        Returns:
            True if execution is allowed, False if circuit is open
        """
        now = time.time()

        if self.state == CircuitBreakerState.OPEN:
            if now - self.opened_at >= self.reset_after_s:
                self.state = CircuitBreakerState.HALF_OPEN
                self.failure_count = 0
                self.success_count = 0
            else:
                return False

        if (self.state == CircuitBreakerState.HALF_OPEN and
            self.success_count >= self.half_open_max_calls):
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.success_count = 0

        return True

    def record_success(self) -> None:
        """Record a successful execution."""
        self.success_count += 1

        if (self.state in {CircuitBreakerState.OPEN, CircuitBreakerState.HALF_OPEN} and
            self.success_count >= self.half_open_max_calls):
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.success_count = 0

    def record_failure(self) -> None:
        """Record a failed execution."""
        self.failure_count += 1

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            self.opened_at = time.time()


_BREAKERS: dict[str, CircuitBreaker] = {}


def get_breaker(
    name: str,
    failure_threshold: int = 5,
    reset_after_s: int = 30,
    half_open_max_calls: int = 3,
) -> CircuitBreaker:
    """Get or create a circuit breaker by name.

    Args:
        name: Unique identifier for the breaker
        failure_threshold: Number of failures before opening
        reset_after_s: Seconds before attempting recovery
        half_open_max_calls: Successes needed to close

    Returns:
        CircuitBreaker instance
    """
    if name not in _BREAKERS:
        _BREAKERS[name] = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            reset_after_s=reset_after_s,
            half_open_max_calls=half_open_max_calls,
        )
    return _BREAKERS[name]


def reset_all_breakers() -> None:
    """Reset all circuit breakers (primarily for testing)."""
    _BREAKERS.clear()
