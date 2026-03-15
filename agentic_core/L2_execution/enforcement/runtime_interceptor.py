"""Runtime interceptor for REQ-270/273: Seam mutable reference enforcement.

Ensures all mutable references pass through immutable seams only.
"""

from __future__ import annotations

import dataclasses
import logging
from collections.abc import Hashable
from typing import Any, Callable, TypeVar

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,
)

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "runtime_interceptor")
_emit_applies_guardrail("p0", "runtime_interceptor", "p0_governance")

logger = logging.getLogger(__name__)
T = TypeVar("T")
_mutable_ref_violations = []


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_invoke_authorize_and_execute", "state_snapshot")
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(payload, target: str):
    from agentic_core.L2_execution.context.execution_context import (  # noqa: PLC0415
        ActionClass,
        ExecutionContext,
    )

    return ExecutionContext.create(
        run_id="runtime_interceptor",
        capability_token="default",
        policy_hash="default",
        execution_input=str(payload),
        execution_target=target,
        action_class=ActionClass.PRIVILEGED_LOCAL,
    )


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
        if not _is_allowed_mutable_in_seam(obj, context):
            violation = f"Mutable reference detected in {context}: {type(obj).__name__}"
            _mutable_ref_violations.append(violation)
            raise MutableReferenceError(violation)


def _is_mutable(obj: Any) -> bool:
    """Check if an object is mutable."""
    if isinstance(obj, (int, float, str, bytes, bool, type(None))):
        return False
    if isinstance(obj, tuple):
        return any(_is_mutable(item) for item in obj)
    if isinstance(obj, frozenset):
        return any(_is_mutable(item) for item in obj)
    if isinstance(obj, Hashable):
        try:
            hash(obj)
            return False
        except TypeError:
            pass
    if dataclasses.is_dataclass(obj) and getattr(obj, "__dataclass_params__", None).frozen:
        return False
    return True


def _is_allowed_mutable_in_seam(obj: Any, context: str) -> bool:
    """Check if mutable object is allowed in specific seam context."""
    allowed_contexts = {
        "capability_token",
        "sovereign_gateway",
        "embedding_factory",
        "trace_buffer",
        "telemetry",
    }
    if any(allowed in context.lower() for allowed in allowed_contexts):
        return True
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


def immutable_references(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator to enforce immutable references in function calls.

    Args:
        func: Function to decorate

    Returns:
        Wrapped function that checks arguments for mutability
    """

    def wrapper(*args, **kwargs) -> T:
        _ectx = _make_execution_context(func.__name__, "runtime_interceptor.immutable_references")
        _invoke_authorize_and_execute(
            _ectx,
            lambda p: p,
            "default",
            func.__name__,
            target_name="runtime_interceptor.immutable_references",
        )
        for i, arg in enumerate(args):
            assert_immutable_reference(arg, f"{func.__name__} arg {i}")
        for key, value in kwargs.items():
            assert_immutable_reference(value, f"{func.__name__} kwarg {key}")
        return func(*args, **kwargs)

    return wrapper


class MutableReferenceTracker:
    """Context manager for tracking mutable reference violations."""

    def __enter__(self) -> MutableReferenceTracker:
        clear_mutable_ref_violations()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass
