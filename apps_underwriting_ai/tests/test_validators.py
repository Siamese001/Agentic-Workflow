"""W2 validator contract tests."""
from __future__ import annotations

import pytest

from apps_underwriting_ai.engines.risk_scorer import (
    APPROVE_CEILING,
    REFER_CEILING,
    DeterministicRiskScorer,
    RiskScoreBreakdown,
)
from apps_underwriting_ai.types.underwriting_types import (
    DecisionPacket,
    DecisionVerdict,
    EvidenceRegister,
    UnderwritingRequest,
)
from apps_underwriting_ai.validators import (
    BaseValidator,
    DecisionPacketValidator,
    RequiredFieldValidator,
    RiskScoreBoundsValidator,
    RubricCoverageValidator,
    ValidationResult,
)


# -- ValidationResult contract -----------------------------------------------


def test_validation_result_is_frozen() -> None:
    from dataclasses import FrozenInstanceError

    r = ValidationResult(validator="v", passed=True)
    with pytest.raises(FrozenInstanceError):
        r.passed = False  # type: ignore[misc]


def test_validation_result_rejects_invalid_severity() -> None:
    with pytest.raises(ValueError, match="severity must be"):
        ValidationResult(validator="v", passed=True, severity="catastrophic")


def test_validation_result_accepts_all_three_severities() -> None:
    for sev in ("info", "warning", "error"):
        r = ValidationResult(validator="v", passed=True, severity=sev)
        assert r.severity == sev


def test_base_validator_raises_notimpl() -> None:
    v = BaseValidator()
    with pytest.raises(NotImplementedError, match="subclass"):
        v.validate()


# -- RequiredFieldValidator --------------------------------------------------


def _good_request() -> UnderwritingRequest:
    return UnderwritingRequest(
        request_id="r1", applicant_id="a1", product_class="auto"
    )


def test_required_field_passes_on_good_request() -> None:
    result = RequiredFieldValidator().validate(request=_good_request())
    assert result.passed
    assert result.severity == "info"


def test_required_field_fails_on_empty_request_id() -> None:
    bad = UnderwritingRequest(
        request_id="", applicant_id="a1", product_class="auto"
    )
    result = RequiredFieldValidator().validate(request=bad)
    assert not result.passed
    assert "request_id" in result.context["missing"]


def test_required_field_fails_on_whitespace_applicant_id() -> None:
    bad = UnderwritingRequest(
        request_id="r1", applicant_id="   ", product_class="auto"
    )
    result = RequiredFieldValidator().validate(request=bad)
    assert not result.passed
    assert "applicant_id" in result.context["missing"]


def test_required_field_fails_when_not_an_underwriting_request() -> None:
    result = RequiredFieldValidator().validate(request={"request_id": "r1"})
    assert not result.passed
    assert "not an UnderwritingRequest" in result.message


def test_required_field_rolls_up_multiple_missing() -> None:
    bad = UnderwritingRequest(
        request_id="", applicant_id="", product_class="auto"
    )
    result = RequiredFieldValidator().validate(request=bad)
    assert not result.passed
    missing = result.context["missing"]
    assert "request_id" in missing
    assert "applicant_id" in missing


# -- RiskScoreBoundsValidator -----------------------------------------------


def _scored(request: UnderwritingRequest) -> RiskScoreBreakdown:
    return DeterministicRiskScorer().score(
        request=request,
        register=EvidenceRegister(request_id=request.request_id),
    )


def test_risk_bounds_passes_on_scorer_output() -> None:
    breakdown = _scored(_good_request())
    result = RiskScoreBoundsValidator().validate(breakdown=breakdown)
    assert result.passed
    assert result.severity == "info"


def test_risk_bounds_rejects_non_breakdown_input() -> None:
    result = RiskScoreBoundsValidator().validate(breakdown="not a breakdown")
    assert not result.passed
    assert "not a RiskScoreBreakdown" in result.message


def test_risk_bounds_fails_on_out_of_range_risk_score() -> None:
    bad = RiskScoreBreakdown(
        risk_score=150.0,
        verdict=DecisionVerdict.DECLINE,
        evidence_completeness=1.0,
        reconciliation_completeness=1.0,
        document_density=1.0,
        coverage_score=1.0,
        product_class="auto",
        product_risk_tier=50.0,
        rationale="",
        threshold_band="decline",
    )
    result = RiskScoreBoundsValidator().validate(breakdown=bad)
    assert not result.passed
    assert "risk_score=150" in result.message


