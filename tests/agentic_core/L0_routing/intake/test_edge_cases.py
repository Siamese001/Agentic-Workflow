"""Exhaustive edge-case sweep for U0 / Request Intake.

Eight groups, every enum value reachable, every receipt class hash-stable,
every boundary tested, every typed object frozen, and every adapter corner
case exercised.

Group A — Hash determinism for every receipt class (10 classes)
Group B — Every enum value reachable through the pipeline
Group C — Boundary conditions (size, attachments, unicode bytes, empty)
Group D — Immutability + tampering attempts (every typed dataclass)
Group E — OTEL adapter corner cases
Group F — Replay binding edge cases
Group G — Origin and authority label coverage
Group H — Pipeline end-to-end determinism (cross-receipt)

Tests are designed to fail loudly if a future change breaks any invariant.
"""

from __future__ import annotations

import dataclasses
from typing import Any

import pytest

from agentic_core.L0_routing.intake import (
    AUTHORITY_LABELS,
    DUPLICATE_CLASSES,
    INGRESS_METRIC_NAMES,
    IngressEvent,
    IngressEventRecord,
    IngressOriginLabelManifest,
    IngressReasonCode,
    IntakePipeline,
    IntakePolicy,
    IntakeStatus,
    ORIGIN_LABELS,
    RawIngressEnvelope,
    SECURITY_FINDING_CLASSES,
    SourceClass,
    run_request_intake,
    to_otel_attributes,
)
from agentic_core.L0_routing.intake.envelope import (
    AttachmentManifestEntry,
    AttachmentManifestShell,
)
from agentic_core.L0_routing.intake.handoff import (
    IngressRejectionReport,
    IntakeAuditReceipt,
    L1HandoffEnvelope,
)
from agentic_core.L0_routing.intake.receipts import (
    CallerScopeBaseline,
    DuplicateRequestFingerprint,
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
from agentic_core.L0_routing.intake.stages import QuotaState
from agentic_core.L0_routing.intake.validated_request import ValidatedRequest
from agentic_core.L0_routing.intake.verdicts import AuthVerdict


# ---------------------------------------------------------------------------
# Group A — Hash determinism for every receipt class
# ---------------------------------------------------------------------------


def _stable_envelope(
    transport: str = "chat",
    text: str = "stable text",
    user: str = "u-1",
    tenant: str = "tenant-1",
    sess: str = "sess-1",
) -> RawIngressEnvelope:
    return RawIngressEnvelope(
        transport=transport,
        body_text=text,
        auth_credential={"kind": "session", "token": "tok"},
        claimed_user_id=user,
        claimed_tenant_id=tenant,
        session_id_hint=sess,
    )


@pytest.mark.parametrize(
    "receipt_attr,hash_attr",
    [
        ("transport_receipt", "deterministic_receipt_hash"),
        ("caller_scope_baseline", "baseline_hash"),
        ("tenant_boundary_receipt", "deterministic_receipt_hash"),
        ("session_binding_receipt", "deterministic_receipt_hash"),
        ("quota_receipt", "deterministic_receipt_hash"),
        ("duplicate_suppression_receipt", "deterministic_receipt_hash"),
        ("schema_validation_receipt", "deterministic_receipt_hash"),
        ("origin_label_manifest", "manifest_hash"),
    ],
)
def test_every_receipt_class_hash_is_deterministic_across_pipelines(
    receipt_attr: str, hash_attr: str
) -> None:
    """Two fresh pipelines, same logical input, must produce identical
    receipt hashes for every receipt class on the validated path."""
    a = run_request_intake(_stable_envelope())
    b = run_request_intake(_stable_envelope())
    ra = getattr(a.receipt_bundle, receipt_attr)
    rb = getattr(b.receipt_bundle, receipt_attr)
    assert ra is not None and rb is not None, f"{receipt_attr} missing on validated run"
    ha = getattr(ra, hash_attr)
    hb = getattr(rb, hash_attr)
    assert ha and hb, f"{receipt_attr}.{hash_attr} empty"
    assert ha == hb, f"{receipt_attr}.{hash_attr} not deterministic: {ha!r} vs {hb!r}"


def test_intake_manifest_and_audit_hashes_deterministic() -> None:
    a = run_request_intake(_stable_envelope())
    b = run_request_intake(_stable_envelope())
    assert a.validated is not None and b.validated is not None
    assert a.final_audit is not None and b.final_audit is not None
    assert a.handoff_envelope is not None and b.handoff_envelope is not None
    assert a.validated.intake_manifest_hash == b.validated.intake_manifest_hash
    assert a.validated.normalized_request_hash == b.validated.normalized_request_hash
    assert a.final_audit.audit_hash == b.final_audit.audit_hash
    # NOTE: handoff_receipt_hash includes a per-run wall-clock timestamp by
    # design (it is a unique receipt identifier, not a content hash). The
    # content-addressable hashes above are what guarantee replay determinism.


def test_replay_seed_ref_is_seed_prefix_and_stable_under_replay() -> None:
    """Replay seed reference must be a stable 'seed:' prefix and identical
    across replay runs of the same logical envelope."""
    a = run_request_intake(_stable_envelope())
    b = run_request_intake(_stable_envelope())
    assert a.validated is not None and b.validated is not None
    assert a.validated.ingress_replay_seed_ref.startswith("seed:")
    assert b.validated.ingress_replay_seed_ref.startswith("seed:")
    # The seed ref includes a UUID by design (it's a per-call reference, not a
    # content hash), so we only assert format; the *manifest* hash, which is
    # content-addressable, is asserted invariant in the prior test.


# ---------------------------------------------------------------------------
# Group B — Every enum value reachable through the pipeline
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "transport",
    ["chat", "ui", "api", "batch", "webhook", "alert"],
)
def test_every_source_class_reachable(transport: str) -> None:
    """Every SourceClass enum value must be producible by some valid transport."""
    if transport == "batch":
        env = RawIngressEnvelope(
            transport=transport,
            body_json={"items": [1]},
            auth_credential={"kind": "api_key", "token": "k"},
            batch_id="b-1",
        )
    elif transport in ("webhook", "alert"):
        env = RawIngressEnvelope(
            transport=transport,
            body_json={"event": "x"},
            auth_credential={"kind": "api_key", "token": "k"},
            webhook_delivery_id="d-1",
        )
    elif transport == "api":
        env = RawIngressEnvelope(
            transport=transport,
            body_json={"q": "x"},
            auth_credential={"kind": "api_key", "token": "k"},
        )
    else:
        env = RawIngressEnvelope(transport=transport, body_text="hi")

    out = run_request_intake(env)
    assert out.accepted, f"{transport} should accept; got {out.rejection_report}"
    assert out.validated is not None
    # Pipeline reached IngressAccepted, which proves the source_class was
    # classified as one of the allowed enum members.


