"""Tests for L5_safety/identity/runtime_entry.py."""

import pytest

from agentic_core.interfaces.principal_chain_types import PermissionLadderRung
from agentic_core.L2_execution.types.capability_token_v4_types import (
    CapabilityTokenV4Artifact,
)
from agentic_core.L5_safety.identity.guardrail_adapter import ChokepointV4Result
from agentic_core.L5_safety.identity.guardrail_bank import (
    GuardrailFamily,
    GuardrailOutcome,
)
from agentic_core.L5_safety.identity.principal_verifier import (
    VerificationResult,
    VerificationStatus,
)
from agentic_core.L5_safety.identity.runtime_entry import (
    RuntimeLaneDecision,
    RuntimeLaneRejected,
    evaluate_runtime_lane,
)
from agentic_core.L5_safety.identity.runtime_rails import (
    HandoffValidationResult,
    RiskTierDecision,
)


@pytest.fixture
def sample_verification_result_pass() -> VerificationResult:
    """Sample verification result with PASS status."""
    return VerificationResult(
        status=VerificationStatus.PASS,
        failures=(),
        required_rung="mutate",
        token_rung="mutate",
        delegation_depth=0,
        delegation_cap=3,
    )


@pytest.fixture
def sample_verification_result_fail() -> VerificationResult:
    """Sample verification result with FAIL status."""
    return VerificationResult(
        status=VerificationStatus.FAIL,
        failures=("TOKEN_EXPIRED",),
        required_rung="mutate",
        token_rung="read",
        delegation_depth=0,
        delegation_cap=3,
    )


@pytest.fixture
def sample_verification_result_step_up() -> VerificationResult:
    """Sample verification result with STEP_UP_REQUIRED status."""
    return VerificationResult(
        status=VerificationStatus.STEP_UP_REQUIRED,
        failures=(),
        required_rung="mutate",
        token_rung="read",
        delegation_depth=0,
        delegation_cap=3,
    )


@pytest.fixture
def sample_risk_tier_decision() -> RiskTierDecision:
    """Sample risk tier decision."""
    from agentic_core.L5_safety.identity.runtime_rails import RiskEscalationReason
    return RiskTierDecision(
        token_band="MODERATE",
        runtime_band="MODERATE",
        escalation_reason=RiskEscalationReason.NONE,
        requires_hitl=False,
        log_verbosity=2,
    )


@pytest.fixture
def sample_chokepoint_result_allow() -> ChokepointV4Result:
    """Sample chokepoint result with allow action."""
    from agentic_core.L5_safety.identity.guardrail_bank import resolve_bank_verdict, compose_egress_inspection
    ingress_verdict = resolve_bank_verdict("ingress", ())
    egress_verdict = resolve_bank_verdict("egress", ())
    egress_inspection = compose_egress_inspection(egress_verdict, None)
    return ChokepointV4Result(
        ingress_verdict=ingress_verdict,
        egress_inspection=egress_inspection,
        final_action="allow",
    )


@pytest.fixture
def sample_chokepoint_result_reject() -> ChokepointV4Result:
    """Sample chokepoint result with reject action."""
    from agentic_core.L5_safety.identity.guardrail_bank import GuardrailOutcome, resolve_bank_verdict, compose_egress_inspection
    reject_outcome = GuardrailOutcome(
        family=GuardrailFamily.PII,
        layer="client_universal",
        stage="ingress",
        action="reject",
        score=1.0,
        evidence="pii_detected",
    )
    ingress_verdict = resolve_bank_verdict("ingress", (reject_outcome,))
    egress_verdict = resolve_bank_verdict("egress", ())
    egress_inspection = compose_egress_inspection(egress_verdict, None)
    return ChokepointV4Result(
        ingress_verdict=ingress_verdict,
        egress_inspection=egress_inspection,
        final_action="reject",
    )


@pytest.fixture
def sample_chokepoint_result_remediate() -> ChokepointV4Result:
    """Sample chokepoint result with remediate action."""
    from agentic_core.L5_safety.identity.guardrail_bank import GuardrailOutcome, resolve_bank_verdict, compose_egress_inspection
    remediate_outcome = GuardrailOutcome(
        family=GuardrailFamily.PII,
        layer="client_universal",
        stage="ingress",
        action="remediate",
        score=0.8,
        evidence="pii_detected_remediable",
    )
    ingress_verdict = resolve_bank_verdict("ingress", (remediate_outcome,))
    egress_verdict = resolve_bank_verdict("egress", ())
    egress_inspection = compose_egress_inspection(egress_verdict, None)
    return ChokepointV4Result(
        ingress_verdict=ingress_verdict,
        egress_inspection=egress_inspection,
        final_action="remediate",
    )


