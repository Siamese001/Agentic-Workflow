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
