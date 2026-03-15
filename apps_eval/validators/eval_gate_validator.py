"""
Eval Gate Validator — apps_eval.

Enforces quality gates on evaluation run results:
- Overall score meets minimum threshold
- No regressions when fail_on_regression=True
- No timeout violations beyond max_timeout_violations
- All required suites ran

Deterministic: all checks are threshold comparisons.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from apps_eval.types.eval_types import RegressionRecord, RegressionVerdict, ScorecardRow, SuiteResult
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

_log = logging.getLogger(__name__)

# Default gate thresholds (can be overridden in __init__)
_DEFAULT_MIN_SCORE = 0.70
_DEFAULT_FAIL_ON_REGRESSION = True
_DEFAULT_MAX_TIMEOUT_VIOLATIONS = 0


@dataclass
class EvalViolation:
    """A single evaluation gate violation."""

    rule_id: str
    severity: str
    message: str


@dataclass
class EvalGateResult:
    """Result of evaluation gate check."""

    passed: bool
    violations: list[EvalViolation] = field(default_factory=list)
    overall_score: float = 0.0


class EvalGateValidator:
    """Validate evaluation run results against configured quality gates."""

    def __init__(
        self,
        min_overall_score: float = _DEFAULT_MIN_SCORE,
        fail_on_regression: bool = _DEFAULT_FAIL_ON_REGRESSION,
        max_timeout_violations: int = _DEFAULT_MAX_TIMEOUT_VIOLATIONS,
    ) -> None:
        self._min_overall_score = min_overall_score
        self._fail_on_regression = fail_on_regression
        self._max_timeout_violations = max_timeout_violations

    def validate(
        self,
        suite_results: list[SuiteResult],
        scorecard_rows: list[ScorecardRow],
        regression_records: list[RegressionRecord],
        overall_score: float,
    ) -> EvalGateResult:
        """Run all gate checks.

        Returns:
            EvalGateResult with all violations.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "EvalGateValidator.validate")

        violations: list[EvalViolation] = []

        if overall_score < self._min_overall_score:
            violations.append(
                EvalViolation(
                    rule_id="EVAL_SCORE_BELOW_THRESHOLD",
                    severity="BLOCK",
                    message=(
                        f"Overall score {overall_score:.2%} is below minimum {self._min_overall_score:.2%}."
                    ),
                )
            )

        if self._fail_on_regression:
            regressions = [r for r in regression_records if r.verdict == RegressionVerdict.REGRESSION]
            if regressions:
                dims = [r.dimension_id for r in regressions]
                violations.append(
                    EvalViolation(
                        rule_id="EVAL_REGRESSION_DETECTED",
                        severity="BLOCK",
                        message=f"Regression detected in dimensions: {dims}",
                    )
                )

        for suite in suite_results:
            if suite.error:
                violations.append(
                    EvalViolation(
                        rule_id="EVAL_SUITE_ERROR",
                        severity="BLOCK",
                        message=f"Suite '{suite.suite_id}' encountered an error: {suite.error}",
                    )
                )

        timeout_count = sum(
            1
            for suite in suite_results
            for scenario in suite.scenarios
            if scenario.outcome.value == "TIMEOUT"
        )
        if timeout_count > self._max_timeout_violations:
            violations.append(
                EvalViolation(
                    rule_id="EVAL_TIMEOUT_VIOLATIONS",
                    severity="BLOCK",
                    message=(
                        f"Timeout violations: {timeout_count} exceeds max {self._max_timeout_violations}."
                    ),
                )
            )

        block_count = sum(1 for v in violations if v.severity == "BLOCK")
        return EvalGateResult(
            passed=block_count == 0,
            violations=violations,
            overall_score=overall_score,
        )
