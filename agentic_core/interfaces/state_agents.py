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

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Import from L3_orchestration where GravityStateAgent was moved
from agentic_core.L3_orchestration.reasoning.GravityStateAgent import GravityStateAgent

# Import from L4_state where the state components remain
from agentic_core.L4_state.reasoning.CachedStateLedger import CachedStateLedger
from agentic_core.L4_state.reasoning.CheckpointManager import CheckpointManager

__all__ = [
    "GravityStateAgent",
    "CachedStateLedger",
    "CheckpointManager",
]