@pytest.fixture
def sample_handoff_result_allow() -> HandoffValidationResult:
    """Sample handoff validation result with allow."""
    return HandoffValidationResult(
        allow=True,
        failures=(),
        target_agent_id="target_agent",
        effective_scopes=("default",),
    )


@pytest.fixture
def sample_handoff_result_reject() -> HandoffValidationResult:
    """Sample handoff validation result with reject."""
    return HandoffValidationResult(
        allow=False,
        failures=("SCOPE_ABOVE_CEILING:admin",),
        target_agent_id="target_agent",
        effective_scopes=(),
    )


def test_runtime_lane_decision_to_dict(
    sample_verification_result_pass,
    sample_risk_tier_decision,
    sample_chokepoint_result_allow,
):
    """Test RuntimeLaneDecision.to_dict serialization."""
    decision = RuntimeLaneDecision(
        verification=sample_verification_result_pass,
        risk_tier=sample_risk_tier_decision,
        chokepoint=sample_chokepoint_result_allow,
        handoff=None,
        final_action="allow",
    )

    d = decision.to_dict()
    assert d["verification"] == sample_verification_result_pass.to_dict()
    assert d["risk_tier"] == sample_risk_tier_decision.to_dict()
    assert d["chokepoint"] == sample_chokepoint_result_allow.to_dict()
    assert d["handoff"] is None
    assert d["final_action"] == "allow"


def test_runtime_lane_decision_to_dict_with_handoff(
    sample_verification_result_pass,
    sample_risk_tier_decision,
    sample_chokepoint_result_allow,
    sample_handoff_result_allow,
):
    """Test RuntimeLaneDecision.to_dict with handoff."""
    decision = RuntimeLaneDecision(
        verification=sample_verification_result_pass,
        risk_tier=sample_risk_tier_decision,
        chokepoint=sample_chokepoint_result_allow,
        handoff=sample_handoff_result_allow,
        final_action="allow",
    )

    d = decision.to_dict()
    assert d["handoff"] == sample_handoff_result_allow.to_dict()


def test_runtime_lane_rejected_exception(
    sample_verification_result_pass,
    sample_risk_tier_decision,
    sample_chokepoint_result_reject,
):
    """Test RuntimeLaneRejected carries decision."""
    decision = RuntimeLaneDecision(
        verification=sample_verification_result_pass,
        risk_tier=sample_risk_tier_decision,
        chokepoint=sample_chokepoint_result_reject,
        handoff=None,
        final_action="reject",
    )

    exc = RuntimeLaneRejected(decision)
    assert exc.decision is decision
    assert "RuntimeLaneRejected" in str(exc)
    assert "reject" in str(exc)


def test_evaluate_runtime_lane_all_allow(
    sample_v4_token,
    sample_verification_result_pass,
    sample_risk_tier_decision,
    sample_chokepoint_result_allow,
    sample_handoff_result_allow,
    monkeypatch,
):
    """Test evaluate_runtime_lane when all components allow."""
    # Mock the composed functions to return allow results
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.verify_v4_token",
        lambda *args, **kwargs: sample_verification_result_pass,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.select_runtime_band",
        lambda *args, **kwargs: sample_risk_tier_decision,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.run_chokepoint_v4",
        lambda *args, **kwargs: sample_chokepoint_result_allow,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.validate_handoff",
        lambda *args, **kwargs: sample_handoff_result_allow,
    )

    # Create a mock AgentRegistryRecord for handoff_target
    from agentic_core.L5_safety.identity.runtime_rails import AgentRegistryRecord
    handoff_target = AgentRegistryRecord(
        agent_id="target_agent",
        allowed_scope_ceiling=("read", "write"),
        allowed_inbound_handoff_scopes=("default",),
    )

    decision = evaluate_runtime_lane(
        token=sample_v4_token,
        action_required_rung="mutate",
        handoff_target=handoff_target,
    )

    assert decision.final_action == "allow"
    assert decision.verification == sample_verification_result_pass
    assert decision.risk_tier == sample_risk_tier_decision
    assert decision.chokepoint == sample_chokepoint_result_allow
    assert decision.handoff == sample_handoff_result_allow