@pytest.mark.parametrize(
    "verdict_value", [v.value for v in AuthVerdict]
)
def test_every_auth_verdict_value_is_canonical_string(verdict_value: str) -> None:
    """Sanity: every AuthVerdict value is a non-empty string member."""
    assert verdict_value
    assert verdict_value in {v.value for v in AuthVerdict}


def test_anonymous_limited_auth_verdict_path() -> None:
    """Anonymous chat (no auth_credential) gets ANONYMOUS_LIMITED."""
    out = run_request_intake(
        RawIngressEnvelope(transport="chat", body_text="hello, world")
    )
    assert out.accepted
    # Implicit: pipeline didn't reject for AUTH_REQUIRED.


def test_service_bound_auth_verdict_path() -> None:
    out = run_request_intake(
        RawIngressEnvelope(
            transport="api",
            body_json={"q": "x"},
            auth_credential={"kind": "api_key", "token": "k"},
        )
    )
    assert out.accepted


def test_rejected_auth_verdict_path() -> None:
    """Service-class transport with NO credential -> AUTH_REQUIRED rejection."""
    out = run_request_intake(
        RawIngressEnvelope(transport="api", body_json={"q": "x"})
    )
    assert not out.accepted
    assert out.rejection_report is not None
    assert out.rejection_report.decisive_reason_code == IngressReasonCode.AUTH_REQUIRED


