"""Runtime interceptor for REQ-270/273: Seam mutable reference enforcement.

Ensures all mutable references pass through immutable seams only.
"""

from __future__ import annotations

import dataclasses
import logging
from collections.abc import Hashable
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Track mutable reference violations
_mutable_ref_violations = []


class MutableReferenceError(RuntimeError):
    """Raised when a mutable reference is detected outside allowed seams."""

    pass


def assert_immutable_reference(obj: Any, context: str = "unknown") -> None:
    """Assert that an object is immutable or passes through allowed seam.

    Args:
        obj: Object to check for immutability
        context: Context description for error reporting

    Raises:
        MutableReferenceError: If object is mutable and not in allowed seam
    """
    if _is_mutable(obj):
        # Check if this is an allowed mutable type in seam context
        if not _is_allowed_mutable_in_seam(obj, context):
            violation = f"Mutable reference detected in {context}: {type(obj).__name__}"
            _mutable_ref_violations.append(violation)
            raise MutableReferenceError(violation)


def _is_mutable(obj: Any) -> bool:
    """Check if an object is mutable."""
    # Immutable built-in types
    if isinstance(obj, (int, float, str, bytes, bool, type(None))):
        return False

    # For tuples, check if they contain mutable elements
    if isinstance(obj, tuple):
        return any(_is_mutable(item) for item in obj)

    # For frozensets, check if they contain mutable elements
    if isinstance(obj, frozenset):
        return any(_is_mutable(item) for item in obj)

    # Hashable objects are generally immutable (but we've already checked tuples)
    if isinstance(obj, Hashable):
        try:
            hash(obj)  # Test hashability
            return False
        except TypeError:
            pass

    # Dataclasses with frozen=True are immutable
    if dataclasses.is_dataclass(obj) and getattr(obj, "__dataclass_params__", None).frozen:
        return False

    # Everything else is considered mutable
    return True


def _is_allowed_mutable_in_seam(obj: Any, context: str) -> bool:
    """Check if mutable object is allowed in specific seam context."""
    # Allowed contexts where mutable objects may pass
    allowed_contexts = {
        "capability_token",
        "sovereign_gateway",
        "embedding_factory",
        "trace_buffer",
        "telemetry",
    }

    # Check if context is allowed
    if any(allowed in context.lower() for allowed in allowed_contexts):
        return True

    # Specific allowed mutable types
    if hasattr(obj, "__class__"):
        class_name = obj.__class__.__name__
        allowed_classes = {
            "CapabilityTokenArtifact",
            "ExecutionTrace",
            "ForensicTraceBuffer",
            "TelemetryArtifact",
            "CognitiveDiff",
        }
        if class_name in allowed_classes:
            return True

    # Check if class name was set directly (for mocks)
    if hasattr(obj, "__name__"):
        if obj.__name__ in allowed_classes:
            return True

    return False


def get_mutable_ref_violations() -> list[str]:
    """Get list of recorded mutable reference violations."""
    return _mutable_ref_violations.copy()


def clear_mutable_ref_violations() -> None:
    """Clear recorded mutable reference violations."""
    _mutable_ref_violations.clear()


# Decorator for functions that must only handle immutable references
def immutable_references(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to enforce immutable references in function calls.

    Args:
        func: Function to decorate

    Returns:
        Wrapped function that checks arguments for mutability
    """

    def wrapper(*args, **kwargs) -> T:
        # Check positional arguments
        for i, arg in enumerate(args):
            assert_immutable_reference(arg, f"{func.__name__} arg {i}")

        # Check keyword arguments
        for key, value in kwargs.items():
            assert_immutable_reference(value, f"{func.__name__} kwarg {key}")

        return func(*args, **kwargs)

    return wrapper


# Context manager for tracking mutable reference violations
class MutableReferenceTracker:
    """Context manager for tracking mutable reference violations."""

    def __enter__(self) -> MutableReferenceTracker:
        clear_mutable_ref_violations()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass  # Violations preserved for inspection
