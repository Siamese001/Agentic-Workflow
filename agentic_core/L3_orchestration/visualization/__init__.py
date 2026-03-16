"""L3 Orchestration Visualization module.

Provides operational visibility for runtime workflow progress as a
queryable, stage-aware orchestration graph.
"""

# P3/L3 Workflow Visualization exports
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
from agentic_core.L3_orchestration.visualization.visualization_updater import (
    get_workflow_visualization_registry as get_updater_registry,
)
from agentic_core.L3_orchestration.visualization.visualization_updater import (
    reset_workflow_visualization_registry as reset_updater_registry,
)
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
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "__init__")
emit_determinism_digest("p0", "__init__")

_emit_dispatches_healing_run("p1", "__init__", "L3")
_emit_routes_through("p1", "__init__", "L3")
_emit_escalates_to_human("p1", "__init__", "L3")
_emit_reads_policy_state("p1", "__init__", "L3")

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")

__all__ = [
    # Visualization Records
    "WorkflowVisualizationRecord",
    "WorkflowStageModel",
    # Enums
    "WorkflowStatus",
    "StageTransitionReason",
    # Exception Classes
    "WorkflowVisualizationError",
    # Context Classes
    "WorkflowVisualizationContext",
    # Emission Functions
    "update_workflow_visualization",
    "record_stage_transition",
    "record_owner_transition",
    "record_workflow_completion",
    "query_workflow_visualization",
    # Registry Access
    "get_workflow_visualization_registry",
    "reset_workflow_visualization_registry",
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
