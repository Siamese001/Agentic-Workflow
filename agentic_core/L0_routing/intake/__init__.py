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
)
from agentic_core.L0_routing.intake.pipeline import IntakePipeline, IntakePolicy
from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode
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
    "AttachmentManifestEntry",
    "AttachmentManifestShell",
    "AuthVerdict",
    "IdempotencyStatus",
    "INGRESS_METRIC_NAMES",
    "IngressAuditRecord",
    "IngressEvent",
    "IngressEventRecord",
    "IngressReasonCode",
    "IntakePipeline",
    "IntakePolicy",
    "ModalityManifest",
    "NormalizationVerdict",
    "PrincipalType",
    "QuotaVerdict",
    "RawIngressEnvelope",
    "RejectedRequestNotice",
    "SchemaVerdict",
    "SourceClass",
    "ValidatedRequest",
]
