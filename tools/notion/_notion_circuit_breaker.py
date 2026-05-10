#!/usr/bin/env python3
"""_notion_circuit_breaker.py — Circuit breaker for Notion API calls.

Pure logic. No I/O at import. Safe to import from any hook or write path.

States:
  - CLOSED: Normal operation, requests pass through
  - OPEN: Failing fast, requests blocked
  - HALF_OPEN: Testing recovery with probe requests

Transitions:
  - 5 consecutive failures → OPEN
  - 30s timeout → HALF_OPEN
  - 3 consecutive successes → CLOSED

Constitutional: §25 (MCP serialization), §36 (plan registration)
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, TypeVar


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = auto()      # Normal operation
    OPEN = auto()        # Failing fast
    HALF_OPEN = auto()   # Testing recovery


# Default configuration
FAILURE_THRESHOLD = 5
SUCCESS_THRESHOLD = 3
OPEN_TIMEOUT_SECONDS = 30.0


@dataclass
class CircuitStats:
    """Statistics for circuit breaker operations."""
    failures: int = 0
    successes: int = 0
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    state_transitions: list[tuple[float, CircuitState, CircuitState]] = field(default_factory=list)
    last_failure_time: float | None = None
    last_success_time: float | None = None
    total_calls: int = 0
    blocked_calls: int = 0
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "failures": self.failures,
            "successes": self.successes,
            "consecutive_failures": self.consecutive_failures,
            "consecutive_successes": self.consecutive_successes,
            "state_transitions": len(self.state_transitions),
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time,
            "total_calls": self.total_calls,
            "blocked_calls": self.blocked_calls,
        }


class CircuitBreaker:
    """Circuit breaker for protecting Notion API calls.
    
    Thread-safe implementation suitable for concurrent use.
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = FAILURE_THRESHOLD,
        success_threshold: int = SUCCESS_THRESHOLD,
        open_timeout: float = OPEN_TIMEOUT_SECONDS,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.open_timeout = open_timeout
        
        self._state = CircuitState.CLOSED
        self._stats = CircuitStats()
        self._last_state_change = time.time()
        self._lock = threading.RLock()
    
    @property
    def state(self) -> CircuitState:
        """Current circuit state (thread-safe read)."""
        with self._lock:
            return self._state
    
    @property
    def stats(self) -> CircuitStats:
        """Copy of current statistics (thread-safe read)."""
        with self._lock:
            # Return a copy to avoid external mutation
            return CircuitStats(
                failures=self._stats.failures,
                successes=self._stats.successes,
                consecutive_failures=self._stats.consecutive_failures,
                consecutive_successes=self._stats.consecutive_successes,
                state_transitions=self._stats.state_transitions.copy(),
                last_failure_time=self._stats.last_failure_time,
                last_success_time=self._stats.last_success_time,
                total_calls=self._stats.total_calls,
                blocked_calls=self._stats.blocked_calls,
            )
    
    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state (must hold lock)."""
        old_state = self._state
        if old_state != new_state:
            self._state = new_state
            now = time.time()
            self._stats.state_transitions.append((now, old_state, new_state))
            self._last_state_change = now
            
            # Reset counters on state change
            if new_state == CircuitState.OPEN:
                self._stats.consecutive_successes = 0
            elif new_state == CircuitState.CLOSED:
                self._stats.consecutive_failures = 0
            elif new_state == CircuitState.HALF_OPEN:
                self._stats.consecutive_failures = 0
                self._stats.consecutive_successes = 0
    
    def _check_timeout_transition(self) -> None:
        """Check if we should transition from OPEN to HALF_OPEN (must hold lock)."""
        if self._state == CircuitState.OPEN:
            elapsed = time.time() - self._last_state_change
            if elapsed >= self.open_timeout:
                self._transition_to(CircuitState.HALF_OPEN)
    
    def can_execute(self) -> bool:
        """Check if a request can be executed."""
        with self._lock:
            self._stats.total_calls += 1
            
            if self._state == CircuitState.CLOSED:
                return True
            
            if self._state == CircuitState.OPEN:
                self._check_timeout_transition()
                
                if self._state == CircuitState.OPEN:
                    # Still open, block the call
                    self._stats.blocked_calls += 1
                    return False
                # Transitioned to HALF_OPEN, allow probe
                return True
            
            if self._state == CircuitState.HALF_OPEN:
                return True
            
            return True  # Shouldn't reach here
    
    def record_success(self) -> None:
        """Record a successful call."""
        with self._lock:
            now = time.time()
            self._stats.successes += 1
            self._stats.consecutive_successes += 1
            self._stats.consecutive_failures = 0
            self._stats.last_success_time = now
            
            if self._state == CircuitState.HALF_OPEN:
                # In half-open, need multiple successes to close
                if self._stats.consecutive_successes >= self.success_threshold:
                    self._transition_to(CircuitState.CLOSED)
            elif self._state == CircuitState.CLOSED:
                # In closed, just track consecutive successes
                pass  # Already incremented above
    
    def record_failure(self) -> None:
        """Record a failed call."""
        with self._lock:
            now = time.time()
            self._stats.failures += 1
            self._stats.consecutive_failures += 1
            self._stats.consecutive_successes = 0
            self._stats.last_failure_time = now
            
            if self._state == CircuitState.CLOSED:
                # Check if we should open
                if self._stats.consecutive_failures >= self.failure_threshold:
                    self._transition_to(CircuitState.OPEN)
            elif self._state == CircuitState.HALF_OPEN:
                # Any failure in half-open re-opens immediately
                self._transition_to(CircuitState.OPEN)
    
    def reset(self) -> None:
        """Manually reset to CLOSED state."""
        with self._lock:
            self._transition_to(CircuitState.CLOSED)
            self._stats = CircuitStats()
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize circuit breaker state."""
        with self._lock:
            return {
                "name": self.name,
                "state": self._state.name,
                "failure_threshold": self.failure_threshold,
                "success_threshold": self.success_threshold,
                "open_timeout": self.open_timeout,
                "stats": self._stats.to_dict(),
                "last_state_change": self._last_state_change,
                "seconds_in_current_state": time.time() - self._last_state_change,
            }


