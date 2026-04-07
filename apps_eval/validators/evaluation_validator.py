"""
L5 Evaluation Validation + Scoring Gates — apps_eval.enterprise.

Validates evaluation results against quality thresholds,
detects scoring anomalies, and enforces evaluation rigor.

Layer 5 Safety: Static analysis, policy enforcement, hallucination gates.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_verifies_policy,
)

_log = logging.getLogger(__name__)


class ViolationSeverity(str, Enum):
    """Severity of validation violation."""

    INFO = "info"
    WARNING = "warning"
    BLOCKING = "blocking"


@dataclass(frozen=True)
class ValidationViolation:
    """A validation violation or concern."""

    violation_id: str
    rule_id: str
    check_id: str
    severity: ViolationSeverity
    message: str
    suggestion: str


@dataclass
class EvaluationValidationResult:
    """Result of evaluation validation."""

    passed: bool
    violations: list[ValidationViolation] = field(default_factory=list)
    score_validations: list[dict[str, Any]] = field(default_factory=list)
    anomaly_flags: list[str] = field(default_factory=list)
    coverage_assessment: dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0


class ValidationRule:
    """A validation rule for evaluation results."""

    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        severity: ViolationSeverity,
        check_fn: callable,
    ):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.severity = severity
        self.check_fn = check_fn


class EvaluationValidator:
    """L5 validator for evaluation results."""

    # Suspicious score patterns
    ANOMALY_PATTERNS: list[tuple[str, str]] = [
        ("perfect_score", "Score is exactly 1.0 - verify no rounding/hand-waving"),
        ("zero_variance", "All dimensions have identical scores - unlikely in practice"),
        ("suspicious_latency", "All scenarios report identical latency - verify measurement"),
        ("no_failures", "Zero failures across all suites - may indicate insufficient test coverage"),
    ]

    def __init__(self) -> None:
        self.rules = self._initialize_rules()

    def validate(
        self,
        eval_result: dict[str, Any],
        suite_configs: list[dict[str, Any]],
        criteria_decompositions: list[dict[str, Any]],
    ) -> EvaluationValidationResult:
        """Validate evaluation result against quality standards."""
        _emit_records_execution_trace("enterprise", "EvaluationValidator", "validate_start")

        violations: list[ValidationViolation] = []
        score_validations: list[dict[str, Any]] = []

        # Run all validation rules
        for rule in self.rules:
            rule_violations = rule.check_fn(eval_result, suite_configs, criteria_decompositions)
            violations.extend(rule_violations)

        # Validate individual scores
        dimension_scores = eval_result.get("dimension_scores", {})
        for dim_id, score in dimension_scores.items():
            validation = self._validate_score(dim_id, score, eval_result)
            score_validations.append(validation)

        # Detect anomalies
        anomaly_flags = self._detect_anomalies(eval_result)

        # Assess coverage
        coverage = self._assess_coverage(eval_result, criteria_decompositions)

        # Calculate quality score
        quality_score = self._calculate_quality_score(violations, anomaly_flags, coverage)

        # Determine pass/fail
        blocking_count = len([v for v in violations if v.severity == ViolationSeverity.BLOCKING])
        passed = blocking_count == 0

        _emit_applies_guardrail("enterprise", "EvaluationValidator", "validation_complete")

        return EvaluationValidationResult(
            passed=passed,
            violations=violations,
            score_validations=score_validations,
            anomaly_flags=anomaly_flags,
            coverage_assessment=coverage,
            quality_score=quality_score,
        )

    def _initialize_rules(self) -> list[ValidationRule]:
        """Initialize all validation rules."""
        return [
            ValidationRule(
                rule_id="R001",
                name="Score Range",
                description="Verify all scores are within valid range [0, 1]",
                severity=ViolationSeverity.BLOCKING,
                check_fn=self._check_score_range,
            ),
            ValidationRule(
                rule_id="R002",
                name="Missing Dimensions",
                description="Check for missing dimension scores",
                severity=ViolationSeverity.WARNING,
                check_fn=self._check_missing_dimensions,
            ),
            ValidationRule(
                rule_id="R003",
                name="Execution Evidence",
                description="Verify evaluation has execution metadata",
                severity=ViolationSeverity.WARNING,
                check_fn=self._check_execution_evidence,
            ),
            ValidationRule(
                rule_id="R004",
                name="Suite Coverage",
                description="Verify all configured suites were evaluated",
                severity=ViolationSeverity.BLOCKING,
                check_fn=self._check_suite_coverage,
            ),
            ValidationRule(
                rule_id="R005",
                name="Latency Plausibility",
                description="Check latency values are plausible",
                severity=ViolationSeverity.WARNING,
                check_fn=self._check_latency_plausibility,
            ),
        ]

    def _check_score_range(
        self,
        eval_result: dict[str, Any],
        suite_configs: list[dict[str, Any]],
        criteria_decompositions: list[dict[str, Any]],
    ) -> list[ValidationViolation]:
        """Check scores are within valid range."""
        violations: list[ValidationViolation] = []

        dimension_scores = eval_result.get("dimension_scores", {})
        for dim_id, score in dimension_scores.items():
            if score < 0.0 or score > 1.0:
                violations.append(
                    ValidationViolation(
                        violation_id=f"V{len(violations)+1:03d}",
                        rule_id="R001",
                        check_id=dim_id,
                        severity=ViolationSeverity.BLOCKING,
                        message=f"Score {score} for {dim_id} is outside valid range [0, 1]",
                        suggestion="Verify score computation logic",
                    ),
                )

        return violations

    def _check_missing_dimensions(
        self,
        eval_result: dict[str, Any],
        suite_configs: list[dict[str, Any]],
        criteria_decompositions: list[dict[str, Any]],
    ) -> list[ValidationViolation]:
        """Check for missing expected dimensions."""
        violations: list[ValidationViolation] = []

        expected_dims = {"correctness", "determinism", "governance", "latency", "output_richness"}
        actual_dims = set(eval_result.get("dimension_scores", {}).keys())

        missing = expected_dims - actual_dims
        for dim in missing:
            violations.append(
                ValidationViolation(
                    violation_id=f"V{len(violations)+1:03d}",
                    rule_id="R002",
                    check_id=dim,
                    severity=ViolationSeverity.WARNING,
                    message=f"Missing dimension score: {dim}",
                    suggestion=f"Add evaluation coverage for {dim} dimension",
                ),
            )

        return violations

    def _check_execution_evidence(
        self,
        eval_result: dict[str, Any],
        suite_configs: list[dict[str, Any]],
        criteria_decompositions: list[dict[str, Any]],
    ) -> list[ValidationViolation]:
        """Check for execution evidence."""
        violations: list[ValidationViolation] = []

        if "execution_metadata" not in eval_result:
            violations.append(
                ValidationViolation(
                    violation_id="V001",
                    rule_id="R003",
                    check_id="metadata",
                    severity=ViolationSeverity.WARNING,
                    message="Missing execution metadata",
                    suggestion="Include timestamp, duration, and execution context",
                ),
            )

        return violations

    def _check_suite_coverage(
        self,
        eval_result: dict[str, Any],
        suite_configs: list[dict[str, Any]],
        criteria_decompositions: list[dict[str, Any]],
    ) -> list[ValidationViolation]:
        """Check all suites were evaluated."""
        violations: list[ValidationViolation] = []

        configured_suites = {s.get("suite_id") for s in suite_configs}
        evaluated_suites = set(eval_result.get("suite_results", {}).keys())

        missing = configured_suites - evaluated_suites
        for suite_id in missing:
            if suite_id:  # Skip None values
                violations.append(
                    ValidationViolation(
                        violation_id=f"V{len(violations)+1:03d}",
                        rule_id="R004",
                        check_id=suite_id,
                        severity=ViolationSeverity.BLOCKING,
                        message=f"Suite not evaluated: {suite_id}",
                        suggestion=f"Execute evaluation for {suite_id} suite",
                    ),
                )

        return violations

    def _check_latency_plausibility(
        self,
        eval_result: dict[str, Any],
        suite_configs: list[dict[str, Any]],
        criteria_decompositions: list[dict[str, Any]],
    ) -> list[ValidationViolation]:
        """Check latency values are plausible."""
        violations: list[ValidationViolation] = []

        mean_latency = eval_result.get("mean_latency_ms", 0)

        if mean_latency < 0:
            violations.append(
                ValidationViolation(
                    violation_id="V001",
                    rule_id="R005",
                    check_id="latency",
                    severity=ViolationSeverity.WARNING,
                    message=f"Negative latency: {mean_latency}ms",
                    suggestion="Verify latency measurement logic",
                ),
            )
        elif mean_latency > 60000:  # > 1 minute
            violations.append(
                ValidationViolation(
                    violation_id="V002",
                    rule_id="R005",
                    check_id="latency",
                    severity=ViolationSeverity.WARNING,
                    message=f"Unusually high latency: {mean_latency}ms",
                    suggestion="Review for timeout or performance degradation",
                ),
            )

        return violations

    def _validate_score(self, dim_id: str, score: float, eval_result: dict[str, Any]) -> dict[str, Any]:
        """Validate an individual dimension score."""
        issues: list[str] = []

        # Check for suspicious precision
        if score in [0.0, 0.5, 1.0]:
            issues.append("round_number")

        # Check for extreme values
        if score == 1.0:
            issues.append("perfect_score")
        elif score < 0.1:
            issues.append("very_low_score")

        # Confidence based on issues
        if not issues:
            confidence = "high"
        elif len(issues) == 1:
            confidence = "medium"
        else:
            confidence = "low"

        return {
            "dimension": dim_id,
            "score": score,
            "issues": issues,
            "confidence": confidence,
            "valid": 0.0 <= score <= 1.0,
        }

    def _detect_anomalies(self, eval_result: dict[str, Any]) -> list[str]:
        """Detect anomalies in evaluation results."""
        flags: list[str] = []

        dimension_scores = eval_result.get("dimension_scores", {})
        values = list(dimension_scores.values())

        if not values:
            return flags

        # Perfect score anomaly
        if all(v == 1.0 for v in values):
            flags.append("perfect_score_all_dimensions")

        # Zero variance anomaly
        if len(set(values)) == 1 and len(values) > 1:
            flags.append("zero_variance_across_dimensions")

        # Too many failures
        scenarios_failed = eval_result.get("scenarios_failed", 0)
        scenarios_total = eval_result.get("scenarios_total", 1)
        if scenarios_total > 0 and scenarios_failed / scenarios_total > 0.5:
            flags.append("high_failure_rate")

        # Missing latency data
        if eval_result.get("mean_latency_ms") is None:
            flags.append("missing_latency_data")

        return flags

    def _assess_coverage(
        self,
        eval_result: dict[str, Any],
        criteria_decompositions: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Assess test coverage against decomposed criteria."""
        total_components = sum(
            len(d.get("components", [])) for d in criteria_decompositions
        )

        if total_components == 0:
            return {"coverage_percentage": 0.0, "gaps": ["no_criteria_decomposed"]}

        # Estimate coverage based on scenarios executed
        scenarios_executed = eval_result.get("scenarios_total", 0)
        # Rough estimate: assume each component needs at least 2 test scenarios
        estimated_needed = total_components * 2
        coverage = min(1.0, scenarios_executed / estimated_needed) if estimated_needed > 0 else 0.0

        gaps: list[str] = []
        if coverage < 0.5:
            gaps.append("insufficient_scenario_coverage")
        if eval_result.get("scenarios_failed", 0) > 0:
            gaps.append("failed_scenarios_need_attention")

        return {
            "coverage_percentage": coverage,
            "scenarios_executed": scenarios_executed,
            "estimated_needed": estimated_needed,
            "gaps": gaps,
        }

    def _calculate_quality_score(
        self,
        violations: list[ValidationViolation],
        anomaly_flags: list[str],
        coverage: dict[str, Any],
    ) -> float:
        """Calculate overall quality score."""
        base_score = 1.0

        # Deduct for violations
        blocking = len([v for v in violations if v.severity == ViolationSeverity.BLOCKING])
        warnings = len([v for v in violations if v.severity == ViolationSeverity.WARNING])

        base_score -= blocking * 0.25
        base_score -= warnings * 0.05

        # Deduct for anomalies
        base_score -= len(anomaly_flags) * 0.03

        # Deduct for coverage gaps
        coverage_pct = coverage.get("coverage_percentage", 0.0)
        base_score -= (1.0 - coverage_pct) * 0.1

        return max(0.0, base_score)


