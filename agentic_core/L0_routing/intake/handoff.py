"""
01.6 — Validated Request Handoff.

Owns:
- IntakeAuditReceipt (deterministic audit_hash + completeness_score)
- IngressRejectionReport
- L1HandoffEnvelope (the only object L1 may read)
- finalize_intake_handoff() public entrypoint

INVARIANTS:
- Handoff is allowed only if a complete ValidatedRequest exists.
- L1HandoffEnvelope MUST contain `no_raw_bypass_assertion` and
  `downstream_read_only_assertion` set to True. Construction enforces this.
- L1HandoffEnvelope MUST NOT carry RouteContract / RetrievalPlan /
  PromptEnvelope / L2ExecutionRequest / ExitDisposition. The dataclass
  shape physically excludes those fields.
- Failed intake still emits an IntakeAuditReceipt when enough data exists.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from typing import Optional

from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode
from agentic_core.L0_routing.intake.receipts import (
    CallerScopeBaseline,
    DuplicateSuppressionReceipt,
    IngressReplaySeed,
    IntakeManifestHash,
    NormalizedRequestHash,
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
    RejectedRequestNotice,
    ValidatedRequest,
)


# ---------------------------------------------------------------------------
# IntakeAuditReceipt (rich, deterministic)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IntakeAuditReceipt:
    """01.6 §3 — deterministic audit envelope across all Intake stages.

    Distinct from `IngressAuditRecord` (the older lightweight stage-summary
    audit) — this one carries the full receipt-ref bundle and the
    completeness score required by the 01.6 contract.
    """

    audit_receipt_id: str
    request_id: Optional[str]
    trace_root: Optional[str]
    intake_status: IntakeStatus
    stage_receipt_refs: tuple[str, ...] = ()
    stage_statuses: tuple[str, ...] = ()
    first_failure_stage: Optional[str] = None
    decisive_reason_code: Optional[IngressReasonCode] = None
    raw_payload_hash: Optional[str] = None
    normalized_request_hash: Optional[str] = None
    intake_manifest_hash: Optional[str] = None
    completeness_score: float = 0.0
    audit_hash: str = ""

    def with_hash(self) -> "IntakeAuditReceipt":
        # Exclude request_id / trace_root / stage_receipt_refs (all volatile
        # per-run uuids) from the hash. Replay identity is established by
        # the deterministic intake_manifest_hash + raw_payload_hash +
        # status + reason code.
        payload = {
            "intake_status": self.intake_status.value,
            "first_failure_stage": self.first_failure_stage,
            "decisive_reason_code": (self.decisive_reason_code.value if self.decisive_reason_code else None),
            "raw_payload_hash": self.raw_payload_hash,
            "normalized_request_hash": self.normalized_request_hash,
            "intake_manifest_hash": self.intake_manifest_hash,
            # completeness_score is rounded to 4 decimals so float repr
            # noise doesn't perturb the digest.
            "completeness_score": round(self.completeness_score, 4),
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        h = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return IntakeAuditReceipt(
            audit_receipt_id=self.audit_receipt_id,
            request_id=self.request_id,
            trace_root=self.trace_root,
            intake_status=self.intake_status,
            stage_receipt_refs=self.stage_receipt_refs,
            stage_statuses=self.stage_statuses,
            first_failure_stage=self.first_failure_stage,
            decisive_reason_code=self.decisive_reason_code,
            raw_payload_hash=self.raw_payload_hash,
            normalized_request_hash=self.normalized_request_hash,
            intake_manifest_hash=self.intake_manifest_hash,
            completeness_score=self.completeness_score,
            audit_hash=h,
        )


# ---------------------------------------------------------------------------
# IngressRejectionReport
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IngressRejectionReport:
    """01.6 §2-extended — closed packet returned when intake fails.

    Distinct from RejectedRequestNotice (the older transport-stage notice).
    This one carries the canonical IntakeStatus enum and the audit refs
    required by the 01.6 contract.
    """

    rejected_request_id: str
    request_id: Optional[str]
    session_id: Optional[str]
    trace_root: Optional[str]
    rejection_stage: str
    rejection_status: IntakeStatus
    decisive_reason_code: IngressReasonCode
    safe_user_visible_summary: str
    audit_receipt_refs: tuple[str, ...] = ()
    raw_payload_hash: Optional[str] = None
    tenant_id: Optional[str] = None
    principal_id_hash: Optional[str] = None
    recoverable_by_user: bool = True
    retry_hint: Optional[str] = None
    intake_manifest_hash: Optional[str] = None

    def __post_init__(self) -> None:
        if self.rejection_status not in REJECTED_STATUSES:
            raise ValueError(
                f"IngressRejectionReport.rejection_status must be a rejected status; "
                f"got {self.rejection_status}"
            )


# ---------------------------------------------------------------------------
# L1HandoffEnvelope
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class L1HandoffEnvelope:
    """01.6 §4 — the ONLY object L1 reads from Intake.

    By construction:
    - Carries a fully-validated ValidatedRequest only.
    - handoff_target is permanently 'L1_REASONING_PLAN'.
    - no_raw_bypass_assertion + downstream_read_only_assertion are required
      and must be True. Construction enforces this.
    - The dataclass shape excludes RouteContract, RetrievalPlan,
      PromptEnvelope, and L2ExecutionRequest fields entirely.
    """

    handoff_id: str
    validated_request: ValidatedRequest
    handoff_target: str = "L1_REASONING_PLAN"
    handoff_status: str = "ready_for_l1"
    handoff_receipt_hash: str = ""
    no_raw_bypass_assertion: bool = True
    downstream_read_only_assertion: bool = True

    def __post_init__(self) -> None:
        if self.handoff_target != "L1_REASONING_PLAN":
            raise ValueError("L1HandoffEnvelope.handoff_target must be 'L1_REASONING_PLAN'.")
        if not self.no_raw_bypass_assertion:
            raise ValueError("L1HandoffEnvelope.no_raw_bypass_assertion must be True.")
        if not self.downstream_read_only_assertion:
            raise ValueError("L1HandoffEnvelope.downstream_read_only_assertion must be True.")

    def with_hash(self) -> "L1HandoffEnvelope":
        payload = {
            "handoff_target": self.handoff_target,
            "handoff_status": self.handoff_status,
            "request_id": self.validated_request.request_id,
            "session_id": self.validated_request.session_id,
            "trace_root": self.validated_request.trace_root,
            "intake_manifest_hash": getattr(self.validated_request, "intake_manifest_hash", "") or "",
            "no_raw_bypass_assertion": self.no_raw_bypass_assertion,
            "downstream_read_only_assertion": self.downstream_read_only_assertion,
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        h = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        return L1HandoffEnvelope(
            handoff_id=self.handoff_id,
            validated_request=self.validated_request,
            handoff_target=self.handoff_target,
            handoff_status=self.handoff_status,
            handoff_receipt_hash=h,
            no_raw_bypass_assertion=self.no_raw_bypass_assertion,
            downstream_read_only_assertion=self.downstream_read_only_assertion,
        )


# ---------------------------------------------------------------------------
# Stage results bundle (input to finalize_intake_handoff)
# ---------------------------------------------------------------------------


@dataclass
class IntakeStageResults:
    """Aggregated output of stages 01.1..01.5.

    `validated_request_candidate` is set only if all 01.1..01.5 succeeded.
    Otherwise `first_failure_stage` and `decisive_reason_code` are set.
    """

    transport_receipt: Optional[TransportEnvelopeReceipt] = None
    caller_scope_baseline: Optional[CallerScopeBaseline] = None
    tenant_boundary_receipt: Optional[TenantBoundaryReceipt] = None
    session_binding_receipt: Optional[SessionBindingReceipt] = None
    quota_receipt: Optional[QuotaReceipt] = None
    duplicate_suppression_receipt: Optional[DuplicateSuppressionReceipt] = None
    schema_validation_receipt: Optional[RequestSchemaValidationReceipt] = None
    correlation_receipt: Optional[RequestCorrelationReceipt] = None
    ingress_replay_seed: Optional[IngressReplaySeed] = None
    normalized_request_hash: Optional[NormalizedRequestHash] = None
    intake_manifest_hash: Optional[IntakeManifestHash] = None
    validated_request_candidate: Optional[ValidatedRequest] = None
    first_failure_stage: Optional[str] = None
    decisive_reason_code: Optional[IngressReasonCode] = None
    decisive_reason_message: str = ""
    raw_payload_hash: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    trace_root: Optional[str] = None
    tenant_id: Optional[str] = None
    principal_id_hash: Optional[str] = None
    rejected_notice: Optional[RejectedRequestNotice] = None


# Total receipts expected on a fully-passing intake. Used to compute
# completeness_score for the audit receipt.
_REQUIRED_RECEIPT_FIELDS: tuple[str, ...] = (
    "transport_receipt",
    "caller_scope_baseline",
    "tenant_boundary_receipt",
    "session_binding_receipt",
    "quota_receipt",
    "duplicate_suppression_receipt",
    "schema_validation_receipt",
    "correlation_receipt",
    "ingress_replay_seed",
    "normalized_request_hash",
    "intake_manifest_hash",
)


def _completeness(stage_results: IntakeStageResults) -> tuple[float, tuple[str, ...], tuple[str, ...]]:
    """Compute completeness_score, list of present receipt refs, and stage statuses."""
    present_refs: list[str] = []
    statuses: list[str] = []
    present_count = 0
    for name in _REQUIRED_RECEIPT_FIELDS:
        val = getattr(stage_results, name, None)
        if val is not None:
            present_count += 1
            statuses.append(f"{name}=ok")
            ref = (
                getattr(val, "receipt_id", None)
                or getattr(val, "manifest_hash_id", None)
                or getattr(val, "hash_id", None)
                or getattr(val, "replay_seed_id", None)
                or getattr(val, "caller_scope_baseline_id", None)
                or "<unknown>"
            )
            present_refs.append(ref)
        else:
            statuses.append(f"{name}=missing")
    score = present_count / float(len(_REQUIRED_RECEIPT_FIELDS))
    return score, tuple(present_refs), tuple(statuses)


# ---------------------------------------------------------------------------
# finalize_intake_handoff
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class IntakeFinalResult:
    """Output of `finalize_intake_handoff`.

    Exactly one of `handoff_envelope` / `rejection_report` is set.
    `audit_receipt` is always set so failed intake still leaves evidence.
    """

    handoff_envelope: Optional[L1HandoffEnvelope]
    rejection_report: Optional[IngressRejectionReport]
    audit_receipt: IntakeAuditReceipt

    def __post_init__(self) -> None:
        if (self.handoff_envelope is None) == (self.rejection_report is None):
            raise ValueError(
                "IntakeFinalResult must carry exactly one of handoff_envelope / rejection_report."
            )


def _safe_user_summary_for(
    reason: IngressReasonCode, fallback: str
) -> str:
    """Build a non-leaky user-visible summary for the rejection.

    Uses a bounded reason->copy catalog. The rejection_stage is captured
    separately on `IngressRejectionReport.rejection_stage` and on the
    `IntakeAuditReceipt.first_failure_stage` field, so it doesn't need to
    leak into user-visible text.
    """
    catalog: dict[IngressReasonCode, str] = {
        IngressReasonCode.UNSUPPORTED_TRANSPORT: "Your request was received on a channel we do not support.",
        IngressReasonCode.EMPTY_PAYLOAD: "Your request did not include any content for us to process.",
        IngressReasonCode.MALFORMED_ENVELOPE: "We could not read the structure of your request. Please retry with a valid request shape.",
        IngressReasonCode.AUTH_REQUIRED: "Your request requires authentication and none was provided.",
        IngressReasonCode.AUTH_EXPIRED: "Your authentication credentials have expired. Please reauthenticate and retry.",
        IngressReasonCode.TENANT_MISMATCH: "Your request and your credential point to different tenants.",
        IngressReasonCode.PRINCIPAL_BLOCKED: "Your account is currently blocked from making requests.",
        IngressReasonCode.QUOTA_EXCEEDED: "You have exceeded your request quota. Please retry shortly.",
        IngressReasonCode.BURST_LIMIT: "You sent too many requests in a short window. Please retry shortly.",
        IngressReasonCode.DUPLICATE_REQUEST: "We have already processed a matching request.",
        IngressReasonCode.WEBHOOK_REPLAY: "We have already processed this webhook delivery.",
        IngressReasonCode.UNSUPPORTED_MODALITY: "Your request includes an attachment type we do not support.",
        IngressReasonCode.PAYLOAD_TOO_LARGE: "Your request is too large for this entry surface.",
        IngressReasonCode.FIELD_TYPE_MISMATCH: "One or more required fields had the wrong type.",
        IngressReasonCode.NORMALIZATION_UNSAFE: "We could not safely normalize your request payload.",
        IngressReasonCode.ATTACHMENT_MANIFEST_BAD: "Your attachment manifest contained an invalid handle.",
        IngressReasonCode.TRACE_BINDING_FAILED: "We could not bind a trace identifier to your request.",
        IngressReasonCode.INTERNAL_INGRESS_ERROR: "An internal error occurred during request intake.",
    }
    return catalog.get(reason, fallback) or "Your request could not be accepted."


def finalize_intake_handoff(
    stage_results: IntakeStageResults,
) -> IntakeFinalResult:
    """01.6 entrypoint.

    Reads stage receipts, decides VALIDATED_FOR_L1 vs REJECTED_AT_*, builds
    the audit receipt, and emits either an L1HandoffEnvelope or an
    IngressRejectionReport.

    Pure function — no I/O.
    """
    score, present_refs, statuses = _completeness(stage_results)

    # ---- failure path ----
    if stage_results.first_failure_stage or stage_results.validated_request_candidate is None:
        stage = stage_results.first_failure_stage or "01.6"
        rejection_status = STAGE_TO_REJECTION_STATUS.get(stage, IntakeStatus.REJECTED_AT_HANDOFF_COMPLETENESS)
        reason = stage_results.decisive_reason_code or IngressReasonCode.INTERNAL_INGRESS_ERROR
        audit = IntakeAuditReceipt(
            audit_receipt_id=f"audit:{uuid.uuid4().hex}",
            request_id=stage_results.request_id,
            trace_root=stage_results.trace_root,
            intake_status=rejection_status,
            stage_receipt_refs=present_refs,
            stage_statuses=statuses,
            first_failure_stage=stage,
            decisive_reason_code=reason,
            raw_payload_hash=stage_results.raw_payload_hash,
            normalized_request_hash=(
                stage_results.normalized_request_hash.normalized_request_hash
                if stage_results.normalized_request_hash
                else None
            ),
            intake_manifest_hash=(
                stage_results.intake_manifest_hash.intake_manifest_hash
                if stage_results.intake_manifest_hash
                else None
            ),
            completeness_score=score,
        ).with_hash()

        rejection = IngressRejectionReport(
            rejected_request_id=f"rej:{uuid.uuid4().hex}",
            request_id=stage_results.request_id,
            session_id=stage_results.session_id,
            trace_root=stage_results.trace_root,
            rejection_stage=stage,
            rejection_status=rejection_status,
            decisive_reason_code=reason,
            safe_user_visible_summary=_safe_user_summary_for(
                reason, stage_results.decisive_reason_message
            ),
            audit_receipt_refs=(audit.audit_receipt_id,),
            raw_payload_hash=stage_results.raw_payload_hash,
            tenant_id=stage_results.tenant_id,
            principal_id_hash=stage_results.principal_id_hash,
            recoverable_by_user=reason
            not in {
                IngressReasonCode.PRINCIPAL_BLOCKED,
                IngressReasonCode.INTERNAL_INGRESS_ERROR,
            },
            retry_hint=(
                "retry_after_seconds"
                if reason
                in {
                    IngressReasonCode.QUOTA_EXCEEDED,
                    IngressReasonCode.BURST_LIMIT,
                    IngressReasonCode.INTERNAL_INGRESS_ERROR,
                }
                else None
            ),
            intake_manifest_hash=(
                stage_results.intake_manifest_hash.intake_manifest_hash
                if stage_results.intake_manifest_hash
                else None
            ),
        )

        return IntakeFinalResult(
            handoff_envelope=None,
            rejection_report=rejection,
            audit_receipt=audit,
        )

    # ---- success path ----
    # Defensive completeness check — the candidate must carry the manifest hash
    # and all 01.1..01.5 receipts must be present.
    if score < 1.0:
        # Treat as completeness rejection.
        audit = IntakeAuditReceipt(
            audit_receipt_id=f"audit:{uuid.uuid4().hex}",
            request_id=stage_results.request_id,
            trace_root=stage_results.trace_root,
            intake_status=IntakeStatus.REJECTED_AT_HANDOFF_COMPLETENESS,
            stage_receipt_refs=present_refs,
            stage_statuses=statuses,
            first_failure_stage="01.6",
            decisive_reason_code=IngressReasonCode.INTERNAL_INGRESS_ERROR,
            raw_payload_hash=stage_results.raw_payload_hash,
            completeness_score=score,
        ).with_hash()
        rejection = IngressRejectionReport(
            rejected_request_id=f"rej:{uuid.uuid4().hex}",
            request_id=stage_results.request_id,
            session_id=stage_results.session_id,
            trace_root=stage_results.trace_root,
            rejection_stage="01.6",
            rejection_status=IntakeStatus.REJECTED_AT_HANDOFF_COMPLETENESS,
            decisive_reason_code=IngressReasonCode.INTERNAL_INGRESS_ERROR,
            safe_user_visible_summary=(
                "An internal error occurred while finalizing your request. Please retry."
            ),
            audit_receipt_refs=(audit.audit_receipt_id,),
            raw_payload_hash=stage_results.raw_payload_hash,
            tenant_id=stage_results.tenant_id,
            principal_id_hash=stage_results.principal_id_hash,
            recoverable_by_user=False,
            retry_hint="retry_after_seconds",
        )
        return IntakeFinalResult(
            handoff_envelope=None,
            rejection_report=rejection,
            audit_receipt=audit,
        )

    audit = IntakeAuditReceipt(
        audit_receipt_id=f"audit:{uuid.uuid4().hex}",
        request_id=stage_results.request_id,
        trace_root=stage_results.trace_root,
        intake_status=IntakeStatus.VALIDATED_FOR_L1,
        stage_receipt_refs=present_refs,
        stage_statuses=statuses,
        first_failure_stage=None,
        decisive_reason_code=None,
        raw_payload_hash=stage_results.raw_payload_hash,
        normalized_request_hash=(
            stage_results.normalized_request_hash.normalized_request_hash
            if stage_results.normalized_request_hash
            else None
        ),
        intake_manifest_hash=(
            stage_results.intake_manifest_hash.intake_manifest_hash
            if stage_results.intake_manifest_hash
            else None
        ),
        completeness_score=score,
    ).with_hash()

    envelope = L1HandoffEnvelope(
        handoff_id=f"handoff:{uuid.uuid4().hex}",
        validated_request=stage_results.validated_request_candidate,
    ).with_hash()

    return IntakeFinalResult(
        handoff_envelope=envelope,
        rejection_report=None,
        audit_receipt=audit,
    )


__all__ = [
    "IngressRejectionReport",
    "IntakeAuditReceipt",
    "IntakeFinalResult",
    "IntakeStageResults",
    "L1HandoffEnvelope",
    "finalize_intake_handoff",
]