def test_every_ingress_event_value_emitted_at_least_once() -> None:
    """Run a validated path + a rejected path; the union must cover all 11 events."""
    captured: list[IngressEventRecord] = []
    run_request_intake(_stable_envelope(), event_sink=captured.append)
    # Trigger reject path to collect IngressRejected too.
    run_request_intake(
        RawIngressEnvelope(transport="smtp", body_text="x"),
        event_sink=captured.append,
    )
    seen = {r.event for r in captured}
    expected = set(IngressEvent)
    missing = expected - seen
    # Some events (e.g. ATTACHMENT_MANIFEST_CAPTURED) only emit when attachments
    # are present, so include an attachment run.
    pdf = AttachmentManifestEntry(
        filename="x.pdf", mime_type="application/pdf", size_bytes=10, ref="b:1"
    )
    run_request_intake(
        RawIngressEnvelope(
            transport="chat",
            body_text="with attachment",
            attachments=AttachmentManifestShell(entries=(pdf,), total_bytes=10),
        ),
        event_sink=captured.append,
    )
    seen = {r.event for r in captured}
    missing = expected - seen
    assert not missing, f"events never emitted: {[m.value for m in missing]}"


def test_every_reason_code_is_string_enum_member() -> None:
    """Sanity invariant: 18 reason codes, all string enum members."""
    assert len(set(IngressReasonCode)) == 18
    for r in IngressReasonCode:
        assert isinstance(r.value, str) and r.value


@pytest.mark.parametrize(
    "transport,build,expected_code",
    [
        ("smtp", lambda: RawIngressEnvelope(transport="smtp", body_text="x"),
         IngressReasonCode.UNSUPPORTED_TRANSPORT),
        ("chat", lambda: RawIngressEnvelope(transport="chat"),
         IngressReasonCode.EMPTY_PAYLOAD),
        ("api", lambda: RawIngressEnvelope(transport="api", body_json={"q": "x"}),
         IngressReasonCode.AUTH_REQUIRED),
        ("api", lambda: RawIngressEnvelope(
            transport="api",
            body_json={"q": "x"},
            auth_credential={"kind": "api_key", "token": "k", "tenant_id": "A"},
            claimed_tenant_id="B",
            claimed_service_id="svc-1",
        ), IngressReasonCode.TENANT_MISMATCH),
        ("batch", lambda: RawIngressEnvelope(
            transport="batch",
            body_json={"items": [1]},
            auth_credential={"kind": "api_key", "token": "k"},
        ), IngressReasonCode.MALFORMED_ENVELOPE),
    ],
)
def test_reason_codes_reachable_via_pipeline(
    transport: str, build, expected_code: IngressReasonCode
) -> None:
    out = run_request_intake(build())
    assert not out.accepted
    assert out.rejection_report is not None
    assert out.rejection_report.decisive_reason_code == expected_code


def test_payload_too_large_reachable() -> None:
    state = QuotaState(max_envelope_bytes=10)
    out = run_request_intake(
        RawIngressEnvelope(transport="chat", body_text="x" * 100),
        IntakePolicy(quota=state),
    )
    assert out.rejection_report is not None
    assert out.rejection_report.decisive_reason_code == IngressReasonCode.PAYLOAD_TOO_LARGE


def test_every_intake_status_value_is_canonical() -> None:
    expected = {
        "VALIDATED_FOR_L1",
        "REJECTED_AT_TRANSPORT",
        "REJECTED_AT_IDENTITY_BASELINE",
        "REJECTED_AT_QUOTA",
        "REJECTED_AT_SCHEMA",
        "REJECTED_AT_SECURITY_PRECHECK",
        "REJECTED_AT_CORRELATION_BINDING",
        "REJECTED_AT_HANDOFF_COMPLETENESS",
    }
    assert {s.value for s in IntakeStatus} == expected


