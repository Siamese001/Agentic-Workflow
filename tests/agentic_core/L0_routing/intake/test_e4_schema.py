"""E4 DID YOU FILL OUT THE FORM? — schema + envelope validity.

Spec section: lines 317-372.
"""

from __future__ import annotations

from agentic_core.L0_routing.intake.envelope import (
    AttachmentManifestEntry,
    AttachmentManifestShell,
    RawIngressEnvelope,
)
from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode
from agentic_core.L0_routing.intake.stages import QuotaState, run_e4_schema
from agentic_core.L0_routing.intake.verdicts import SchemaVerdict, SourceClass


def test_basic_chat_text_passes() -> None:
    env = RawIngressEnvelope(transport="chat", body_text="Hello there")
    res = run_e4_schema(env, SourceClass.USER, state=QuotaState())
    assert res.passed
    assert res.fields["schema_verdict"] is SchemaVerdict.VALID
    assert res.fields["request_shape_class"] == "user_chat"


def test_unknown_envelope_version_rejects() -> None:
    env = RawIngressEnvelope(transport="api", body_json={"x": 1}, extras={"envelope_version": "9.9"})
    res = run_e4_schema(env, SourceClass.SERVICE, state=QuotaState())
    assert not res.passed
    assert IngressReasonCode.MALFORMED_ENVELOPE in res.reason_codes


def test_oversized_text_rejects() -> None:
    env = RawIngressEnvelope(transport="chat", body_text="x" * (300 * 1024))
    res = run_e4_schema(env, SourceClass.USER, state=QuotaState())
    assert not res.passed
    assert IngressReasonCode.PAYLOAD_TOO_LARGE in res.reason_codes


def test_unsupported_mime_rejects() -> None:
    entry = AttachmentManifestEntry(
        filename="evil.exe",
        mime_type="application/x-msdownload",
        size_bytes=1,
        ref="r:1",
    )
    env = RawIngressEnvelope(
        transport="api",
        body_text="x",
        attachments=AttachmentManifestShell(entries=(entry,), total_bytes=1),
    )
    res = run_e4_schema(env, SourceClass.SERVICE, state=QuotaState())
    assert not res.passed
    assert IngressReasonCode.UNSUPPORTED_MODALITY in res.reason_codes


def test_pdf_attachment_passes() -> None:
    entry = AttachmentManifestEntry(
        filename="policy.pdf", mime_type="application/pdf", size_bytes=10, ref="r:1"
    )
    env = RawIngressEnvelope(
        transport="chat",
        body_text="Review this policy",
        attachments=AttachmentManifestShell(entries=(entry,), total_bytes=10),
    )
    res = run_e4_schema(env, SourceClass.USER, state=QuotaState())
    assert res.passed
    mod = res.fields["modality_manifest"]
    assert "file" in mod.observed
    assert "text" in mod.observed


def test_batch_without_batch_id_rejects() -> None:
    env = RawIngressEnvelope(transport="batch", body_json={"items": []})
    res = run_e4_schema(env, SourceClass.BATCH, state=QuotaState())
    assert not res.passed
    assert IngressReasonCode.MALFORMED_ENVELOPE in res.reason_codes


def test_batch_oversize_rejects() -> None:
    state = QuotaState(max_batch_size=2)
    env = RawIngressEnvelope(
        transport="batch",
        body_json={"items": [1, 2, 3, 4, 5]},
        batch_id="b1",
    )
    res = run_e4_schema(env, SourceClass.BATCH, state=state)
    assert not res.passed
    assert IngressReasonCode.PAYLOAD_TOO_LARGE in res.reason_codes


def test_webhook_without_delivery_id_rejects() -> None:
    env = RawIngressEnvelope(transport="webhook", body_json={"a": 1})
    res = run_e4_schema(env, SourceClass.WEBHOOK, state=QuotaState())
    assert not res.passed
    assert IngressReasonCode.MALFORMED_ENVELOPE in res.reason_codes


def test_alert_with_alert_id_passes() -> None:
    env = RawIngressEnvelope(
        transport="alert",
        body_json={"a": 1},
        alert_id="alert-1",
    )
    res = run_e4_schema(env, SourceClass.ALERT, state=QuotaState())
    assert res.passed


def test_bad_url_field_rejects() -> None:
    env = RawIngressEnvelope(
        transport="api",
        body_json={"callback_url": "not a url"},
    )
    res = run_e4_schema(env, SourceClass.SERVICE, state=QuotaState())
    assert not res.passed
    assert IngressReasonCode.FIELD_TYPE_MISMATCH in res.reason_codes


def test_good_url_field_passes() -> None:
    env = RawIngressEnvelope(
        transport="api",
        body_json={"callback_url": "https://example.com/cb"},
    )
    res = run_e4_schema(env, SourceClass.SERVICE, state=QuotaState())
    assert res.passed
