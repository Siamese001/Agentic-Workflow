"""
agentic_core/interfaces/state_agents.py

Sovereign State Agent interfaces for L1_cognition consumption.

Re-exports state agents and related components so L1_cognition can
access state management without directly importing from L4_state.

AUTHORITY CONSTRAINTS:
- State agents provide persistence and state management only
- No execution authority through these interfaces
- State operations are recorded for audit and replay

USAGE (L1_cognition):
    from agentic_core.interfaces.state_agents import (
        CachedStateLedger,
        CheckpointManager,
    )

NOTE (2026-04-24 W3.2): GravityStateAgent removed from re-export. The class is
a DEPRECATED delegating shim whose canonical replacement is
agentic_core.L3_orchestration.utils.gravity_state_util. Import directly from
the util module for state gravity operations.

Defensive imports: matches the ``routing_types.py`` /
``orchestration.py`` pattern. If an L4 dependency cannot be loaded
(e.g., a transitive ``agentic_core.runtime.types.anomaly_report``
miss), the symbol becomes a fail-fast stub instead of crashing every
caller of this interface module at import time.
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
    from agentic_core.L4_state.reasoning.CachedStateLedger import CachedStateLedger
except ImportError as exc:
    CachedStateLedger = _MissingOptionalDependency("CachedStateLedger", str(exc))

try:
    from agentic_core.L4_state.reasoning.CheckpointManager import CheckpointManager
except ImportError as exc:
    CheckpointManager = _MissingOptionalDependency("CheckpointManager", str(exc))

__all__ = ["CachedStateLedger", "CheckpointManager"]
