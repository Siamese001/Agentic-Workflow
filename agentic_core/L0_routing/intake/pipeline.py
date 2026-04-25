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

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Mapping

from agentic_core.L0_routing.intake.envelope import (
    AttachmentManifestShell,
    ModalityManifest,
    RawIngressEnvelope,
)
from agentic_core.L0_routing.intake.events import (
    IngressEvent,
    IngressEventRecord,
)
from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode
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
class IntakeOutcome:
    """Pipeline.run() return shape — exactly one of validated / rejected is set."""

    validated: ValidatedRequest | None
    rejected: RejectedRequestNotice | None
    audit: IngressAuditRecord
    events: tuple[IngressEventRecord, ...]

    @property
    def accepted(self) -> bool:
        return self.validated is not None

    def __post_init__(self) -> None:
        if (self.validated is None) == (self.rejected is None):
            raise ValueError(
                "IntakeOutcome must carry exactly one of validated / rejected."
            )


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

        # ---- E1 ----
        e1 = run_e1_real_request(
            env,
            allowed_transports=self.policy.allowed_transports,
            consumed_frames=self.policy.consumed_frames,
        )
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
            )

        # ---- E2 ----
        assert source_class is not None  # E1 pass guarantees this
        e2 = run_e2_identity(env, source_class, resolver=self._identity_resolver)
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
            )

        # ---- E3 ----
        e3 = run_e3_quota(env, source_class, e1.fields, e2.fields, state=self.policy.quota)
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
            )

        # ---- E4 ----
        e4 = run_e4_schema(env, source_class, state=self.policy.quota)
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
            )

        # ---- E5 ----
        e5 = run_e5_normalize(env, e1.fields)
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

        return IntakeOutcome(
            validated=validated,
            rejected=None,
            audit=audit,
            events=tuple(events),
        )

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
        return IntakeOutcome(
            validated=None,
            rejected=notice,
            audit=audit,
            events=tuple(events),
        )

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


__all__ = [
    "EventEmitter",
    "IntakeOutcome",
    "IntakePipeline",
    "IntakePolicy",
]
