"""Validates that a DecisionPacket is sufficiently rubric-covered.

The judge rubric (``policy/rubrics/judge_underwriting_decision.yaml``)
declares the evidence/feature/unresolved counts that the rationale must
reference. This validator checks that the DecisionPacket carries enough
grounding for the judge pass.

Scope intent: the rubric wiring service (W3) feeds rubric dimensions to
the assembler; this validator enforces that the resulting DecisionPacket
is judge-readable. This is a CHEAP gate — full judge evaluation happens
elsewhere.
"""
from __future__ import annotations

from typing import Any, Iterable

from apps_underwriting_ai.types.underwriting_types import DecisionPacket
from apps_underwriting_ai.validators.base_validator import (
    BaseValidator,
    ValidationResult,
)


_DEFAULT_REQUIRED_FEATURE_KEYS: tuple[str, ...] = (
    "evidence_completeness",
    "reconciliation_completeness",
)
"""Minimum feature-vector keys that must be present for rubric coverage."""


class RubricCoverageValidator(BaseValidator):
    """Check that a DecisionPacket has the rubric-required grounding."""

    name = "rubric_coverage"

    def __init__(
        self,
        required_feature_keys: Iterable[str] | None = None,
        min_rationale_chars: int = 20,
    ) -> None:
        self._required_feature_keys = tuple(
            required_feature_keys or _DEFAULT_REQUIRED_FEATURE_KEYS
        )
        self._min_rationale_chars = int(min_rationale_chars)

    def validate(self, **kwargs: Any) -> ValidationResult:
        decision = kwargs.get("decision")
        if not isinstance(decision, DecisionPacket):
            return ValidationResult(
                validator=self.name,
                passed=False,
                severity="error",
                message="decision keyword is not a DecisionPacket",
                context={"type": type(decision).__name__},
            )
        violations: list[str] = []

        # Required feature-vector keys for judge grounding
        missing_keys = tuple(
            k for k in self._required_feature_keys if k not in decision.feature_summary
        )
        if missing_keys:
            violations.append(
                f"missing feature_summary keys: {', '.join(missing_keys)}"
            )

        # Rationale must be non-trivial (≥ min_rationale_chars)
        if len(decision.rationale.strip()) < self._min_rationale_chars:
            violations.append(
                f"rationale below minimum length "
                f"({len(decision.rationale.strip())} < {self._min_rationale_chars})"
            )

        if violations:
            return ValidationResult(
                validator=self.name,
                passed=False,
                severity="warning",  # not fatal — judge may still pass
                message="; ".join(violations),
                context={
                    "violations": tuple(violations),
                    "required_keys": self._required_feature_keys,
                    "present_keys": tuple(sorted(decision.feature_summary)),
                },
            )
        return ValidationResult(
            validator=self.name,
            passed=True,
            severity="info",
            message="rubric grounding present",
            context={
                "checked_keys": self._required_feature_keys,
                "rationale_chars": len(decision.rationale.strip()),
            },
        )
