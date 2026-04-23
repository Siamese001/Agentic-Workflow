"""Telemetry adapter for apps_eval.

Delegates all ``_emit_*`` / ``emit_*`` calls to the canonical SSOT at
``agentic_core.runtime.contracts.lifecycle_trace_contract`` when it is
importable, and falls back to a no-op shim otherwise. Standalone apps_eval
runs (without agentic_core on the path) continue to work — ``fail-open``.

This replaces the original pure-noop shim. Design goals:

* Zero behavior change for apps_eval callers — the 117-function API surface is
  identical (all functions take ``(*args, **kwargs)`` and return ``None``).
* When agentic_core is available, emits land on the real contract and flow
  into OTel spans, event ledger, etc.
* Lazy import: we do not import agentic_core at module-load time to preserve
  the original "resilient" property. The first real call attempts the import
  once and caches the result.

See ADR-028 §4.3 for the publisher-boundary context that motivated this.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Callable


class LayerSegment(StrEnum):
    """Layer identifier used by lifecycle trace emits.

    Kept at module top for standalone imports (e.g. ``from apps_eval._telemetry
    import LayerSegment``). Values match the canonical SSOT members exactly.
    """

    L0_ROUTING = "L0_ROUTING"
    L1_REASONING = "L1_REASONING"
    L2_EXECUTION = "L2_EXECUTION"
    L3_ORCHESTRATION = "L3_ORCHESTRATION"
    L4_STATE = "L4_STATE"
    L5_POLICY = "L5_POLICY"
    L6_OBSERVABILITY = "L6_OBSERVABILITY"


def _noop(*args: Any, **kwargs: Any) -> None:
    """Fallback used when the SSOT contract cannot be imported."""
    return None


# Lazy SSOT resolution. The module is resolved at most once per process; if the
# import fails (e.g. minimal apps_eval install), every emit permanently no-ops.
_SSOT_MODULE: Any = None
_SSOT_RESOLVED: bool = False


def _resolve_ssot() -> Any:
    global _SSOT_MODULE, _SSOT_RESOLVED
    if _SSOT_RESOLVED:
        return _SSOT_MODULE
    _SSOT_RESOLVED = True
    try:
        # guardian: allow-cross-layer-import -- L_APP -> agentic_core.runtime is
        # the documented lifecycle-trace SSOT boundary. Delegating the emit
        # surface is the whole point of this shim (see module docstring + ADR-028).
        from agentic_core.runtime.contracts import lifecycle_trace_contract as _m

        _SSOT_MODULE = _m
    except ImportError:
        _SSOT_MODULE = None
    return _SSOT_MODULE


_EMIT_CACHE: dict[str, Callable[..., None]] = {}


def __getattr__(name: str) -> Any:
    """Resolve ``_emit_*`` / ``emit_*`` via SSOT-then-noop; ``LayerSegment`` via local."""
    if name.startswith("_emit_") or name.startswith("emit_"):
        cached = _EMIT_CACHE.get(name)
        if cached is not None:
            return cached
        ssot = _resolve_ssot()
        resolved: Callable[..., None]
        if ssot is not None:
            resolved = getattr(ssot, name, _noop)
        else:
            resolved = _noop
        _EMIT_CACHE[name] = resolved
        return resolved
    raise AttributeError(name)
