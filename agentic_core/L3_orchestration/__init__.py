"""
L3 Orchestration Layer — Governed runtime orchestration with workflow visualization.

This layer provides orchestration, agent handoff, capability registry, and workflow visualization.
No cognition, routing, or execution logic belongs in this layer.
Only orchestration contracts, capability management, and visualization are exported.
"""
from enum import Enum

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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

from .contracts.agent_handoff import (  # noqa: F401
    HandoffDispatcher,
)
from .registry.capability_registry import (  # noqa: F401
    CapabilityDecision,
    CapabilityDecisionStore,
    CapabilityNotFoundError,
    CapabilityOwnership,
    CapabilityPermissionError,
    CapabilityRegistry,
    CapabilityRegistryEntry,
    CapabilityToken,
    ExclusiveCapabilityConflictError,
    RegistryVersionError,
    RunContext,
    UnregisteredAgentError,
    UnregisteredDispatchError,
    get_capability_decision_store,
    get_capability_registry,
    resolve_agent_for_capability,
)

_emit_records_execution_trace("p0", "evidence", "__init__")

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
