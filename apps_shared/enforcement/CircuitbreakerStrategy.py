"""Circuit Breaker - Resilience pattern for preventing cascading failures.

This module implements the Circuit Breaker pattern to detect failures,
"Open" the circuit (stop calling failing services), and automatically
attempt recovery after a timeout.
"""

import asyncio
import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_reads_policy_state("p0", "CircuitbreakerStrategy", "policy_binding")
_emit_snapshots_state("p0", "CircuitbreakerStrategy", "state_snapshot")
emit_replay_key("p0", "CircuitbreakerStrategy")
emit_determinism_digest("p0", "CircuitbreakerStrategy")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitOpenError(Exception):
    """Raised when circuit is open and requests are blocked."""

    pass


class CriticalServiceFailure(Exception):
    """Raised when a critical service fails and no fallback is available."""

    pass


@dataclass
class CircuitBreakerConfig:
    """configuration for circuit breaker behavior."""

    failure_threshold: int = 3
    recovery_timeout: float = 60.0
    expected_exception: type = Exception
    timeout: float = 30.0
    success_threshold: int = 2
    monitor_timeout: bool = True


class CircuitBreaker:
    """Stateful circuit breaker implementation.

    Tracks failures and automatically opens/closes based on configuration.
    """

    def __init__(self, name: str, config: CircuitBreakerConfig | None = None):
        """Initialize the circuit breaker.

        Args:
            name: Name for logging/tracking
            config: Optional configuration overrides
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
        self.state = CircuitState.CLOSED
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "timeout_calls": 0,
            "circuit_opens": 0,
            "circuit_closes": 0,
        }
        logger.info(f"Initialized CircuitBreaker '{name}' with threshold {self.config.failure_threshold}")

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute a function through the circuit breaker.

        Args:
            func: The function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            The result of the function call

        Raises:
            CircuitOpenError: If circuit is open
            CriticalServiceFailure: If service fails and circuit is open
            The original exception if call fails and circuit is not open
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CircuitBreaker.call")

        self.stats["total_calls"] += 1
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit '{self.name}' entering HALF_OPEN state")
            else:
                self.stats["circuit_opens"] += 1
                raise CircuitOpenError(f"Circuit '{self.name}' is OPEN")
        try:
            if self.config.monitor_timeout:
                result = await asyncio.wait_for(func(*args, **kwargs), timeout=self.config.timeout)
            else:
                result = await func(*args, **kwargs)
            self._on_success()
            return result
        except asyncio.TimeoutError as e:
            self.stats["timeout_calls"] += 1
            self._on_failure()
            logger.warning(f"Timeout in circuit '{self.name}': {e}")
            raise
        except self.config.expected_exception as e:
            self._on_failure()
            logger.error(f"Expected exception in circuit '{self.name}': {e}")
            raise
        except Exception as e:
            self._on_failure()
            logger.error(f"Unexpected exception in circuit '{self.name}': {e}")
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        return time.time() - self.last_failure_time >= self.config.recovery_timeout

    def _on_success(self) -> None:
        """Handle a successful call."""
        self.stats["successful_calls"] += 1
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._close_circuit()
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def _on_failure(self) -> None:
        """Handle a failed call."""
        self.stats["failed_calls"] += 1
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.state == CircuitState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self._open_circuit()
        elif self.state == CircuitState.HALF_OPEN:
            self._open_circuit()

    def _open_circuit(self) -> None:
        """Open the circuit to block further calls."""
        self.state = CircuitState.OPEN
        self.success_count = 0
        self.stats["circuit_opens"] += 1
        logger.warning(f"Circuit '{self.name}' OPENED after {self.failure_count} failures")

    def _close_circuit(self) -> None:
        """Close the circuit to allow normal operation."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.stats["circuit_closes"] += 1
        logger.info(f"Circuit '{self.name}' CLOSED after successful recovery")

    def get_state(self) -> CircuitState:
        """Get the current circuit state."""
        return self.state

    def get_stats(self) -> dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            **self.stats,
        }

    def reset(self) -> None:
        """Manually reset the circuit to CLOSED state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
        logger.info(f"Circuit '{self.name}' manually reset to CLOSED state")


class CircuitBreakerFactory:
    """Factory for managing named circuit breakers with thread safety.

    Provides singleton access to circuit breakers by name, ensuring
    that failures in one service don't affect others. Thread-safe
    implementation prevents race conditions in concurrent environments.
    """

    _instance = None
    _lock = threading.Lock()
    _breakers: dict[str, CircuitBreaker] = {}
    _breakers_lock = threading.RLock()

    def __new__(cls):
        """Thread-safe singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the factory with thread safety."""
        if self._initialized:
            return
        with self._lock:
            if self._initialized:
                return
            self._initialized = True
            logger.info("Initialized CircuitBreakerFactory with thread safety")

    @classmethod
    def get(cls, name: str, config: CircuitBreakerConfig | None = None) -> CircuitBreaker:
        """Get or create a circuit breaker by name with thread safety.

        Args:
            name: Unique name for the circuit breaker
            config: Optional configuration for new breakers

        Returns:
            CircuitBreaker instance
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CircuitBreakerFactory.get")

        factory = cls()
        if name not in factory._breakers:
            with factory._breakers_lock:
                if name not in factory._breakers:
                    factory._breakers[name] = CircuitBreaker(name, config)
                    logger.debug(f"Created new CircuitBreaker: {name}")
        return factory._breakers[name]

    @classmethod
    def list_all(cls) -> dict[str, dict[str, Any]]:
        """List all circuit breakers and their states with thread safety.

        Returns:
            Dictionary mapping breaker names to their stats
        """
        factory = cls()
        with factory._breakers_lock:
            return {name: breaker.get_stats() for name, breaker in factory._breakers.items()}

    @classmethod
    def reset_all(cls) -> None:
        """Reset all circuit breakers to CLOSED state with thread safety."""
        factory = cls()
        with factory._breakers_lock:
            for breaker in factory._breakers.values():
                breaker.reset()
        logger.info("All circuit breakers reset to CLOSED state")

    @classmethod
    def reset(cls, name: str) -> None:
        """Reset a specific circuit breaker with thread safety.

        Args:
            name: Name of the circuit breaker to reset
        """
        factory = cls()
        with factory._breakers_lock:
            if name in factory._breakers:
                factory._breakers[name].reset()
                logger.info(f"CircuitBreaker '{name}' reset to CLOSED state")
            else:
                logger.warning(f"CircuitBreaker '{name}' not found")

    @classmethod
    def remove(cls, name: str) -> bool:
        """Remove a circuit breaker from the factory with thread safety.

        Args:
            name: Name of the circuit breaker to remove

        Returns:
            True if removed, False if not found
        """
        factory = cls()
        with factory._breakers_lock:
            if name in factory._breakers:
                del factory._breakers[name]
                logger.info(f"CircuitBreaker '{name}' removed from factory")
                return True
            return False

    @classmethod
    def clear_all(cls) -> None:
        """Clear all circuit breakers from the factory with thread safety."""
        factory = cls()
        with factory._breakers_lock:
            factory._breakers.clear()
        logger.info("All circuit breakers cleared from factory")


def get_circuit_breaker(name: str, config: CircuitBreakerConfig | None = None) -> CircuitBreaker:
    """Get a circuit breaker by name.

    Args:
        name: Unique name for the circuit breaker
        config: Optional configuration

    Returns:
        CircuitBreaker instance
    """
    return CircuitBreakerFactory.get(name, config)


def with_circuit_breaker(breaker_name: str, config: CircuitBreakerConfig | None = None):
    """Decorator to wrap functions with circuit breaker protection.

    Args:
        breaker_name: Name for the circuit breaker
        config: Optional configuration

    Returns:
        Decorated function
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            breaker = get_circuit_breaker(breaker_name, config)
            return await breaker.call(func, *args, **kwargs)

        return wrapper

    return decorator