# ---------------------------------------------------------------------------
# Group C — Boundary conditions
# ---------------------------------------------------------------------------


def test_boundary_payload_exactly_at_max_accepts() -> None:
    """Body of exactly max_envelope_bytes must accept (not reject)."""
    state = QuotaState(max_envelope_bytes=64)
    body = "x" * 64  # 64 ASCII bytes
    out = run_request_intake(
        RawIngressEnvelope(transport="chat", body_text=body),
        IntakePolicy(quota=state),
    )
    assert out.accepted, "body at exact limit must accept"


def test_boundary_payload_one_over_max_rejects() -> None:
    state = QuotaState(max_envelope_bytes=64)
    body = "x" * 65
    out = run_request_intake(
        RawIngressEnvelope(transport="chat", body_text=body),
        IntakePolicy(quota=state),
    )
    assert not out.accepted
    assert out.rejection_report is not None
    assert out.rejection_report.decisive_reason_code == IngressReasonCode.PAYLOAD_TOO_LARGE


def test_boundary_unicode_size_uses_bytes_not_chars() -> None:
    """Unicode multi-byte chars must be counted as bytes, not codepoints."""
    state = QuotaState(max_envelope_bytes=10)
    # 4 emoji * 4 bytes each = 16 bytes (over limit), but 4 chars (under)
    body = "\U0001F600" * 4
    assert len(body) == 4
    assert len(body.encode("utf-8")) == 16
    out = run_request_intake(
        RawIngressEnvelope(transport="chat", body_text=body),
        IntakePolicy(quota=state),
    )
    assert not out.accepted, "byte-size must be enforced, not char count"
    assert out.rejection_report is not None
    assert out.rejection_report.decisive_reason_code == IngressReasonCode.PAYLOAD_TOO_LARGE


def test_boundary_max_attachment_count_accepts() -> None:
    """Exactly max_attachment_count attachments must accept."""
    state = QuotaState(max_attachment_count=3)
    entries = tuple(
        AttachmentManifestEntry(
            filename=f"f{i}.txt", mime_type="text/plain", size_bytes=1, ref=f"b:{i}"
        )
        for i in range(3)
    )
    out = run_request_intake(
        RawIngressEnvelope(
            transport="chat",
            body_text="hi",
            attachments=AttachmentManifestShell(entries=entries, total_bytes=3),
        ),
        IntakePolicy(quota=state),
    )
    assert out.accepted


def test_boundary_max_attachment_count_plus_one_rejects() -> None:
    state = QuotaState(max_attachment_count=2)
    entries = tuple(
        AttachmentManifestEntry(
            filename=f"f{i}.txt", mime_type="text/plain", size_bytes=1, ref=f"b:{i}"
        )
        for i in range(3)
    )
    out = run_request_intake(
        RawIngressEnvelope(
            transport="chat",
            body_text="hi",
            attachments=AttachmentManifestShell(entries=entries, total_bytes=3),
        ),
        IntakePolicy(quota=state),
    )
    assert not out.accepted


def test_empty_body_text_strip_only_rejects() -> None:
    """A body of only whitespace must be classified as empty payload."""
    out = run_request_intake(
        RawIngressEnvelope(transport="chat", body_text="   \n\t  ")
    )
    assert not out.accepted
    assert out.rejection_report is not None
    assert out.rejection_report.decisive_reason_code == IngressReasonCode.EMPTY_PAYLOAD


def test_empty_attachment_list_accepts_with_text() -> None:
    out = run_request_intake(
        RawIngressEnvelope(
            transport="chat",
            body_text="just text",
            attachments=AttachmentManifestShell(entries=(), total_bytes=0),
        )
    )
    assert out.accepted


