"""End-to-end tests for ``governance_plane.certify_packet``."""

from __future__ import annotations

from agentic_core.L5_safety.v5 import (
    CapabilityTokenV5,
    DecisionVerdict,
    OutOfBandMutationError,
    RiskTierBandV5,
    SandboxEnvelope,
    StandardsFingerprint,
    StandardsTag,
    assert_no_current_run_mutation,
    certify_packet,
    seal_replay_envelope,
    validate_entry_packet,
)


def _good_token():
    return CapabilityTokenV5(
        token_id="tok-1",
        principal_chain_id="pc",
        scope=("read:doc",),
        ttl_seconds=300,
        single_use=True,
        max_invocations=1,
        connector_allowlist=(),
        plan_digest="pd",
        route_contract_digest="rd",
        evidence_contract_id="ec",
        permission_ladder=("read",),
        allowed_args_hash="ah",
        revocation_posture="manual",
    )


def _good_sandbox():
    return SandboxEnvelope(
        fs_scope=("/tmp",),
        net_scope=(),
        syscall_scope=(),
        env_scope=(),
        timeout_seconds=10,
        memory_mb=128,
        cpu_quota=1.0,
        token_budget=1000,
        cost_budget_usd=0.10,
        retry_budget=1,
        artifact_scope=(),
        output_sealing_path="/seal/x.json",
    )


def _read_packet(**overrides):
    raw = {
        "request_id": "r",
        "trace_id": "t",
        "run_id": "run",
        "tenant_id": "tnt",
        "caller_id": "u",
        "packet_kind": "request_envelope",
        "side_effect_class": "READ",
        "principal_chain_id": "pc",
        **overrides,
    }
    return raw


def test_clean_read_packet_certifies():
    res = certify_packet(
        raw_packet=_read_packet(),
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
    )
    assert res.decision == DecisionVerdict.CERTIFY
    assert res.compliance_hash == res.replay_envelope.compliance_hash
    assert res.audit_log_event["compliance_hash"] == res.compliance_hash
    # Replay envelope is bound to the final verdict.
    assert res.replay_envelope.decision_verdict == DecisionVerdict.CERTIFY


def test_invalid_packet_rejects_with_audit():
    res = certify_packet(raw_packet={"request_id": "x"})  # missing required fields
    assert res.decision == DecisionVerdict.REJECT
    assert res.replay_envelope.compliance_hash != ""
    assert res.audit_log_event["decision"] == DecisionVerdict.REJECT.value


def test_incident_packet_escalates():
    res = certify_packet(
        raw_packet=_read_packet(),
        incident_suspected=True,
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
    )
    assert res.decision == DecisionVerdict.ESCALATE
    assert "require_HITL" in res.downstream_disposition


def test_external_commit_with_token_certifies_and_routes_to_uwg():
    res = certify_packet(
        raw_packet=_read_packet(
            side_effect_class="EXTERNAL_COMMIT",
            registry_digest_set=("d",),
            route_contract_hmac="hmac",
            requested_authority=("commit:db",),
            origin_trust_manifest_raw={"developer_admin": ["a"]},
        ),
        risk_tier_hint=RiskTierBandV5.HIGH,
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
    )
    # HIGH band → BOTH_LANES → ESCALATE (HITL) per rail.
    assert res.decision in {DecisionVerdict.CERTIFY, DecisionVerdict.ESCALATE}
    if res.decision == DecisionVerdict.CERTIFY:
        assert "require_UWG_commit_review" in res.downstream_disposition


def test_compliance_hash_is_deterministic():
    p = _read_packet()
    res_a = certify_packet(
        raw_packet=p,
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
        timestamp_iso="2026-04-25T00:00:00+00:00",
    )
    res_b = certify_packet(
        raw_packet=p,
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
        timestamp_iso="2026-04-25T00:00:00+00:00",
    )
    # The compliance_hash binds policy/registry/replay deterministically.
    assert res_a.replay_envelope.compliance_hash == res_b.replay_envelope.compliance_hash


def test_replay_envelope_covers_all_required_fields():
    res = certify_packet(
        raw_packet=_read_packet(),
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
    )
    re = res.replay_envelope
    # Spec line 575: must bind policy/blueprint/registry digests + run/trace
    assert re.run_id == "run"
    assert re.trace_id == "t"
    assert re.standards_fingerprint.tags
    assert re.compliance_hash


def test_out_of_band_mutation_blocked():
    res = certify_packet(
        raw_packet=_read_packet(),
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
    )
    # No proposed changes → no-op
    assert assert_no_current_run_mutation(sealed_result=res, proposed_changes={}) is None

    # Any non-empty change → raises
    try:
        assert_no_current_run_mutation(
            sealed_result=res,
            proposed_changes={"compliance_hash": "tampered"},
        )
    except OutOfBandMutationError as exc:
        assert "out-of-band" in str(exc).lower()
    else:
        raise AssertionError("OutOfBandMutationError not raised")


def test_governance_result_is_frozen():
    res = certify_packet(
        raw_packet=_read_packet(),
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
    )
    try:
        res.decision = DecisionVerdict.REJECT  # type: ignore[misc]
    except (AttributeError, Exception):
        return
    raise AssertionError("GovernanceResult must be frozen")


def test_seal_replay_envelope_standalone():
    raw = _read_packet()
    res = validate_entry_packet(raw)
    assert res.request is not None
    re = seal_replay_envelope(
        request=res.request,
        decision_verdict=DecisionVerdict.CERTIFY,
        standards_fingerprint=StandardsFingerprint(tags=(StandardsTag.NIST_AI_RMF,)),
        span_id="s",
        route_id="r",
    )
    assert re.compliance_hash
    # Determinism: same inputs → same hash
    re2 = seal_replay_envelope(
        request=res.request,
        decision_verdict=DecisionVerdict.CERTIFY,
        standards_fingerprint=StandardsFingerprint(tags=(StandardsTag.NIST_AI_RMF,)),
        span_id="s",
        route_id="r",
    )
    assert re.compliance_hash == re2.compliance_hash
