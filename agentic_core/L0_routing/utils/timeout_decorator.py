"""
Canonical timeout decorator implementation.

This is the SSOT for the timeout decorator. All imports should use:
    from agentic_core.L0_routing.utils.timeout_decorator import timeout

Currently a placeholder pass-through decorator as timeout functionality
is not implemented in the current architecture.

Canonical location: agentic_core/L0_routing/utils/timeout_decorator.py
Backward-compat shim: agentic_core/L0_routing/utils/timeout_decorator_util.py
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

F = TypeVar("F", bound=Callable)


def timeout(seconds: int) -> Callable[[F], F]:
    """
    Timeout decorator for long-running operations.

    Currently a placeholder that returns the original function unchanged.
    Future implementations may add actual timeout enforcement.

    Args:
        seconds: Timeout duration in seconds (currently ignored).

    Returns:
        Decorator function that returns the original function unchanged.
    """

    def decorator(func: F) -> F:
        return func

    return decorator


__all__ = [
    "timeout",
]