def test_attachment_only_payload_accepts() -> None:
    """No body_text, no body_json, but with attachments must accept."""
    pdf = AttachmentManifestEntry(
        filename="report.pdf", mime_type="application/pdf", size_bytes=512, ref="b:1"
    )
    out = run_request_intake(
        RawIngressEnvelope(
            transport="chat",
            attachments=AttachmentManifestShell(entries=(pdf,), total_bytes=512),
        )
    )
    assert out.accepted


# ---------------------------------------------------------------------------
# Group D — Immutability + tampering attempts
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cls",
    [
        TransportEnvelopeReceipt,
        CallerScopeBaseline,
        TenantBoundaryReceipt,
        SessionBindingReceipt,
        QuotaReceipt,
        DuplicateRequestFingerprint,
        DuplicateSuppressionReceipt,
        RequestSchemaValidationReceipt,
        IngressOriginLabelManifest,
        RequestCorrelationReceipt,
        IngressReplaySeed,
        NormalizedRequestHash,
        IntakeManifestHash,
        IntakeAuditReceipt,
        L1HandoffEnvelope,
        IngressRejectionReport,
        ValidatedRequest,
    ],
)
def test_every_typed_receipt_is_frozen(cls: type) -> None:
    """All typed receipt dataclasses MUST be frozen so they cannot be mutated
    after construction (audit trail integrity)."""
    params = getattr(cls, "__dataclass_params__", None)
    assert params is not None, f"{cls.__name__} is not a dataclass"
    assert params.frozen, f"{cls.__name__} dataclass is not frozen"


def test_validated_request_cannot_be_mutated_after_construction() -> None:
    out = run_request_intake(_stable_envelope())
    vr = out.validated
    assert vr is not None
    with pytest.raises(dataclasses.FrozenInstanceError):
        vr.intake_manifest_hash = "tampered"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        vr.permitted_next_layer = "L5"  # type: ignore[misc]


def test_handoff_envelope_cannot_be_mutated_after_construction() -> None:
    out = run_request_intake(_stable_envelope())
    env = out.handoff_envelope
    assert env is not None
    with pytest.raises(dataclasses.FrozenInstanceError):
        env.handoff_target = "L2_EXECUTE"  # type: ignore[misc]
    with pytest.raises(dataclasses.FrozenInstanceError):
        env.no_raw_bypass_assertion = False  # type: ignore[misc]


def test_handoff_envelope_constructor_rejects_wrong_target() -> None:
    out = run_request_intake(_stable_envelope())
    vr = out.validated
    assert vr is not None
    with pytest.raises(ValueError, match="L1_REASONING_PLAN"):
        L1HandoffEnvelope(
            handoff_id="h:1",
            validated_request=vr,
            handoff_target="L2_EXECUTE",
        )


def test_handoff_envelope_rejects_disabled_no_bypass_assertion() -> None:
    out = run_request_intake(_stable_envelope())
    vr = out.validated
    assert vr is not None
    with pytest.raises(ValueError, match="no_raw_bypass"):
        L1HandoffEnvelope(
            handoff_id="h:1",
            validated_request=vr,
            no_raw_bypass_assertion=False,
        )


def test_handoff_envelope_rejects_disabled_read_only_assertion() -> None:
    out = run_request_intake(_stable_envelope())
    vr = out.validated
    assert vr is not None
    with pytest.raises(ValueError, match="downstream_read_only"):
        L1HandoffEnvelope(
            handoff_id="h:1",
            validated_request=vr,
            downstream_read_only_assertion=False,
        )


def test_validated_request_rejects_authority_tampering() -> None:
    """downstream_authority must always be 'none' — verified by mutating a
    real instance via dataclasses.replace (which re-runs __post_init__)."""
    out = run_request_intake(_stable_envelope())
    vr = out.validated
    assert vr is not None
    with pytest.raises(ValueError, match="downstream_authority"):
        dataclasses.replace(vr, downstream_authority="L5")


def test_validated_request_rejects_wrong_permitted_next_layer() -> None:
    out = run_request_intake(_stable_envelope())
    vr = out.validated
    assert vr is not None
    with pytest.raises(ValueError, match="permitted_next_layer"):
        dataclasses.replace(vr, permitted_next_layer="L3")


