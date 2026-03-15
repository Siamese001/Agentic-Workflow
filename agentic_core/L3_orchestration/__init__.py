"""
L3 Orchestration Layer — Governed runtime orchestration with workflow visualization.

This layer provides orchestration, agent handoff, capability registry, and workflow visualization.
No cognition, routing, or execution logic belongs in this layer.
Only orchestration contracts, capability management, and visualization are exported.
"""

# Orchestration contracts and capability registry
from agentic_core.L3_orchestration.visualization.visualization_updater import (
    WorkflowVisualizationContext,
    owner_transition_recorded,
    query_workflow_visualization,
    record_owner_transition,
    record_stage_transition,
    record_workflow_completion,
    stage_transition_recorded,
    update_workflow_visualization,
    workflow_completed_recorded,
    workflow_visualization_emitted,
)

# P3/L3 Workflow Visualization exports
from agentic_core.L3_orchestration.visualization.workflow_visualization import (
    # Enum values for ADG scanner detection
    ACTIVE,
    BLOCK_DETECTED,
    BLOCKED,
    COMPLETED,
    ESCALATED,
    ESCALATION_TRIGGERED,
    FAILED,
    NORMAL_TRANSITION,
    RETRY_TRIGGERED,
    RETRYING,
    WORKFLOW_ERROR,
    StageTransitionReason,
    WorkflowStageModel,
    WorkflowStatus,
    WorkflowVisualizationError,
    WorkflowVisualizationRecord,
    get_workflow_visualization_registry,
    reset_workflow_visualization_registry,
)

from .contracts.agent_handoff import (  # noqa: F401
    CapabilityDecision,
    CapabilityNotFoundError,
    CapabilityPermissionError,
    CapabilityToken,
    ExclusiveCapabilityConflictError,
    HandoffDispatcher,
    RegistryVersionError,
    UnregisteredAgentError,
    UnregisteredDispatchError,
    get_capability_decision_store,
    get_capability_registry,
    resolve_agent_for_capability,
)
from .registry.capability_registry import (  # noqa: F401
    CapabilityDecisionStore,
    CapabilityOwnership,
    CapabilityRegistry,
    CapabilityRegistryEntry,
    RunContext,
)

__all__ = [
    # Orchestration Contracts
    "HandoffDispatcher",
    "CapabilityToken",
    "CapabilityDecision",
    "CapabilityNotFoundError",
    "CapabilityPermissionError",
    "UnregisteredAgentError",
    "ExclusiveCapabilityConflictError",
    "RegistryVersionError",
    "UnregisteredDispatchError",
    "resolve_agent_for_capability",
    "get_capability_registry",
    "get_capability_decision_store",
    # Capability Registry
    "CapabilityRegistry",
    "CapabilityRegistryEntry",
    "CapabilityOwnership",
    "CapabilityDecisionStore",
    "RunContext",
    # Visualization Records
    "WorkflowVisualizationRecord",
    "WorkflowStageModel",
    # Enums
    "WorkflowStatus",
    "StageTransitionReason",
    # Exception Classes
    "WorkflowVisualizationError",
    # Registry Access
    "get_workflow_visualization_registry",
    "reset_workflow_visualization_registry",
    # Context Classes
    "WorkflowVisualizationContext",
    # Emission Functions
    "update_workflow_visualization",
    "record_stage_transition",
    "record_owner_transition",
    "record_workflow_completion",
    "query_workflow_visualization",
    # ADG Edge Emitters
    "workflow_visualization_emitted",
    "stage_transition_recorded",
    "owner_transition_recorded",
    "workflow_completed_recorded",
    # Enum values for ADG scanner detection
    "ACTIVE",
    "BLOCKED",
    "RETRYING",
    "ESCALATED",
    "COMPLETED",
    "FAILED",
    "NORMAL_TRANSITION",
    "RETRY_TRIGGERED",
    "ESCALATION_TRIGGERED",
    "BLOCK_DETECTED",
    "WORKFLOW_ERROR",
]

# Sovereignty assertion: This layer contains NO cognition or routing logic
# L3 may only orchestrate governed actions; cognition belongs to L1, routing to L0
