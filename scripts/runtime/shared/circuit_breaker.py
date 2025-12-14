"""Circuit Breaker - Prevents cascade failures.

This module implements the circuit breaker pattern to automatically
stop calling failing services and allow them time to recover.
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, stop calling
    HALF_OPEN = "half_open"  # Testing recovery

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Number of failures before opening
    success_threshold: int = 3  # Number of successes to close from half-open
    timeout: float = 60.0       # Seconds to wait before trying half-open
    reset_timeout: float = 300.0  # Max time in open state before force reset
    min_requests: int = 10      # Minimum requests before calculating failure rate
    failure_rate_threshold: float = 0.5  # 50% failure rate triggers opening
    sliding_window_size: int = 100  # Number of recent requests to track

@dataclass
class RequestResult:
    """Result of a request through circuit breaker."""
    success: bool
    timestamp: datetime
    duration_ms: float
    error: Optional[Exception] = None

class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    pass

class CircuitBreaker:
    """Circuit breaker implementation."""

    def __init__(self, name: str, config: Optional[CircuitBreakerConfig] = None):
            """Initialize circuit breaker.

        Args:
            name: Circuit breaker name
            config: Configuration
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()

        # State
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change = datetime.utcnow()

        # Sliding window for failure rate calculation
        self.request_history: List[RequestResult] = []

        # Statistics
        self._stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "circuit_opened_count": 0,
            "circuit_closed_count": 0
        }

        logger.debug(f"Initialized CircuitBreaker: {name}")

    async def call(self, func: Callable, *args, **kwargs) -> Any:
            """Execute function through circuit breaker.

        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Original exception from function
        """
        start_time = time.time()

        # Check circuit state
        if not self.can_execute():
            raise CircuitBreakerError(f"Circuit '{self.name}' is {self.state.value}")

        try:
            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Record success
            duration_ms = (time.time() - start_time) * 1000
            self.record_success(duration_ms)

            return result

        except Exception as e:
            # Record failure
            duration_ms = (time.time() - start_time) * 1000
            self.record_failure(e, duration_ms)
            raise

    def can_execute(self) -> bool:
            """Check if execution is allowed.

        Returns:
            True if can execute
        """
        if self.state == CircuitState.CLOSED:
            return True

        elif self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = datetime.utcnow()
                self.success_count = 0
                logger.info(f"Circuit '{self.name}' entering HALF_OPEN state")
                return True
            return False

        elif self.state == CircuitState.HALF_OPEN:
            return True

        return False

    def record_success(self, duration_ms: float) -> None:
            """Record a successful execution.

        Args:
            duration_ms: Execution duration
        """
        # Update statistics
        self._stats["total_requests"] += 1
        self._stats["successful_requests"] += 1

        # Add to history
        result = RequestResult(
            success=True,
            timestamp=datetime.utcnow(),
            duration_ms=duration_ms
        )
        self._add_to_history(result)

        # Update state
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self._close_circuit()
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0  # Reset on success

    def record_failure(self, error: Exception, duration_ms: float) -> None:
            """Record a failed execution.

        Args:
            error: Exception that occurred
            duration_ms: Execution duration
        """
        # Update statistics
        self._stats["total_requests"] += 1
        self._stats["failed_requests"] += 1

        # Add to history
        result = RequestResult(
            success=False,
            timestamp=datetime.utcnow(),
            duration_ms=duration_ms,
            error=error
        )
        self._add_to_history(result)

        # Update state
        if self.state == CircuitState.HALF_OPEN:
            self._open_circuit("Failed in half-open state")
        elif self.state == CircuitState.CLOSED:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()

            # Check if should open based on count or rate
            if self._should_open_circuit():
                self._open_circuit(f"Failure threshold reached: {self.failure_count}")

    def _add_to_history(self, result: RequestResult) -> None:
            """Add result to sliding window.

        Args:
            result: Request result
        """
        self.request_history.append(result)

        # Trim to window size
        if len(self.request_history) > self.config.sliding_window_size:
            self.request_history = self.request_history[-self.config.sliding_window_size:]

    def _should_open_circuit(self) -> bool:
            """Check if circuit should open.

        Returns:
            True if should open
        """
        # Check failure count
        if self.failure_count >= self.config.failure_threshold:
            return True

        # Check failure rate
        if len(self.request_history) >= self.config.min_requests:
            recent_failures = sum(1 for r in self.request_history if not r.success)
            failure_rate = recent_failures / len(self.request_history)
            if failure_rate >= self.config.failure_rate_threshold:
                logger.warning(
                    f"Circuit '{self.name}' failure rate {failure_rate:.2%} "
                    f"exceeds threshold {self.config.failure_rate_threshold:.2%}"
                )
                return True

        return False

    def _should_attempt_reset(self) -> bool:
            """Check if should attempt reset from open to half-open.

        Returns:
            True if should attempt reset
        """
        if not self.last_failure_time:
            return True

        time_since_failure = datetime.utcnow() - self.last_failure_time
        return time_since_failure.total_seconds() >= self.config.timeout

    def _open_circuit(self, reason: str) -> None:
            """Open the circuit.

        Args:
            reason: Reason for opening
        """
        self.state = CircuitState.OPEN
        self.last_state_change = datetime.utcnow()
        self._stats["circuit_opened_count"] += 1
        logger.warning(f"Circuit '{self.name}' OPENED: {reason}")

    def _close_circuit(self) -> None:
            """Close the circuit."""
        self.state = CircuitState.CLOSED
        self.last_state_change = datetime.utcnow()
        self.failure_count = 0
        self.success_count = 0
        self._stats["circuit_closed_count"] += 1
        logger.info(f"Circuit '{self.name}' CLOSED")

    def force_open(self, reason: str = "Manual override") -> None:
            """Force circuit open.

        Args:
            reason: Reason for forcing open
        """
        self._open_circuit(reason)

    def force_close(self) -> None:
            """Force circuit closed."""
        self._close_circuit()

    def get_stats(self) -> Dict[str, Any]:
            """Get circuit breaker statistics.

        Returns:
            Statistics dictionary
        """
        stats = self._stats.copy()
        stats.update({
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,


            "last_state_change": self.last_state_change.isoformat(),
            "current_failure_rate": self._get_current_failure_rate()
        })
        return stats

    def _get_current_failure_rate(self) -> float:
            """Get current failure rate.

        Returns:
            Failure rate (0.0 to 1.0)
        """
        if not self.request_history:
            return 0.0

        failures = sum(1 for r in self.request_history if not r.success)
        return failures / len(self.request_history)

    def reset_stats(self) -> None:
            """Reset statistics."""
        self._stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "circuit_opened_count": 0,
            "circuit_closed_count": 0
        }
        self.request_history.clear()