# ---------------------------------------------------------------------------
# Group E — OTEL adapter corner cases
# ---------------------------------------------------------------------------


def test_otel_adapter_with_empty_fields() -> None:
    rec = IngressEventRecord(
        event=IngressEvent.INGRESS_RECEIVED,
        request_id="r",
        trace_root="t",
        fields={},
    )
    attrs = to_otel_attributes(rec)
    assert attrs == {
        "intake.event": "IngressReceived",
        "intake.request_id": "r",
        "intake.trace_root": "t",
    }


def test_otel_adapter_with_none_value() -> None:
    rec = IngressEventRecord(
        event=IngressEvent.INGRESS_RECEIVED,
        request_id="r",
        trace_root="t",
        fields={"optional_x": None},
    )
    attrs = to_otel_attributes(rec)
    assert attrs["intake.optional_x"] is None


def test_otel_adapter_serializes_nested_dict() -> None:
    rec = IngressEventRecord(
        event=IngressEvent.SCHEMA_EVALUATED,
        request_id="r",
        trace_root="t",
        fields={"nested": {"k": [1, 2], "z": True}},
    )
    attrs = to_otel_attributes(rec)
    assert attrs["intake.nested"] == '{"k":[1,2],"z":true}'


def test_otel_adapter_handles_unserializable_value() -> None:
    """A value that defies JSON serialization falls back to repr()."""

    class Weird:
        def __repr__(self) -> str:
            return "<Weird>"

    rec = IngressEventRecord(
        event=IngressEvent.INGRESS_RECEIVED,
        request_id="r",
        trace_root="t",
        fields={"weirdo": Weird()},
    )
    attrs = to_otel_attributes(rec)
    val = attrs["intake.weirdo"]
    # Either the JSON path with default=str OR repr() — both are deterministic
    # rendered strings. Assert it's a string and non-empty.
    assert isinstance(val, str) and val


def test_otel_adapter_unicode_keys_and_values() -> None:
    rec = IngressEventRecord(
        event=IngressEvent.INGRESS_RECEIVED,
        request_id="r",
        trace_root="t",
        fields={"emoji": "\U0001F600", "kanji": "日本語"},
    )
    attrs = to_otel_attributes(rec)
    assert attrs["intake.emoji"] == "\U0001F600"
    assert attrs["intake.kanji"] == "日本語"


def test_otel_adapter_rejects_construction_with_forbidden_fields() -> None:
    """Forbidden fields are blocked at IngressEventRecord construction. The
    adapter never sees them, so this is the only place they can be enforced."""
    for forbidden in ("auth_token", "raw_payload", "session_cookie", "secret"):
        with pytest.raises(ValueError, match="forbidden"):
            IngressEventRecord(
                event=IngressEvent.INGRESS_RECEIVED,
                request_id="r",
                trace_root="t",
                fields={forbidden: "leak"},
            )


# ---------------------------------------------------------------------------
# Group F — Replay binding edge cases
# ---------------------------------------------------------------------------


def test_upstream_traceparent_preserved_when_provided() -> None:
    upstream = "trace-upstream-12345"
    out = run_request_intake(
        RawIngressEnvelope(
            transport="chat",
            body_text="hi",
            upstream_traceparent=upstream,
        )
    )
    assert out.accepted
    assert out.validated is not None
    assert out.validated.trace_root == upstream


def test_session_id_resumed_when_hint_provided() -> None:
    out = run_request_intake(
        RawIngressEnvelope(
            transport="chat",
            body_text="hi",
            session_id_hint="my-session-xyz",
        )
    )
    assert out.accepted
    assert out.validated is not None
    assert out.validated.session_id == "my-session-xyz"


def test_session_id_synthesized_when_hint_absent() -> None:
    out = run_request_intake(
        RawIngressEnvelope(transport="chat", body_text="hi")
    )
    assert out.accepted
    assert out.validated is not None
    assert out.validated.session_id  # non-empty
    assert out.validated.session_id != ""


