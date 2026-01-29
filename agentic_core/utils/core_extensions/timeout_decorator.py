"""
Timeout decorator for agent methods.

Provides timeout functionality to prevent methods from running indefinitely.
"""

from __future__ import annotations

import functools
import logging
import signal
from typing import Any, TypeVar, cast
from collections.abc import Callable

Logger = logging.getLogger(__name__)

# Type variable for decorated functions
F = TypeVar("F", bound=Callable[..., Any])


def timeout(seconds: int = 300):
    """
    Decorator that adds a timeout to a method.

    Args:
        seconds: Timeout in seconds (default: 300)

    Returns:
        Decorated function that will raise TimeoutError if it runs too long

    Usage:
        @timeout(60)
        def my_method(self):
            # Method that should complete within 60 seconds
            pass
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            # Define the timeout handler
            def _handle_timeout(signum: int, frame: Any) -> None:
                raise TimeoutError(f"Method {func.__name__} timed out after {seconds} seconds")

            # Set up the timeout signal
            old_handler = signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)

            try:
                result = func(self, *args, **kwargs)
                return result
            finally:
                # Clean up: restore old handler and cancel alarm
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

        return cast(F, wrapper)

    return decorator


# For Windows systems where SIGALRM is not available
def timeout_windows(seconds: int = 300):
    """
    Windows-compatible timeout decorator using threading.

    Args:
        seconds: Timeout in seconds (default: 300)

    Returns:
        Decorated function that will raise TimeoutError if it runs too long
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            import threading

            result = None
            exception = None

            def worker():
                nonlocal result, exception
                try:
                    result = func(self, *args, **kwargs)
                except Exception as e:
                    exception = e

            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()
            thread.join(seconds)

            if thread.is_alive():
                Logger.warning(f"Method {func.__name__} timed out after {seconds} seconds")
                raise TimeoutError(f"Method {func.__name__} timed out after {seconds} seconds")

            if exception:
                raise exception

            return result

        return cast(F, wrapper)

    return decorator


# Platform-specific timeout
import platform

if platform.system() == "Windows":
    timeout = timeout_windows  # type: ignore


__all__ = [
    "timeout",
    "timeout_windows",
]
