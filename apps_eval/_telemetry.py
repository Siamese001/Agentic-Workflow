"""Fail-open telemetry shim for apps_eval compatibility imports.

apps_eval is a deterministic harness, so this module does not own telemetry.
It lazily delegates ``emit_*`` and ``_emit_*`` calls to the core lifecycle trace
contract when available and otherwise returns no-op emitters.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Callable


class LayerSegment(StrEnum):
    """Enum-shaped layer labels matching the core lifecycle trace contract."""

    L0_ROUTING = "L0_ROUTING"
    L1_REASONING = "L1_REASONING"
    L2_EXECUTION = "L2_EXECUTION"
    L3_ORCHESTRATION = "L3_ORCHESTRATION"
    L4_STATE = "L4_STATE"
    L5_POLICY = "L5_POLICY"
    L6_OBSERVABILITY = "L6_OBSERVABILITY"


def _noop(*_args: Any, **_kwargs: Any) -> None:
    return None


def _resolve_emit(name: str) -> Callable[..., None]:
    try:
        from agentic_core.runtime.contracts import lifecycle_trace_contract as ssot
    except ImportError:
        resolved = _noop
    else:
        resolved = getattr(ssot, name, _noop)

    globals()[name] = resolved
    return resolved


def __getattr__(name: str) -> Callable[..., None]:
    if name.startswith("_emit_") or name.startswith("emit_"):
        return _resolve_emit(name)
    raise AttributeError(name)


__all__ = ["LayerSegment", "_noop"]
