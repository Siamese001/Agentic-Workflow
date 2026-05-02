"""Validates that a RiskScoreBreakdown respects the named-constant bounds.

Invariants checked (all defined in
:mod:`apps_underwriting_ai.engines.risk_scorer`):
  1. ``risk_score`` is in [0, 100].
  2. ``coverage_score`` is in [0, 1].
  3. Evidence/reconciliation/density sub-scores are in [0, 1].
  4. If verdict is APPROVE, ``risk_score < APPROVE_CEILING``.
  5. If verdict is DECLINE, ``risk_score >= REFER_CEILING``.
  6. If verdict is REFER, ``APPROVE_CEILING <= risk_score < REFER_CEILING``.

The scorer SHOULD always produce bounds-respecting output. This validator
catches drift between scorer logic and the documented invariants.
"""
from __future__ import annotations

from typing import Any

from apps_underwriting_ai.engines.risk_scorer import (
    APPROVE_CEILING,
    REFER_CEILING,
    RiskScoreBreakdown,
)
from apps_underwriting_ai.types.underwriting_types import DecisionVerdict
from apps_underwriting_ai.validators.base_validator import (
    BaseValidator,
    ValidationResult,
)


class RiskScoreBoundsValidator(BaseValidator):
    """Validate a scorer breakdown against documented bounds + verdict rules."""

    name = "risk_score_bounds"

    def validate(self, **kwargs: Any) -> ValidationResult:
        breakdown = kwargs.get("breakdown")
        if not isinstance(breakdown, RiskScoreBreakdown):
            return ValidationResult(
                validator=self.name,
                passed=False,
                severity="error",
                message="breakdown keyword is not a RiskScoreBreakdown",
                context={"type": type(breakdown).__name__},
            )

        violations: list[str] = []
        if not 0.0 <= breakdown.risk_score <= 100.0:
            violations.append(
                f"risk_score={breakdown.risk_score} out of [0, 100]"
            )
        if not 0.0 <= breakdown.coverage_score <= 1.0:
            violations.append(
                f"coverage_score={breakdown.coverage_score} out of [0, 1]"
            )
        for sub in (
            "evidence_completeness",
            "reconciliation_completeness",
            "document_density",
        ):
            value = getattr(breakdown, sub, None)
            if value is None:
                continue
            if not 0.0 <= float(value) <= 1.0:
                violations.append(f"{sub}={value} out of [0, 1]")

        verdict = breakdown.verdict
        if verdict == DecisionVerdict.APPROVE and breakdown.risk_score >= APPROVE_CEILING:
            violations.append(
                f"APPROVE with risk_score={breakdown.risk_score} >= "
                f"APPROVE_CEILING={APPROVE_CEILING}"
            )
        elif verdict == DecisionVerdict.REFER and not (
            APPROVE_CEILING <= breakdown.risk_score < REFER_CEILING
        ):
            violations.append(
                f"REFER with risk_score={breakdown.risk_score} outside "
                f"[{APPROVE_CEILING}, {REFER_CEILING})"
            )
        elif verdict == DecisionVerdict.DECLINE and breakdown.risk_score < REFER_CEILING:
            violations.append(
                f"DECLINE with risk_score={breakdown.risk_score} < "
                f"REFER_CEILING={REFER_CEILING}"
            )

        if violations:
            return ValidationResult(
                validator=self.name,
                passed=False,
                severity="error",
                message="; ".join(violations),
                context={
                    "violations": tuple(violations),
                    "risk_score": breakdown.risk_score,
                    "verdict": verdict.value if hasattr(verdict, "value") else str(verdict),
                },
            )
        return ValidationResult(
            validator=self.name,
            passed=True,
            severity="info",
            message="all bounds + verdict-band invariants respected",
            context={
                "risk_score": breakdown.risk_score,
                "verdict": verdict.value if hasattr(verdict, "value") else str(verdict),
            },
        )
