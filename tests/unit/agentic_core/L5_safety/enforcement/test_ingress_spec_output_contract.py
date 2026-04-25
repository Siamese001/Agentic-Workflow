"""Spec-conformance tests for the Ingress Output Contract (W1 + W2).

Validates the additions made to close gaps G1-G9 against
``docs/reference/01_Request_Intake/01_request_intake.md`` lines 95-119
(the INGRESS OUTPUT CONTRACT block) and lines 79-83 (E2 attachment / modality
sub-checks).
"""

from __future__ import annotations

from typing import Any

import pytest

from agentic_core.L5_safety.enforcement.ingress_envelope_check import (
    IngressEnvelopeCheck,
    IngressRejected,
    RejectionReasonCode,
    StampedRequest,
)
from agentic_core.L5_safety.enforcement.rate_limit import UnboundedRateLimiter
from agentic_core.runtime.entry.batch_adapter import BatchIngressAdapter
from agentic_core.runtime.entry.chat_adapter import ChatIngressAdapter
from agentic_core.runtime.entry.http_adapter import HttpIngressAdapter
from agentic_core.runtime.entry.webhook_adapter import WebhookIngressAdapter


def _ok_envelope(**overrides: Any) -> dict[str, Any]:
    env: dict[str, Any] = {
        "schema_version": "1.0",
        "caller_identity": "user-alice",
        "request_payload": {"intent": "tell me a joke"},
        "tenant_id": "tenant-alpha",
    }
    env.update(overrides)
    return env


def _gate(**overrides: Any) -> IngressEnvelopeCheck:
    defaults: dict[str, Any] = {
        "rate_limiter": UnboundedRateLimiter(),
        "enable_safety_screen": False,
    }
    defaults.update(overrides)
    return IngressEnvelopeCheck(**defaults)


# ---------------------------------------------------------------------------
# G1 — ingress_source_class
# ---------------------------------------------------------------------------


def test_ingress_source_class_defaults_to_unknown_when_envelope_unset() -> None:
    out = _gate().check(_ok_envelope())
    assert isinstance(out, StampedRequest)
    assert out.ingress_source_class == "unknown"


@pytest.mark.parametrize(
    "value,expected",
    [
        ("user", "user"),
        ("service", "service"),
        ("batch", "batch"),
        ("webhook", "webhook"),
        ("alert", "alert"),
        ("USER", "user"),  # case-folded
        ("not-a-class", "unknown"),  # invalid -> unknown
    ],
)
def test_ingress_source_class_accepts_valid_and_normalizes(value: str, expected: str) -> None:
    out = _gate().check(_ok_envelope(ingress_source_class=value))
    assert isinstance(out, StampedRequest)
    assert out.ingress_source_class == expected


# ---------------------------------------------------------------------------
# G1 (per-adapter) — each U-adapter tags its own source class
# ---------------------------------------------------------------------------


def test_chat_adapter_tags_user() -> None:
    gate = _gate()
    out = ChatIngressAdapter(gate).handle({"caller_identity": "u-1", "message": "hi"})
    assert isinstance(out, StampedRequest)
    assert out.ingress_source_class == "user"


def test_http_adapter_tags_service() -> None:
    gate = _gate()
    out = HttpIngressAdapter(gate).handle(
        headers={"X-Caller-Identity": "svc-foo"},
        body={"intent": "ping"},
    )
    assert isinstance(out, StampedRequest)
    assert out.ingress_source_class == "service"


def test_batch_adapter_tags_batch() -> None:
    gate = _gate()
    rows = [{"caller_identity": "submitter-1", "request_payload": {"intent": "x"}}]
    results = BatchIngressAdapter(gate).handle_rows(rows, batch_id="b-1")
    assert isinstance(results[0], StampedRequest)
    assert results[0].ingress_source_class == "batch"


def test_webhook_adapter_tags_webhook_default() -> None:
    gate = _gate()
    out = WebhookIngressAdapter(gate).handle(
        headers={},
        body_bytes=b"{}",
        parsed_body={"caller_identity": "hook-1", "request_payload": {"intent": "evt"}},
    )
    assert isinstance(out, StampedRequest)
    assert out.ingress_source_class == "webhook"