# Global circuit breaker instances (per-API-endpoint)
_circuit_breakers: dict[str, CircuitBreaker] = {}
_circuit_lock = threading.Lock()


def get_circuit_breaker(
    name: str = "notion_api",
    failure_threshold: int = FAILURE_THRESHOLD,
    success_threshold: int = SUCCESS_THRESHOLD,
    open_timeout: float = OPEN_TIMEOUT_SECONDS,
) -> CircuitBreaker:
    """Get or create a named circuit breaker instance.
    
    Thread-safe singleton per name.
    """
    global _circuit_breakers
    
    with _circuit_lock:
        if name not in _circuit_breakers:
            _circuit_breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                success_threshold=success_threshold,
                open_timeout=open_timeout,
            )
        return _circuit_breakers[name]


def reset_all_circuits() -> None:
    """Reset all circuit breakers (useful for testing)."""
    global _circuit_breakers
    
    with _circuit_lock:
        for cb in _circuit_breakers.values():
            cb.reset()
        _circuit_breakers.clear()


def get_all_circuit_states() -> dict[str, dict[str, Any]]:
    """Get state of all circuit breakers."""
    global _circuit_breakers
    
    with _circuit_lock:
        return {
            name: cb.to_dict()
            for name, cb in _circuit_breakers.items()
        }


# ---------------------------------------------------------------------------
# Decorator for circuit breaker integration
# ---------------------------------------------------------------------------

F = TypeVar('F', bound=Callable[..., Any])

def with_circuit_breaker(
    circuit_name: str = "notion_api",
    on_open: Callable[[], Any] | None = None,
) -> Callable[[F], F]:
    """Decorator that adds circuit breaker protection to a function.
    
    Args:
        circuit_name: Name of the circuit breaker to use
        on_open: Optional callback when circuit is open (instead of raising)
    
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cb = get_circuit_breaker(circuit_name)
            
            if not cb.can_execute():
                # Circuit is open
                if on_open:
                    return on_open()
                raise CircuitBreakerOpenError(
                    f"Circuit '{circuit_name}' is OPEN. "
                    f"Notion API calls blocked until recovery."
                )
            
            try:
                result = func(*args, **kwargs)
                cb.record_success()
                return result
            except Exception as e:
                cb.record_failure()
                raise
        
        return wrapper  # type: ignore[return-value]
    
    return decorator


class CircuitBreakerOpenError(Exception):
    """Raised when a call is blocked by an open circuit breaker."""
    pass
