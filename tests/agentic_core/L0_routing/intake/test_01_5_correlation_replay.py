"""Tests for 01.5 Trace / Replay / Correlation Binding."""

from __future__ import annotations

from agentic_core.L0_routing.intake import (
    IngressReplaySeed,
    IntakeManifestHash,
    IntakePipeline,
    IntakePolicy,
    NormalizedRequestHash,
    RawIngressEnvelope,
    RequestCorrelationReceipt,
)


def _pipe() -> IntakePipeline:
    return IntakePipeline(IntakePolicy())


def _accepted_run(transport: str = "chat", body: str = "hello", **kwargs):
    env = RawIngressEnvelope(transport=transport, body_text=body, **kwargs)
    out = _pipe().run(env)
    assert out.accepted, f"intake should accept; got {out.rejected}"
    return out


def test_validated_request_carries_intake_manifest_hash() -> None:
    out = _accepted_run()
    vr = out.validated
    assert vr is not None
    assert vr.intake_status == "VALIDATED_FOR_L1"
    assert vr.intake_manifest_hash != ""
    assert vr.normalized_request_hash != ""
    assert vr.transport_receipt_ref != ""
    assert vr.identity_receipt_ref != ""
    assert vr.quota_receipt_ref != ""
    assert vr.schema_validation_receipt_ref != ""
    assert vr.correlation_receipt_ref != ""
    assert vr.ingress_replay_seed_ref != ""


def test_correlation_receipt_emitted() -> None:
    out = _accepted_run()
    final_audit = out.final_audit
    assert final_audit is not None
    # Correlation receipt id present in stage_receipt_refs by construction
    assert any("corr:" in ref for ref in final_audit.stage_receipt_refs)


def test_replay_seed_is_not_route_replay_key() -> None:
    """01.5 §IngressReplaySeed.replay_key_seed != L0 RouteContract replay_key."""
    out = _accepted_run()
    vr = out.validated
    assert vr is not None
    # The validated request only carries the *seed reference id*, not a routing key.
    assert vr.ingress_replay_seed_ref.startswith("seed:")
    # Make sure none of the forbidden route fields leaked.
    forbidden_route_attrs = {"route_decision", "proposed_route", "route_confidence"}
    for attr in forbidden_route_attrs:
        assert not hasattr(vr, attr)


def test_intake_manifest_hash_deterministic_across_runs() -> None:
    """Same logical input → same intake_manifest_hash, even though
    receipt_id / request_id are random per-run.
    """
    env = RawIngressEnvelope(
        transport="chat",
        body_text="stable text",
        auth_credential={"kind": "session", "token": "t"},
        claimed_user_id="u-stable",
        claimed_tenant_id="tenant-stable",
        session_id_hint="sess-stable",
    )
    a = _pipe().run(env)
    b = _pipe().run(env)
    assert a.accepted and b.accepted
    assert a.validated is not None and b.validated is not None
    assert a.validated.intake_manifest_hash == b.validated.intake_manifest_hash
    assert a.validated.normalized_request_hash == b.validated.normalized_request_hash


def test_intake_manifest_hash_changes_when_tenant_changes() -> None:
    def _build(tenant: str) -> RawIngressEnvelope:
        return RawIngressEnvelope(
            transport="chat",
            body_text="same text",
            auth_credential={"kind": "session", "token": "t"},
            claimed_user_id="u-1",
            session_id_hint="sess-stable",
            claimed_tenant_id=tenant,
        )

    a = _pipe().run(_build("tenant-A"))
    b = _pipe().run(_build("tenant-B"))
    assert a.accepted and b.accepted
    assert a.validated is not None and b.validated is not None
    assert a.validated.normalized_request_hash != b.validated.normalized_request_hash


