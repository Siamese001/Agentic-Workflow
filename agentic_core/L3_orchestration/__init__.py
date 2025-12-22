"""L3 Orchestration Layer.

Phase 2 - Pillars 1 & 4: Layering Model + Workflow (DAGs)
Coordinates between cognitive and action planes with DAG-based workflow execution.
"""
import re

import logging

LOGGER = logging.getLogger(__name__)

# Lazy imports to avoid hard dependency failures
try:
    from agentic_core.L3_orchestration.dag_engine import (
        DAGEngine,
        Task,
        TaskStatus,
        TaskType,
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
        CycleConfig,
        CycleState,
        ThinkActObserveEngine,
    )
except Exception as e:
    LOGGER.debug(f"ThinkActObserveEngine not available: {e}")
    ThinkActObserveEngine = None
    CycleConfig = None
    CycleState = None

try:
    from agentic_core.L3_orchestration.canon_scheduler import (
        CanonSwarmScheduler,
        IntelligentOrchestrator,
        SwarmScheduler,
    )
except Exception as e:
    LOGGER.debug(f"CanonSwarmScheduler not available: {e}")
    CanonSwarmScheduler = None
    SwarmScheduler = None
    IntelligentOrchestrator = None

try:
    from agentic_core.L3_orchestration.mission_runner import (
        GITPYTHON_AVAILABLE,
        WATCHDOG_AVAILABLE,
        WEBSOCKETS_AVAILABLE,
        run_daemon_mode,
        run_standard_mode,
        run_surgical_mode,
    )
except Exception as e:
    LOGGER.debug(f"mission_runner not available: {e}")
    run_daemon_mode = None
    run_surgical_mode = None
    run_standard_mode = None
    WATCHDOG_AVAILABLE = False
    WEBSOCKETS_AVAILABLE = False
    GITPYTHON_AVAILABLE = False

try:
    from agentic_core.L3_orchestration.intervention_server import (
        FASTAPI_AVAILABLE,
        approval_event,
        reset_approval_event,
        start_intervention_server,
        wait_for_approval,
    )
except Exception as e:
    LOGGER.debug(f"intervention_server not available: {e}")
    start_intervention_server = None
    approval_event = None
    FASTAPI_AVAILABLE = False
    wait_for_approval = None
    reset_approval_event = None

try:
    from agentic_core.L3_orchestration.fission_manager import FissionManager
except Exception as e:
    LOGGER.debug(f"FissionManager not available: {e}")
    FissionManager = None

try:
    from agentic_core.L3_orchestration.fission_executor import apply_fission_blueprint
except Exception as e:
    LOGGER.debug(f"apply_fission_blueprint not available: {e}")
    apply_fission_blueprint = None

__all__ = [
    "NervousSystem",
    "DAGEngine",
    "Task",
    "TaskType",
    "TaskStatus",
    "ThinkActObserveEngine",
    "CycleConfig",
    # Canon Scheduler
    "CanonSwarmScheduler",
    "SwarmScheduler",
    "IntelligentOrchestrator",
    # Intervention Server
    "start_intervention_server",
    "approval_event",
    "FASTAPI_AVAILABLE",
    "wait_for_approval",
    "reset_approval_event",
    # Mission Runner
    "run_daemon_mode",
    "run_surgical_mode",
    "run_standard_mode",
    "WATCHDOG_AVAILABLE",
    "WEBSOCKETS_AVAILABLE",
    "GITPYTHON_AVAILABLE",
    "CycleState",
    # Fission Components
    "FissionManager",
    "apply_fission_blueprint",
]