def test_evaluate_runtime_lane_verification_reject(
    sample_v4_token,
    sample_verification_result_fail,
    sample_risk_tier_decision,
    sample_chokepoint_result_allow,
    monkeypatch,
):
    """Test evaluate_runtime_lane when verification rejects."""
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.verify_v4_token",
        lambda *args, **kwargs: sample_verification_result_fail,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.select_runtime_band",
        lambda *args, **kwargs: sample_risk_tier_decision,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.run_chokepoint_v4",
        lambda *args, **kwargs: sample_chokepoint_result_allow,
    )

    decision = evaluate_runtime_lane(
        token=sample_v4_token,
        action_required_rung="mutate",
    )

    assert decision.final_action == "reject"
    assert decision.verification == sample_verification_result_fail


def test_evaluate_runtime_lane_verification_step_up(
    sample_v4_token,
    sample_verification_result_step_up,
    sample_risk_tier_decision,
    sample_chokepoint_result_allow,
    monkeypatch,
):
    """Test evaluate_runtime_lane when verification requires step-up."""
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.verify_v4_token",
        lambda *args, **kwargs: sample_verification_result_step_up,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.select_runtime_band",
        lambda *args, **kwargs: sample_risk_tier_decision,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.run_chokepoint_v4",
        lambda *args, **kwargs: sample_chokepoint_result_allow,
    )

    decision = evaluate_runtime_lane(
        token=sample_v4_token,
        action_required_rung="mutate",
    )

    assert decision.final_action == "step_up"
    assert decision.verification == sample_verification_result_step_up


def test_evaluate_runtime_lane_chokepoint_reject(
    sample_v4_token,
    sample_verification_result_pass,
    sample_risk_tier_decision,
    sample_chokepoint_result_reject,
    monkeypatch,
):
    """Test evaluate_runtime_lane when chokepoint rejects."""
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.verify_v4_token",
        lambda *args, **kwargs: sample_verification_result_pass,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.select_runtime_band",
        lambda *args, **kwargs: sample_risk_tier_decision,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.run_chokepoint_v4",
        lambda *args, **kwargs: sample_chokepoint_result_reject,
    )

    decision = evaluate_runtime_lane(
        token=sample_v4_token,
        action_required_rung="mutate",
    )

    assert decision.final_action == "reject"
    assert decision.chokepoint == sample_chokepoint_result_reject


def test_evaluate_runtime_lane_chokepoint_remediate(
    sample_v4_token,
    sample_verification_result_pass,
    sample_risk_tier_decision,
    sample_chokepoint_result_remediate,
    monkeypatch,
):
    """Test evaluate_runtime_lane when chokepoint requires remediation."""
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.verify_v4_token",
        lambda *args, **kwargs: sample_verification_result_pass,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.select_runtime_band",
        lambda *args, **kwargs: sample_risk_tier_decision,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.run_chokepoint_v4",
        lambda *args, **kwargs: sample_chokepoint_result_remediate,
    )

    decision = evaluate_runtime_lane(
        token=sample_v4_token,
        action_required_rung="mutate",
    )

    assert decision.final_action == "remediate"
    assert decision.chokepoint == sample_chokepoint_result_remediate


def test_evaluate_runtime_lane_handoff_reject(
    sample_v4_token,
    sample_verification_result_pass,
    sample_risk_tier_decision,
    sample_chokepoint_result_allow,
    sample_handoff_result_reject,
    monkeypatch,
):
    """Test evaluate_runtime_lane when handoff validation rejects."""
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.verify_v4_token",
        lambda *args, **kwargs: sample_verification_result_pass,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.select_runtime_band",
        lambda *args, **kwargs: sample_risk_tier_decision,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.run_chokepoint_v4",
        lambda *args, **kwargs: sample_chokepoint_result_allow,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.validate_handoff",
        lambda *args, **kwargs: sample_handoff_result_reject,
    )

    from agentic_core.L5_safety.identity.runtime_rails import AgentRegistryRecord
    handoff_target = AgentRegistryRecord(
        agent_id="target_agent",
        allowed_scope_ceiling=("read", "write"),
        allowed_inbound_handoff_scopes=("default",),
    )

    decision = evaluate_runtime_lane(
        token=sample_v4_token,
        action_required_rung="mutate",
        handoff_target=handoff_target,
    )

    assert decision.final_action == "reject"
    assert decision.handoff == sample_handoff_result_reject


def test_evaluate_runtime_lane_no_handoff_when_target_none(
    sample_v4_token,
    sample_verification_result_pass,
    sample_risk_tier_decision,
    sample_chokepoint_result_allow,
    monkeypatch,
):
    """Test evaluate_runtime_lane skips handoff validation when target is None."""
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.verify_v4_token",
        lambda *args, **kwargs: sample_verification_result_pass,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.select_runtime_band",
        lambda *args, **kwargs: sample_risk_tier_decision,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.run_chokepoint_v4",
        lambda *args, **kwargs: sample_chokepoint_result_allow,
    )

    decision = evaluate_runtime_lane(
        token=sample_v4_token,
        action_required_rung="mutate",
        handoff_target=None,
    )

    assert decision.handoff is None
    assert decision.final_action == "allow"


