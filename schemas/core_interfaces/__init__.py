"""Core architectural interfaces for Agentic Workflow.

Phase 2 - Pillar 1: Layering Model (Architectural Refactor)
Defines strict boundaries between Brain (cognitive) and Hands (action).
"""

    ICognitivePlane,
    PlanningRequest,
    PlanningResult,
    CognitiveCapability,
)
    IActionPlane,
    ActionRequest,
    ActionResult,
    ActionCapability,
)
    IOrchestrator,
    OrchestratorConfig,
    ExecutionContext,
    ExecutionResult,
    ExecutionPhase,
)

__all__ = [
    "ICognitivePlane",
    "PlanningRequest",
    "PlanningResult",
    "CognitiveCapability",
    "IActionPlane",
    "ActionRequest",
    "ActionResult",
    "ActionCapability",
    "IOrchestrator",
    "OrchestratorConfig",
    "ExecutionContext",
    "ExecutionResult",
    "ExecutionPhase",
]
