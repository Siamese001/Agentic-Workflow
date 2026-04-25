"""
ValidatedRequest, RejectedRequestNotice, IngressAuditRecord.

Spec section: E6 STAMPING THE TICKET (lines 440-497) and INGRESS OUTPUT
CONTRACT (lines 499-554).

INVARIANT: A ValidatedRequest carries NO route, NO answer, NO retrieval
result, NO prompt, NO tool authority, NO write capability. Its
`downstream_authority` is permanently `"none"` and `permitted_next_layer`
is `"L1"` only when all required gates passed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from agentic_core.L0_routing.intake.envelope import (
    AttachmentManifestShell,
    ModalityManifest,
)
from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode
from agentic_core.L0_routing.intake.verdicts import (
    AuthVerdict,
    IdempotencyStatus,
    NormalizationVerdict,
    PrincipalType,
    QuotaVerdict,
    SchemaVerdict,
    SourceClass,
)


# ----------------------------------------------------------------------
# Field-level forbidden-content guard
# ----------------------------------------------------------------------

# Per spec lines 535-551 (INGRESS OUTPUT CONTRACT — MUST NOT INCLUDE).
# We never expose these names on the validated_request struct itself.
# Tests assert this denylist.
FORBIDDEN_VALIDATED_REQUEST_KEYS: frozenset[str] = frozenset(
    {
        "final_answer",
        "route_decision",
        "proposed_route",
        "route_confidence",
        "retrieval_result",
        "evidence_chunks",
        "cited_spans",
        "prompt_packet",
        "tool_call",
        "model_execution_result",
        "l2_artifact",
        "l3_workflow_graph",
        "mutation_proposal",
        "capability_token",
        "uwg_commit_request",
    }
)


@dataclass(frozen=True)
class ValidatedRequest:
    """Bounded slip handed to L1 when intake passes.

    Stamped by E6. Contains identity, quota, schema, normalization verdicts,
    plus normalized + raw payload references and trace metadata. Does NOT
    contain semantic interpretation, route decision, or capability tokens.
    """

    # --- core identifiers ---
    request_id: str
    session_id: str
    trace_root: str

    # --- timing / origin ---
    ingress_time_unix: float
    received_at_iso: str
    source_channel: str
    source_class: SourceClass

    # --- identity ---
    tenant_bind: str | None
    workspace_bind: str | None
    principal_type: PrincipalType
    principal_id: str | None
    auth_verdict: AuthVerdict
    caller_scope_baseline: str  # e.g. "user:standard", "service:internal", "anonymous:limited"
    region_scope_baseline: str | None
    baseline_entitlements: tuple[str, ...]

    # --- quota / dedupe ---
    quota_verdict: QuotaVerdict
    quota_bucket: str
    rate_window_state: str
    dedupe_status: str
    idempotency_status: IdempotencyStatus
    abuse_precheck_status: str
    retry_after_seconds: int | None

    # --- schema / modality ---
    schema_verdict: SchemaVerdict
    envelope_version: str
    request_shape_class: str
    modality_manifest: ModalityManifest
    field_validation_report: tuple[str, ...]

    # --- normalization ---
    normalization_verdict: NormalizationVerdict
    normalized_payload: str | None  # bounded text representation
    normalized_payload_ref: str
    raw_payload_ref: str
    raw_payload_hash: str
    normalized_payload_hash: str
    normalization_report: tuple[str, ...]
    suspicious_field_markers: tuple[str, ...]
    attachment_manifest: AttachmentManifestShell

    # --- routing-neutral metadata ---
    upstream_traceparent: str | None
    locale: str | None
    timezone: str | None
    client_version: str | None
    platform: str | None
    batch_id: str | None
    job_id: str | None
    alert_id: str | None
    webhook_delivery_id: str | None

    # --- reason codes (warnings even on PASS path) ---
    ingress_reason_codes: tuple[IngressReasonCode, ...] = ()

    # --- authority guard ---
    # downstream_authority MUST always be "none" on this object.
    downstream_authority: str = "none"
    # permitted_next_layer MUST always be "L1" on a passing slip.
    permitted_next_layer: str = "L1"

    def __post_init__(self) -> None:
        if self.downstream_authority != "none":
            raise ValueError(
                "ValidatedRequest.downstream_authority MUST be 'none' "
                "(intake never grants downstream authority)."
            )
        if self.permitted_next_layer != "L1":
            raise ValueError(
                "ValidatedRequest.permitted_next_layer MUST be 'L1' "
                "(intake hands off to L1 only)."
            )


@dataclass(frozen=True)
class RejectedRequestNotice:
    """Emitted when any required gate fails. Contains structural reason and trace."""

    request_id: str
    trace_root: str
    source_class: SourceClass | None
    received_at_iso: str
    rejection_stage: str  # "E1" | "E2" | "E3" | "E4" | "E5" | "E6" | "INTERNAL"
    rejection_reason: IngressReasonCode
    reason_codes: tuple[IngressReasonCode, ...]
    retry_after_seconds: int | None = None
    machine_readable_detail: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class IngressAuditRecord:
    """Persistent audit trail entry for the run, regardless of outcome."""

    request_id: str
    trace_root: str
    received_at_iso: str
    source_class: SourceClass | None
    accepted: bool
    rejection_reason: IngressReasonCode | None
    reason_codes: tuple[IngressReasonCode, ...]
    auth_verdict: AuthVerdict | None
    quota_verdict: QuotaVerdict | None
    schema_verdict: SchemaVerdict | None
    normalization_verdict: NormalizationVerdict | None
    raw_payload_hash: str
    normalized_payload_hash: str
    duration_ms: float


__all__ = [
    "FORBIDDEN_VALIDATED_REQUEST_KEYS",
    "IngressAuditRecord",
    "RejectedRequestNotice",
    "ValidatedRequest",
]
