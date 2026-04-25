"""Tests for the v5 decision rail (spec lines 590–650)."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.v5 import (
    BoundaryClassification,
    CapabilityTokenV5,
    DecisionVerdict,
    GovernanceMode,
    GovernanceResult,
    NextLane,
    OriginLabel,
    OriginTrustManifest,
    PacketKind,
    ReasonCode,
    ReplayEnvelope,
    ReviewDepth,
    RiskTierBandV5,
    SandboxEnvelope,
    SideEffectClass,
    StandardsFingerprint,
    StandardsTag,
    TriageFlag,
    TriageReport,
    emit_verdict,
    seal_replay_envelope,
    validate_entry_packet,
)


@pytest.fixture
def standards():
    return StandardsFingerprint(tags=(StandardsTag.NIST_AI_RMF,))


@pytest.fixture
def good_request():
    raw = {
        "request_id": "r",
        "trace_id": "t",
        "run_id": "run",
        "tenant_id": "tnt",
        "caller_id": "u",
        "packet_kind": "request_envelope",
        "side_effect_class": "READ",
        "principal_chain_id": "pc",
    }
    res = validate_entry_packet(raw)
    assert res.request is not None
    return res.request


def _ok_triage():
    return TriageReport(
        governance_mode=GovernanceMode.RUNTIME_CHECK,
        risk_tier_band=RiskTierBandV5.LOW,
        review_depth=ReviewDepth.FAST_PATH,
        triage_flags=(),
        next_lane=NextLane.RUNTIME_LANE,
    )


def _ok_origin():
    return OriginTrustManifest(
        labeled_fields={OriginLabel.SYSTEM_POLICY: ("p",)},
        boundary_classification=BoundaryClassification.TRUSTED_INSTRUCTION,
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


def _make_replay(request, standards, verdict=DecisionVerdict.CERTIFY) -> ReplayEnvelope:
    return seal_replay_envelope(
        request=request,
        decision_verdict=verdict,
        standards_fingerprint=standards,
        span_id="s",
        route_id="r",
    )


def test_certifies_clean_packet(good_request, standards):
    res = emit_verdict(
        review_request=good_request,
        triage=_ok_triage(),
        origin_trust=_ok_origin(),
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
        replay_envelope=_make_replay(good_request, standards),
        audit_log_event={"actor": "test"},
        standards_fingerprint=standards,
    )
    assert res.decision == DecisionVerdict.CERTIFY
    assert "allow_l2_execution" in res.downstream_disposition
    assert res.hard_stop is False


def test_hard_constraint_breach_forces_reject_with_hard_stop(good_request, standards):
    triage = TriageReport(
        governance_mode=GovernanceMode.RUNTIME_CHECK,
        risk_tier_band=RiskTierBandV5.CRITICAL,
        review_depth=ReviewDepth.LOCKDOWN,
        triage_flags=(TriageFlag.HARD_CONSTRAINT_CANDIDATE,),
        next_lane=NextLane.DECISION_RAIL_REJECT,
    )
    res = emit_verdict(
        review_request=good_request,
        triage=triage,
        origin_trust=_ok_origin(),
        capability_token=None,
        sandbox_envelope=None,
        replay_envelope=_make_replay(good_request, standards, DecisionVerdict.REJECT),
        audit_log_event={},
        standards_fingerprint=standards,
    )
    assert res.decision == DecisionVerdict.REJECT
    assert res.hard_stop is True
    assert ReasonCode.HARD_CONSTRAINT_BREACH in res.reason_codes
    assert "incident_lockdown" in res.downstream_disposition


def test_critical_band_without_hard_constraint_escalates(good_request, standards):
    triage = TriageReport(
        governance_mode=GovernanceMode.RUNTIME_CHECK,
        risk_tier_band=RiskTierBandV5.CRITICAL,
        review_depth=ReviewDepth.LOCKDOWN,
        triage_flags=(),  # no hard_constraint_candidate
        next_lane=NextLane.BOTH_LANES,
    )
    res = emit_verdict(
        review_request=good_request,
        triage=triage,
        origin_trust=_ok_origin(),
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
        replay_envelope=_make_replay(good_request, standards, DecisionVerdict.ESCALATE),
        audit_log_event={},
        standards_fingerprint=standards,
    )
    assert res.decision == DecisionVerdict.ESCALATE
    assert res.re_clearance_required is True


def test_quarantined_origin_forces_remediate(good_request, standards):
    origin = OriginTrustManifest(
        labeled_fields={OriginLabel.RETRIEVED: ("doc",)},
        boundary_classification=BoundaryClassification.QUARANTINED,
        quarantine_reasons=("doc:html_comment",),
    )
    res = emit_verdict(
        review_request=good_request,
        triage=_ok_triage(),
        origin_trust=origin,
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
        replay_envelope=_make_replay(good_request, standards, DecisionVerdict.REMEDIATE),
        audit_log_event={},
        standards_fingerprint=standards,
    )
    assert res.decision == DecisionVerdict.REMEDIATE
    assert res.revalidate_required is True


def test_remediate_forbidden_when_hard_constraint_breached(good_request, standards):
    """Spec line 645: REMEDIATE is forbidden when hard_constraint=True."""
    triage = TriageReport(
        governance_mode=GovernanceMode.RUNTIME_CHECK,
        risk_tier_band=RiskTierBandV5.CRITICAL,
        review_depth=ReviewDepth.LOCKDOWN,
        triage_flags=(TriageFlag.HARD_CONSTRAINT_CANDIDATE,),
        next_lane=NextLane.DECISION_RAIL_REJECT,
    )
    # Even if the rail downgrades to remediate, GovernanceResult.__post_init__ rejects.
    # We assert the rail does NOT produce REMEDIATE here (it produces REJECT).
    res = emit_verdict(
        review_request=good_request,
        triage=triage,
        origin_trust=_ok_origin(),
        capability_token=None,
        sandbox_envelope=None,
        replay_envelope=_make_replay(good_request, standards, DecisionVerdict.REJECT),
        audit_log_event={},
        standards_fingerprint=standards,
    )
    assert res.decision == DecisionVerdict.REJECT


def test_certify_requires_token_and_sandbox(good_request, standards):
    """Spec line 647: CERTIFY is scoped to the token/sandbox."""
    res = emit_verdict(
        review_request=good_request,
        triage=_ok_triage(),
        origin_trust=_ok_origin(),
        capability_token=None,  # missing!
        sandbox_envelope=None,
        replay_envelope=_make_replay(good_request, standards),
        audit_log_event={},
        standards_fingerprint=standards,
    )
    # Rail downgrades CERTIFY → ESCALATE when token/sandbox missing.
    assert res.decision == DecisionVerdict.ESCALATE
    assert ReasonCode.SANDBOX_INSUFFICIENT in res.reason_codes


def test_governance_result_constructor_invariant():
    """Direct construction of an invalid GovernanceResult must raise."""
    bad = {
        "decision": DecisionVerdict.REMEDIATE,
        "reason_codes": (ReasonCode.HARD_CONSTRAINT_BREACH,),
    }
    with pytest.raises(ValueError):
        # Build a minimum-shape result that violates the remediate invariant.
        from agentic_core.L5_safety.v5.contracts import (
            GovernanceReviewRequest as Req,
        )

        req = Req(
            request_id="r",
            trace_id="t",
            run_id="run",
            tenant_id="tnt",
            caller_id="u",
            packet_kind=PacketKind.REQUEST_ENVELOPE,
            side_effect_class=SideEffectClass.READ,
        )
        replay = seal_replay_envelope(
            request=req,
            decision_verdict=DecisionVerdict.REMEDIATE,
            standards_fingerprint=StandardsFingerprint(tags=(StandardsTag.NIST_AI_RMF,)),
            span_id="s",
            route_id="r",
        )
        GovernanceResult(
            decision=bad["decision"],
            reason_codes=bad["reason_codes"],
            compliance_hash=replay.compliance_hash,
            standards_fingerprint=StandardsFingerprint(tags=(StandardsTag.NIST_AI_RMF,)),
            review_request=req,
            triage=_ok_triage(),
            origin_trust=_ok_origin(),
            capability_token=None,
            sandbox_envelope=None,
            replay_envelope=replay,
            audit_log_event={},
            governance_reports={},
            downstream_disposition=(),
            hard_stop=False,
            revalidate_required=True,
            re_clearance_required=False,
        )
