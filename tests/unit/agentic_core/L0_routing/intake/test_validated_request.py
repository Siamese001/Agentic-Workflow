"""Unit tests for agentic_core.L0_routing.intake.validated_request.

Wave 2 (plan adg-testing-hotspots-wave-plan-a7f3c1) — L0 intake output contract.
``validated_request`` (fan_in=20) carries the bounded slip handed to L1 after
E1..E6 intake passes. INVARIANT: it grants NO downstream authority —
``downstream_authority`` is permanently "none" and ``permitted_next_layer`` is
"L1". Covers the three frozen dataclasses, their defaults, the two
``__post_init__`` ValueError paths, and the forbidden-key denylist.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.L0_routing.intake.envelope import (
    AttachmentManifestShell,
    ModalityManifest,
)
from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode
from agentic_core.L0_routing.intake.validated_request import (
    FORBIDDEN_VALIDATED_REQUEST_KEYS,
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

# The dataclass has many required positional fields; this helper builds a
# minimal valid instance and lets tests override individual slots.
_REQUIRED = dict(
    request_id="req-1",
    session_id="sess-1",
    trace_root="trace-1",
    ingress_time_unix=1.0,
    received_at_iso="2026-01-01T00:00:00Z",
    source_channel="chat",
    source_class=SourceClass.USER,
    tenant_bind=None,
    workspace_bind=None,
    principal_type=PrincipalType.USER,
    principal_id="p-1",
    auth_verdict=AuthVerdict.AUTHENTICATED,
    caller_scope_baseline="user:standard",
    region_scope_baseline=None,
    baseline_entitlements=("user:standard",),
    quota_verdict=QuotaVerdict.ALLOWED,
    quota_bucket="t:p",
    rate_window_state="ok",
    dedupe_status="fresh",
    idempotency_status=IdempotencyStatus.NOT_APPLICABLE,
    abuse_precheck_status="clear",
    retry_after_seconds=None,
    schema_verdict=SchemaVerdict.VALID,
    envelope_version="1",
    request_shape_class="user_chat",
    modality_manifest=ModalityManifest(),
    field_validation_report=(),
    normalization_verdict=NormalizationVerdict.PRESERVED,
    normalized_payload="hi",
    normalized_payload_ref="normalized://req-1",
    raw_payload_ref="raw://req-1",
    raw_payload_hash="h1",
    normalized_payload_hash="h2",
    normalization_report=(),
    suspicious_field_markers=(),
    attachment_manifest=AttachmentManifestShell(),
    upstream_traceparent=None,
    locale=None,
    timezone=None,
    client_version=None,
    platform=None,
    batch_id=None,
    job_id=None,
    alert_id=None,
    webhook_delivery_id=None,
)


def _make(**overrides: object) -> ValidatedRequest:
    slots = dict(_REQUIRED)
    slots.update(overrides)
    return ValidatedRequest(**slots)  # type: ignore[arg-type]


class TestValidatedRequestConstruction:
    def test_minimal_valid_instance(self) -> None:
        vr = _make()
        assert vr.request_id == "req-1"
        assert vr.source_class is SourceClass.USER

    def test_authority_defaults(self) -> None:
        vr = _make()
        assert vr.downstream_authority == "none"
        assert vr.permitted_next_layer == "L1"

    def test_ingress_reason_codes_default_empty(self) -> None:
        assert _make().ingress_reason_codes == ()

    def test_extended_field_defaults(self) -> None:
        vr = _make()
        assert vr.intake_status == "VALIDATED_FOR_L1"
        assert vr.intake_manifest_hash == ""
        assert vr.normalized_request_hash == ""
        assert vr.ingress_replay_seed_ref == ""
        assert vr.transport_receipt_ref == ""
        assert vr.identity_receipt_ref == ""
        assert vr.quota_receipt_ref == ""
        assert vr.schema_validation_receipt_ref == ""
        assert vr.correlation_receipt_ref == ""
        assert vr.origin_label_manifest_ref == ""
        assert vr.intake_warnings == ()
        assert vr.handoff_created_at_observed == ""

    def test_reason_codes_carried_on_pass(self) -> None:
        vr = _make(ingress_reason_codes=(IngressReasonCode.QUOTA_EXCEEDED,))
        assert IngressReasonCode.QUOTA_EXCEEDED in vr.ingress_reason_codes

    def test_frozen(self) -> None:
        vr = _make()
        with pytest.raises(dataclasses.FrozenInstanceError):
            vr.request_id = "other"  # type: ignore[misc]


class TestValidatedRequestPostInit:
    @pytest.mark.parametrize("bad", ["L1", "full", "write", ""])
    def test_downstream_authority_must_be_none(self, bad: str) -> None:
        with pytest.raises(ValueError, match="downstream_authority MUST be 'none'"):
            _make(downstream_authority=bad)

    @pytest.mark.parametrize("bad", ["L2", "L0", "L3", ""])
    def test_permitted_next_layer_must_be_l1(self, bad: str) -> None:
        with pytest.raises(ValueError, match="permitted_next_layer MUST be 'L1'"):
            _make(permitted_next_layer=bad)

    def test_authority_none_passes(self) -> None:
        # Explicitly setting the canonical values is accepted.
        assert _make(downstream_authority="none", permitted_next_layer="L1").permitted_next_layer == "L1"


class TestForbiddenKeys:
    def test_denylist_is_frozenset(self) -> None:
        assert isinstance(FORBIDDEN_VALIDATED_REQUEST_KEYS, frozenset)

    @pytest.mark.parametrize(
        "key",
        [
            "final_answer",
            "route_decision",
            "proposed_route",
            "retrieval_result",
            "prompt_packet",
            "tool_call",
            "capability_token",
            "uwg_commit_request",
        ],
    )
    def test_known_forbidden_keys_present(self, key: str) -> None:
        assert key in FORBIDDEN_VALIDATED_REQUEST_KEYS

    def test_no_forbidden_key_is_a_field(self) -> None:
        fields = {f.name for f in dataclasses.fields(ValidatedRequest)}
        assert FORBIDDEN_VALIDATED_REQUEST_KEYS.isdisjoint(fields)


class TestRejectedRequestNotice:
    def test_construction_and_defaults(self) -> None:
        n = RejectedRequestNotice(
            request_id="req-2",
            trace_root="trace-2",
            source_class=SourceClass.SERVICE,
            received_at_iso="2026-01-01T00:00:00Z",
            rejection_stage="E2",
            rejection_reason=IngressReasonCode.AUTH_REQUIRED,
            reason_codes=(IngressReasonCode.AUTH_REQUIRED,),
        )
        assert n.retry_after_seconds is None
        assert n.machine_readable_detail == {}

    def test_machine_readable_detail_independent_per_instance(self) -> None:
        a = RejectedRequestNotice(
            request_id="a",
            trace_root="t",
            source_class=None,
            received_at_iso="x",
            rejection_stage="E1",
            rejection_reason=IngressReasonCode.EMPTY_PAYLOAD,
            reason_codes=(),
        )
        b = RejectedRequestNotice(
            request_id="b",
            trace_root="t",
            source_class=None,
            received_at_iso="x",
            rejection_stage="E1",
            rejection_reason=IngressReasonCode.EMPTY_PAYLOAD,
            reason_codes=(),
        )
        assert a.machine_readable_detail is not b.machine_readable_detail

    def test_frozen(self) -> None:
        n = RejectedRequestNotice(
            request_id="r",
            trace_root="t",
            source_class=None,
            received_at_iso="x",
            rejection_stage="E1",
            rejection_reason=IngressReasonCode.EMPTY_PAYLOAD,
            reason_codes=(),
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            n.rejection_stage = "E2"  # type: ignore[misc]


class TestIngressAuditRecord:
    def test_construction(self) -> None:
        rec = IngressAuditRecord(
            request_id="req-3",
            trace_root="trace-3",
            received_at_iso="2026-01-01T00:00:00Z",
            source_class=SourceClass.BATCH,
            accepted=True,
            rejection_reason=None,
            reason_codes=(),
            auth_verdict=AuthVerdict.SERVICE_BOUND,
            quota_verdict=QuotaVerdict.ALLOWED,
            schema_verdict=SchemaVerdict.VALID,
            normalization_verdict=NormalizationVerdict.NORMALIZED,
            raw_payload_hash="r",
            normalized_payload_hash="n",
            duration_ms=12.5,
        )
        assert rec.accepted is True
        assert rec.duration_ms == 12.5

    def test_frozen(self) -> None:
        rec = IngressAuditRecord(
            request_id="r",
            trace_root="t",
            received_at_iso="x",
            source_class=None,
            accepted=False,
            rejection_reason=IngressReasonCode.AUTH_REQUIRED,
            reason_codes=(IngressReasonCode.AUTH_REQUIRED,),
            auth_verdict=None,
            quota_verdict=None,
            schema_verdict=None,
            normalization_verdict=None,
            raw_payload_hash="",
            normalized_payload_hash="",
            duration_ms=0.0,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            rec.accepted = True  # type: ignore[misc]
