"""End-to-end pipeline tests covering EXAMPLES A/B/C/D from spec lines 705-781.

Each example is encoded as a single test that walks E1->E6 (or rejection) and
asserts the fields the spec promises in the example walkthrough.
"""

from __future__ import annotations

import time

from agentic_core.L0_routing.intake.envelope import (
    AttachmentManifestEntry,
    AttachmentManifestShell,
    RawIngressEnvelope,
)
from agentic_core.L0_routing.intake.events import IngressEvent
from agentic_core.L0_routing.intake.pipeline import IntakePipeline, IntakePolicy
from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode
from agentic_core.L0_routing.intake.stages import QuotaState
from agentic_core.L0_routing.intake.verdicts import (
    AuthVerdict,
    IdempotencyStatus,
    NormalizationVerdict,
    QuotaVerdict,
    SchemaVerdict,
    SourceClass,
)


def _pipeline(quota: QuotaState | None = None) -> IntakePipeline:
    return IntakePipeline(IntakePolicy(quota=quota or QuotaState()))


# ----------------------------------------------------------------------
# EXAMPLE A — Direct user chat with attachment (spec 708-728)
# ----------------------------------------------------------------------


def test_example_a_direct_user_chat() -> None:
    pdf = AttachmentManifestEntry(
        filename="policy.pdf", mime_type="application/pdf", size_bytes=1024, ref="blob:pdf-1"
    )
    env = RawIngressEnvelope(
        transport="chat",
        body_text="Review this policy and summarize the main risks.",
        auth_credential={"kind": "session", "token": "tok"},
        claimed_user_id="user-1",
        claimed_tenant_id="tenant-1",
        attachments=AttachmentManifestShell(entries=(pdf,), total_bytes=1024),
    )

    out = _pipeline().run(env)

    assert out.accepted
    vr = out.validated
    assert vr is not None
    # source_class = user
    assert vr.source_class is SourceClass.USER
    # E2 binds authenticated user / tenant
    assert vr.auth_verdict is AuthVerdict.AUTHENTICATED
    assert vr.tenant_bind == "tenant-1"
    # E3 quota allowed
    assert vr.quota_verdict is QuotaVerdict.ALLOWED
    # E4 schema valid + attachment captured
    assert vr.schema_verdict is SchemaVerdict.VALID
    assert vr.attachment_manifest.count == 1
    # E5 normalized text + canonical mime
    assert vr.attachment_manifest.entries[0].mime_type == "application/pdf"
    # E6 stamps - downstream authority none, next layer L1
    assert vr.downstream_authority == "none"
    assert vr.permitted_next_layer == "L1"
    # No semantic interpretation leaked
    assert vr.normalized_payload == "Review this policy and summarize the main risks."


# ----------------------------------------------------------------------
# EXAMPLE B — Service-to-service handoff (spec 729-746)
# ----------------------------------------------------------------------


def test_example_b_service_to_service() -> None:
    env = RawIngressEnvelope(
        transport="api",
        body_json={"action": "analyze", "incident_id": "INC-123"},
        auth_credential={
            "kind": "api_key",
            "token": "k",
            "principal_kind": "service",
            "tenant_id": "tenant-int",
        },
        claimed_service_id="svc-incident-analyzer",
        claimed_tenant_id="tenant-int",
        idempotency_key="idem-INC-123",
        request_id_hint="req-INC-123",
    )

    out = _pipeline().run(env)
    assert out.accepted
    vr = out.validated
    assert vr is not None
    assert vr.source_class is SourceClass.SERVICE
    assert vr.auth_verdict is AuthVerdict.SERVICE_BOUND
    assert vr.idempotency_status is IdempotencyStatus.NEW
    assert vr.schema_verdict is SchemaVerdict.VALID
    # Intake never fetches incident logs (HARD NO line 746)
    assert vr.normalized_payload == ""  # body_text was None — only JSON


# ----------------------------------------------------------------------
# EXAMPLE C — Webhook replay (spec 748-763)
# ----------------------------------------------------------------------


def test_example_c_webhook_replay() -> None:
    state = QuotaState()
    pipeline = _pipeline(state)
    base_env = RawIngressEnvelope(
        transport="webhook",
        body_json={"alert": "down"},
        auth_credential={"kind": "api_key", "token": "k"},
        webhook_delivery_id="abc123",
        request_id_hint="req-1",
    )
    first = pipeline.run(base_env)
    assert first.accepted

    # Same delivery_id arrives again with a new request_id
    replay = RawIngressEnvelope(
        transport="webhook",
        body_json={"alert": "down"},
        auth_credential={"kind": "api_key", "token": "k"},
        webhook_delivery_id="abc123",
        request_id_hint="req-2",
    )
    second = pipeline.run(replay)
    assert not second.accepted
    notice = second.rejected
    assert notice is not None
    assert notice.rejection_reason is IngressReasonCode.WEBHOOK_REPLAY
    assert notice.rejection_stage == "E3"
    # No L1 planning, no downstream work (line 761-763)
    assert second.validated is None


