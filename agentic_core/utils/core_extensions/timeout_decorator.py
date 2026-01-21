from __future__ import annotations

"""
Timeout decorator for autonomous agent healing.
Cross-platform: threading.Timer (works on Windows + Unix).
Canon Key 51 support — prevents hanging heal_repository() calls.
"""
import threading
from collections.abc import Callable
from functools import wraps
from typing import Any


class HealTimeoutError(Exception):
    """Raised when heal_repository() exceeds time limit."""

    pass


def timeout(seconds: int):
    """
    Decorator to enforce timeout on heal_repository() or any long method.
    Cross-platform using threading (works on Windows).

    Args:
        seconds: Maximum execution time in seconds

    Usage:
        @timeout(300)  # 5-minute limit
        def heal_repository(self, ...):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = [None]
            exception = [None]
            completed = threading.Event()

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
                finally:
                    completed.set()

            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()

            # Wait for completion or timeout
            completed.wait(timeout=seconds)

            if not completed.is_set():
                # Thread still running — timeout occurred
                raise HealTimeoutError(
                    f"{func.__name__} timed out after {seconds}s — "
                    f"consider splitting large operations or increasing limit"
                )

            if exception[0]:
                raise exception[0]

            return result[0]

        return wrapper

    return decorator