class ScoringGate:
    """Enforces scoring thresholds and gates."""

    def __init__(self, min_overall_score: float = 0.70, min_dimension_score: float = 0.60) -> None:
        self.min_overall_score = min_overall_score
        self.min_dimension_score = min_dimension_score

    def evaluate(self, eval_result: dict[str, Any]) -> dict[str, Any]:
        """Evaluate result against gates."""
        _emit_verifies_policy("enterprise", "ScoringGate", "evaluate")

        gates_passed = True
        violations: list[str] = []

        # Overall score gate
        overall = eval_result.get("overall_score", 0.0)
        if overall < self.min_overall_score:
            gates_passed = False
            violations.append(
                f"Overall score {overall:.2f} below threshold {self.min_overall_score}",
            )

        # Dimension score gates
        dimension_scores = eval_result.get("dimension_scores", {})
        for dim_id, score in dimension_scores.items():
            if score < self.min_dimension_score:
                gates_passed = False
                violations.append(
                    f"Dimension {dim_id} score {score:.2f} below threshold {self.min_dimension_score}",
                )

        # Regression gate
        if eval_result.get("regression_detected", False):
            gates_passed = False
            violations.append("Regression detected - manual review required")

        return {
            "gates_passed": gates_passed,
            "violations": violations,
            "violation_count": len(violations),
            "thresholds": {
                "min_overall": self.min_overall_score,
                "min_dimension": self.min_dimension_score,
            },
        }
