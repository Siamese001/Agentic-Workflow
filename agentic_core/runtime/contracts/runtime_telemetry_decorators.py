"""Declarative decorators for runtime telemetry that produce statically
introspectable ADG edges.

This module is the W4.2 skeleton landed under ADR-075. It introduces a
NEW way to declare side-effect emission that is:

  1. **Statically introspectable** — the decorator argument is the ADG edge
     declaration. The AST walker can produce an edge from the decorator
     without any runtime call.
  2. **Runtime-equivalent to inline _emit_*** — by default the decorator
     wraps the function with an OTEL emission (delegating to the existing
     ``lifecycle_trace_contract._emit_*`` functions). Same observable
     behavior as today.
  3. **Test-isolation friendly** — set ``EMITS_SUPPRESS=1`` in the
     environment to short-circuit the runtime emission while keeping the
     static declaration. No monkey-patch needed.

Usage:

    from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
        emits_side_effect,
        appends_hash_chain,
    )

    @emits_side_effect("decision_packet_write")
    def write_decision(packet: DecisionPacket) -> None:
        ...

    @appends_hash_chain("evidence_register")
    def append_evidence(entry: EvidenceEntry) -> str:
        ...

Static introspection from anywhere with a function reference:

    >>> write_decision.__adg_side_effects__
    ('decision_packet_write',)
    >>> emits_for(write_decision)
    {'side_effect': ('decision_packet_write',), 'hash_chain': ()}

This module is **additive** — existing ``_emit_*`` inline calls continue to
work unchanged. The migration plan (ADR-075 §"Migration Plan") will
incrementally convert the unconditional, top-of-function cases.

Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (W4.2)
ADR: docs/architecture/adr/ADR-075-split-runtime-telemetry-from-adg-edges.md
"""
from __future__ import annotations

import functools
import logging
import os
from typing import Any, Callable, TypeVar

_LOGGER = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


# Intent attributes attached to decorated functions. These are the static
# ADG-edge declarations and are read by the AST walker (and any code that
# wants to introspect a function's declared side effects).
_INTENT_ATTRS: tuple[str, ...] = (
    "__adg_side_effects__",
    "__adg_hash_chain__",
    "__adg_telemetry_events__",
)


def _suppress_runtime_emission() -> bool:
    """True when EMITS_SUPPRESS is truthy — used by tests for isolation."""
    val = os.environ.get("EMITS_SUPPRESS", "").strip().lower()
    return val in ("1", "true", "yes", "on")


def _set_intent(func: Callable[..., Any], attr: str, value: str) -> None:
    """Append `value` to the tuple at `attr` on `func` (idempotent on repeats)."""
    current: tuple[str, ...] = getattr(func, attr, ())
    if value in current:
        return
    setattr(func, attr, current + (value,))


def emits_side_effect(kind: str) -> Callable[[F], F]:
    """Declare that the decorated function emits a side effect of `kind`.

    The decoration is the ADG-edge declaration. At runtime, the wrapper
    delegates to the existing ``_emit_emits_side_effect`` function unless
    ``EMITS_SUPPRESS=1`` is set (test mode).
    """
    if not isinstance(kind, str) or not kind:
        raise ValueError(f"emits_side_effect requires a non-empty str kind, got {kind!r}")

    def decorator(func: F) -> F:
        _set_intent(func, "__adg_side_effects__", kind)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not _suppress_runtime_emission():
                _emit_runtime("side_effect", kind, func.__qualname__)
            return func(*args, **kwargs)

        # Mirror the intent attribute onto the wrapper so introspection on
        # the decorated form (which is what callers see) returns the truth.
        for attr in _INTENT_ATTRS:
            if hasattr(func, attr):
                setattr(wrapper, attr, getattr(func, attr))
        return wrapper  # type: ignore[return-value]

    return decorator


def appends_hash_chain(chain_id: str) -> Callable[[F], F]:
    """Declare that the decorated function appends to an immutable hash chain.

    Used by audit-trail-critical paths (e.g. underwriting decision packets,
    evidence register entries). The static declaration is queryable; the
    runtime emission is suppressible in tests.
    """
    if not isinstance(chain_id, str) or not chain_id:
        raise ValueError(f"appends_hash_chain requires a non-empty str chain_id, got {chain_id!r}")

    def decorator(func: F) -> F:
        _set_intent(func, "__adg_hash_chain__", chain_id)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not _suppress_runtime_emission():
                _emit_runtime("hash_chain", chain_id, func.__qualname__)
            return func(*args, **kwargs)

        for attr in _INTENT_ATTRS:
            if hasattr(func, attr):
                setattr(wrapper, attr, getattr(func, attr))
        return wrapper  # type: ignore[return-value]

    return decorator


def emits_telemetry_event(event_name: str) -> Callable[[F], F]:
    """Declare that the decorated function emits a named telemetry event.

    Less specific than ``emits_side_effect`` — used for general-purpose
    telemetry events that don't fit a more specific category.
    """
    if not isinstance(event_name, str) or not event_name:
        raise ValueError(f"emits_telemetry_event requires a non-empty str event_name, got {event_name!r}")

    def decorator(func: F) -> F:
        _set_intent(func, "__adg_telemetry_events__", event_name)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not _suppress_runtime_emission():
                _emit_runtime("telemetry_event", event_name, func.__qualname__)
            return func(*args, **kwargs)

        for attr in _INTENT_ATTRS:
            if hasattr(func, attr):
                setattr(wrapper, attr, getattr(func, attr))
        return wrapper  # type: ignore[return-value]

    return decorator


def emits_for(func: Callable[..., Any]) -> dict[str, tuple[str, ...]]:
    """Return the static intent declarations for a decorated function.

    Returns a dict with keys ``side_effect``, ``hash_chain``,
    ``telemetry_event`` and tuple values. Any function (decorated or not)
    can be passed; undeclared keys return empty tuples.
    """
    return {
        "side_effect": tuple(getattr(func, "__adg_side_effects__", ())),
        "hash_chain": tuple(getattr(func, "__adg_hash_chain__", ())),
        "telemetry_event": tuple(getattr(func, "__adg_telemetry_events__", ())),
    }


def _emit_runtime(category: str, kind: str, qualname: str) -> None:
    """Internal — bridge to the existing ``_emit_records_telemetry_event``.

    The ADG edge kinds (``emits_side_effect``, ``appends_hash_chain``,
    etc.) are produced by the AST walker recognizing decorator patterns —
    NOT by separate runtime functions. So all three categories funnel into
    the single generic telemetry-event sink, with category encoded in the
    ``source`` and ``event`` arguments.

    Fail-soft per constitutional §28-style discipline: telemetry must never
    break the wrapped function. If the runtime emission backend is
    unreachable, log debug and proceed.
    """
    try:
        from agentic_core.runtime.contracts.lifecycle_trace_contract import (  # noqa: PLC0415
            _emit_records_telemetry_event,
        )

        # signature: (root_trace_id, source, event, **kwargs)
        # We don't have a root_trace_id at decoration scope; use the qualname
        # as the source-correlation key. Real call sites that need a trace_id
        # will continue to use inline _emit_records_execution_trace.
        _emit_records_telemetry_event(qualname, category, kind)
    except Exception:  # guardian: allow-broad-catch -- telemetry must never break callers; ADR-075
        _LOGGER.debug(
            "runtime telemetry emit failed: %s/%s in %s",
            category, kind, qualname, exc_info=True,
        )


__all__ = [
    "appends_hash_chain",
    "emits_for",
    "emits_side_effect",
    "emits_telemetry_event",
]
