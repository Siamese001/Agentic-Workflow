"""
CircuitBreakerMixin - V10 Failure Isolation Pattern.

Provides circuit breaker functionality to prevent cascading failures
and protect system resources during healing operations.

References:
- V10 Safe Execution: Auto-rollback if problems
- Failure isolation and recovery
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting calls
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitStats:
    """Statistics for circuit breaker."""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    rejected_calls: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0


class CircuitBreakerMixin:
    """
    Mixin providing circuit breaker pattern for failure isolation.

    Prevents cascading failures by temporarily disabling operations
    that are consistently failing.

    MRO RULE: This mixin MUST precede base agent classes in inheritance.

    Usage:
        class MyAgent(CircuitBreakerMixin, SovereignBaseAgent):
            pass

    Configuration:
        failure_threshold: Number of failures before opening circuit (default: 5)
        recovery_timeout: Seconds before attempting recovery (default: 30)
        success_threshold: Successes needed to close circuit (default: 2)
    """

    _circuit_state: CircuitState = CircuitState.CLOSED
    _circuit_stats: CircuitStats = field(default_factory=CircuitStats)
    _circuit_opened_at: Optional[datetime] = None

    # Configuration
    _failure_threshold: int = 5
    _recovery_timeout: int = 30
    _success_threshold: int = 2

    def __init_subclass__(cls, **kwargs):
        """Initialize circuit breaker state for subclasses."""
        super().__init_subclass__(**kwargs)
        cls._circuit_stats = CircuitStats()

    def configure_circuit_breaker(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        success_threshold: int = 2,
    ) -> None:
        """
        Configure circuit breaker parameters.

        Args:
            failure_threshold: Failures before opening circuit
            recovery_timeout: Seconds before recovery attempt
            success_threshold: Successes needed to close circuit
        """
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._success_threshold = success_threshold

    def circuit_protected(
        self,
        operation: Callable[..., T],
        *args: Any,
        fallback: Optional[Callable[..., T]] = None,
        **kwargs: Any,
    ) -> T:
        """
        Execute operation with circuit breaker protection.

        Args:
            operation: The operation to execute
            *args: Positional arguments for operation
            fallback: Optional fallback if circuit is open
            **kwargs: Keyword arguments for operation

        Returns:
            Result of operation or fallback

        Raises:
            CircuitOpenError: If circuit is open and no fallback provided
        """
        if not hasattr(self, "_circuit_stats") or self._circuit_stats is None:
            self._circuit_stats = CircuitStats()

        # Check if circuit should transition from OPEN to HALF_OPEN
        if self._circuit_state == CircuitState.OPEN:
            if self._should_attempt_recovery():
                self._circuit_state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                self._circuit_stats.rejected_calls += 1
                if fallback:
                    return fallback(*args, **kwargs)
                raise CircuitOpenError(
                    f"Circuit is OPEN. Rejected call. Recovery in {self._time_until_recovery()}s"
                )

        # Execute operation
        self._circuit_stats.total_calls += 1
        try:
            result = operation(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure(e)
            raise

    def _record_success(self) -> None:
        """Record a successful operation."""
        self._circuit_stats.successful_calls += 1
        self._circuit_stats.last_success_time = datetime.utcnow()
        self._circuit_stats.consecutive_successes += 1
        self._circuit_stats.consecutive_failures = 0

        if self._circuit_state == CircuitState.HALF_OPEN:
            if self._circuit_stats.consecutive_successes >= self._success_threshold:
                self._circuit_state = CircuitState.CLOSED
                self._circuit_opened_at = None
                logger.info("Circuit breaker CLOSED after recovery")

    def _record_failure(self, error: Exception) -> None:
        """Record a failed operation."""
        self._circuit_stats.failed_calls += 1
        self._circuit_stats.last_failure_time = datetime.utcnow()
        self._circuit_stats.consecutive_failures += 1
        self._circuit_stats.consecutive_successes = 0

        logger.warning(f"Circuit breaker recorded failure: {error}")

        if self._circuit_state == CircuitState.HALF_OPEN:
            # Failed during recovery attempt, reopen
            self._circuit_state = CircuitState.OPEN
            self._circuit_opened_at = datetime.utcnow()
            logger.warning("Circuit breaker reopened after failed recovery")

        elif self._circuit_state == CircuitState.CLOSED:
            if self._circuit_stats.consecutive_failures >= self._failure_threshold:
                self._circuit_state = CircuitState.OPEN
                self._circuit_opened_at = datetime.utcnow()
                logger.warning(f"Circuit breaker OPENED after {self._failure_threshold} failures")

    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self._circuit_opened_at is None:
            return True
        elapsed = (datetime.utcnow() - self._circuit_opened_at).total_seconds()
        return elapsed >= self._recovery_timeout

    def _time_until_recovery(self) -> int:
        """Get seconds until recovery attempt."""
        if self._circuit_opened_at is None:
            return 0
        elapsed = (datetime.utcnow() - self._circuit_opened_at).total_seconds()
        return max(0, int(self._recovery_timeout - elapsed))

    def get_circuit_state(self) -> Dict[str, Any]:
        """Get current circuit breaker state and statistics."""
        if not hasattr(self, "_circuit_stats") or self._circuit_stats is None:
            self._circuit_stats = CircuitStats()

        return {
            "state": self._circuit_state.value,
            "total_calls": self._circuit_stats.total_calls,
            "successful_calls": self._circuit_stats.successful_calls,
            "failed_calls": self._circuit_stats.failed_calls,
            "rejected_calls": self._circuit_stats.rejected_calls,
            "consecutive_failures": self._circuit_stats.consecutive_failures,
            "time_until_recovery": (
                self._time_until_recovery() if self._circuit_state == CircuitState.OPEN else None
            ),
        }

    def reset_circuit(self) -> None:
        """Manually reset the circuit breaker."""
        self._circuit_state = CircuitState.CLOSED
        self._circuit_stats = CircuitStats()
        self._circuit_opened_at = None
        logger.info("Circuit breaker manually reset")


class CircuitOpenError(Exception):
    """Raised when circuit is open and no fallback provided."""

    pass
