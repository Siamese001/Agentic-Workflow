"""L3 Orchestration Layer.

Phase 2 - Pillars 1 & 4: Layering Model + Workflow (DAGs)
Coordinates between cognitive and action planes with DAG-based workflow execution.
"""
import logging

LOGGER = logging.getLogger(__name__)

# Lazy imports to avoid hard dependency failures
try:
    from agentic_core.L3_orchestration.dag_engine import (
        DAGEngine,
        Task,
        TaskType,
        TaskStatus,
    )
except Exception as e:
    LOGGER.debug(f"DAGEngine not available: {e}")
    DAGEngine = None
    Task = None
    TaskType = None
    TaskStatus = None

try:
    from agentic_core.L3_orchestration.nervous_system import NervousSystem
except Exception as e:
    LOGGER.debug(f"NervousSystem not available: {e}")
    NervousSystem = None

try:
    from agentic_core.L3_orchestration.think_act_observe import (
        ThinkActObserveEngine,
        CycleConfig,
        CycleState,
    )
except Exception as e:
    LOGGER.debug(f"ThinkActObserveEngine not available: {e}")
    ThinkActObserveEngine = None
    CycleConfig = None
    CycleState = None

__all__ = [
    "NervousSystem",
    "DAGEngine",
    "Task",
    "TaskType",
    "TaskStatus",
    "ThinkActObserveEngine",
    "CycleConfig",
    "CycleState",
]