# ----------------------------------------------------------------------
# EXAMPLE D — Malformed batch (spec 765-780)
# ----------------------------------------------------------------------


def test_example_d_malformed_batch_oversize() -> None:
    state = QuotaState(max_batch_size=100)
    pipeline = _pipeline(state)
    env = RawIngressEnvelope(
        transport="batch",
        body_json={"items": list(range(10_000))},  # batch oversize
        auth_credential={"kind": "api_key", "token": "k"},
        # missing batch_id deliberately (per example: "missing job_id")
    )
    out = pipeline.run(env)
    assert not out.accepted
    notice = out.rejected
    assert notice is not None
    # E4 catches missing batch_id first (malformed envelope)
    assert notice.rejection_reason is IngressReasonCode.MALFORMED_ENVELOPE
    assert notice.rejection_stage == "E4"


def test_example_d_with_batch_id_but_oversize() -> None:
    state = QuotaState(max_batch_size=10)
    pipeline = _pipeline(state)
    env = RawIngressEnvelope(
        transport="batch",
        body_json={"items": list(range(10_000))},
        batch_id="b-1",
        auth_credential={"kind": "api_key", "token": "k"},
    )
    out = pipeline.run(env)
    assert not out.accepted
    notice = out.rejected
    assert notice is not None
    # may fail at E3 (envelope_size) OR E4 (batch_oversize); both are acceptable
    assert notice.rejection_reason in (
        IngressReasonCode.PAYLOAD_TOO_LARGE,
        IngressReasonCode.MALFORMED_ENVELOPE,
    )


# ----------------------------------------------------------------------
# Pipeline contract guarantees
# ----------------------------------------------------------------------


def test_pipeline_emits_required_events() -> None:
    out = _pipeline().run(RawIngressEnvelope(transport="chat", body_text="hi"))
    assert out.accepted
    event_types = {e.event for e in out.events}
    # Required events on a passing run (spec 622-632)
    assert IngressEvent.INGRESS_RECEIVED in event_types
    assert IngressEvent.REQUEST_ID_ASSIGNED in event_types
    assert IngressEvent.TRACE_ROOT_BOUND in event_types
    assert IngressEvent.SOURCE_CLASSIFIED in event_types
    assert IngressEvent.AUTH_BASELINE_EVALUATED in event_types
    assert IngressEvent.QUOTA_EVALUATED in event_types
    assert IngressEvent.SCHEMA_EVALUATED in event_types
    assert IngressEvent.PAYLOAD_NORMALIZED in event_types
    assert IngressEvent.INGRESS_ACCEPTED in event_types


def test_pipeline_emits_ingress_rejected_on_failure() -> None:
    out = _pipeline().run(RawIngressEnvelope(transport="smtp", body_text="x"))
    assert not out.accepted
    event_types = {e.event for e in out.events}
    assert IngressEvent.INGRESS_RECEIVED in event_types
    assert IngressEvent.INGRESS_REJECTED in event_types


def test_audit_record_always_produced() -> None:
    out = _pipeline().run(RawIngressEnvelope(transport="chat", body_text="x"))
    assert out.audit is not None
    assert out.audit.duration_ms >= 0
    assert out.audit.accepted is True

    out2 = _pipeline().run(RawIngressEnvelope(transport="smtp", body_text="x"))
    assert out2.audit is not None
    assert out2.audit.accepted is False
    assert out2.audit.rejection_reason is IngressReasonCode.UNSUPPORTED_TRANSPORT


def test_event_sink_is_called() -> None:
    captured: list = []
    pipeline = IntakePipeline(IntakePolicy(), event_sink=captured.append)
    pipeline.run(RawIngressEnvelope(transport="chat", body_text="hi"))
    assert len(captured) >= 8  # at least the core 8 events on a passing run


def test_validated_request_carries_no_route_or_answer() -> None:
    """Spec INGRESS OUTPUT CONTRACT — MUST NOT INCLUDE (lines 535-551)."""
    out = _pipeline().run(RawIngressEnvelope(transport="chat", body_text="hi"))
    assert out.validated is not None
    # The dataclass shape itself enforces this; double-check no leaked attrs.
    forbidden = {
        "final_answer",
        "route_decision",
        "proposed_route",
        "retrieval_result",
        "evidence_chunks",
        "tool_call",
        "model_execution_result",
        "capability_token",
        "uwg_commit_request",
    }
    actual = set(out.validated.__dataclass_fields__.keys())
    assert actual.isdisjoint(forbidden), f"Leaked forbidden field: {actual & forbidden}"


def test_received_at_iso_is_utc() -> None:
    out = _pipeline().run(RawIngressEnvelope(transport="chat", body_text="hi"))
    assert out.validated is not None
    assert out.validated.received_at_iso.endswith("+00:00")
    # ingress_time is roughly now
    assert abs(out.validated.ingress_time_unix - time.time()) < 5
