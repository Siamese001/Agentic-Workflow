"""Tests for L5_safety/identity/guardrail_bank.py."""

import pytest

from agentic_core.L5_safety.identity.guardrail_bank import (
    EgressInspectionResult,
    GuardrailBankVerdict,
    GuardrailFamily,
    GuardrailOutcome,
    compose_egress_inspection,
    resolve_bank_verdict,
)


def test_resolve_bank_verdict_all_allow():
    """Test resolve_bank_verdict when all outcomes are ALLOW."""
    outcomes = (
        GuardrailOutcome(
            family=GuardrailFamily.PII,
            layer="client_universal",
            stage="ingress",
            action="allow",
            score=0.0,
            evidence="no_pii",
        ),
        GuardrailOutcome(
            family=GuardrailFamily.SECRETS,
            layer="client_universal",
            stage="ingress",
            action="allow",
            score=0.0,
            evidence="no_secrets",
        ),
    )
    
    verdict = resolve_bank_verdict(stage="ingress", outcomes=outcomes)
    
    assert verdict.verdict == "allow"
    assert verdict.stage == "ingress"
    assert len(verdict.ordered_outcomes) == 2


def test_resolve_bank_verdict_one_reject():
    """Test resolve_bank_verdict when one outcome is REJECT."""
    outcomes = (
        GuardrailOutcome(
            family=GuardrailFamily.PII,
            layer="client_universal",
            stage="ingress",
            action="allow",
            score=0.0,
            evidence="no_pii",
        ),
        GuardrailOutcome(
            family=GuardrailFamily.SECRETS,
            layer="client_universal",
            stage="ingress",
            action="reject",
            score=0.9,
            evidence="api_key_detected",
            hard_constraint=True,
        ),
    )
    
    verdict = resolve_bank_verdict(stage="ingress", outcomes=outcomes)
    
    assert verdict.verdict == "reject"


def test_resolve_bank_verdict_remediate_vs_reject_precedence():
    """Test that REJECT takes precedence over REMEDIATE."""
    outcomes = (
        GuardrailOutcome(
            family=GuardrailFamily.PII,
            layer="client_universal",
            stage="ingress",
            action="remediate",
            score=0.5,
            evidence="pii_found",
        ),
        GuardrailOutcome(
            family=GuardrailFamily.SECRETS,
            layer="client_universal",
            stage="ingress",
            action="reject",
            score=0.9,
            evidence="api_key_detected",
            hard_constraint=True,
        ),
    )
    
    verdict = resolve_bank_verdict(stage="ingress", outcomes=outcomes)
    
    # REJECT should win
    assert verdict.verdict == "reject"


def test_resolve_bank_verdict_layer_ordering():
    """Test that client_universal outcomes are ordered before agent_domain."""
    outcomes = (
        GuardrailOutcome(
            family=GuardrailFamily.PII,
            layer="agent_domain",
            stage="ingress",
            action="remediate",
            score=0.5,
            evidence="pii_found",
        ),
        GuardrailOutcome(
            family=GuardrailFamily.SECRETS,
            layer="client_universal",
            stage="ingress",
            action="allow",
            score=0.0,
            evidence="no_secrets",
        ),
    )
    
    verdict = resolve_bank_verdict(stage="ingress", outcomes=outcomes)
    
    # client_universal should come first despite being second in input
    assert verdict.ordered_outcomes[0].layer == "client_universal"
    assert verdict.ordered_outcomes[1].layer == "agent_domain"


def test_guardrail_outcome_validation_requires_score_in_range():
    """Test that GuardrailOutcome requires score in [0.0, 1.0]."""
    with pytest.raises(ValueError, match="score must be in"):
        GuardrailOutcome(
            family=GuardrailFamily.PII,
            layer="client_universal",
            stage="ingress",
            action="allow",
            score=1.5,  # Invalid score
            evidence="test",
        )


def test_guardrail_outcome_validation_requires_valid_action():
    """Test that GuardrailOutcome requires valid action."""
    with pytest.raises(ValueError, match="action must be allow|remediate|reject"):
        GuardrailOutcome(
            family=GuardrailFamily.PII,
            layer="client_universal",
            stage="ingress",
            action="invalid",  # Invalid action
            score=0.0,
            evidence="test",
        )


