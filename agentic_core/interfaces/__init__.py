"""Agentic Core Interfaces - Strictly-typed architecture definitions.

This module provides Protocol-based interfaces and dataclass types for
the agentic framework, replacing temporary Any fallbacks with real types.
"""

from agentic_core.interfaces.execution import (
    ExecutionContext,
    ExecutionResult,
    ExecutionPhase,
)
from agentic_core.interfaces.planes import (
    ICognitivePlane,
    IActionPlane,
    IOrchestrator,
)
from agentic_core.interfaces.requests import (
    ActionRequest,
    PlanningRequest,
    PlanningResult,
)
from agentic_core.interfaces.config import (
    OrchestratorConfig,
)

__all__ = [
    # Execution
    "ExecutionContext",
    "ExecutionResult",
    "ExecutionPhase",
    # Planes
    "ICognitivePlane",
    "IActionPlane",
    "IOrchestrator",
    # Requests
    "ActionRequest",
    "PlanningRequest",
    "PlanningResult",
    # Config
    "OrchestratorConfig",
]
