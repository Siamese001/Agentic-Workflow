"""L1 Cognition Layer — Propose-only cognitive processing.

This layer provides cognitive processing, pattern recognition, and reasoning.
No execution, routing, or persistence logic belongs in this layer.
Only cognitive interfaces, reasoning engines, and telemetry are exported.
"""

# Cognitive interfaces and reasoning
from agentic_core.L1_cognition.knowledge.knowledge_orchestrator import (
    EvaluationResult,
    ReasoningContext,
    ReasoningTrace,
    capture_reasoning_pattern,
    get_pattern_recommendations,
    pattern_stored,
    pattern_validated,
    pattern_versioned,
    query_reasoning_patterns,
    reasoning_pattern_captured,
    reasoning_pattern_reused,
    reuse_outcome_recorded,
    reuse_reasoning_pattern,
    validate_reasoning_pattern,
)

# P4/L1 Reasoning Knowledge Base exports
from agentic_core.L1_cognition.knowledge.reasoning_knowledge import (
    ReasoningKnowledgeError,
    ReasoningKnowledgeRecord,
    get_reasoning_knowledge_registry,
    originating_trace_id,
    outcome_quality_score,
    pattern_version,
    reasoning_context_hash,
    reasoning_goal_hash,
    # Dataclass field exports for ADG scanner detection
    reasoning_pattern_id,
    reasoning_steps_hash,
    reuse_count,
    validation_status,
)
from agentic_core.L1_cognition.planning.plan_creator import (
    PlanningPolicy,
    ReasoningPlanContext,
    create_reasoning_plan,
    create_simple_reasoning_plan,
    enforce_plan_checkpoint,
    execute_plan_step,
    plan_checkpoint_enforced,
    plan_revision_recorded,
    plan_step_executed,
    query_reasoning_plans,
    reasoning_plan_emitted,
    record_plan_revision,
)

# P3/L1 Multi-Step Reasoning Planning exports
from agentic_core.L1_cognition.planning.reasoning_plan import (
    CheckpointResult,
    PlanCheckpoint,
    PlanRevision,
    PlanStatus,
    PlanStep,
    ReasoningPlan,
    ReasoningPlanError,
    StepStatus,
    get_plan_registry,
    reset_plan_registry,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "__init__", "execution_auth")
_emit_validates_capability("p2", "__init__", "capability_check")
_emit_routes_to_capability("p2", "__init__", "capability_route")
_emit_writes_via_uwg("p2", "__init__", "uwg_write")
_emit_blocks_direct_write("p2", "__init__", "direct_write_block")
_emit_records_tool_invocation("p2", "__init__", "tool_invocation")
_emit_captures_execution_output("p2", "__init__", "exec_output")
_emit_dispatches_agent("p3", "__init__", "agent_dispatch")
_emit_coordinates_agents("p3", "__init__", "agent_coordination")
_emit_records_workflow_lineage("p3", "__init__", "workflow_lineage")
_emit_records_healing_outcome("p3", "__init__", "healing_outcome")
_emit_escalates_failure("p3", "__init__", "failure_escalation")
_emit_orchestrates_workflow("p3", "__init__", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "__init__", "healing_dispatch")
_emit_invokes_evaluation("p3", "__init__", "evaluation_signal")
_emit_records_telemetry_event("p4", "__init__", "telemetry_event")
_emit_captures_evaluation_metric("p4", "__init__", "eval_metric")
_emit_stores_embedding("p4", "__init__", "embedding_store")
_emit_updates_meta_learning_state("p4", "__init__", "meta_learning")
_emit_links_execution_to_snapshot("p4", "__init__", "exec_snapshot_link")
from .types.action_request_types import (  # noqa: F401
    ActionRequest,
    ActionResult,
    PlanningRequest,
    PlanningResult,
)

emit_replay_key("p0", "__init__")
emit_determinism_digest("p0", "__init__")

_emit_dispatches_healing_run("p1", "__init__", "L1")
_emit_routes_through("p1", "__init__", "L1")
_emit_escalates_to_human("p1", "__init__", "L1")
_emit_reads_policy_state("p1", "__init__", "L1")

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")

__all__ = [
    # Action Types
    "ActionRequest",
    "ActionResult",
    "PlanningRequest",
    "PlanningResult",
    # Plan Records
    "ReasoningPlan",
    "PlanStep",
    "PlanCheckpoint",
    "PlanRevision",
    # Enums
    "PlanStatus",
    "StepStatus",
    "CheckpointResult",
    # Exception Classes
    "ReasoningPlanError",
    # Registry Access
    "get_plan_registry",
    "reset_plan_registry",
    # Context Classes
    "ReasoningPlanContext",
    "PlanningPolicy",
    # Emission Functions
    "create_reasoning_plan",
    "execute_plan_step",
    "enforce_plan_checkpoint",
    "record_plan_revision",
    "query_reasoning_plans",
    "create_simple_reasoning_plan",
    # ADG Edge Emitters
    "reasoning_plan_emitted",
    "plan_step_executed",
    "plan_checkpoint_enforced",
    "plan_revision_recorded",
    # Reasoning Knowledge Records
    "ReasoningKnowledgeRecord",
    # Reasoning Knowledge Exception Classes
    "ReasoningKnowledgeError",
    # Reasoning Knowledge Registry Access
    "get_reasoning_knowledge_registry",
    # Reasoning Knowledge Context Classes
    "ReasoningTrace",
    "EvaluationResult",
    "ReasoningContext",
    # Reasoning Knowledge Functions
    "capture_reasoning_pattern",
    "query_reasoning_patterns",
    "reuse_reasoning_pattern",
    "get_pattern_recommendations",
    "validate_reasoning_pattern",
    # Reasoning Knowledge ADG Edge Emitters
    "reasoning_pattern_captured",
    "pattern_validated",
    "pattern_versioned",
    "pattern_stored",
    "reuse_outcome_recorded",
    "reasoning_pattern_reused",
    # Reasoning Knowledge Dataclass field exports for ADG scanner detection
    "reasoning_pattern_id",
    "originating_trace_id",
    "reasoning_goal_hash",
    "reasoning_context_hash",
    "reasoning_steps_hash",
    "outcome_quality_score",
    "reuse_count",
    "pattern_version",
    "validation_status",
]

# Sovereignty assertion: This layer contains NO execution or routing logic
# L1 may only propose actions; execution belongs to L2, routing to L3
