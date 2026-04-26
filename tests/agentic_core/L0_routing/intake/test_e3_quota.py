"""E3 CHECKING DAILY LIMITS — quota / dedupe / abuse / replay.

Spec section: lines 262-315.
"""

from __future__ import annotations

from agentic_core.L0_routing.intake.envelope import (
    AttachmentManifestEntry,
    AttachmentManifestShell,
    RawIngressEnvelope,
)
from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode
from agentic_core.L0_routing.intake.stages import QuotaState, run_e3_quota
from agentic_core.L0_routing.intake.verdicts import (
    IdempotencyStatus,
    QuotaVerdict,
    SourceClass,
)


def _e1_e2(request_id: str = "req-x") -> tuple[dict, dict]:
    return (
        {"request_id": request_id},
        {"tenant_bind": "t1", "principal_id": "p1"},
    )


# ----------------------------------------------------------------------
# Allowed path
# ----------------------------------------------------------------------


def test_first_request_passes() -> None:
    env = RawIngressEnvelope(transport="chat", body_text="hello")
    e1, e2 = _e1_e2()
    res = run_e3_quota(env, SourceClass.USER, e1, e2, state=QuotaState())
    assert res.passed
    assert res.fields["quota_verdict"] is QuotaVerdict.ALLOWED
    assert res.fields["dedupe_status"] == "fresh"


# ----------------------------------------------------------------------
# Payload size
# ----------------------------------------------------------------------


def test_oversized_envelope_rejects() -> None:
    state = QuotaState(max_envelope_bytes=100)
    env = RawIngressEnvelope(transport="api", body_text="x" * 200)
    e1, e2 = _e1_e2()
    res = run_e3_quota(env, SourceClass.SERVICE, e1, e2, state=state)
    assert not res.passed
    assert IngressReasonCode.PAYLOAD_TOO_LARGE in res.reason_codes
    assert res.fields["quota_verdict"] is QuotaVerdict.DENIED


def test_too_many_attachments_rejects() -> None:
    state = QuotaState(max_attachment_count=2)
    entries = tuple(
        AttachmentManifestEntry(
            filename=f"f{i}.bin", mime_type="application/octet-stream", size_bytes=1, ref=f"r{i}"
        )
        for i in range(5)
    )
    env = RawIngressEnvelope(
        transport="api",
        body_text="x",
        attachments=AttachmentManifestShell(entries=entries, total_bytes=5),
    )
    e1, e2 = _e1_e2()
    res = run_e3_quota(env, SourceClass.SERVICE, e1, e2, state=state)
    assert not res.passed
    assert IngressReasonCode.PAYLOAD_TOO_LARGE in res.reason_codes


# ----------------------------------------------------------------------
# Webhook replay
# ----------------------------------------------------------------------


def test_webhook_replay_rejected() -> None:
    state = QuotaState()
    env = RawIngressEnvelope(transport="webhook", body_json={"a": 1}, webhook_delivery_id="d-1")
    e1, e2 = _e1_e2()
    first = run_e3_quota(env, SourceClass.WEBHOOK, e1, e2, state=state)
    assert first.passed
    second = run_e3_quota(env, SourceClass.WEBHOOK, e1, e2, state=state)
    assert not second.passed
    assert IngressReasonCode.WEBHOOK_REPLAY in second.reason_codes
    assert second.fields["quota_verdict"] is QuotaVerdict.DUPLICATE


# ----------------------------------------------------------------------
# Idempotency
# ----------------------------------------------------------------------


def test_idempotency_replay_rejected() -> None:
    state = QuotaState()
    env = RawIngressEnvelope(transport="api", body_json={"a": 1}, idempotency_key="idem-1")
    e1, e2 = _e1_e2()
    first = run_e3_quota(env, SourceClass.SERVICE, e1, e2, state=state)
    assert first.passed
    assert first.fields["idempotency_status"] is IdempotencyStatus.NEW
    # different request_id, same idempotency key, different payload
    env2 = RawIngressEnvelope(transport="api", body_json={"a": 2}, idempotency_key="idem-1")
    e1b, _ = _e1_e2(request_id="req-y")
    second = run_e3_quota(env2, SourceClass.SERVICE, e1b, e2, state=state)
    assert not second.passed
    assert IngressReasonCode.DUPLICATE_REQUEST in second.reason_codes


# ----------------------------------------------------------------------
# Payload hash dedupe
# ----------------------------------------------------------------------


def test_identical_payload_within_window_dedupes() -> None:
    state = QuotaState()
    env = RawIngressEnvelope(transport="api", body_text="same")
    e1, e2 = _e1_e2()
    first = run_e3_quota(env, SourceClass.SERVICE, e1, e2, state=state)
    assert first.passed
    e1b, _ = _e1_e2(request_id="req-other")
    second = run_e3_quota(env, SourceClass.SERVICE, e1b, e2, state=state)
    assert not second.passed
    assert IngressReasonCode.DUPLICATE_REQUEST in second.reason_codes


# ----------------------------------------------------------------------
# Rate limit
# ----------------------------------------------------------------------


def test_rate_limit_throttles() -> None:
    state = QuotaState(rate_limit_per_window=3, burst_limit=10)
    _, e2 = _e1_e2()
    for i in range(3):
        env = RawIngressEnvelope(transport="api", body_text=f"unique-{i}")
        e1 = {"request_id": f"req-{i}"}
        res = run_e3_quota(env, SourceClass.SERVICE, e1, e2, state=state)
        assert res.passed, f"request {i} should pass"
    # 4th hits the rate cap
    env = RawIngressEnvelope(transport="api", body_text="unique-4")
    res = run_e3_quota(env, SourceClass.SERVICE, {"request_id": "req-4"}, e2, state=state)
    assert not res.passed
    assert IngressReasonCode.QUOTA_EXCEEDED in res.reason_codes
    assert res.fields["quota_verdict"] is QuotaVerdict.THROTTLED
    assert res.fields["retry_after_seconds"] is not None


def test_burst_limit_throttles() -> None:
    state = QuotaState(rate_limit_per_window=1000, burst_limit=2)
    _, e2 = _e1_e2()
    for i in range(2):
        env = RawIngressEnvelope(transport="api", body_text=f"u-{i}")
        res = run_e3_quota(env, SourceClass.SERVICE, {"request_id": f"r{i}"}, e2, state=state)
        assert res.passed
    env = RawIngressEnvelope(transport="api", body_text="u-3")
    res = run_e3_quota(env, SourceClass.SERVICE, {"request_id": "r3"}, e2, state=state)
    assert not res.passed
    assert IngressReasonCode.BURST_LIMIT in res.reason_codes
