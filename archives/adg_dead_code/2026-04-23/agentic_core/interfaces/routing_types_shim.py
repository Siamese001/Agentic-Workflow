"""
agentic_core/interfaces/routing_types_shim.py

Sovereign routing types interface shim for apps_* consumption.
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
