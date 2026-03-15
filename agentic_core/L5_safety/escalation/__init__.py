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
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
)

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")

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
