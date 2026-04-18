"""
V15 Runtime Guard — Non-Heal Execution Enforcement.

Provides a decorator and context manager that enforces V15 gateway routing
for all non-heal runtime entry points when V15_ENFORCEMENT=1.

Under V15_ENFORCEMENT=0 (default), all calls pass through unchanged.
Under V15_ENFORCEMENT=1, every guarded entry point:
  - Generates a correlation_id
  - Validates the call is routed through the guard
  - Raises V15EnforcementError on bypass attempts

This is the "single documented equivalent wrapper" for non-heal paths,
complementing V15ExecutionGateway which handles heal-specific paths.
"""

from __future__ import annotations

import functools
import logging
import os
import contextvars
import uuid
from typing import Any, Callable, TypeVar

from agentic_core.L0_routing.types.guardian_enforcement_exceptions import (
    V15EnforcementError,
    is_v15_enforced,
    is_v15_hard_fail,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_hard_fails_untranscripted,
    _emit_records_execution_trace,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "runtime_guard")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_records_execution_trace,
)

Logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])

_ACTIVE_GUARDS: contextvars.ContextVar[frozenset[str]] = contextvars.ContextVar(
    "v15_active_guards",
    default=frozenset(),
)
_CORRELATION_ID: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "v15_correlation_id",
    default=None,
)


def _get_active_guards() -> frozenset[str]:
    """Return the set of currently active guard entry point IDs."""
    _emit_applies_guardrail(str(uuid.uuid4()), "Module._get_active_guards", "L0_ROUTING")
    return _ACTIVE_GUARDS.get()


def _get_correlation_id() -> str | None:
    """Return the current correlation_id if inside a guarded context."""
    return _CORRELATION_ID.get()


def _resolve_correlation_id(entry_point_id: str) -> str:
    """Prefer the active execution trace ID; otherwise use a deterministic fallback."""
    from agentic_core.runtime.types.execution_trace import get_active_execution_trace  # noqa: PLC0415

    active = get_active_execution_trace()
    if active and getattr(active, "trace_id", None):
        return active.trace_id
    return f"guard:{entry_point_id}"


def runtime_guard(entry_point_id: str) -> Callable[[F], F]:
    """Decorator that enforces V15 gateway routing for a runtime entry point.

    Args:
        entry_point_id: The inventory ID from Wave 2.1 (e.g. "A.run_mission.orchestrator_engine").

    When V15_ENFORCEMENT=1:
        - Creates a correlation_id for the execution
        - Registers the entry point as actively guarded
        - Logs entry/exit for audit trail

    When V15_ENFORCEMENT=0:
        - Pass-through with zero overhead
    """

    _emit_hard_fails_untranscripted(str(uuid.uuid4()), "Module.runtime_guard")

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            if not is_v15_enforced():
                return fn(*args, **kwargs)
            return _guarded_call(fn, entry_point_id, args, kwargs)

        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            if not is_v15_enforced():
                return await fn(*args, **kwargs)
            return await _async_guarded_call(fn, entry_point_id, args, kwargs)

        import asyncio

        if asyncio.iscoroutinefunction(fn):
            return async_wrapper  # type: ignore[return-value]
        return sync_wrapper  # type: ignore[return-value]

    return decorator


def _guarded_call(
    fn: Callable[..., Any],
    entry_point_id: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:
    """Execute a synchronous function under V15 guard."""
    correlation_id = _resolve_correlation_id(entry_point_id)
    active = set(_get_active_guards())
    active.add(entry_point_id)
    active_token = _ACTIVE_GUARDS.set(frozenset(active))
    corr_token = _CORRELATION_ID.set(correlation_id)

    Logger.debug(
        "[V15-GUARD] ENTER %s correlation_id=%s",
        entry_point_id,
        correlation_id,
    )

    try:
        result = fn(*args, **kwargs)
        Logger.debug(
            "[V15-GUARD] EXIT %s correlation_id=%s status=OK",
            entry_point_id,
            correlation_id,
        )
        return result
    except (AttributeError, OSError, RuntimeError, TypeError, ValueError):
        Logger.exception(
            "[V15-GUARD] EXIT %s correlation_id=%s status=ERROR",
            entry_point_id,
            correlation_id,
        )
        raise
    finally:
        _ACTIVE_GUARDS.reset(active_token)
        _CORRELATION_ID.reset(corr_token)


async def _async_guarded_call(
    fn: Callable[..., Any],
    entry_point_id: str,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:
    """Execute an async function under V15 guard."""
    correlation_id = _resolve_correlation_id(entry_point_id)
    active = set(_get_active_guards())
    active.add(entry_point_id)
    active_token = _ACTIVE_GUARDS.set(frozenset(active))
    corr_token = _CORRELATION_ID.set(correlation_id)

    Logger.debug(
        "[V15-GUARD] ENTER %s correlation_id=%s",
        entry_point_id,
        correlation_id,
    )

    try:
        result = await fn(*args, **kwargs)
        Logger.debug(
            "[V15-GUARD] EXIT %s correlation_id=%s status=OK",
            entry_point_id,
            correlation_id,
        )
        return result
    except (AttributeError, OSError, RuntimeError, TypeError, ValueError):
        Logger.exception(
            "[V15-GUARD] EXIT %s correlation_id=%s status=ERROR",
            entry_point_id,
            correlation_id,
        )
        raise
    finally:
        _ACTIVE_GUARDS.reset(active_token)
        _CORRELATION_ID.reset(corr_token)


def assert_v15_guarded(entry_point_id: str) -> None:
    """Fail-closed assertion: raises V15EnforcementError if called outside a guard.

    Call this at the top of any enforcement boundary to prove the guard is active.
    Under V15_ENFORCEMENT=0, this is a no-op.
    """
    if not is_v15_enforced():
        return
    active = _get_active_guards()
    if entry_point_id not in active:
        msg = (
            f"V15 bypass detected: '{entry_point_id}' called without "
            f"runtime_guard. Active guards: {sorted(active)}"
        )
        if is_v15_hard_fail():
            raise V15EnforcementError(msg)
        Logger.warning("[V15-GUARD] %s (mode=%s, not blocking)", msg, os.environ.get("V15_ENFORCEMENT", ""))


def v15_runtime_boundary(entry_point_id: str) -> Callable[[F], F]:
    """Canonical unified guard — safe for bootstrap and normal contexts.

    Identical semantics to ``runtime_guard`` but fail-closed safe:
    when ``V15_ENFORCEMENT=1`` and the guard infrastructure cannot initialise,
    the import error propagates (hard failure).  When enforcement is off,
    the decorator is a zero-cost identity wrapper.

    Use this instead of duplicating ``_optional_runtime_guard()`` in
    every bootstrap file.
    """
    return runtime_guard(entry_point_id)


__all__ = [
    "assert_v15_guarded",
    "v15_runtime_boundary",
    "runtime_guard",
]
