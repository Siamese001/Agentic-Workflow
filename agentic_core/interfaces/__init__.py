"""Agentic Core Interfaces - Strictly-typed architecture definitions.

This module provides Protocol-based interfaces and dataclass types for
the agentic framework, replacing temporary Any fallbacks with real types.
"""
# Standard library imports
import re
from typing import Any, Optional, Protocol, Dict, List

# Local project imports
from .config import (
    OrchestratorConfig,
)
from .execution import (
    ExecutionContext,
    ExecutionPhase,
    ExecutionResult,
)
from .planes import (
    IActionPlane,
    ICognitivePlane,
    IOrchestrator,
)
from .requests import (
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