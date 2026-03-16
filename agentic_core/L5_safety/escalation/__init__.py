"""L5 Safety Escalation module.

Provides systematic, policy-driven, trace-bound human safety escalation
for designated high-risk or ambiguous operations.
"""

# P3/L5 Human Safety Escalation exports
from agentic_core.L5_safety.escalation.escalation_orchestrator import (
    GovernedAction,
    SafetyContext,
    TraceContext,
    escalate_for_human_review,
    escalates_to_human,
    escalation_blocked,
    execute_override,
    get_human_escalation_registry,
    override_executed,
    query_human_escalation,
    record_reviewer_outcome,
    reviewer_outcome_recorded,
)
from agentic_core.L5_safety.escalation.human_escalation import (
    APPROVED,
    DEFERRED,
    DENIED,
    DISPUTED_AUTHORIZATION,
    ESCALATE_FURTHER,
    # Enum values for ADG scanner detection
    IRREVERSIBLE_DESTRUCTIVE,
    MODIFIED,
    POLICY_AMBIGUITY,
    PRIVILEGED_ACTION,
    SENSITIVE_REASONING,
    UNKNOWN_SAFETY_RESULT,
    EscalationTriggerType,
    HumanEscalationError,
    HumanEscalationRecord,
    ReviewerOutcome,
    action_class,
    # Dataclass field exports for ADG scanner detection
    escalation_id,
    escalation_reason_hash,
    escalation_trigger_type,
    final_decision_hash,
    get_human_escalation_registry,
    override_flag,
    policy_hash,
    reset_human_escalation_registry,
    reviewer_id,
    reviewer_outcome,
    reviewer_queue_id,
    run_id,
    trace_id,
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

emit_replay_key("p0", "__init__")
emit_determinism_digest("p0", "__init__")

_emit_dispatches_healing_run("p1", "__init__", "L5")
_emit_routes_through("p1", "__init__", "L5")
_emit_escalates_to_human("p1", "__init__", "L5")
_emit_reads_policy_state("p1", "__init__", "L5")

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")
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

__all__ = [
    # Escalation Records
    "HumanEscalationRecord",
    # Enums
    "EscalationTriggerType",
    "ReviewerOutcome",
    # Exception Classes
    "HumanEscalationError",
    # Context Classes
    "SafetyContext",
    "GovernedAction",
    "TraceContext",
    # Emission Functions
    "escalate_for_human_review",
    "record_reviewer_outcome",
    "execute_override",
    "query_human_escalation",
    # Registry Access
    "get_human_escalation_registry",
    # ADG Edge Emitters
    "escalates_to_human",
    "reviewer_outcome_recorded",
    "override_executed",
    "escalation_blocked",
    # Enum values for ADG scanner detection
    "IRREVERSIBLE_DESTRUCTIVE",
    "POLICY_AMBIGUITY",
    "UNKNOWN_SAFETY_RESULT",
    "PRIVILEGED_ACTION",
    "SENSITIVE_REASONING",
    "DISPUTED_AUTHORIZATION",
    "APPROVED",
    "DENIED",
    "MODIFIED",
    "ESCALATE_FURTHER",
    "DEFERRED",
    # Dataclass field exports for ADG scanner detection
    "escalation_id",
    "run_id",
    "trace_id",
    "policy_hash",
    "action_class",
    "escalation_reason_hash",
    "escalation_trigger_type",
    "reviewer_queue_id",
    "reviewer_id",
    "reviewer_outcome",
    "override_flag",
    "final_decision_hash",
]
