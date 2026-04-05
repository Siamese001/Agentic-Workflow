"""
agentic_core/interfaces/spine.py

Sovereign spine interface for apps_* consumption.

Re-exports the L0/L2 spine components that apps_* spine adapters legitimately
need for wiring (AirlockAssembler, GovernedPayload, PathRouter, ExecutionOrchestrator,
ReEntryLoop).  These are structural wiring types only — no authority is granted.

AUTHORITY CONSTRAINTS:
- Apps_* may wire the spine but cannot bypass L0 routing authority
- No direct model resolution or tier selection
- No gateway instantiation (use agentic_core.interfaces.gateway instead)
- No mutation of routing state

USAGE (apps_*):
    from agentic_core.interfaces.spine import (
        AirlockAssembler,
        GovernedPayload,
        PathRouter,
        ExecutionOrchestrator,
        ReEntryLoop,
    )
"""

from __future__ import annotations

from agentic_core.L0_routing.engines.assembly_stage import AirlockAssembler, GovernedPayload
from agentic_core.L0_routing.engines.execution_orchestrator import ExecutionOrchestrator
from agentic_core.L0_routing.engines.path_router import PathRouter
from agentic_core.L2_execution.reentry_loop import ReEntryLoop

__all__ = ["AirlockAssembler", "GovernedPayload", "PathRouter", "ExecutionOrchestrator", "ReEntryLoop"]
