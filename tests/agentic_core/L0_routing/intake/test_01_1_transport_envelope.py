"""Tests for 01.1 Transport / Envelope Ingress receipts.

Spec source: docs/reference/01_Request_Intake/01.1_Transport_Envelope_Ingress_detailed.md
"""

from __future__ import annotations

from agentic_core.L0_routing.intake import (
    IntakePipeline,
    IntakePolicy,
    MalformedEnvelopeReport,
    RawIngressEnvelope,
    TransportEnvelopeReceipt,
)
from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode


def _pipe() -> IntakePipeline:
    return IntakePipeline(IntakePolicy())


def test_transport_receipt_emitted_on_accept() -> None:
    out = _pipe().run(RawIngressEnvelope(transport="chat", body_text="hi"))
    assert out.accepted
    tep = out.receipt_bundle.transport_receipt
    assert isinstance(tep, TransportEnvelopeReceipt)
    assert tep.accepted_transport is True
    assert tep.transport == "chat"
    assert tep.frame_parse_status == "ok"
    assert tep.deterministic_receipt_hash != ""


def test_transport_receipt_emitted_on_reject_with_reason_codes() -> None:
    out = _pipe().run(RawIngressEnvelope(transport="smtp", body_text="x"))
    assert not out.accepted
    tep = out.receipt_bundle.transport_receipt
    assert isinstance(tep, TransportEnvelopeReceipt)
    assert tep.accepted_transport is False
    assert IngressReasonCode.UNSUPPORTED_TRANSPORT in tep.rejection_reason_codes


def test_transport_receipt_hash_deterministic() -> None:
    p1 = _pipe()
    p2 = _pipe()
    e1 = RawIngressEnvelope(transport="chat", body_text="hi", request_id_hint="r1")
    e2 = RawIngressEnvelope(transport="chat", body_text="hi", request_id_hint="r1")
    out1 = p1.run(e1)
    out2 = p2.run(e2)
    assert out1.receipt_bundle.transport_receipt is not None
    assert out2.receipt_bundle.transport_receipt is not None
    # Hash should be identical because hash inputs exclude observed_at /
    # receipt_id volatile fields.
    assert (
        out1.receipt_bundle.transport_receipt.deterministic_receipt_hash
        == out2.receipt_bundle.transport_receipt.deterministic_receipt_hash
    )


def test_transport_receipt_excludes_volatile_observed_fields() -> None:
    """receipt_id is volatile per-call but the hash field MUST be stable.

    Use two SEPARATE pipelines so the in-process consumed-frames guard
    in E1 doesn't reject the second run as a duplicate transport frame.
    """
    out_a = _pipe().run(RawIngressEnvelope(transport="chat", body_text="hi", request_id_hint="r2"))
    out_b = _pipe().run(RawIngressEnvelope(transport="chat", body_text="hi", request_id_hint="r2"))
    a = out_a.receipt_bundle.transport_receipt
    b = out_b.receipt_bundle.transport_receipt
    assert a is not None and b is not None
    assert a.receipt_id != b.receipt_id  # volatile (uuid)
    # request_id_hint is reused; payload identical → hash should match.
    assert a.deterministic_receipt_hash == b.deterministic_receipt_hash


def test_malformed_envelope_report_construction() -> None:
    # MalformedEnvelopeReport is a typed report builder — exercise its hash.
    report = MalformedEnvelopeReport(
        report_id="rep:1",
        raw_envelope_id="raw:1",
        malformed_class="unsupported_transport",
        decisive_reason=IngressReasonCode.UNSUPPORTED_TRANSPORT,
        parse_error_summary="smtp not in allowlist",
        recoverable_by_user=True,
        safe_user_visible_summary="Channel not supported.",
    ).with_hash()
    assert report.deterministic_report_hash != ""
    # Hash deterministic across rebuilds:
    again = MalformedEnvelopeReport(
        report_id="rep:1",
        raw_envelope_id="raw:1",
        malformed_class="unsupported_transport",
        decisive_reason=IngressReasonCode.UNSUPPORTED_TRANSPORT,
        parse_error_summary="smtp not in allowlist",
        recoverable_by_user=True,
        safe_user_visible_summary="Channel not supported.",
    ).with_hash()
    assert again.deterministic_report_hash == report.deterministic_report_hash
