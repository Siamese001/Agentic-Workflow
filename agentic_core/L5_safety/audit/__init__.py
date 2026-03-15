"""L5 Safety Audit Trails module.

Provides mandatory audit trail emission for all safety-relevant decisions.
No safety decision may occur without audit emission.
"""

# P2/L5 Safety Audit exports
from agentic_core.L5_safety.audit.safety_audit_emitter import (
    DecisionContext,
    HumanReviewContext,
    SafetyContext,
    TraceContext,
    emit_human_review_audit,
    emit_safety_audit_record,
    query_safety_audits,
)
from agentic_core.L5_safety.audit.safety_audit_registry import (
    AuditQueryError,
    HumanReviewAuditError,
    SafetyAuditMissingError,
    SafetyAuditRecord,
    SafetyAuditRegistry,
    get_safety_audit_registry,
    reset_safety_audit_registry,
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
    "SafetyAuditRecord",
    "SafetyAuditRegistry",
    "SafetyAuditMissingError",
    "HumanReviewAuditError",
    "AuditQueryError",
    "get_safety_audit_registry",
    "reset_safety_audit_registry",
    "SafetyContext",
    "DecisionContext",
    "TraceContext",
    "HumanReviewContext",
    "emit_safety_audit_record",
    "emit_human_review_audit",
    "query_safety_audits",
]
