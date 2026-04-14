"""
Timeout decorator for execution time limits.

This module provides a timeout decorator to prevent functions from running
indefinitely. It's used across the agentic system for safety and reliability.
"""

from __future__ import annotations

import signal
from functools import wraps
from threading import current_thread, main_thread, Thread
from typing import Any, Callable


class TimeoutError(Exception):
    """Raised when function execution exceeds timeout limit."""

    pass


def timeout(seconds: int) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to limit function execution time.

    Args:
        seconds: Maximum execution time in seconds

    Returns:
        Decorated function that raises TimeoutError if execution exceeds limit

    Note:
        Only works on Unix-like systems with signal module.
        On Windows, the function will execute without timeout.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if seconds <= 0:
                msg = "seconds must be greater than zero"
                raise ValueError(msg)

            if not hasattr(signal, "SIGALRM") or current_thread() is not main_thread():
                return func(*args, **kwargs)

            def _handle_timeout(signum: int, frame: Any) -> None:
                raise TimeoutError(f"Function {func.__name__} timed out after {seconds} seconds")

            old_handler = signal.getsignal(signal.SIGALRM)
            if old_handler == signal.SIG_IGN:
                return func(*args, **kwargs)
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                return func(*args, **kwargs)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

        return wrapper

    return decorator


__all__ = ["timeout", "TimeoutError"]