def test_guardrail_outcome_validation_forbids_remediate_on_hard_constraint():
    """Test that GuardrailOutcome forbids remediate with hard_constraint=True."""
    with pytest.raises(ValueError, match="remediate is FORBIDDEN on hard_constraint"):
        GuardrailOutcome(
            family=GuardrailFamily.PII,
            layer="client_universal",
            stage="ingress",
            action="remediate",
            score=0.5,
            evidence="test",
            hard_constraint=True,
        )


def test_guardrail_outcome_validation_requires_evidence():
    """Test that GuardrailOutcome requires non-empty evidence."""
    with pytest.raises(ValueError, match="evidence required"):
        GuardrailOutcome(
            family=GuardrailFamily.PII,
            layer="client_universal",
            stage="ingress",
            action="allow",
            score=0.0,
            evidence="",  # Empty evidence
        )


def test_guardrail_bank_verdict_validation_requires_digest():
    """Test that GuardrailBankVerdict requires non-empty digest."""
    with pytest.raises(ValueError, match="digest required"):
        GuardrailBankVerdict(
            stage="ingress",
            verdict="allow",
            ordered_outcomes=(),
            digest="",  # Empty digest
        )


def test_compose_egress_inspection():
    """Test compose_egress_inspection for egress-side guardrail evaluation."""
    outcomes = (
        GuardrailOutcome(
            family=GuardrailFamily.PII,
            layer="agent_domain",
            stage="egress",
            action="allow",
            score=0.0,
            evidence="no_pii_in_response",
        ),
        GuardrailOutcome(
            family=GuardrailFamily.HALLUCINATION,
            layer="agent_domain",
            stage="egress",
            action="allow",
            score=0.1,
            evidence="low_hallucination_risk",
        ),
    )
    
    bank_verdict = resolve_bank_verdict(stage="egress", outcomes=outcomes)
    result = compose_egress_inspection(bank_verdict=bank_verdict)
    
    assert isinstance(result, EgressInspectionResult)
    assert result.final_action == "allow"
    assert result.guard_model_outcome is None


def test_compose_egress_inspection_with_guard_model():
    """Test compose_egress_inspection with guard_model outcome."""
    outcomes = (
        GuardrailOutcome(
            family=GuardrailFamily.PII,
            layer="agent_domain",
            stage="egress",
            action="allow",
            score=0.0,
            evidence="no_pii_in_response",
        ),
    )
    
    bank_verdict = resolve_bank_verdict(stage="egress", outcomes=outcomes)
    guard_model_outcome = GuardrailOutcome(
        family=GuardrailFamily.HALLUCINATION,
        layer="guard_model",
        stage="guard_model",
        action="remediate",
        score=0.7,
        evidence="guard_model_flagged",
    )
    
    result = compose_egress_inspection(
        bank_verdict=bank_verdict,
        guard_model_outcome=guard_model_outcome,
    )
    
    # remediate (guard model) should override allow (bank)
    assert result.final_action == "remediate"
    assert result.guard_model_outcome is not None


def test_egress_inspection_result_validation_requires_egress_stage():
    """Test that EgressInspectionResult requires bank_verdict.stage='egress'."""
    bank_verdict = resolve_bank_verdict(
        stage="ingress",
        outcomes=(
            GuardrailOutcome(
                family=GuardrailFamily.PII,
                layer="agent_domain",
                stage="ingress",
                action="allow",
                score=0.0,
                evidence="no_pii",
            ),
        ),
    )
    
    with pytest.raises(ValueError, match="bank_verdict.stage must be 'egress'"):
        EgressInspectionResult(
            bank_verdict=bank_verdict,
            guard_model_outcome=None,
            final_action="allow",
        )


def test_egress_inspection_result_validation_requires_guard_model_stage():
    """Test that EgressInspectionResult requires guard_model_outcome.stage='guard_model' if provided."""
    bank_verdict = resolve_bank_verdict(
        stage="egress",
        outcomes=(
            GuardrailOutcome(
                family=GuardrailFamily.PII,
                layer="agent_domain",
                stage="egress",
                action="allow",
                score=0.0,
                evidence="no_pii",
            ),
        ),
    )
    
    guard_model_outcome = GuardrailOutcome(
        family=GuardrailFamily.HALLUCINATION,
        layer="guard_model",
        stage="egress",  # Wrong stage - should be 'guard_model'
        action="allow",
        score=0.0,
        evidence="test",
    )
    
    with pytest.raises(ValueError, match="guard_model_outcome.stage must be 'guard_model'"):
        EgressInspectionResult(
            bank_verdict=bank_verdict,
            guard_model_outcome=guard_model_outcome,
            final_action="allow",
        )
