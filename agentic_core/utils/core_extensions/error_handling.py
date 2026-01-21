from __future__ import annotations

"""
Error Handling and Retry Utilities

Cluster: Exception classes and retry logic with exponential backoff
Lines: 253-316 from core_utils.py
"""
import time
from collections.abc import Callable
from typing import Any


# NAMING FIXED: MCPError → McpError
class McpError(Exception):
    """Base exception for MCP-related errors."""


# NAMING FIXED: CircuitBreakerOpenError → CircuitBreakerOpenError
class CircuitBreakerOpenError(MCPError):
    """Raised when circuit breaker is open."""


def _perform_single_attempt(func: Callable, *args, **kwargs) -> tuple[bool, Any, Exception | None]:
    """
    Helper to perform a single function call attempt and capture its result or exception.
    This helps reduce nesting depth in the retry_with_backoff decorator.
    """
    try:
        result = func(*args, **kwargs)
        return True, result, None
    except Exception as e:
        return False, None, e


def _execute_with_retries_internal(func: Callable, max_retries: int, base_delay: float,
                                   *args, **kwargs) -> tuple[bool, Any, Exception | None]:
    """
    Helper function to execute a function with retries and exponential backoff.
    Returns exceptions instead of raising them to allow the wrapper to handle the final raise.
    """
    for attempt in range(max_retries):
        success, result, exception = _perform_single_attempt(func, *args, **kwargs)

        if success:
            return True, result, None

        # If not successful and it's the last attempt, return the exception
        if attempt == max_retries - 1:
            return False, None, exception

        # Otherwise, delay and retry
        delay = base_delay * (2 ** attempt)
        time.sleep(delay)

    # This line is only reachable if max_retries is 0
    return False, None, None


def retry_with_backoff(func: Callable, max_retries: int = 3, base_delay: float = 1.0) -> Callable:
    """
    Retry decorator for MCP calls with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (doubles with each retry)

    Returns:
        Wrapped function with retry logic
    """
    def wrapper(*args, **kwargs):

        # Delegate the actual retry logic to the helper function
        success, result, exception = _execute_with_retries_internal(
            func, max_retries, base_delay, *args, **kwargs
        )

        if success:
            return result

        if exception:
            raise exception

        # This case handles max_retries = 0 where no success or exception occurred
        return None

    return wrapper
