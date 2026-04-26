"""E1 IS IT A REAL REQUEST? — transport + presence checks.

Spec section: lines 153-205.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.intake.envelope import (
    AttachmentManifestEntry,
    AttachmentManifestShell,
    RawIngressEnvelope,
)
from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode
from agentic_core.L0_routing.intake.stages import (
    DEFAULT_ALLOWED_TRANSPORTS,
    classify_source,
    run_e1_real_request,
)
from agentic_core.L0_routing.intake.verdicts import SourceClass, StageVerdict


# ----------------------------------------------------------------------
# Transport allowlist
# ----------------------------------------------------------------------


def test_default_allowed_transports_match_spec() -> None:
    """Spec line 170: chat | ui | api | batch | webhook | queue | alert."""
    assert DEFAULT_ALLOWED_TRANSPORTS == frozenset(
        {"chat", "ui", "api", "batch", "webhook", "queue", "alert"}
    )


@pytest.mark.parametrize("transport", sorted(DEFAULT_ALLOWED_TRANSPORTS))
def test_each_allowed_transport_passes_e1(transport: str) -> None:
    env = RawIngressEnvelope(
        transport=transport,
        body_text="hello",
        webhook_delivery_id="d1" if transport in {"webhook", "alert"} else None,
        batch_id="b1" if transport in {"batch", "queue"} else None,
    )
    res = run_e1_real_request(env)
    assert res.passed, f"transport {transport!r} should pass"
    assert res.fields["E1_verdict"] == StageVerdict.PASS.value


@pytest.mark.parametrize("transport", ["smtp", "fax", "carrier_pigeon", "", "  "])
def test_unsupported_transport_rejects(transport: str) -> None:
    res = run_e1_real_request(RawIngressEnvelope(transport=transport, body_text="hello"))
    assert not res.passed
    assert IngressReasonCode.UNSUPPORTED_TRANSPORT in res.reason_codes


# ----------------------------------------------------------------------
# Empty payload
# ----------------------------------------------------------------------


def test_empty_payload_rejects() -> None:
    res = run_e1_real_request(RawIngressEnvelope(transport="chat"))
    assert not res.passed
    assert IngressReasonCode.EMPTY_PAYLOAD in res.reason_codes


def test_whitespace_only_payload_rejects() -> None:
    res = run_e1_real_request(RawIngressEnvelope(transport="chat", body_text="   \n\t "))
    assert not res.passed
    assert IngressReasonCode.EMPTY_PAYLOAD in res.reason_codes


def test_attachment_only_payload_passes() -> None:
    """Spec line 37: attachments are valid payload presence."""
    manifest = AttachmentManifestShell(
        entries=(
            AttachmentManifestEntry(filename="x.pdf", mime_type="application/pdf", size_bytes=10, ref="r:1"),
        ),
        total_bytes=10,
    )
    env = RawIngressEnvelope(transport="api", attachments=manifest)
    res = run_e1_real_request(env)
    assert res.passed


def test_json_only_payload_passes() -> None:
    res = run_e1_real_request(RawIngressEnvelope(transport="api", body_json={"k": 1}))
    assert res.passed


# ----------------------------------------------------------------------
# Body parser failure
# ----------------------------------------------------------------------


def test_body_parser_failed_rejects() -> None:
    res = run_e1_real_request(
        RawIngressEnvelope(transport="api", body_text="garbage", body_parser_failed=True)
    )
    assert not res.passed
    assert IngressReasonCode.MALFORMED_ENVELOPE in res.reason_codes


# ----------------------------------------------------------------------
# Identifier assignment
# ----------------------------------------------------------------------


def test_e1_assigns_identifiers_when_absent() -> None:
    res = run_e1_real_request(RawIngressEnvelope(transport="chat", body_text="hi"))
    assert res.fields["request_id"].startswith("req-")
    assert res.fields["session_id"].startswith("sess-")
    assert res.fields["trace_root"].startswith("trace-")


def test_e1_preserves_upstream_traceparent() -> None:
    """Spec line 167: upstream traceparent preserved if present."""
    env = RawIngressEnvelope(
        transport="api",
        body_text="x",
        upstream_traceparent="00-aaa-bbb-01",
    )
    res = run_e1_real_request(env)
    assert res.fields["trace_root"] == "00-aaa-bbb-01"


def test_e1_preserves_request_id_hint() -> None:
    env = RawIngressEnvelope(transport="api", body_text="x", request_id_hint="req-fixed")
    res = run_e1_real_request(env)
    assert res.fields["request_id"] == "req-fixed"


# ----------------------------------------------------------------------
# Duplicate transport frame guard (spec line 179)
# ----------------------------------------------------------------------


def test_duplicate_transport_frame_rejected() -> None:
    consumed: set[str] = set()
    env = RawIngressEnvelope(transport="chat", body_text="hi", request_id_hint="req-x")
    first = run_e1_real_request(env, consumed_frames=consumed)
    assert first.passed
    second = run_e1_real_request(env, consumed_frames=consumed)
    assert not second.passed
    assert IngressReasonCode.DUPLICATE_REQUEST in second.reason_codes


# ----------------------------------------------------------------------
# Source classification
# ----------------------------------------------------------------------


@pytest.mark.parametrize(
    "transport,expected",
    [
        ("chat", SourceClass.USER),
        ("ui", SourceClass.USER),
        ("api", SourceClass.SERVICE),
        ("batch", SourceClass.BATCH),
        ("queue", SourceClass.BATCH),
        ("webhook", SourceClass.WEBHOOK),
        ("alert", SourceClass.ALERT),
    ],
)
def test_classify_source(transport: str, expected: SourceClass) -> None:
    assert classify_source(transport) is expected


def test_classify_source_unknown_returns_none() -> None:
    assert classify_source("smtp") is None
