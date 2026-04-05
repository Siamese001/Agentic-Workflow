"""L5 Safety Layer — Safety governance and audit trails only.

This layer provides safety enforcement, policy validation, and audit trails.
No execution logic or agent orchestration belongs in this layer.
Only safety policies, guardrails, and audit utilities are exported.
"""
from enum import Enum
from typing import Any

# Sovereignty assertion: This layer contains NO agents with execute() methods
# Any agent classes belong in L2 (Execute) or L3 (Route) layers only
# P2/L5 Safety Audit exports
from agentic_core.L5_safety.enforcement.audit.safety_audit_emitter import (
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
from agentic_core.L5_safety.enforcement.audit.safety_audit_registry import (
    AuditQueryError,
    HumanReviewAuditError,
    HumanReviewAuditRecord,
    SafetyAuditMissingError,
    SafetyAuditRecord,
    SafetyAuditRegistry,
    get_safety_audit_registry,
    reset_safety_audit_registry,
)
from agentic_core.L5_safety.enforcement.escalation.escalation_orchestrator import (
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
from agentic_core.L5_safety.enforcement.escalation.escalation_orchestrator import (
    SafetyContext as EscalationSafetyContext,
)
from agentic_core.L5_safety.enforcement.escalation.escalation_orchestrator import (
    TraceContext as EscalationTraceContext,
)

# P3/L5 Human Safety Escalation exports
from agentic_core.L5_safety.enforcement.escalation.human_escalation import (
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
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

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