def test_webhook_adapter_tags_alert_when_event_kind_alert() -> None:
    gate = _gate()
    out = WebhookIngressAdapter(gate).handle(
        headers={},
        body_bytes=b"{}",
        parsed_body={
            "caller_identity": "hook-1",
            "request_payload": {"intent": "evt"},
            "event_kind": "alert",
        },
    )
    assert isinstance(out, StampedRequest)
    assert out.ingress_source_class == "alert"


# ---------------------------------------------------------------------------
# G2 — auth_verdict
# ---------------------------------------------------------------------------


def test_auth_verdict_authenticated_for_user_caller() -> None:
    out = _gate().check(_ok_envelope(caller_identity="user-alice"))
    assert isinstance(out, StampedRequest)
    assert out.auth_verdict == "authenticated"


def test_auth_verdict_service_bound_for_svc_prefix() -> None:
    out = _gate().check(_ok_envelope(caller_identity="svc-underwriting"))
    assert isinstance(out, StampedRequest)
    assert out.auth_verdict == "service_bound"


def test_auth_verdict_anonymous_for_anon_suffix() -> None:
    out = _gate().check(_ok_envelope(caller_identity="chat-anon"))
    assert isinstance(out, StampedRequest)
    assert out.auth_verdict == "anonymous"


# ---------------------------------------------------------------------------
# G3 — quota_verdict (success path)
# ---------------------------------------------------------------------------


def test_quota_verdict_allowed_on_pass() -> None:
    out = _gate().check(_ok_envelope())
    assert isinstance(out, StampedRequest)
    assert out.quota_verdict == "allowed"


# ---------------------------------------------------------------------------
# G4 — schema_verdict
# ---------------------------------------------------------------------------


def test_schema_verdict_valid_on_pass() -> None:
    out = _gate().check(_ok_envelope())
    assert isinstance(out, StampedRequest)
    assert out.schema_verdict == "valid"


# ---------------------------------------------------------------------------
# G5 — raw_payload_ref
# ---------------------------------------------------------------------------


def test_raw_payload_ref_is_stable_sha256_hash() -> None:
    out_a = _gate().check(_ok_envelope(request_id="r-a"))
    out_b = _gate().check(_ok_envelope(request_id="r-b"))
    assert isinstance(out_a, StampedRequest) and isinstance(out_b, StampedRequest)
    assert out_a.raw_payload_ref.startswith("sha256:")
    # Same payload produces identical content hash even with different request_id.
    assert out_a.raw_payload_ref == out_b.raw_payload_ref


def test_raw_payload_ref_changes_when_payload_changes() -> None:
    a = _gate().check(_ok_envelope(request_payload={"intent": "a"}, request_id="r-a"))
    b = _gate().check(_ok_envelope(request_payload={"intent": "b"}, request_id="r-b"))
    assert isinstance(a, StampedRequest) and isinstance(b, StampedRequest)
    assert a.raw_payload_ref != b.raw_payload_ref


# ---------------------------------------------------------------------------
# G6, G7, G8 — attachment manifest + count + shape
# ---------------------------------------------------------------------------


def test_attachment_manifest_default_empty() -> None:
    out = _gate().check(_ok_envelope())
    assert isinstance(out, StampedRequest)
    assert out.attachment_manifest == ()


def test_attachment_manifest_captured_from_envelope() -> None:
    atts = [
        {"filename": "report.pdf", "size": 1024, "content_type": "application/pdf"},
        {"name": "logo.png", "size": 512, "mime": "image/png"},
    ]
    out = _gate().check(_ok_envelope(attachments=atts))
    assert isinstance(out, StampedRequest)
    assert len(out.attachment_manifest) == 2
    assert out.attachment_manifest[0]["filename"] == "report.pdf"
    assert out.attachment_manifest[1]["filename"] == "logo.png"
    assert out.attachment_manifest[1]["content_type"] == "image/png"


def test_attachment_manifest_captured_from_payload() -> None:
    payload = {
        "intent": "review",
        "attachments": [{"filename": "a.txt", "size": 10}],
    }
    out = _gate().check(_ok_envelope(request_payload=payload))
    assert isinstance(out, StampedRequest)
    assert len(out.attachment_manifest) == 1


