"""Agentic Core Interfaces - Strictly-typed architecture definitions.

This module provides Protocol-based interfaces and dataclass types for
the agentic framework, replacing temporary Any fallbacks with real types.
"""
# Standard library imports
import re
from typing import Any, Optional, Protocol, Dict, List

# Local project imports
from agentic_core.L1_cognition.P1_interfaces.config import (
    OrchestratorConfig,
)
from agentic_core.L1_cognition.P1_interfaces.execution import (
    ExecutionContext,
    ExecutionPhase,
    ExecutionResult,
)
from agentic_core.L1_cognition.P1_interfaces.planes import (
    IActionPlane,
    ICognitivePlane,
    IOrchestrator,
)
from agentic_core.L1_cognition.P1_interfaces.requests import (
    ActionRequest,
    PlanningRequest,
    PlanningResult,
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