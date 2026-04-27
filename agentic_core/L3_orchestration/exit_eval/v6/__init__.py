"""Exit Evaluation & Control — v6 surface.

Implements the spec at
``docs/reference/05_Exit_Evaluation_&_Control/05_Live_Runtime_Exit_Control_&_Evaluation_v6.md``.

Coexists with the v4/v5 modules at ``agentic_core/L3_orchestration/exit_eval/``;
v6 is the SSOT for the spec sections it covers (5.0/5.1 preflight, X1A-J,
X2 aggregate, X3A-E packet builders, HITL H1-H4 + L5 re-clearance).

Production wiring into composition roots is intentionally out of scope —
see plan ``exit-eval-v6-gaps-d7a3f1.md``.
"""

from __future__ import annotations

from agentic_core.L3_orchestration.exit_eval.v6.grader_composition import (
    ABSTAIN_REASON_CODE,
    GATE_COMPOSITION_MODE,
    BusPRow,
    CompositionMode,
    CompositionResult,
    DimensionScore,
    GraderClass,
    Rubric,
    RubricDimension,
    compose,
)
from agentic_core.L3_orchestration.exit_eval.v6.hardening import (
    FAULT_INJECTION_CODES,
    FAULT_INJECTION_DISPOSITION_HINT,
    PASS_K_INSUFFICIENT_HISTORY_REASON,
    PASS_K_THRESHOLD_TABLE,
    FaultInjectionReasonCode,
    is_fault_injection_code,
    pass_k_observed,
    pass_k_required_p,
)
from agentic_core.L3_orchestration.exit_eval.v6.hitl import (
    H1_FREEZE_FIELDS,
    FreezeReceipt,
    HITLDecision,
    HITLPacket,
    HITLVerdict,
    HumanDecisionReceipt,
    HumanReviewPacket,
    L5ReclearanceRequest,
    L5ReclearanceResult,
    build_freeze_receipt,
    build_human_decision_receipt,
    build_human_review_packet,
    build_l5_reclearance_request,
    materialize_review_packet,
    run_l5_reclearance,
)
from agentic_core.L3_orchestration.exit_eval.v6.otel import (
    EXIT_V6_SPAN_CATALOG,
    REQUIRED_ATTRIBUTES,
    SpanRecord,
    collected_span_names,
    missing_required_attributes,
    record_span,
    span,
)
from agentic_core.L3_orchestration.exit_eval.v6.return_payload import (
    RETURN_PAYLOAD_FAILURE_CODES,
    ReturnPayload,
    RuntimeBoundaryStatus,
    RuntimeExhaustManifest,
    build_return_payload,
    close_runtime_boundary,
    enqueue_l6_handoff,
    seal_runtime_exhaust,
    validate_return_payload,
)
from agentic_core.L3_orchestration.exit_eval.v6.preflight import (
    IMMEDIATE_FAIL_CODES,
    PreflightFailure,
    classify_source,
    normalize_to_packet,
    validate_required_receipts,
)
from agentic_core.L3_orchestration.exit_eval.v6.types import (
    ExitReviewPacket,
    GateResult,
    GateVerdict,
    SourceType,
    V6Disposition,
    X3DenyPacket,
    X3EscalatePacket,
    X3CommitRequestPacket,
    X3AllowPacket,
    X3SafeAbstainPacket,
    X3BreakGlassAllowPacket,
)
from agentic_core.L3_orchestration.exit_eval.v6.x1_gates import (
    GATE_EVALUATORS,
    eval_x1a,
    eval_x1b,
    eval_x1c,
    eval_x1d,
    eval_x1e,
    eval_x1f,
    eval_x1g,
    eval_x1h,
    eval_x1i,
    eval_x1j,
    run_all_x1_gates,
)
from agentic_core.L3_orchestration.exit_eval.v6.x2_matrix import (
    AggregateDecision,
    aggregate_decision,
)
from agentic_core.L3_orchestration.exit_eval.v6.pipeline import (
    ExitEvalPipeline,
    ExitEvalResult,
    run_exit_eval,
)
from agentic_core.L3_orchestration.exit_eval.v6.rollback import (
    NoopRollbackHandler,
    RollbackOutcome,
    RollbackPlan,
    RollbackResult,
    RollbackStep,
    SequentialRollbackExecutor,
)
from agentic_core.L3_orchestration.exit_eval.v6.sqlite_ledger import SqliteLedger
from agentic_core.L3_orchestration.exit_eval.v6.uwg import (
    UwgBackends,
    UwgError,
    UwgOutcome,
    UwgReceipt,
    default_backends,
    process_commit_request,
)
from agentic_core.L3_orchestration.exit_eval.v6.x3_dispositions import (
    BreakGlassValidationError,
    build_x3a_deny,
    build_x3b_escalate,
    build_x3c_commit_request,
    build_x3d_allow,
    build_x3e_safe_abstain,
    build_x3f_break_glass_allow,
    build_x3_packet,
)

