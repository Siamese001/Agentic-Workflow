"""
L4 Resilience module.

Provides resilience and fault-tolerance capabilities.
"""
from typing import Any, Dict, Optional, Callable
import logging
import functools

logger = logging.getLogger(__name__)


from enum import Enum

class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


def get_breaker(name: str = "default") -> "CircuitBreaker":
    """Get or create a named circuit breaker."""
    if not hasattr(get_breaker, "_breakers"):
        get_breaker._breakers = {}
    if name not in get_breaker._breakers:
        get_breaker._breakers[name] = CircuitBreaker()
    return get_breaker._breakers[name]


class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(self, failure_threshold: int = 5, reset_timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self._failure_count = 0
        self._state = CircuitBreakerState.CLOSED
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self._state == "open":
            raise RuntimeError("Circuit breaker is open")
        try:
            result = func(*args, **kwargs)
            self._failure_count = 0
            return result
        except Exception as e:
            self._failure_count += 1
            if self._failure_count >= self.failure_threshold:
                self._state = "open"
            raise


class RetryPolicy:
    """Retry policy for resilient operations."""
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0):
        self.max_retries = max_retries
        self.delay = delay
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry policy."""
        import time
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    time.sleep(self.delay)
        raise last_error


def resilient(max_retries: int = 3, circuit_breaker: bool = False):
    """Decorator for resilient function execution."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            policy = RetryPolicy(max_retries=max_retries)
            return policy.execute(func, *args, **kwargs)
        return wrapper
    return decorator


__all__ = ['CircuitBreaker', 'CircuitBreakerState', 'CircuitBreakerOpenError', 'get_breaker', 'RetryPolicy', 'resilient']