class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""

    def __init__(self):
            """Initialize registry."""
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()

        """Docstring."""
    async def get_circuit_breaker(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None
    ) -> CircuitBreaker:
            """Get or create circuit breaker.

        Args:
            name: Circuit breaker name
            config: Configuration (only used for new circuit breaker)

        Returns:
            CircuitBreaker instance
        """
        async with self._lock:
            if name not in self.circuit_breakers:
                self.circuit_breakers[name] = CircuitBreaker(name, config)
            return self.circuit_breakers[name]

        """Docstring."""
    async def call_through(
        self,
        circuit_name: str,
        func: Callable,
        *args,
        config: Optional[CircuitBreakerConfig] = None,
        **kwargs
    ) -> Any:
            """Call function through circuit breaker.

        Args:
            circuit_name: Name of circuit breaker
            func: Function to call
            *args: Function arguments
            config: Circuit breaker config
            **kwargs: Function keyword arguments

        Returns:
            Function result
        """
        breaker = await self.get_circuit_breaker(circuit_name, config)
        return await breaker.call(func, *args, **kwargs)

    def list_circuit_breakers(self) -> List[str]:
            """List all circuit breaker names.

        Returns:
            List of names
        """
        return list(self.circuit_breakers.keys())

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
            """Get stats for all circuit breakers.

        Returns:
            Stats dictionary
        """
        return {name: cb.get_stats() for name, cb in self.circuit_breakers.items()}

    async def reset_all(self) -> None:
            """Reset all circuit breakers."""
        async with self._lock:
            for cb in self.circuit_breakers.values():
                cb.force_close()
                cb.reset_stats()

# Global registry
_registry: Optional[CircuitBreakerRegistry] = None
_registry_lock = asyncio.Lock()

async def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """Get global circuit breaker registry.

    Returns:
        CircuitBreakerRegistry instance
    """
    global _registry
    async with _registry_lock:
        if _registry is None:
            _registry = CircuitBreakerRegistry()
    return _registry

# Decorators
    """Docstring."""
def circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None
):
    """Decorator to add circuit breaker to functions.

    Args:
        name: Circuit breaker name
        config: Circuit breaker configuration

    Returns:
        Decorated function
    """
    def decorator(func):
            """TODO: Add docstring."""

            """TODO: Add docstring."""

        async def async_wrapper(*args, **kwargs):
                """Docstring."""
            registry = await get_circuit_breaker_registry()
            return await registry.call_through(name, func, *args, config=config, **kwargs)
            """TODO: Add docstring."""


                """TODO: Add docstring."""

        def sync_wrapper(*args, **kwargs):
                """Docstring."""
            # For sync functions, run in thread pool
            async def async_func():
                    """Docstring."""
                return func(*args, **kwargs)

            return asyncio.run(async_func())

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