def test_risk_bounds_fails_on_approve_above_ceiling() -> None:
    bad = RiskScoreBreakdown(
        risk_score=APPROVE_CEILING + 5,
        verdict=DecisionVerdict.APPROVE,
        evidence_completeness=1.0,
        reconciliation_completeness=1.0,
        document_density=1.0,
        coverage_score=1.0,
        product_class="auto",
        product_risk_tier=50.0,
        rationale="",
        threshold_band="approve",
    )
    result = RiskScoreBoundsValidator().validate(breakdown=bad)
    assert not result.passed
    assert "APPROVE_CEILING" in result.message


def test_risk_bounds_fails_on_decline_below_ceiling() -> None:
    bad = RiskScoreBreakdown(
        risk_score=REFER_CEILING - 10,
        verdict=DecisionVerdict.DECLINE,
        evidence_completeness=0.1,
        reconciliation_completeness=0.1,
        document_density=0.1,
        coverage_score=0.1,
        product_class="auto",
        product_risk_tier=50.0,
        rationale="",
        threshold_band="decline",
    )
    result = RiskScoreBoundsValidator().validate(breakdown=bad)
    assert not result.passed
    assert "REFER_CEILING" in result.message


# -- RubricCoverageValidator ------------------------------------------------


def _decision_packet(with_keys: bool = True, rationale: str = "A" * 100) -> DecisionPacket:
    feature_summary: dict[str, float] = (
        {"evidence_completeness": 0.8, "reconciliation_completeness": 0.9}
        if with_keys
        else {}
    )
    return DecisionPacket(
        request_id="r-rub",
        verdict=DecisionVerdict.APPROVE,
        rationale=rationale,
        evidence_refs=(),
        feature_summary=feature_summary,
        gate_violations=(),
    )


def test_rubric_coverage_passes_with_all_required() -> None:
    result = RubricCoverageValidator().validate(decision=_decision_packet(True))
    assert result.passed


def test_rubric_coverage_warns_on_missing_keys() -> None:
    result = RubricCoverageValidator().validate(decision=_decision_packet(False))
    assert not result.passed
    assert result.severity == "warning"
    assert "missing feature_summary keys" in result.message


def test_rubric_coverage_warns_on_short_rationale() -> None:
    result = RubricCoverageValidator().validate(
        decision=_decision_packet(True, rationale="short")
    )
    assert not result.passed
    assert "below minimum length" in result.message


def test_rubric_coverage_honors_custom_required_keys() -> None:
    result = RubricCoverageValidator(
        required_feature_keys=("custom_metric",)
    ).validate(decision=_decision_packet(True))
    assert not result.passed
    assert "custom_metric" in result.message


def test_rubric_coverage_rejects_non_decision_input() -> None:
    result = RubricCoverageValidator().validate(decision={"not": "a decision"})
    assert not result.passed
    assert "not a DecisionPacket" in result.message


# -- DecisionPacketValidator composite --------------------------------------


def test_composite_runs_all_subvalidators() -> None:
    request = _good_request()
    breakdown = _scored(request)
    decision = _decision_packet(True)
    result = DecisionPacketValidator().validate(
        request=request, breakdown=breakdown, decision=decision
    )
    assert result.passed
    assert len(result.context["results"]) == 3
    validators = [r.validator for r in result.context["results"]]
    assert "required_field" in validators
    assert "risk_score_bounds" in validators
    assert "rubric_coverage" in validators


def test_composite_passes_when_only_non_error_fails() -> None:
    """Rubric-coverage warnings don't block the composite."""
    request = _good_request()
    breakdown = _scored(request)
    result = DecisionPacketValidator().validate(
        request=request,
        breakdown=breakdown,
        decision=_decision_packet(False),  # fails rubric (warning)
    )
    assert result.passed  # warning-severity failure does not block
    assert result.context["blocking_count"] == 0


def test_composite_fails_when_error_severity_fails() -> None:
    request = UnderwritingRequest(
        request_id="", applicant_id="a", product_class="auto"
    )
    breakdown = _scored(_good_request())
    result = DecisionPacketValidator().validate(
        request=request, breakdown=breakdown, decision=_decision_packet(True)
    )
    assert not result.passed
    assert result.context["blocking_count"] >= 1


def test_composite_skips_validators_with_missing_inputs() -> None:
    result = DecisionPacketValidator().validate()
    # All skipped; composite passes (skips are info)
    assert result.passed
    skipped = [r for r in result.context["results"] if r.context.get("skipped")]
    assert len(skipped) == 3