def test_attachment_count_too_many_rejected() -> None:
    atts = [{"filename": f"f{i}.bin", "size": 1} for i in range(20)]
    with pytest.raises(IngressRejected) as exc:
        _gate(max_attachments=4).check(_ok_envelope(attachments=atts))
    assert exc.value.slip.reason_code is RejectionReasonCode.TOO_MANY_ATTACHMENTS


def test_attachment_oversized_rejected() -> None:
    with pytest.raises(IngressRejected) as exc:
        _gate(max_attachment_bytes=100).check(
            _ok_envelope(attachments=[{"filename": "big.bin", "size": 1000}])
        )
    assert exc.value.slip.reason_code is RejectionReasonCode.ATTACHMENT_OVERSIZED


def test_attachment_malformed_not_a_list() -> None:
    with pytest.raises(IngressRejected) as exc:
        _gate().check(_ok_envelope(attachments="not-a-list"))
    assert exc.value.slip.reason_code is RejectionReasonCode.ATTACHMENT_MALFORMED


def test_attachment_missing_filename_rejected() -> None:
    with pytest.raises(IngressRejected) as exc:
        _gate().check(_ok_envelope(attachments=[{"size": 10}]))
    assert exc.value.slip.reason_code is RejectionReasonCode.ATTACHMENT_MALFORMED


def test_attachment_missing_size_rejected() -> None:
    with pytest.raises(IngressRejected) as exc:
        _gate().check(_ok_envelope(attachments=[{"filename": "a.txt"}]))
    assert exc.value.slip.reason_code is RejectionReasonCode.ATTACHMENT_MALFORMED


def test_attachment_negative_size_rejected() -> None:
    with pytest.raises(IngressRejected) as exc:
        _gate().check(_ok_envelope(attachments=[{"filename": "a.txt", "size": -1}]))
    assert exc.value.slip.reason_code is RejectionReasonCode.ATTACHMENT_MALFORMED


# ---------------------------------------------------------------------------
# G9 — modality validation
# ---------------------------------------------------------------------------


def test_modality_default_text() -> None:
    out = _gate().check(_ok_envelope())
    assert isinstance(out, StampedRequest)
    assert out.modality == "text"


@pytest.mark.parametrize("modality", ["text", "image", "audio", "video", "document", "mixed"])
def test_modality_allowed_values(modality: str) -> None:
    out = _gate().check(_ok_envelope(modality=modality))
    assert isinstance(out, StampedRequest)
    assert out.modality == modality


def test_modality_unsupported_rejected() -> None:
    with pytest.raises(IngressRejected) as exc:
        _gate().check(_ok_envelope(modality="hologram"))
    assert exc.value.slip.reason_code is RejectionReasonCode.UNSUPPORTED_MODALITY


def test_modality_custom_allowlist() -> None:
    gate = _gate(allowed_modalities={"text", "telemetry"})
    out = gate.check(_ok_envelope(modality="telemetry"))
    assert isinstance(out, StampedRequest)
    assert out.modality == "telemetry"
    with pytest.raises(IngressRejected) as exc:
        gate.check(_ok_envelope(modality="image", request_id="r-2"))
    assert exc.value.slip.reason_code is RejectionReasonCode.UNSUPPORTED_MODALITY


def test_modality_from_payload_dict() -> None:
    payload = {"intent": "describe", "modality": "image"}
    out = _gate().check(_ok_envelope(request_payload=payload))
    assert isinstance(out, StampedRequest)
    assert out.modality == "image"


# ---------------------------------------------------------------------------
# Output contract — to_dict carries every spec field
# ---------------------------------------------------------------------------


def test_to_dict_includes_all_spec_output_contract_keys() -> None:
    out = _gate().check(
        _ok_envelope(
            ingress_source_class="user",
            attachments=[{"filename": "a.txt", "size": 4}],
            modality="text",
        )
    )
    assert isinstance(out, StampedRequest)
    d = out.to_dict()
    for key in (
        "ingress_source_class",
        "auth_verdict",
        "quota_verdict",
        "schema_verdict",
        "raw_payload_ref",
        "attachment_manifest",
        "modality",
    ):
        assert key in d, f"missing {key}"
    assert d["attachment_manifest"][0]["filename"] == "a.txt"
    assert d["raw_payload_ref"].startswith("sha256:")