def test_evaluate_runtime_lane_reject_takes_precedence_over_step_up(
    sample_v4_token,
    sample_verification_result_step_up,
    sample_risk_tier_decision,
    sample_chokepoint_result_reject,
    monkeypatch,
):
    """Test that reject takes precedence over step_up in final_action composition."""
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.verify_v4_token",
        lambda *args, **kwargs: sample_verification_result_step_up,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.select_runtime_band",
        lambda *args, **kwargs: sample_risk_tier_decision,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.run_chokepoint_v4",
        lambda *args, **kwargs: sample_chokepoint_result_reject,
    )

    decision = evaluate_runtime_lane(
        token=sample_v4_token,
        action_required_rung="mutate",
    )

    # Chokepoint reject should take precedence over verification step_up
    assert decision.final_action == "reject"


def test_evaluate_runtime_lane_step_up_takes_precedence_over_remediate(
    sample_v4_token,
    sample_verification_result_step_up,
    sample_risk_tier_decision,
    sample_chokepoint_result_remediate,
    monkeypatch,
):
    """Test that step_up takes precedence over remediate in final_action composition."""
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.verify_v4_token",
        lambda *args, **kwargs: sample_verification_result_step_up,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.select_runtime_band",
        lambda *args, **kwargs: sample_risk_tier_decision,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.run_chokepoint_v4",
        lambda *args, **kwargs: sample_chokepoint_result_remediate,
    )

    decision = evaluate_runtime_lane(
        token=sample_v4_token,
        action_required_rung="mutate",
    )

    # Verification step_up should take precedence over chokepoint remediate
    assert decision.final_action == "step_up"


def test_evaluate_runtime_lane_remediate_takes_precedence_over_allow(
    sample_v4_token,
    sample_verification_result_pass,
    sample_risk_tier_decision,
    sample_chokepoint_result_remediate,
    monkeypatch,
):
    """Test that remediate takes precedence over allow in final_action composition."""
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.verify_v4_token",
        lambda *args, **kwargs: sample_verification_result_pass,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.select_runtime_band",
        lambda *args, **kwargs: sample_risk_tier_decision,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.run_chokepoint_v4",
        lambda *args, **kwargs: sample_chokepoint_result_remediate,
    )

    decision = evaluate_runtime_lane(
        token=sample_v4_token,
        action_required_rung="mutate",
    )

    # Chokepoint remediate should take precedence over allow
    assert decision.final_action == "remediate"


def test_evaluate_runtime_lane_passes_all_parameters(
    sample_v4_token,
    sample_verification_result_pass,
    sample_risk_tier_decision,
    sample_chokepoint_result_allow,
    monkeypatch,
):
    """Test evaluate_runtime_lane accepts all parameters without error."""
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.verify_v4_token",
        lambda *args, **kwargs: sample_verification_result_pass,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.select_runtime_band",
        lambda *args, **kwargs: sample_risk_tier_decision,
    )
    monkeypatch.setattr(
        "agentic_core.L5_safety.identity.runtime_entry.run_chokepoint_v4",
        lambda *args, **kwargs: sample_chokepoint_result_allow,
    )

    guardrail_outcome = GuardrailOutcome(
        family=GuardrailFamily.PII,
        layer="client_universal",
        stage="ingress",
        action="allow",
        score=0.0,
        evidence="no_pii",
    )
    guard_model_outcome = GuardrailOutcome(
        family=GuardrailFamily.JAILBREAK,
        layer="client_universal",
        stage="guard_model",
        action="allow",
        score=0.0,
        evidence="no_jailbreak",
    )

    # This test just verifies the function accepts all parameters without error
    decision = evaluate_runtime_lane(
        token=sample_v4_token,
        action_required_rung="mutate",
        ingress_outcomes=[guardrail_outcome],
        egress_outcomes=[guardrail_outcome],
        guard_model_outcome=guard_model_outcome,
        action_connector_id="test_connector",
        action_tool_id="test_tool",
        connector_is_registered=True,
        touches_write_surface=True,
        current_semantic_tick=1000,
        expected_plan_digest="plan_digest_abc",
        revoked_token_ids=("revoked_123",),
        active_policy_version="v4.0.0",
    )

    assert decision.final_action == "allow"
