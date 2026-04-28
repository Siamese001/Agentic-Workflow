"""Comprehensive tests for guardrail_adapter.py module."""

import pytest

from agentic_core.L5_safety.identity.guardrail_adapter import ChokepointV4Result, run_chokepoint_v4
from agentic_core.L5_safety.identity.guardrail_bank import (
    GuardrailFamily,
    GuardrailOutcome,
    resolve_bank_verdict,
    compose_egress_inspection,
)


@pytest.fixture
def sample_allow_outcome() -> GuardrailOutcome:
    """Sample guardrail outcome with allow action."""
    return GuardrailOutcome(
        family=GuardrailFamily.PII,
        layer="client_universal",
        stage="ingress",
        action="allow",
        score=0.0,
        evidence="no_pii",
    )


@pytest.fixture
def sample_reject_outcome() -> GuardrailOutcome:
    """Sample guardrail outcome with reject action."""
    return GuardrailOutcome(
        family=GuardrailFamily.PII,
        layer="client_universal",
        stage="ingress",
        action="reject",
        score=1.0,
        evidence="pii_detected",
    )


@pytest.fixture
def sample_remediate_outcome() -> GuardrailOutcome:
    """Sample guardrail outcome with remediate action."""
    return GuardrailOutcome(
        family=GuardrailFamily.PII,
        layer="client_universal",
        stage="ingress",
        action="remediate",
        score=0.8,
        evidence="pii_detected_remediable",
    )


def test_chokepoint_v4_result_to_dict(sample_allow_outcome):
    """Test ChokepointV4Result.to_dict serialization."""
    ingress_verdict = resolve_bank_verdict("ingress", (sample_allow_outcome,))
    egress_verdict = resolve_bank_verdict("egress", (sample_allow_outcome,))
    egress_inspection = compose_egress_inspection(egress_verdict, None)

    result = ChokepointV4Result(
        ingress_verdict=ingress_verdict,
        egress_inspection=egress_inspection,
        final_action="allow",
    )

    data = result.to_dict()
    assert data["final_action"] == "allow"
    assert "ingress_verdict" in data
    assert "egress_inspection" in data
    assert data["ingress_verdict"]["verdict"] == "allow"
    assert data["egress_inspection"]["final_action"] == "allow"


def test_run_chokepoint_v4_all_allow(sample_allow_outcome):
    """Test run_chokepoint_v4 when all outcomes allow."""
    result = run_chokepoint_v4(
        ingress_outcomes=[sample_allow_outcome],
        egress_outcomes=[sample_allow_outcome],
        guard_model_outcome=None,
    )

    assert result.final_action == "allow"
    assert result.ingress_verdict.verdict == "allow"
    assert result.egress_inspection.final_action == "allow"


def test_run_chokepoint_v4_ingress_reject(sample_allow_outcome, sample_reject_outcome):
    """Test run_chokepoint_v4 when ingress rejects."""
    result = run_chokepoint_v4(
        ingress_outcomes=[sample_reject_outcome],
        egress_outcomes=[sample_allow_outcome],
        guard_model_outcome=None,
    )

    # Ingress reject should take precedence
    assert result.final_action == "reject"
    assert result.ingress_verdict.verdict == "reject"


def test_run_chokepoint_v4_egress_reject(sample_allow_outcome, sample_reject_outcome):
    """Test run_chokepoint_v4 when egress rejects."""
    # Create egress reject outcome
    egress_reject = GuardrailOutcome(
        family=GuardrailFamily.PII,
        layer="client_universal",
        stage="egress",
        action="reject",
        score=1.0,
        evidence="pii_detected",
    )

    result = run_chokepoint_v4(
        ingress_outcomes=[sample_allow_outcome],
        egress_outcomes=[egress_reject],
        guard_model_outcome=None,
    )

    # Egress reject should take precedence
    assert result.final_action == "reject"
    assert result.egress_inspection.final_action == "reject"


def test_run_chokepoint_v4_guard_model_reject(sample_allow_outcome, sample_reject_outcome):
    """Test run_chokepoint_v4 when guard model rejects."""
    # Create guard model reject outcome
    guard_model_reject = GuardrailOutcome(
        family=GuardrailFamily.JAILBREAK,
        layer="client_universal",
        stage="guard_model",
        action="reject",
        score=1.0,
        evidence="jailbreak_detected",
    )

    result = run_chokepoint_v4(
        ingress_outcomes=[sample_allow_outcome],
        egress_outcomes=[sample_allow_outcome],
        guard_model_outcome=guard_model_reject,
    )

    # Guard model reject should take precedence
    assert result.final_action == "reject"
    assert result.egress_inspection.final_action == "reject"


def test_run_chokepoint_v4_remediate(sample_allow_outcome, sample_remediate_outcome):
    """Test run_chokepoint_v4 when remediate is required."""
    result = run_chokepoint_v4(
        ingress_outcomes=[sample_remediate_outcome],
        egress_outcomes=[sample_allow_outcome],
        guard_model_outcome=None,
    )

    assert result.final_action == "remediate"
    assert result.ingress_verdict.verdict == "remediate"


def test_run_chokepoint_v4_reject_takes_precedence_over_remediate(
    sample_reject_outcome, sample_remediate_outcome
):
    """Test that reject takes precedence over remediate."""
    result = run_chokepoint_v4(
        ingress_outcomes=[sample_reject_outcome],
        egress_outcomes=[sample_remediate_outcome],
        guard_model_outcome=None,
    )

    # Reject should take precedence over remediate
    assert result.final_action == "reject"


def test_run_chokepoint_v4_remediate_takes_precedence_over_allow(
    sample_allow_outcome, sample_remediate_outcome
):
    """Test that remediate takes precedence over allow."""
    result = run_chokepoint_v4(
        ingress_outcomes=[sample_allow_outcome],
        egress_outcomes=[sample_remediate_outcome],
        guard_model_outcome=None,
    )

    # Remediate should take precedence over allow
    assert result.final_action == "remediate"


def test_run_chokepoint_v4_empty_outcomes():
    """Test run_chokepoint_v4 with empty outcomes."""
    result = run_chokepoint_v4(
        ingress_outcomes=[],
        egress_outcomes=[],
        guard_model_outcome=None,
    )

    # Empty outcomes should default to allow
    assert result.final_action == "allow"
    assert result.ingress_verdict.verdict == "allow"
    assert result.egress_inspection.final_action == "allow"


def test_run_chokepoint_v4_multiple_outcomes(sample_allow_outcome, sample_reject_outcome):
    """Test run_chokepoint_v4 with multiple outcomes."""
    result = run_chokepoint_v4(
        ingress_outcomes=[sample_allow_outcome, sample_reject_outcome],
        egress_outcomes=[sample_allow_outcome],
        guard_model_outcome=None,
    )

    # One reject should cause overall reject
    assert result.final_action == "reject"
    assert result.ingress_verdict.verdict == "reject"


def test_chokepoint_v4_result_frozen():
    """Test that ChokepointV4Result is frozen."""
    ingress_verdict = resolve_bank_verdict("ingress", ())
    egress_verdict = resolve_bank_verdict("egress", ())
    egress_inspection = compose_egress_inspection(egress_verdict, None)

    result = ChokepointV4Result(
        ingress_verdict=ingress_verdict,
        egress_inspection=egress_inspection,
        final_action="allow",
    )

    with pytest.raises(Exception):  # frozen dataclass raises on assignment
        result.final_action = "reject"