__all__ = [
    # types
    "ExitReviewPacket",
    "GateResult",
    "GateVerdict",
    "SourceType",
    "V6Disposition",
    "X3DenyPacket",
    "X3EscalatePacket",
    "X3CommitRequestPacket",
    "X3AllowPacket",
    "X3SafeAbstainPacket",
    "X3BreakGlassAllowPacket",
    # preflight
    "IMMEDIATE_FAIL_CODES",
    "PreflightFailure",
    "classify_source",
    "normalize_to_packet",
    "validate_required_receipts",
    # x1
    "GATE_EVALUATORS",
    "eval_x1a",
    "eval_x1b",
    "eval_x1c",
    "eval_x1d",
    "eval_x1e",
    "eval_x1f",
    "eval_x1g",
    "eval_x1h",
    "eval_x1i",
    "eval_x1j",
    "run_all_x1_gates",
    # x2
    "AggregateDecision",
    "aggregate_decision",
    # x3
    "build_x3a_deny",
    "build_x3b_escalate",
    "build_x3c_commit_request",
    "build_x3d_allow",
    "build_x3e_safe_abstain",
    "build_x3f_break_glass_allow",
    "build_x3_packet",
    "BreakGlassValidationError",
    # hitl
    "H1_FREEZE_FIELDS",
    "FreezeReceipt",
    "HITLDecision",
    "HITLPacket",
    "HITLVerdict",
    "HumanDecisionReceipt",
    "HumanReviewPacket",
    "L5ReclearanceRequest",
    "L5ReclearanceResult",
    "build_freeze_receipt",
    "build_human_decision_receipt",
    "build_human_review_packet",
    "build_l5_reclearance_request",
    "materialize_review_packet",
    "run_l5_reclearance",
    # otel (5.8)
    "EXIT_V6_SPAN_CATALOG",
    "REQUIRED_ATTRIBUTES",
    "SpanRecord",
    "collected_span_names",
    "missing_required_attributes",
    "record_span",
    "span",
    # return / exhaust (5.7)
    "RETURN_PAYLOAD_FAILURE_CODES",
    "ReturnPayload",
    "RuntimeBoundaryStatus",
    "RuntimeExhaustManifest",
    "build_return_payload",
    "close_runtime_boundary",
    "enqueue_l6_handoff",
    "seal_runtime_exhaust",
    "validate_return_payload",
    # uwg
    "UwgBackends",
    "UwgError",
    "UwgOutcome",
    "UwgReceipt",
    "default_backends",
    "process_commit_request",
    # ledger
    "SqliteLedger",
    # rollback
    "NoopRollbackHandler",
    "RollbackOutcome",
    "RollbackPlan",
    "RollbackResult",
    "RollbackStep",
    "SequentialRollbackExecutor",
    # pipeline
    "ExitEvalPipeline",
    "ExitEvalResult",
    "run_exit_eval",
    # hardening (Wave 2: H5/H6/H8)
    "FAULT_INJECTION_CODES",
    "FAULT_INJECTION_DISPOSITION_HINT",
    "PASS_K_INSUFFICIENT_HISTORY_REASON",
    "PASS_K_THRESHOLD_TABLE",
    "FaultInjectionReasonCode",
    "is_fault_injection_code",
    "pass_k_observed",
    "pass_k_required_p",
    # grader composition (Wave 3)
    "ABSTAIN_REASON_CODE",
    "GATE_COMPOSITION_MODE",
    "BusPRow",
    "CompositionMode",
    "CompositionResult",
    "DimensionScore",
    "GraderClass",
    "Rubric",
    "RubricDimension",
    "compose",
]
