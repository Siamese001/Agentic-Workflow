"""
Intake pipeline — orchestrates E1..E6 with fail-closed semantics.

Spec section: THE FRONT DESK / SECURITY CHECK (lines 75-150) and the full
six-question gate (E1..E6).

INVARIANTS (asserted by tests):
- Pipeline never imports a model, retriever, tool runner, or L1+ module.
- Pipeline returns ValidatedRequest XOR RejectedRequestNotice.
- On any stage failure, downstream stages do not run.
- On reject, an IngressAuditRecord is still produced.
- Emitted events never contain forbidden secret/payload fields.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Mapping

from agentic_core.L0_routing.intake.correlation import bind_trace_and_replay
from agentic_core.L0_routing.intake.envelope import (
    AttachmentManifestShell,
    ModalityManifest,
    RawIngressEnvelope,
)
from agentic_core.L0_routing.intake.events import (
    IngressEvent,
    IngressEventRecord,
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
    IngressOriginLabelManifest,
    PayloadSecurityFinding,
    build_origin_label_manifest,
)
from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode
from agentic_core.L0_routing.intake.receipts import (
    CallerScopeBaseline,
    DuplicateSuppressionReceipt,
    QuotaReceipt,
    RequestSchemaValidationReceipt,
    SessionBindingReceipt,
    TenantBoundaryReceipt,
    TransportEnvelopeReceipt,
)
from agentic_core.L0_routing.intake.stages import (
    DEFAULT_ALLOWED_TRANSPORTS,
    IdentityResolver,
    QuotaState,
    StageResult,
    run_e1_real_request,
    run_e2_identity,
    run_e3_quota,
    run_e4_schema,
    run_e5_normalize,
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


@dataclass
class IntakePolicy:
    """Configuration knobs for the intake pipeline."""

    allowed_transports: frozenset[str] = DEFAULT_ALLOWED_TRANSPORTS
    quota: QuotaState = field(default_factory=QuotaState)
    consumed_frames: set[str] = field(default_factory=set)


EventEmitter = Callable[[IngressEventRecord], None]


@dataclass
class IntakeReceiptBundle:
    """Bundle of typed Intake receipts (01.1..01.5) attached to an outcome.

    All fields are optional because rejected outcomes may carry only a
    partial bundle (everything up to the failing stage).
    """

    transport_receipt: TransportEnvelopeReceipt | None = None
    caller_scope_baseline: CallerScopeBaseline | None = None
    tenant_boundary_receipt: TenantBoundaryReceipt | None = None
    session_binding_receipt: SessionBindingReceipt | None = None
    quota_receipt: QuotaReceipt | None = None
    duplicate_suppression_receipt: DuplicateSuppressionReceipt | None = None
    schema_validation_receipt: RequestSchemaValidationReceipt | None = None
    origin_label_manifest: IngressOriginLabelManifest | None = None
    payload_security_findings: tuple[PayloadSecurityFinding, ...] = ()


@dataclass
class IntakeOutcome:
    """Pipeline.run() return shape — exactly one of validated / rejected is set.

    Carries the legacy stage-summary `audit` (`IngressAuditRecord`) AND the
    extended `final_audit` (`IntakeAuditReceipt`) plus the typed receipt
    bundle and L1 handoff envelope per the 01.6 contract.
    """

    validated: ValidatedRequest | None
    rejected: RejectedRequestNotice | None
    audit: IngressAuditRecord
    events: tuple[IngressEventRecord, ...]
    # New (additive) — handoff layer outputs from 01.5 / 01.6.
    receipt_bundle: IntakeReceiptBundle = field(default_factory=IntakeReceiptBundle)
    handoff_envelope: L1HandoffEnvelope | None = None
    rejection_report: IngressRejectionReport | None = None
    final_audit: IntakeAuditReceipt | None = None

    @property
    def accepted(self) -> bool:
        return self.validated is not None

    def __post_init__(self) -> None:
        if (self.validated is None) == (self.rejected is None):
            raise ValueError("IntakeOutcome must carry exactly one of validated / rejected.")


class IntakePipeline:
    """Front-desk pipeline. Run once per RawIngressEnvelope.

    Construct with an IntakePolicy + optional identity resolver + optional
    event sink. The pipeline is stateless across calls except for the
    QuotaState and consumed-frame set which it borrows from policy.
    """

    def __init__(
        self,
        policy: IntakePolicy | None = None,
        *,
        identity_resolver: IdentityResolver | None = None,
        event_sink: EventEmitter | None = None,
    ) -> None:
        self.policy = policy or IntakePolicy()
        self._identity_resolver = identity_resolver
        self._event_sink = event_sink

    # ------------------------------------------------------------------
    # public api
    # ------------------------------------------------------------------

    def run(self, env: RawIngressEnvelope) -> IntakeOutcome:
        events: list[IngressEventRecord] = []
        start = time.time()
        request_id = "pre-e1"
        trace_root = "pre-e1"
        source_class: SourceClass | None = None
        # Mutable accumulator for stage fields — passed to receipt builders
        # at every exit point. Empty dict means "stage did not run".
        stage_fields: dict[str, Mapping] = {"e1": {}, "e2": {}, "e3": {}, "e4": {}, "e5": {}}

        # ---- E1 ----
        e1 = run_e1_real_request(
            env,
            allowed_transports=self.policy.allowed_transports,
            consumed_frames=self.policy.consumed_frames,
        )
        stage_fields["e1"] = e1.fields
        if e1.fields.get("request_id"):
            request_id = e1.fields["request_id"]
        if e1.fields.get("trace_root"):
            trace_root = e1.fields["trace_root"]
        if isinstance(e1.fields.get("source_class"), SourceClass):
            source_class = e1.fields["source_class"]

        self._emit(
            events,
            IngressEvent.INGRESS_RECEIVED,
            request_id,
            trace_root,
            {"transport": env.transport, "source_channel": env.source_channel},
        )
        self._emit(events, IngressEvent.REQUEST_ID_ASSIGNED, request_id, trace_root, {})
        self._emit(events, IngressEvent.TRACE_ROOT_BOUND, request_id, trace_root, {})
        if source_class is not None:
            self._emit(
                events,
                IngressEvent.SOURCE_CLASSIFIED,
                request_id,
                trace_root,
                {"source_class": source_class.value},
            )

        if not e1.passed:
            return self._reject(
                env,
                stage="E1",
                primary=e1.reason_codes[0],
                reason_codes=tuple(e1.reason_codes),
                events=events,
                start=start,
                request_id=request_id,
                trace_root=trace_root,
                source_class=source_class,
                auth_verdict=None,
                quota_verdict=None,
                schema_verdict=None,
                normalization_verdict=None,
                raw_payload_hash="",
                normalized_payload_hash="",
                retry_after_seconds=None,
                stage_fields=stage_fields,
            )

        # ---- E2 ----
        assert source_class is not None  # E1 pass guarantees this
        e2 = run_e2_identity(env, source_class, resolver=self._identity_resolver)
        stage_fields["e2"] = e2.fields
        _av = e2.fields.get("auth_verdict")
        _pt = e2.fields.get("principal_type")
        self._emit(
            events,
            IngressEvent.AUTH_BASELINE_EVALUATED,
            request_id,
            trace_root,
            {
                "auth_verdict": _av.value if isinstance(_av, AuthVerdict) else None,
                "principal_type": _pt.value if isinstance(_pt, PrincipalType) else None,
            },
        )
        if not e2.passed:
            return self._reject(
                env,
                stage="E2",
                primary=e2.reason_codes[0],
                reason_codes=tuple(e2.reason_codes),
                events=events,
                start=start,
                request_id=request_id,
                trace_root=trace_root,
                source_class=source_class,
                auth_verdict=e2.fields.get("auth_verdict"),
                quota_verdict=None,
                schema_verdict=None,
                normalization_verdict=None,
                raw_payload_hash="",
                normalized_payload_hash="",
                retry_after_seconds=None,
                stage_fields=stage_fields,
            )

        # ---- E3 ----
        e3 = run_e3_quota(env, source_class, e1.fields, e2.fields, state=self.policy.quota)
        stage_fields["e3"] = e3.fields
        _qv = e3.fields.get("quota_verdict")
        self._emit(
            events,
            IngressEvent.QUOTA_EVALUATED,
            request_id,
            trace_root,
            {
                "quota_verdict": _qv.value if isinstance(_qv, QuotaVerdict) else None,
                "rate_window_state": e3.fields.get("rate_window_state"),
                "dedupe_status": e3.fields.get("dedupe_status"),
            },
        )
        if not e3.passed:
            return self._reject(
                env,
                stage="E3",
                primary=e3.reason_codes[0],
                reason_codes=tuple(e3.reason_codes),
                events=events,
                start=start,
                request_id=request_id,
                trace_root=trace_root,
                source_class=source_class,
                auth_verdict=e2.fields.get("auth_verdict"),
                quota_verdict=e3.fields.get("quota_verdict"),
                schema_verdict=None,
                normalization_verdict=None,
                raw_payload_hash=e3.fields.get("raw_payload_hash", ""),
                normalized_payload_hash="",
                retry_after_seconds=e3.fields.get("retry_after_seconds"),
                stage_fields=stage_fields,
            )

        # ---- E4 ----
        e4 = run_e4_schema(env, source_class, state=self.policy.quota)
        stage_fields["e4"] = e4.fields
        _sv = e4.fields.get("schema_verdict")
        self._emit(
            events,
            IngressEvent.SCHEMA_EVALUATED,
            request_id,
            trace_root,
            {
                "schema_verdict": _sv.value if isinstance(_sv, SchemaVerdict) else None,
                "envelope_version": e4.fields.get("envelope_version"),
                "request_shape_class": e4.fields.get("request_shape_class"),
            },
        )
        if not e4.passed:
            return self._reject(
                env,
                stage="E4",
                primary=e4.reason_codes[0],
                reason_codes=tuple(e4.reason_codes),
                events=events,
                start=start,
                request_id=request_id,
                trace_root=trace_root,
                source_class=source_class,
                auth_verdict=e2.fields.get("auth_verdict"),
                quota_verdict=e3.fields.get("quota_verdict"),
                schema_verdict=e4.fields.get("schema_verdict"),
                normalization_verdict=None,
                raw_payload_hash=e3.fields.get("raw_payload_hash", ""),
                normalized_payload_hash="",
                retry_after_seconds=e3.fields.get("retry_after_seconds"),
                stage_fields=stage_fields,
            )

        # ---- E5 ----
        e5 = run_e5_normalize(env, e1.fields)
        stage_fields["e5"] = e5.fields
        _nv = e5.fields.get("normalization_verdict")
        self._emit(
            events,
            IngressEvent.PAYLOAD_NORMALIZED,
            request_id,
            trace_root,
            {
                "normalization_verdict": _nv.value if isinstance(_nv, NormalizationVerdict) else None,
                "report_steps": list(e5.fields.get("normalization_report", ())),
                "suspicious_marker_count": len(e5.fields.get("suspicious_field_markers", ())),
            },
        )
        if env.attachments.count > 0:
            self._emit(
                events,
                IngressEvent.ATTACHMENT_MANIFEST_CAPTURED,
                request_id,
                trace_root,
                {"attachment_count": env.attachments.count},
            )
        if not e5.passed:
            return self._reject(
                env,
                stage="E5",
                primary=e5.reason_codes[0],
                reason_codes=tuple(e5.reason_codes),
                events=events,
                start=start,
                request_id=request_id,
                trace_root=trace_root,
                source_class=source_class,
                auth_verdict=e2.fields.get("auth_verdict"),
                quota_verdict=e3.fields.get("quota_verdict"),
                schema_verdict=e4.fields.get("schema_verdict"),
                normalization_verdict=e5.fields.get("normalization_verdict"),
                raw_payload_hash=e3.fields.get("raw_payload_hash", ""),
                normalized_payload_hash="",
                retry_after_seconds=e3.fields.get("retry_after_seconds"),
                stage_fields=stage_fields,
            )

        # ---- E6 stamp ----
        validated = self._stamp(env, source_class, e1.fields, e2.fields, e3.fields, e4.fields, e5.fields)

        self._emit(
            events,
            IngressEvent.INGRESS_ACCEPTED,
            request_id,
            trace_root,
            {
                "source_class": source_class.value,
                "auth_verdict": validated.auth_verdict.value,
                "quota_verdict": validated.quota_verdict.value,
                "schema_verdict": validated.schema_verdict.value,
                "normalization_verdict": validated.normalization_verdict.value,
            },
        )

        audit = IngressAuditRecord(
            request_id=request_id,
            trace_root=trace_root,
            received_at_iso=validated.received_at_iso,
            source_class=source_class,
            accepted=True,
            rejection_reason=None,
            reason_codes=validated.ingress_reason_codes,
            auth_verdict=validated.auth_verdict,
            quota_verdict=validated.quota_verdict,
            schema_verdict=validated.schema_verdict,
            normalization_verdict=validated.normalization_verdict,
            raw_payload_hash=validated.raw_payload_hash,
            normalized_payload_hash=validated.normalized_payload_hash,
            duration_ms=(time.time() - start) * 1000.0,
        )

        # Build typed receipts (01.1–01.4) and run 01.5 binding + 01.6 handoff.
        outcome = IntakeOutcome(
            validated=validated,
            rejected=None,
            audit=audit,
            events=tuple(events),
        )
        self._attach_receipts_and_handoff(
            outcome,
            env=env,
            source_class=source_class,
            stage_fields=stage_fields,
            failure_stage=None,
            decisive_reason=None,
        )
        return outcome

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _stamp(
        self,
        env: RawIngressEnvelope,
        source_class: SourceClass,
        e1: Mapping,
        e2: Mapping,
        e3: Mapping,
        e4: Mapping,
        e5: Mapping,
    ) -> ValidatedRequest:
        ingress_time = e1.get("ingress_time_unix", time.time())
        received_at_iso = datetime.fromtimestamp(ingress_time, tz=timezone.utc).isoformat()

        modality = e4.get("modality_manifest") or ModalityManifest()
        attachment_manifest: AttachmentManifestShell = (
            e5.get("attachment_manifest_canonical")
            or e1.get("attachment_manifest_shell")
            or AttachmentManifestShell()
        )

        return ValidatedRequest(
            request_id=e1["request_id"],
            session_id=e1["session_id"],
            trace_root=e1["trace_root"],
            ingress_time_unix=ingress_time,
            received_at_iso=received_at_iso,
            source_channel=e1.get("source_channel", env.source_channel or env.transport),
            source_class=source_class,
            tenant_bind=e2.get("tenant_bind"),
            workspace_bind=e2.get("workspace_bind"),
            principal_type=e2.get("principal_type", PrincipalType.UNKNOWN),
            principal_id=e2.get("principal_id"),
            auth_verdict=e2.get("auth_verdict", AuthVerdict.REJECTED),
            caller_scope_baseline=e2.get("caller_scope_baseline", "rejected"),
            region_scope_baseline=e2.get("region_scope_baseline"),
            baseline_entitlements=tuple(e2.get("baseline_entitlements", ())),
            quota_verdict=e3.get("quota_verdict", QuotaVerdict.ALLOWED),
            quota_bucket=e3.get("quota_bucket", "unknown"),
            rate_window_state=e3.get("rate_window_state", "ok"),
            dedupe_status=e3.get("dedupe_status", "fresh"),
            idempotency_status=e3.get("idempotency_status", IdempotencyStatus.NOT_APPLICABLE),
            abuse_precheck_status=e3.get("abuse_precheck_status", "clear"),
            retry_after_seconds=e3.get("retry_after_seconds"),
            schema_verdict=e4.get("schema_verdict", SchemaVerdict.VALID),
            envelope_version=e4.get("envelope_version", "1"),
            request_shape_class=e4.get("request_shape_class", "unknown"),
            modality_manifest=modality,
            field_validation_report=tuple(e4.get("field_validation_report", ())),
            normalization_verdict=e5.get("normalization_verdict", NormalizationVerdict.PRESERVED),
            normalized_payload=e5.get("normalized_payload"),
            normalized_payload_ref=e5.get("normalized_payload_ref", ""),
            raw_payload_ref=e5.get("raw_payload_ref", e1.get("raw_payload_ref", "")),
            raw_payload_hash=e5.get("raw_payload_hash", ""),
            normalized_payload_hash=e5.get("normalized_payload_hash", ""),
            normalization_report=tuple(e5.get("normalization_report", ())),
            suspicious_field_markers=tuple(e5.get("suspicious_field_markers", ())),
            attachment_manifest=attachment_manifest,
            upstream_traceparent=env.upstream_traceparent,
            locale=env.locale,
            timezone=env.timezone,
            client_version=env.client_version,
            platform=env.platform,
            batch_id=env.batch_id,
            job_id=env.job_id,
            alert_id=env.alert_id,
            webhook_delivery_id=env.webhook_delivery_id,
            ingress_reason_codes=(),
        )

    def _reject(
        self,
        env: RawIngressEnvelope,
        *,
        stage: str,
        primary: IngressReasonCode,
        reason_codes: tuple[IngressReasonCode, ...],
        events: list[IngressEventRecord],
        start: float,
        request_id: str,
        trace_root: str,
        source_class: SourceClass | None,
        auth_verdict: AuthVerdict | None,
        quota_verdict: QuotaVerdict | None,
        schema_verdict: SchemaVerdict | None,
        normalization_verdict: NormalizationVerdict | None,
        raw_payload_hash: str,
        normalized_payload_hash: str,
        retry_after_seconds: int | None,
        stage_fields: dict[str, Mapping] | None = None,
    ) -> IntakeOutcome:
        received_at_iso = datetime.now(tz=timezone.utc).isoformat()
        notice = RejectedRequestNotice(
            request_id=request_id,
            trace_root=trace_root,
            source_class=source_class,
            received_at_iso=received_at_iso,
            rejection_stage=stage,
            rejection_reason=primary,
            reason_codes=reason_codes,
            retry_after_seconds=retry_after_seconds,
            machine_readable_detail={
                "transport": env.transport,
                "source_channel": env.source_channel or env.transport,
            },
        )
        self._emit(
            events,
            IngressEvent.INGRESS_REJECTED,
            request_id,
            trace_root,
            {
                "stage": stage,
                "primary_reason": primary.value,
                "reason_codes": [c.value for c in reason_codes],
            },
        )
        audit = IngressAuditRecord(
            request_id=request_id,
            trace_root=trace_root,
            received_at_iso=received_at_iso,
            source_class=source_class,
            accepted=False,
            rejection_reason=primary,
            reason_codes=reason_codes,
            auth_verdict=auth_verdict,
            quota_verdict=quota_verdict,
            schema_verdict=schema_verdict,
            normalization_verdict=normalization_verdict,
            raw_payload_hash=raw_payload_hash,
            normalized_payload_hash=normalized_payload_hash,
            duration_ms=(time.time() - start) * 1000.0,
        )
        outcome = IntakeOutcome(
            validated=None,
            rejected=notice,
            audit=audit,
            events=tuple(events),
        )
        # Best-effort partial receipts for the stages that ran.
        self._attach_receipts_and_handoff(
            outcome,
            env=env,
            source_class=source_class,
            stage_fields=stage_fields or {},
            failure_stage=stage,
            decisive_reason=primary,
        )
        return outcome

    # ------------------------------------------------------------------
    # 01.1–01.6 receipt builders + handoff finalization
    # ------------------------------------------------------------------

    def _attach_receipts_and_handoff(
        self,
        outcome: "IntakeOutcome",
        *,
        env: RawIngressEnvelope,
        source_class: SourceClass | None,
        stage_fields: Mapping[str, Mapping],
        failure_stage: str | None,
        decisive_reason: IngressReasonCode | None,
    ) -> None:
        """Build typed Intake receipts and 01.6 handoff/audit. Mutates outcome.

        Pure-ish: builds receipts from the data captured during E1..E5 stage
        execution. Failed stages produce best-effort partial receipts where
        we have enough info; missing receipts are simply None.
        """
        e1 = stage_fields.get("e1") or {}
        e2 = stage_fields.get("e2") or {}
        e3 = stage_fields.get("e3") or {}
        e4 = stage_fields.get("e4") or {}
        e5 = stage_fields.get("e5") or {}

        bundle = outcome.receipt_bundle

        raw_envelope_id = e1.get("raw_payload_ref") or f"raw:{uuid.uuid4().hex}"

        # ---- 01.1 TransportEnvelopeReceipt ----
        if e1:
            transport_normalized = e1.get("transport_normalized") or env.transport
            tep_rejection_codes: tuple[IngressReasonCode, ...] = ()
            if failure_stage == "E1" and decisive_reason is not None:
                tep_rejection_codes = (decisive_reason,)
            tep = TransportEnvelopeReceipt(
                receipt_id=f"tep:{uuid.uuid4().hex}",
                raw_envelope_id=raw_envelope_id,
                transport=transport_normalized,
                channel=env.source_channel or transport_normalized,
                accepted_transport=failure_stage != "E1",
                frame_parse_status=("ok" if not env.body_parser_failed else "malformed"),
                method_allowed=True,
                content_type_allowed=True,
                encoding_allowed=True,
                body_size_status=("ok" if env.has_payload() else "absent"),
                attachment_inventory_status=("ok" if env.attachments.count >= 0 else "bad_handle"),
                raw_capture_status=("ok" if e1.get("raw_payload_ref") else "missing"),
                transport_policy_ref="policy:intake:transport:v1",
                rejection_reason_codes=tep_rejection_codes,
            ).with_hash()
            bundle.transport_receipt = tep
        else:
            tep = None

        # ---- 01.2 CallerScopeBaseline / TenantBoundaryReceipt / SessionBindingReceipt ----
        if e2:
            principal_id = e2.get("principal_id")
            principal_id_hash = (
                hashlib.sha256(str(principal_id).encode("utf-8")).hexdigest() if principal_id else None
            )
            scope_baseline = CallerScopeBaseline(
                caller_scope_baseline_id=f"csb:{uuid.uuid4().hex}",
                caller_claim_id=f"cic:{uuid.uuid4().hex}",
                tenant_id=e2.get("tenant_bind"),
                tenant_scope=("tenant:scoped" if e2.get("tenant_bind") else None),
                session_id=e1.get("session_id"),
                session_scope=("session:active" if e1.get("session_id") else None),
                region=e2.get("region_scope_baseline") or env.region,
                data_residency_hint=env.region,
                account_status=(
                    "active" if e2.get("auth_verdict") not in (None, AuthVerdict.REJECTED) else "unknown"
                ),
                baseline_acl_tags=tuple(e2.get("baseline_entitlements", ())),
                allowed_intake_surfaces=("intake_default",),
                restricted_intake_surfaces=(),
                cross_tenant_risk="none",
                cross_session_risk="none",
            ).with_hash()
            bundle.caller_scope_baseline = scope_baseline

            tenant_resolved = bool(e2.get("tenant_bind"))
            tenant_conflict = failure_stage == "E2" and decisive_reason is IngressReasonCode.TENANT_MISMATCH
            tbr_codes: tuple[IngressReasonCode, ...] = ()
            if failure_stage == "E2" and decisive_reason is not None:
                tbr_codes = (decisive_reason,)
            # tenant_source is "claim" (envelope), "credential" (auth token),
            # "header" (transport metadata for webhook/alert), or "inferred"
            # (fallback). We choose based on where the binding came from.
            if env.claimed_tenant_id:
                tenant_source = "claim"
            elif source_class in (SourceClass.WEBHOOK, SourceClass.ALERT):
                tenant_source = "header"
            elif e2.get("tenant_bind"):
                tenant_source = "credential"
            else:
                tenant_source = "none"
            bundle.tenant_boundary_receipt = TenantBoundaryReceipt(
                receipt_id=f"tbr:{uuid.uuid4().hex}",
                tenant_id=e2.get("tenant_bind"),
                tenant_resolved=tenant_resolved,
                tenant_source=tenant_source,
                tenant_allowed=tenant_resolved and not tenant_conflict,
                tenant_conflict_detected=tenant_conflict,
                conflicting_tenant_refs=(),
                region_allowed=True,
                data_residency_status="ok",
                reason_codes=tbr_codes,
            ).with_hash()

            session_valid = failure_stage not in ("E1", "E2") or e1.get("session_id") is not None
            sbr_codes: tuple[IngressReasonCode, ...] = ()
            if failure_stage == "E2" and decisive_reason is not None:
                sbr_codes = (decisive_reason,)
            bundle.session_binding_receipt = SessionBindingReceipt(
                receipt_id=f"sbr:{uuid.uuid4().hex}",
                session_id=e1.get("session_id"),
                session_created_or_resumed=("resumed" if env.session_id_hint else "created"),
                session_scope=("session:active" if session_valid else None),
                session_valid=session_valid,
                session_expiry_status="ok",
                conversation_context_allowed=False,
                prior_context_access_baseline="none",
                reason_codes=sbr_codes,
            ).with_hash()
        else:
            scope_baseline = None
            principal_id_hash = None

        # ---- 01.3 QuotaReceipt + DuplicateSuppressionReceipt ----
        if e3:
            qv = e3.get("quota_verdict")
            qr_codes: tuple[IngressReasonCode, ...] = ()
            if failure_stage == "E3" and decisive_reason is not None:
                qr_codes = (decisive_reason,)
            qr = QuotaReceipt(
                receipt_id=f"qr:{uuid.uuid4().hex}",
                tenant_id=e2.get("tenant_bind"),
                principal_id_hash=principal_id_hash,
                session_id=e1.get("session_id"),
                quota_policy_ref="policy:intake:quota:v1",
                request_size_status=(
                    "too_large" if decisive_reason is IngressReasonCode.PAYLOAD_TOO_LARGE else "ok"
                ),
                attachment_count_status="ok",
                rate_limit_status=("throttled" if qv is QuotaVerdict.THROTTLED else "ok"),
                daily_limit_status="unknown",
                concurrent_request_status="unknown",
                allowed_to_continue_intake=(failure_stage != "E3"),
                reason_codes=qr_codes,
                quota_snapshot_ref=(
                    f"quota:{e3.get('quota_bucket', 'unknown')}:{e3.get('rate_window_state', 'ok')}"
                ),
            ).with_hash()
            bundle.quota_receipt = qr

            duplicate = qv is QuotaVerdict.DUPLICATE
            dup_class = (
                "exact_replay_same_idempotency_key"
                if e3.get("dedupe_status") == "idempotency_hit"
                else "exact_replay_same_payload"
                if e3.get("dedupe_status") == "payload_hash_hit"
                else "near_duplicate_transport_retry"
                if e3.get("dedupe_status") == "webhook_replay"
                else "not_duplicate"
            )
            dsr_codes: tuple[IngressReasonCode, ...] = ()
            if duplicate and decisive_reason is not None:
                dsr_codes = (decisive_reason,)
            bundle.duplicate_suppression_receipt = DuplicateSuppressionReceipt(
                receipt_id=f"dsr:{uuid.uuid4().hex}",
                duplicate_detected=duplicate,
                duplicate_class=dup_class,
                prior_request_ref=None,
                suppress_or_continue=("suppress" if duplicate else "continue"),
                reason_codes=dsr_codes,
            ).with_hash()
        else:
            qr = None

        # ---- 01.4 RequestSchemaValidationReceipt ----
        if e4:
            sv = e4.get("schema_verdict")
            schema_valid = sv is SchemaVerdict.VALID
            ssv_codes: tuple[IngressReasonCode, ...] = ()
            if failure_stage == "E4" and decisive_reason is not None:
                ssv_codes = (decisive_reason,)
            ssv = RequestSchemaValidationReceipt(
                receipt_id=f"ssv:{uuid.uuid4().hex}",
                request_schema_ref="schema:intake:default:v1",
                schema_version=str(e4.get("envelope_version", "1")),
                schema_valid=schema_valid,
                missing_fields=tuple(),
                malformed_fields=tuple(str(x) for x in e4.get("field_validation_report", ())),
                unknown_fields=tuple(),
                coercions_applied=tuple(),
                structural_risk_flags=tuple(),
                reason_codes=ssv_codes,
            ).with_hash()
            bundle.schema_validation_receipt = ssv
        else:
            ssv = None

        # ---- 01.4 IngressOriginLabelManifest + PayloadSecurityFinding ----
        if e5 or e1:
            normalized_text = e5.get("normalized_payload") or env.body_text or ""
            request_id_for_manifest = e1.get("request_id") or "unknown"
            try:
                manifest, findings = build_origin_label_manifest(
                    env,
                    normalized_text=normalized_text or "",
                    request_id=request_id_for_manifest,
                )
            except (UnicodeError, ValueError, TypeError):
                manifest = None
                findings = ()
            bundle.origin_label_manifest = manifest
            bundle.payload_security_findings = findings
        else:
            manifest = None
            findings = ()

        # ---- 01.5 binding (only if all five stages succeeded) ----
        binding_result = None
        if (
            failure_stage is None
            and tep is not None
            and scope_baseline is not None
            and qr is not None
            and ssv is not None
            and manifest is not None
            and outcome.validated is not None
        ):
            try:
                binding_result = bind_trace_and_replay(
                    request_id=outcome.validated.request_id,
                    session_id=outcome.validated.session_id,
                    trace_root=outcome.validated.trace_root,
                    raw_envelope_id=raw_envelope_id,
                    normalized_payload_id=outcome.validated.normalized_payload_ref or None,
                    transport_receipt=tep,
                    caller_scope_baseline=scope_baseline,
                    quota_receipt=qr,
                    schema_validation_receipt=ssv,
                    origin_label_manifest=manifest,
                    raw_payload_hash=outcome.validated.raw_payload_hash,
                    normalized_payload_hash=outcome.validated.normalized_payload_hash,
                    schema_version=outcome.validated.envelope_version,
                    transport=outcome.validated.source_channel or env.transport,
                )
            except (ValueError, TypeError):  # narrow; binding is pure
                binding_result = None

        # ---- enrich validated_request with refs/hashes ----
        if (
            outcome.validated is not None
            and binding_result is not None
            and tep is not None
            and qr is not None
            and ssv is not None
        ):
            vr = outcome.validated
            enriched = ValidatedRequest(
                **{
                    f.name: getattr(vr, f.name)
                    for f in vr.__dataclass_fields__.values()
                    if f.name
                    not in {
                        "intake_status",
                        "intake_manifest_hash",
                        "normalized_request_hash",
                        "ingress_replay_seed_ref",
                        "transport_receipt_ref",
                        "identity_receipt_ref",
                        "quota_receipt_ref",
                        "schema_validation_receipt_ref",
                        "correlation_receipt_ref",
                        "origin_label_manifest_ref",
                        "intake_warnings",
                        "handoff_created_at_observed",
                    }
                },
                intake_status="VALIDATED_FOR_L1",
                intake_manifest_hash=binding_result.intake_manifest_hash.intake_manifest_hash,
                normalized_request_hash=binding_result.normalized_request_hash.normalized_request_hash,
                ingress_replay_seed_ref=binding_result.ingress_replay_seed.replay_seed_id,
                transport_receipt_ref=tep.receipt_id,
                identity_receipt_ref=(
                    bundle.tenant_boundary_receipt.receipt_id if bundle.tenant_boundary_receipt else ""
                ),
                quota_receipt_ref=qr.receipt_id,
                schema_validation_receipt_ref=ssv.receipt_id,
                correlation_receipt_ref=binding_result.correlation_receipt.receipt_id,
                origin_label_manifest_ref=(manifest.manifest_id if manifest else ""),
                intake_warnings=tuple(),
                handoff_created_at_observed=datetime.now(tz=timezone.utc).isoformat(),
            )
            outcome.validated = enriched

        # ---- 01.6 finalize handoff ----
        stage_results = IntakeStageResults(
            transport_receipt=bundle.transport_receipt,
            caller_scope_baseline=bundle.caller_scope_baseline,
            tenant_boundary_receipt=bundle.tenant_boundary_receipt,
            session_binding_receipt=bundle.session_binding_receipt,
            quota_receipt=bundle.quota_receipt,
            duplicate_suppression_receipt=bundle.duplicate_suppression_receipt,
            schema_validation_receipt=bundle.schema_validation_receipt,
            correlation_receipt=binding_result.correlation_receipt if binding_result else None,
            ingress_replay_seed=binding_result.ingress_replay_seed if binding_result else None,
            normalized_request_hash=binding_result.normalized_request_hash if binding_result else None,
            intake_manifest_hash=binding_result.intake_manifest_hash if binding_result else None,
            validated_request_candidate=outcome.validated,
            first_failure_stage=failure_stage,
            decisive_reason_code=decisive_reason,
            decisive_reason_message=(decisive_reason.value if decisive_reason else ""),
            raw_payload_hash=(
                outcome.validated.raw_payload_hash
                if outcome.validated
                else (e3.get("raw_payload_hash") or e5.get("raw_payload_hash") or None)
            ),
            request_id=(outcome.validated.request_id if outcome.validated else e1.get("request_id")),
            session_id=(outcome.validated.session_id if outcome.validated else e1.get("session_id")),
            trace_root=(outcome.validated.trace_root if outcome.validated else e1.get("trace_root")),
            tenant_id=e2.get("tenant_bind"),
            principal_id_hash=principal_id_hash,
            rejected_notice=outcome.rejected,
        )
        final = finalize_intake_handoff(stage_results)
        outcome.handoff_envelope = final.handoff_envelope
        outcome.rejection_report = final.rejection_report
        outcome.final_audit = final.audit_receipt

    def _emit(
        self,
        events: list[IngressEventRecord],
        event: IngressEvent,
        request_id: str,
        trace_root: str,
        fields: Mapping,
    ) -> None:
        record = IngressEventRecord(
            event=event,
            request_id=request_id,
            trace_root=trace_root,
            fields=dict(fields),
        )
        events.append(record)
        if self._event_sink is not None:
            self._event_sink(record)


def run_request_intake(
    raw_input: RawIngressEnvelope,
    intake_config: IntakePolicy | None = None,
    *,
    identity_resolver: "IdentityResolver | None" = None,
    event_sink: EventEmitter | None = None,
) -> IntakeOutcome:
    """Public composite entrypoint matching 01.6 §Phase 4 spec verbatim.

    Equivalent to constructing IntakePipeline(intake_config) and calling
    run(raw_input). Provided as a top-level function so callers can adopt
    the spec wording without binding to the pipeline class.

    Returns the IntakeOutcome; the only object L1 may read is
    `outcome.handoff_envelope`. On rejection `outcome.handoff_envelope is
    None` and `outcome.rejection_report` is set.
    """
    pipeline = IntakePipeline(
        intake_config,
        identity_resolver=identity_resolver,
        event_sink=event_sink,
    )
    return pipeline.run(raw_input)


__all__ = [
    "EventEmitter",
    "IntakeOutcome",
    "IntakePipeline",
    "IntakePolicy",
    "IntakeReceiptBundle",
    "run_request_intake",
]