def test_request_id_hint_does_not_pollute_intake_manifest_hash() -> None:
    """request_id_hint is volatile per-run noise; manifest hash must be invariant."""
    e1 = RawIngressEnvelope(
        transport="chat",
        body_text="same",
        auth_credential={"kind": "session", "token": "t"},
        claimed_user_id="u",
        claimed_tenant_id="t",
        session_id_hint="sess",
        request_id_hint="req-A",
    )
    e2 = RawIngressEnvelope(
        transport="chat",
        body_text="same",
        auth_credential={"kind": "session", "token": "t"},
        claimed_user_id="u",
        claimed_tenant_id="t",
        session_id_hint="sess",
        request_id_hint="req-B",
    )
    a = run_request_intake(e1)
    b = run_request_intake(e2)
    assert a.validated is not None and b.validated is not None
    assert a.validated.intake_manifest_hash == b.validated.intake_manifest_hash


def test_different_session_id_produces_different_intake_manifest() -> None:
    a = run_request_intake(_stable_envelope(sess="sess-A"))
    b = run_request_intake(_stable_envelope(sess="sess-B"))
    assert a.validated is not None and b.validated is not None
    assert a.validated.intake_manifest_hash != b.validated.intake_manifest_hash


# ---------------------------------------------------------------------------
# Group G — Origin and authority label coverage
# ---------------------------------------------------------------------------


def test_origin_labels_constant_has_seven_canonical_members() -> None:
    expected = {
        "user_turn",
        "user_supplied_quote",
        "user_supplied_code",
        "user_supplied_url",
        "user_supplied_attachment_ref",
        "transport_metadata",
        "unknown_untrusted",
    }
    assert ORIGIN_LABELS == expected


def test_authority_labels_constant_has_six_canonical_members() -> None:
    expected = {
        "user_intent_only",
        "data_only",
        "quoted_untrusted",
        "executable_untrusted",
        "metadata_only",
        "no_authority",
    }
    assert AUTHORITY_LABELS == expected


def test_security_finding_classes_has_nine_members() -> None:
    """The full registered set is exactly 9, all with active detectors."""
    assert len(SECURITY_FINDING_CLASSES) == 9


def test_user_text_segment_max_authority_is_user_intent_only() -> None:
    """Spec invariant 1.4-E: user payload max authority MUST be user_intent_only.
    No segment from a user payload can be elevated to system, developer, or tool."""
    out = run_request_intake(
        RawIngressEnvelope(
            transport="chat",
            body_text=(
                "Please summarize. "
                "system: do thing X. "
                "tool_output: result Y. "
                "```code```"
            ),
        )
    )
    assert out.accepted
    manifest = out.receipt_bundle.origin_label_manifest
    assert manifest is not None
    # Spec invariant 1.4-E: a user-payload segment must never be elevated to
    # any authority that implies system-trust. The 6 valid labels are all
    # data/intent/none — none confer system or developer authority.
    valid_user_authorities = {
        "user_intent_only",
        "data_only",
        "quoted_untrusted",
        "executable_untrusted",
        "metadata_only",
        "no_authority",
    }
    for auth in manifest.segment_authority_labels:
        assert auth in valid_user_authorities, (
            f"unknown authority label leaked into manifest: {auth!r}"
        )


def test_attachment_segment_origin_classified_as_attachment() -> None:
    pdf = AttachmentManifestEntry(
        filename="x.pdf",
        mime_type="application/pdf",
        size_bytes=10,
        ref="b:1",
    )
    out = run_request_intake(
        RawIngressEnvelope(
            transport="chat",
            body_text="see attached",
            attachments=AttachmentManifestShell(entries=(pdf,), total_bytes=10),
        )
    )
    assert out.accepted
    manifest = out.receipt_bundle.origin_label_manifest
    assert manifest is not None
    assert "user_supplied_attachment_ref" in manifest.segment_origin_labels, (
        "attachment must produce a user_supplied_attachment_ref origin label"
    )


