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
        GravityStateAgent,
        CachedStateLedger,
        CheckpointManager,
    )
"""

from __future__ import annotations

from agentic_core.L3_orchestration.reasoning.GravityStateAgent import GravityStateAgent
from agentic_core.L4_state.reasoning.CachedStateLedger import CachedStateLedger
from agentic_core.L4_state.reasoning.CheckpointManager import CheckpointManager

__all__ = ["GravityStateAgent", "CachedStateLedger", "CheckpointManager"]
