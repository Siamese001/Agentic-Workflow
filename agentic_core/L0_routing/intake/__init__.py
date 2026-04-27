"""
L0 Request Intake — Front-Desk Envelope Check
==============================================

Implements the [1] REQUEST INTAKE + ENVELOPE CHECK subsystem per
docs/reference/01_Request_Intake/01_request_intake.md.

This layer is deliberately mechanical. It validates the envelope, normalizes
the slip, and stamps a bounded request slip that L1 may read. It does NOT
interpret semantic intent, route, retrieve, execute tools, or mutate state.

CORE LAW
--------
- Intake may normalize the envelope.
- Intake may reject malformed / unauthorized / over-limit packets.
- Intake may stamp identity, tenancy, source class, and trace metadata.
- Intake may NOT interpret the user's semantic goal beyond shape + safety.
- Intake may NOT plan, route, retrieve, answer, call a model for task work,
  call a tool, ask L3 to orchestrate, or mutate L4.

PASS  = validated_request for L1.
FAIL  = structural rejection / refill request.
There is NO third path where Intake quietly performs work.
"""

from agentic_core.L0_routing.intake.correlation import (
    TraceReplayBindingResult,
    bind_trace_and_replay,
)
from agentic_core.L0_routing.intake.doctrine_contracts import (
    DoctrineContractBundle,
    IngressDataBoundaryMap,
    InjectionTriageReceipt,
    IntakeIdempotencyReceipt,
    IntakeTraceReceipt,
    QuotedContentLabelReceipt,
    UserContentAuthorityReceipt,
)
from agentic_core.L0_routing.intake.envelope import (
    AttachmentManifestEntry,
    AttachmentManifestShell,
    ModalityManifest,
    RawIngressEnvelope,
)
from agentic_core.L0_routing.intake.events import (
    INGRESS_METRIC_NAMES,
    IngressEvent,
    IngressEventRecord,
    to_otel_attributes,
)
from agentic_core.L0_routing.intake.handoff import (
    IngressRejectionReport,
    IntakeAuditReceipt,
    IntakeFinalResult,
    IntakeStageResults,
    L1HandoffEnvelope,
    finalize_intake_handoff,
)
from agentic_core.L0_routing.intake.origin_labels import (
    AUTHORITY_LABELS,
    ORIGIN_LABELS,
    SECURITY_FINDING_CLASSES,
    IngressOriginLabelManifest,
    PayloadSecurityFinding,
    build_origin_label_manifest,
)
from agentic_core.L0_routing.intake.pipeline import (
    IntakeOutcome,
    IntakePipeline,
    IntakePolicy,
    IntakeReceiptBundle,
    run_request_intake,
)
from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode
from agentic_core.L0_routing.intake.receipts import (
    DUPLICATE_CLASSES,
    CallerIdentityClaim,
    CallerScopeBaseline,
    DuplicateRequestFingerprint,
    DuplicateSuppressionReceipt,
    IngressReplaySeed,
    IntakeManifestHash,
    MalformedEnvelopeReport,
    NormalizedRequestHash,
    NormalizedUserPayload,
    QuotaReceipt,
    RequestCorrelationReceipt,
    RequestSchemaValidationReceipt,
    SessionBindingReceipt,
    TenantBoundaryReceipt,
    TransportEnvelopeReceipt,
)
from agentic_core.L0_routing.intake.status import (
    REJECTED_STATUSES,
    STAGE_TO_REJECTION_STATUS,
    IntakeStatus,
)
from agentic_core.L0_routing.intake.validated_request import (
    IngressAuditRecord,
    RejectedRequestNotice,
    ValidatedRequest,
)
from agentic_core.L0_routing.intake.verdicts import (
    AuthVerdict,
    IdempotencyStatus,
    NormalizationVerdict,
    PrincipalType,
    QuotaVerdict,
    SchemaVerdict,
    SourceClass,
)

__all__ = [
    "AUTHORITY_LABELS",
    "AttachmentManifestEntry",
    "AttachmentManifestShell",
    "AuthVerdict",
    "CallerIdentityClaim",
    "CallerScopeBaseline",
    "DUPLICATE_CLASSES",
    "DoctrineContractBundle",
    "DuplicateRequestFingerprint",
    "DuplicateSuppressionReceipt",
    "IngressDataBoundaryMap",
    "IdempotencyStatus",
    "INGRESS_METRIC_NAMES",
    "IngressAuditRecord",
    "IngressEvent",
    "IngressEventRecord",
    "IngressOriginLabelManifest",
    "IngressReasonCode",
    "IngressRejectionReport",
    "IngressReplaySeed",
    "InjectionTriageReceipt",
    "IntakeAuditReceipt",
    "IntakeFinalResult",
    "IntakeIdempotencyReceipt",
    "IntakeManifestHash",
    "IntakeOutcome",
    "IntakePipeline",
    "IntakePolicy",
    "IntakeReceiptBundle",
    "IntakeStageResults",
    "IntakeStatus",
    "IntakeTraceReceipt",
    "L1HandoffEnvelope",
    "MalformedEnvelopeReport",
    "ModalityManifest",
    "NormalizationVerdict",
    "NormalizedRequestHash",
    "NormalizedUserPayload",
    "ORIGIN_LABELS",
    "PayloadSecurityFinding",
    "PrincipalType",
    "QuotaReceipt",
    "QuotaVerdict",
    "QuotedContentLabelReceipt",
    "RawIngressEnvelope",
    "REJECTED_STATUSES",
    "RejectedRequestNotice",
    "RequestCorrelationReceipt",
    "RequestSchemaValidationReceipt",
    "SECURITY_FINDING_CLASSES",
    "STAGE_TO_REJECTION_STATUS",
    "SchemaVerdict",
    "SessionBindingReceipt",
    "SourceClass",
    "TenantBoundaryReceipt",
    "TraceReplayBindingResult",
    "TransportEnvelopeReceipt",
    "UserContentAuthorityReceipt",
    "ValidatedRequest",
    "bind_trace_and_replay",
    "build_origin_label_manifest",
    "finalize_intake_handoff",
    "run_request_intake",
    "to_otel_attributes",
]
