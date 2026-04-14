"""
agentic_core/interfaces/routing_types.py

Sovereign routing types interface for apps_* consumption.

Re-exports L0 routing type definitions so apps_* reasoning files
can import from the approved interface boundary (TYPE_CHECKING use).

AUTHORITY CONSTRAINTS:
- Type re-exports only — no routing authority granted
- No access to routing logic or tier selection

USAGE (apps_*):
    from agentic_core.interfaces.routing_types_shim import ReasoningIntensityProfile
"""

from __future__ import annotations


class _MissingOptionalDependency:
    def __init__(self, symbol: str, reason: str) -> None:
        self._symbol = symbol
        self._reason = reason

    def __getattr__(self, attr: str):
        raise ModuleNotFoundError(f"{self._symbol} is unavailable because {self._reason}")

    def __call__(self, *args, **kwargs):
        raise ModuleNotFoundError(f"{self._symbol} is unavailable because {self._reason}")


try:
    from agentic_core.L0_routing.types.reasoning_intensity_types import ReasoningIntensityProfile
except ImportError as exc:
    ReasoningIntensityProfile = _MissingOptionalDependency("ReasoningIntensityProfile", str(exc))

__all__ = ["ReasoningIntensityProfile"]