def test_volatile_observed_fields_do_not_perturb_manifest_hash() -> None:
    """Even if request_id_hint differs, identity-equivalent requests with
    identical session/tenant/payload produce the same manifest hash."""
    a = _pipe().run(
        RawIngressEnvelope(
            transport="chat",
            body_text="same",
            auth_credential={"kind": "session", "token": "t"},
            claimed_tenant_id="t1",
            session_id_hint="sess-1",
            request_id_hint="req-A",
        )
    )
    b = _pipe().run(
        RawIngressEnvelope(
            transport="chat",
            body_text="same",
            auth_credential={"kind": "session", "token": "t"},
            claimed_tenant_id="t1",
            session_id_hint="sess-1",
            request_id_hint="req-B",
        )
    )
    assert a.accepted and b.accepted
    assert a.validated is not None and b.validated is not None
    # Same logical input → same manifest hash regardless of request_id.
    assert a.validated.intake_manifest_hash == b.validated.intake_manifest_hash


def test_no_route_or_prompt_hashes_emitted() -> None:
    """01.5 hard-no: 'No route_digest. No prompt_hash. No evidence_contract_hash.'"""
    out = _accepted_run()
    vr = out.validated
    assert vr is not None
    forbidden = {"route_digest", "prompt_hash", "evidence_contract_hash", "attempt_seed"}
    for attr in forbidden:
        assert not hasattr(vr, attr)


def test_correlation_receipt_typed_and_hashed() -> None:
    from agentic_core.L0_routing.intake.correlation import bind_trace_and_replay
    from agentic_core.L0_routing.intake.origin_labels import IngressOriginLabelManifest
    from agentic_core.L0_routing.intake.receipts import (
        CallerScopeBaseline,
        QuotaReceipt,
        RequestSchemaValidationReceipt,
        TransportEnvelopeReceipt,
    )

    tep = TransportEnvelopeReceipt(
        receipt_id="tep:1",
        raw_envelope_id="raw:1",
        transport="chat",
        channel="chat",
        accepted_transport=True,
        frame_parse_status="ok",
        method_allowed=True,
        content_type_allowed=True,
        encoding_allowed=True,
        body_size_status="ok",
        attachment_inventory_status="ok",
        raw_capture_status="ok",
        transport_policy_ref="p:t:1",
    ).with_hash()
    csb = CallerScopeBaseline(
        caller_scope_baseline_id="csb:1",
        caller_claim_id="cic:1",
        tenant_id="t",
        tenant_scope=None,
        session_id="s",
        session_scope=None,
        region=None,
        data_residency_hint=None,
        account_status="active",
    ).with_hash()
    qr = QuotaReceipt(
        receipt_id="qr:1",
        tenant_id="t",
        principal_id_hash=None,
        session_id="s",
        quota_policy_ref="p:q:1",
        request_size_status="ok",
        attachment_count_status="ok",
        rate_limit_status="ok",
        daily_limit_status="unknown",
        concurrent_request_status="unknown",
        allowed_to_continue_intake=True,
    ).with_hash()
    ssv = RequestSchemaValidationReceipt(
        receipt_id="ssv:1",
        request_schema_ref="p:s:1",
        schema_version="1",
        schema_valid=True,
    ).with_hash()
    olm = IngressOriginLabelManifest(
        manifest_id="m:1",
        payload_segment_refs=("seg:1",),
        segment_origin_labels=("user_turn",),
        segment_authority_labels=("user_intent_only",),
    ).with_hash()
    res = bind_trace_and_replay(
        request_id="req:1",
        session_id="s",
        trace_root="trace:1",
        raw_envelope_id="raw:1",
        normalized_payload_id="nup:1",
        transport_receipt=tep,
        caller_scope_baseline=csb,
        quota_receipt=qr,
        schema_validation_receipt=ssv,
        origin_label_manifest=olm,
        raw_payload_hash="rh",
        normalized_payload_hash="nh",
        schema_version="1",
        transport="chat",
    )
    assert isinstance(res.correlation_receipt, RequestCorrelationReceipt)
    assert isinstance(res.ingress_replay_seed, IngressReplaySeed)
    assert isinstance(res.normalized_request_hash, NormalizedRequestHash)
    assert isinstance(res.intake_manifest_hash, IntakeManifestHash)
    assert res.intake_manifest_hash.intake_manifest_hash != ""
    assert res.correlation_receipt.deterministic_receipt_hash != ""
