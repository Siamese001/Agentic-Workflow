"""Composite validator — orchestrates the three gate validators.

The composite pattern lets callers (L2 step adapters, audit tools)
run the full validator stack against a DecisionPacket with one call
and inspect per-validator results.
"""
from __future__ import annotations

from typing import Any, Iterable

from apps_underwriting_ai.engines.risk_scorer import RiskScoreBreakdown
from apps_underwriting_ai.types.underwriting_types import (
    DecisionPacket,
    UnderwritingRequest,
)
from apps_underwriting_ai.validators.base_validator import (
    BaseValidator,
    ValidationResult,
)
from apps_underwriting_ai.validators.required_field_validator import (
    RequiredFieldValidator,
)
from apps_underwriting_ai.validators.risk_score_bounds_validator import (
    RiskScoreBoundsValidator,
)
from apps_underwriting_ai.validators.rubric_coverage_validator import (
    RubricCoverageValidator,
)


class DecisionPacketValidator(BaseValidator):
    """Composite of required-field + risk-score-bounds + rubric-coverage.

    Accepts all three sub-validator inputs:
      - ``request`` (UnderwritingRequest)
      - ``breakdown`` (RiskScoreBreakdown)
      - ``decision`` (DecisionPacket)

    Missing inputs skip that validator with a structured ``skipped``
    result rather than raising.
    """

    name = "decision_packet"

    def __init__(self, validators: Iterable[BaseValidator] | None = None) -> None:
        if validators is None:
            self._validators: tuple[BaseValidator, ...] = (
                RequiredFieldValidator(),
                RiskScoreBoundsValidator(),
                RubricCoverageValidator(),
            )
        else:
            self._validators = tuple(validators)

    def validate(self, **kwargs: Any) -> ValidationResult:
        """Aggregate: ``passed`` = all sub-validators pass.

        The ``context['results']`` field carries the per-validator
        :class:`ValidationResult` list so callers can inspect individual
        outcomes without re-running.
        """
        results = self.run_all(**kwargs)
        # Only "error" severity failures break the gate
        blocking = tuple(r for r in results if not r.passed and r.severity == "error")
        passed = not blocking
        message = (
            f"{len(results)} validators ran, {len(blocking)} blocking failures"
        )
        return ValidationResult(
            validator=self.name,
            passed=passed,
            severity="error" if blocking else "info",
            message=message,
            context={
                "results": tuple(results),
                "blocking_count": len(blocking),
                "validator_names": tuple(v.name for v in self._validators),
            },
        )

    def run_all(self, **kwargs: Any) -> tuple[ValidationResult, ...]:
        """Run every sub-validator, returning results in registration order."""
        results: list[ValidationResult] = []
        for validator in self._validators:
            results.append(self._run_one(validator, **kwargs))
        return tuple(results)

    def _run_one(self, validator: BaseValidator, **kwargs: Any) -> ValidationResult:
        # Each sub-validator only uses its own kwargs; skip if required input missing
        if isinstance(validator, RequiredFieldValidator):
            if "request" not in kwargs or not isinstance(
                kwargs["request"], UnderwritingRequest
            ):
                return _skipped(validator.name, "request not provided")
            return validator.validate(request=kwargs["request"])
        if isinstance(validator, RiskScoreBoundsValidator):
            if "breakdown" not in kwargs or not isinstance(
                kwargs["breakdown"], RiskScoreBreakdown
            ):
                return _skipped(validator.name, "breakdown not provided")
            return validator.validate(breakdown=kwargs["breakdown"])
        if isinstance(validator, RubricCoverageValidator):
            if "decision" not in kwargs or not isinstance(
                kwargs["decision"], DecisionPacket
            ):
                return _skipped(validator.name, "decision not provided")
            return validator.validate(decision=kwargs["decision"])
        # Unknown validator type — call it with all kwargs and trust it
        return validator.validate(**kwargs)


def _skipped(name: str, reason: str) -> ValidationResult:
    return ValidationResult(
        validator=name,
        passed=True,  # Skipped validators don't block — they're informational
        severity="info",
        message=f"skipped: {reason}",
        context={"skipped": True, "reason": reason},
    )
