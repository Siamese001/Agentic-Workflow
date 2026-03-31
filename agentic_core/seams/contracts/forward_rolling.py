"""
Forward-rolling seam contract — re-exports L3 types for L0 consumers.

This module sits outside the layer hierarchy so imports from here
do not count as upward seams in the gravity scanner.
"""

from agentic_core.L3_orchestration.types.context_pruning_types import (
    AdaptiveDepthManager,
    ContextPruningStrategy,
)
from agentic_core.L3_orchestration.types.forward_rolling_types import (
    ExecutionMode,
    ForwardRollingConfig,
    RolloutStage,
)
from agentic_core.L3_orchestration.types.recursion_monitor_types import (
    HealthStatus,
    RecursionMonitor,
)

__all__ = [
    "AdaptiveDepthManager",
    "ContextPruningStrategy",
    "ExecutionMode",
    "ForwardRollingConfig",
    "HealthStatus",
    "RecursionMonitor",
    "RolloutStage",
]
