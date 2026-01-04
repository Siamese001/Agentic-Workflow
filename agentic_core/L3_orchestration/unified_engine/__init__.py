"""
Unified Workflow Engine Package

Consolidates 51 orchestrators into ~19 agents:
- 1 UnifiedWorkflowEngine (replaces 8 core engines)
- 10 Specialized Coordinators (replaces 35 overlapping agents)
- 8 Specialized Agents (kept as-is)
"""

from .execution_strategy import (
    ExecutionStrategy,
    ExecutionStatus,
    WorkflowContext,
    WorkflowResult,
    WorkflowStep,
    DAGStrategy,
    StateMachineStrategy,
    EventDrivenStrategy,
    ReactiveStrategy,
    get_strategy,
    STRATEGY_REGISTRY,
)

from .base_coordinator import (
    WorkflowCoordinator,
    CoordinatorCapability,
    CoordinatorRegistry,
    coordinator_registry,
)

from .unified_workflow_engine import (
    UnifiedWorkflowEngine,
    WorkflowMetrics,
    ErrorHandler,
    unified_engine,
)

from .coordinators import (
    RLCoordinator,
    TerritoryCoordinator,
    MCPCoordinator,
    MissionCoordinator,
    ModelCoordinator,
    HealthCoordinator,
    GovernanceCoordinator,
    UtilityCoordinator,
    CachingCoordinator,
    SecurityCoordinator,
    register_all_coordinators,
)

__all__ = [
    # Execution Strategies
    "ExecutionStrategy",
    "ExecutionStatus",
    "WorkflowContext",
    "WorkflowResult",
    "WorkflowStep",
    "DAGStrategy",
    "StateMachineStrategy",
    "EventDrivenStrategy",
    "ReactiveStrategy",
    "get_strategy",
    "STRATEGY_REGISTRY",
    # Coordinator Base
    "WorkflowCoordinator",
    "CoordinatorCapability",
    "CoordinatorRegistry",
    "coordinator_registry",
    # Unified Engine
    "UnifiedWorkflowEngine",
    "WorkflowMetrics",
    "ErrorHandler",
    "unified_engine",
    # Coordinators
    "RLCoordinator",
    "TerritoryCoordinator",
    "MCPCoordinator",
    "MissionCoordinator",
    "ModelCoordinator",
    "HealthCoordinator",
    "GovernanceCoordinator",
    "UtilityCoordinator",
    "CachingCoordinator",
    "SecurityCoordinator",
    "register_all_coordinators",
]
