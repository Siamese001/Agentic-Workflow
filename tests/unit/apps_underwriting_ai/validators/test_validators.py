"""Tests for apps_underwriting_ai validators module."""

from __future__ import annotations

from apps_underwriting_ai.engines.risk_scorer import RiskScoreBreakdown
from apps_underwriting_ai.types.underwriting_types import (
    DecisionPacket,
    DecisionVerdict,
    UnderwritingRequest,
)
from apps_underwriting_ai.validators.decision_packet_validator import (
    DecisionPacketValidator,
)


class TestValidatorsImportable:
    """Verify validators module is importable."""

    def test_validators_module_importable(self):
        """Test that apps_underwriting_ai.validators can be imported."""
        from apps_underwriting_ai import validators

        assert validators is not None


class TestDecisionPacketValidator:
    """Composite validator: skip semantics, aggregation, blocking errors."""

    def _valid_request(self) -> UnderwritingRequest:
        return UnderwritingRequest(
            request_id="r1",
            applicant_id="a1",
            product_class="auto",
        )

    def _invalid_breakdown(self) -> RiskScoreBreakdown:
        """risk_score out of [0, 100] — RiskScoreBoundsValidator must fail closed."""
        return RiskScoreBreakdown(
            risk_score=150.0,
            verdict=DecisionVerdict.APPROVE,
            evidence_completeness=0.5,
            reconciliation_completeness=0.5,
            document_density=0.5,
            coverage_score=0.5,
            product_class="auto",
            product_risk_tier=1.0,
            rationale="test-breakdown",
            threshold_band="approve",
        )

    def test_all_subvalidators_skipped_when_no_inputs(self) -> None:
        v = DecisionPacketValidator()
        result = v.validate()
        assert result.passed is True
        assert result.severity == "info"
        ctx = result.context
        assert ctx is not None
        assert ctx.get("blocking_count") == 0
        subs = ctx.get("results", ())
        assert len(subs) == 3
        assert all("skipped" in (s.message or "").lower() for s in subs)

    def test_required_field_failure_is_blocking(self) -> None:
        v = DecisionPacketValidator()
        bad = UnderwritingRequest(
            request_id="",
            applicant_id="a1",
            product_class="auto",
        )
        result = v.validate(request=bad)
        assert result.passed is False
        assert result.severity == "error"
        assert result.context and result.context.get("blocking_count", 0) >= 1

    def test_bounds_violation_on_breakdown_is_blocking(self) -> None:
        v = DecisionPacketValidator()
        result = v.validate(breakdown=self._invalid_breakdown())
        assert result.passed is False
        assert result.severity == "error"
        blocking = result.context.get("blocking_count") if result.context else 0
        assert blocking == 1

    def test_rubric_warning_does_not_block_composite(self) -> None:
        """RubricCoverageValidator uses severity=warning — must not fail the packet gate."""
        decision = DecisionPacket(
            request_id="r1",
            verdict=DecisionVerdict.APPROVE,
            rationale="too short",
            feature_summary={},
        )
        v = DecisionPacketValidator()
        result = v.validate(
            request=self._valid_request(),
            decision=decision,
        )
        assert result.passed is True
        subs = result.context.get("results", ()) if result.context else ()
        rubric = next((s for s in subs if s.validator == "rubric_coverage"), None)
        assert rubric is not None
        assert rubric.passed is False
        assert rubric.severity == "warning"
