"""
agentic_core/interfaces/orchestration.py

Sovereign Orchestration interfaces for L1_cognition consumption.

Re-exports orchestration components so L1_cognition can
access routing and orchestration services without directly importing from L3_orchestration.

AUTHORITY CONSTRAINTS:
- Orchestration components provide routing and coordination services
- No direct execution authority through these interfaces
- All routing decisions are recorded for audit

USAGE (L1_cognition):
    from agentic_core.interfaces.orchestration_shim import (
        ActionRouter,
        # Add other orchestration components as needed
    )
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
    from agentic_core.L3_orchestration.reasoning.engines.action_router import ActionRouter
except ImportError as exc:
    ActionRouter = _MissingOptionalDependency("ActionRouter", str(exc))

__all__ = ["ActionRouter"]
