"""
validators/GovernanceAgent.py — backward-compat re-export shim.

Canonical implementation lives at:
    agentic_core.L5_safety.reasoning.GovernanceAgent

This file is a pure re-export stub with NO mutation logic of its own.
All writes_to / healing operations are in reasoning/GovernanceAgent.py
(L5 healer territory, which correctly uses write_gateway).

ADG fix: A-07 (dedup) + A-01 (validators/ mutation boundary).
"""

from __future__ import annotations

from agentic_core.L5_safety.reasoning.GovernanceAgent import (
    DependencyGraph,
    GovernanceAgent,
    heal,
)

__all__ = ["DependencyGraph", "GovernanceAgent", "heal"]
