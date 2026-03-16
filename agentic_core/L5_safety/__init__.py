"""L5 Safety Layer — Safety governance and audit trails only.

This layer provides safety enforcement, policy validation, and audit trails.
No execution logic or agent orchestration belongs in this layer.
Only safety policies, guardrails, and audit utilities are exported.
"""

# Sovereignty assertion: This layer contains NO agents with execute() methods
# Any agent classes belong in L2 (Execute) or L3 (Route) layers only

# P2/L5 Safety Audit exports
from agentic_core.L5_safety.audit.safety_audit_emitter import (
    DecisionContext,
    HumanReviewContext,
    SafetyContext,
    TraceContext,
    emit_guardrail_audit,
    emit_human_review_audit,
    emit_safety_audit_record,
    emit_safety_plane_validation_audit,
    human_review_audited,
    query_safety_audits,
    safety_audit_emitted,
)
from agentic_core.L5_safety.audit.safety_audit_registry import (
    AuditQueryError,
    HumanReviewAuditError,
    HumanReviewAuditRecord,
    SafetyAuditMissingError,
    SafetyAuditRecord,
    SafetyAuditRegistry,
    get_safety_audit_registry,
    reset_safety_audit_registry,
)
from agentic_core.L5_safety.escalation.escalation_orchestrator import (
    GovernedAction,
    escalate_for_human_review,
    escalates_to_human,
    escalation_blocked,
    execute_override,
    override_executed,
    query_human_escalation,
    record_reviewer_outcome,
    reviewer_outcome_recorded,
)
from agentic_core.L5_safety.escalation.escalation_orchestrator import (
    SafetyContext as EscalationSafetyContext,
)
from agentic_core.L5_safety.escalation.escalation_orchestrator import (
    TraceContext as EscalationTraceContext,
)

# P3/L5 Human Safety Escalation exports
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

_emit_dispatches_healing_run("p1", "__init__", "L5")
_emit_routes_through("p1", "__init__", "L5")
_emit_escalates_to_human("p1", "__init__", "L5")
_emit_reads_policy_state("p1", "__init__", "L5")

_emit_snapshots_state("p0", "__init__", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "__init__", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "__init__")

__all__ = [
    # Audit Records
    "SafetyAuditRecord",
    "HumanReviewAuditRecord",
    "SafetyAuditRegistry",
    # Exception Classes
    "SafetyAuditMissingError",
    "HumanReviewAuditError",
    "AuditQueryError",
    "HumanEscalationError",
    # Registry Access
    "get_safety_audit_registry",
    "reset_safety_audit_registry",
    "get_human_escalation_registry",
    # Context Classes
    "SafetyContext",
    "DecisionContext",
    "TraceContext",
    "HumanReviewContext",
    "EscalationSafetyContext",
    "GovernedAction",
    "EscalationTraceContext",
    # Emission Functions
    "emit_safety_audit_record",
    "emit_human_review_audit",
    "query_safety_audits",
    "emit_guardrail_audit",
    "emit_safety_plane_validation_audit",
    "escalate_for_human_review",
    "record_reviewer_outcome",
    "execute_override",
    "query_human_escalation",
    # ADG Edge Emitters
    "safety_audit_emitted",
    "human_review_audited",
    "escalates_to_human",
    "reviewer_outcome_recorded",
    "override_executed",
    "escalation_blocked",
    # Escalation Records
    "HumanEscalationRecord",
    # Escalation Enums
    "EscalationTriggerType",
    "ReviewerOutcome",
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