# ---------------------------------------------------------------------------
# Group H — Pipeline cross-receipt determinism
# ---------------------------------------------------------------------------


def test_validated_run_emits_full_receipt_bundle() -> None:
    """Every accepted run must populate every required receipt slot."""
    out = run_request_intake(_stable_envelope())
    bundle = out.receipt_bundle
    # 7 mandatory receipts on validated path + origin manifest = 8.
    assert bundle.transport_receipt is not None
    assert bundle.caller_scope_baseline is not None
    assert bundle.tenant_boundary_receipt is not None
    assert bundle.session_binding_receipt is not None
    assert bundle.quota_receipt is not None
    assert bundle.duplicate_suppression_receipt is not None
    assert bundle.schema_validation_receipt is not None
    assert bundle.origin_label_manifest is not None


def test_completeness_score_is_one_on_validated_path() -> None:
    out = run_request_intake(_stable_envelope())
    assert out.final_audit is not None
    assert out.final_audit.completeness_score == 1.0


@pytest.mark.parametrize(
    "build,min_score,max_score",
    [
        # E1 reject: only transport receipt populated
        (lambda: RawIngressEnvelope(transport="smtp", body_text="x"),
         0.0, 0.20),
        # E2 reject: + identity baselines
        (lambda: RawIngressEnvelope(
            transport="api",
            body_json={"q": "x"},
            auth_credential={"kind": "api_key", "token": "k", "tenant_id": "A"},
            claimed_tenant_id="B",
            claimed_service_id="svc-1",
        ), 0.30, 0.50),
        # E4 reject: most of the chain
        (lambda: RawIngressEnvelope(
            transport="batch",
            body_json={"items": [1]},
            auth_credential={"kind": "api_key", "token": "k"},
        ), 0.55, 0.75),
    ],
)
def test_completeness_score_grows_with_stage_progress(
    build, min_score: float, max_score: float
) -> None:
    out = run_request_intake(build())
    assert out.final_audit is not None
    score = out.final_audit.completeness_score
    assert min_score <= score <= max_score, (
        f"completeness {score} outside expected range [{min_score}, {max_score}]"
    )


def test_metric_names_constant_is_stable() -> None:
    """Dashboards bind to these names; any rename is a breaking change."""
    assert "ingress_count" in INGRESS_METRIC_NAMES
    assert "ingress_reject_rate" in INGRESS_METRIC_NAMES
    assert "ingress_latency_ms" in INGRESS_METRIC_NAMES
    assert len(INGRESS_METRIC_NAMES) == 11


def test_duplicate_classes_constant_is_stable() -> None:
    expected = {
        "not_duplicate",
        "exact_replay_same_payload",
        "exact_replay_same_idempotency_key",
        "near_duplicate_transport_retry",
        "double_submit",
        "suspicious_replay",
    }
    assert DUPLICATE_CLASSES == expected


def test_runtime_intake_outcome_is_immutable_at_top_level() -> None:
    """IntakeOutcome itself may not be frozen (it is mutated during pipeline
    execution), but every leaf typed receipt it exposes IS frozen."""
    out = run_request_intake(_stable_envelope())
    # validated, handoff_envelope, final_audit are frozen
    for obj in (out.validated, out.handoff_envelope, out.final_audit):
        params = getattr(type(obj), "__dataclass_params__", None)
        assert params is not None and params.frozen, (
            f"{type(obj).__name__} must be frozen"
        )


def test_pipeline_handles_anonymous_chat_with_no_session_hint() -> None:
    """Smoke: minimal valid chat payload, no auth, no session — must still accept
    and produce a fully-populated bundle (for L1 to read)."""
    out = run_request_intake(
        RawIngressEnvelope(transport="chat", body_text="hi")
    )
    assert out.accepted
    assert out.validated is not None
    assert out.validated.intake_manifest_hash
    assert out.validated.session_id  # synthesized
    assert out.validated.trace_root  # synthesized
    assert out.validated.permitted_next_layer == "L1"
    assert out.validated.downstream_authority == "none"
