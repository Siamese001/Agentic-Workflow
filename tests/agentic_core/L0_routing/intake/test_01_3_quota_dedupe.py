"""Tests for 01.3 Quota / Size / Duplicate receipts."""

from __future__ import annotations

from agentic_core.L0_routing.intake import (
    DUPLICATE_CLASSES,
    DuplicateRequestFingerprint,
    DuplicateSuppressionReceipt,
    IntakePipeline,
    IntakePolicy,
    QuotaReceipt,
    RawIngressEnvelope,
)
from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode
from agentic_core.L0_routing.intake.stages import QuotaState


def _pipe(state: QuotaState | None = None) -> IntakePipeline:
    return IntakePipeline(IntakePolicy(quota=state or QuotaState()))


def test_quota_receipt_emitted_when_allowed() -> None:
    out = _pipe().run(RawIngressEnvelope(transport="chat", body_text="hi"))
    assert out.accepted
    qr = out.receipt_bundle.quota_receipt
    assert isinstance(qr, QuotaReceipt)
    assert qr.allowed_to_continue_intake is True
    assert qr.rate_limit_status == "ok"
    assert qr.deterministic_receipt_hash != ""


def test_quota_receipt_marks_too_large_when_payload_oversize() -> None:
    state = QuotaState(max_envelope_bytes=10)
    out = _pipe(state).run(RawIngressEnvelope(transport="chat", body_text="x" * 1000))
    assert not out.accepted
    qr = out.receipt_bundle.quota_receipt
    assert qr is not None
    assert qr.allowed_to_continue_intake is False
    assert qr.request_size_status == "too_large"
    assert IngressReasonCode.PAYLOAD_TOO_LARGE in qr.reason_codes


def test_duplicate_suppression_on_idempotency_key() -> None:
    state = QuotaState()
    pipe = _pipe(state)
    env = RawIngressEnvelope(
        transport="api",
        body_json={"x": 1},
        auth_credential={"kind": "api_key", "token": "t"},
        idempotency_key="idem-1",
    )
    a = pipe.run(env)
    assert a.accepted
    assert a.receipt_bundle.duplicate_suppression_receipt is not None
    assert a.receipt_bundle.duplicate_suppression_receipt.duplicate_detected is False

    # Second submission with same idempotency_key
    b = pipe.run(env)
    assert not b.accepted
    dsr = b.receipt_bundle.duplicate_suppression_receipt
    assert isinstance(dsr, DuplicateSuppressionReceipt)
    assert dsr.duplicate_detected is True
    assert dsr.duplicate_class in DUPLICATE_CLASSES
    assert dsr.suppress_or_continue == "suppress"


def test_duplicate_fingerprint_is_deterministic() -> None:
    fp1 = DuplicateRequestFingerprint(
        fingerprint_id="fp:1",
        raw_payload_hash="abc",
        normalized_payload_pre_hash=None,
        principal_id_hash="ph",
        tenant_id="t1",
        session_id="s1",
        transport="chat",
        idempotency_key="idem",
        dedupe_window=60,
    ).with_hash()
    fp2 = DuplicateRequestFingerprint(
        fingerprint_id="fp:2",
        raw_payload_hash="abc",
        normalized_payload_pre_hash=None,
        principal_id_hash="ph",
        tenant_id="t1",
        session_id="s1",
        transport="chat",
        idempotency_key="idem",
        dedupe_window=60,
    ).with_hash()
    assert fp1.fingerprint_hash == fp2.fingerprint_hash
    # Tenant boundary changes invalidate the hash
    fp3 = DuplicateRequestFingerprint(
        fingerprint_id="fp:3",
        raw_payload_hash="abc",
        normalized_payload_pre_hash=None,
        principal_id_hash="ph",
        tenant_id="t2",  # changed
        session_id="s1",
        transport="chat",
        idempotency_key="idem",
        dedupe_window=60,
    ).with_hash()
    assert fp3.fingerprint_hash != fp1.fingerprint_hash
