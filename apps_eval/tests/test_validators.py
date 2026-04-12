"""
Test Validators — Compliance and quality gate validation.
"""

import unittest

from apps_eval.types import (
    EvalConfig,
    EvalRequest,
    EvalResult,
    RegressionRecord,
    ScenarioResult,
    SuiteResult,
)
from apps_eval.validators import ComplianceValidator, QualityGateValidator


class TestComplianceValidator(unittest.TestCase):
    """Test cases for compliance validator."""

    def setUp(self):
        self.validator = ComplianceValidator()

    def test_validate_pass(self):
        """Test validation passes."""
        request = EvalRequest(
            config=EvalConfig(min_pass_rate=0.7, require_deterministic=True),
        )
        result = EvalResult(
            overall_score=0.85,
            status="complete",
            gate_violations=[],
        )

        passed, violations = self.validator.validate(request, result)
        self.assertTrue(passed)
        self.assertEqual(violations, [])

    def test_validate_fails_min_pass_rate(self):
        """Test validation fails on min pass rate."""
        request = EvalRequest(config=EvalConfig(min_pass_rate=0.8))
        result = EvalResult(overall_score=0.5, status="complete")

        passed, violations = self.validator.validate(request, result)
        self.assertFalse(passed)
        self.assertTrue(any("COMPLIANCE" in v for v in violations))

    def test_validate_fails_nondeterministic(self):
        """Test validation fails on non-deterministic results."""
        request = EvalRequest(config=EvalConfig(require_deterministic=True))
        result = EvalResult(
            status="complete",
            suite_results=[
                SuiteResult(
                    suite_id="suite-001",
                    display_name="Test",
                    scenarios=[
                        ScenarioResult(
                            scenario_id="s1",
                            suite_id="suite-001",
                            outcome="PASS",
                            score=0.9,
                            deterministic=False,
                        ),
                    ],
                ),
            ],
        )

        passed, violations = self.validator.validate(request, result)
        self.assertFalse(passed)
        self.assertTrue(any("Non-deterministic" in v for v in violations))


class TestQualityGateValidator(unittest.TestCase):
    """Test cases for quality gate validator."""

    def setUp(self):
        self.validator = QualityGateValidator(
            config={"min_scenarios": 2, "max_latency_ms": 1000},
        )

    def test_validate_pass(self):
        """Test quality gates pass."""
        result = EvalResult(
            status="complete",
            suite_results=[
                SuiteResult(
                    suite_id="suite-001",
                    display_name="Test",
                    scenarios=[
                        ScenarioResult(
                            scenario_id="s1",
                            suite_id="suite-001",
                            outcome="PASS",
                            score=0.9,
                        ),
                        ScenarioResult(
                            scenario_id="s2",
                            suite_id="suite-001",
                            outcome="PASS",
                            score=0.9,
                        ),
                    ],
                    mean_latency_ms=500,
                ),
            ],
        )

        passed, violations = self.validator.validate(result)
        self.assertTrue(passed)

    def test_validate_fails_min_scenarios(self):
        """Test validation fails on insufficient scenarios."""
        result = EvalResult(
            status="complete",
            suite_results=[SuiteResult(suite_id="suite-001", display_name="Test")],
        )

        passed, violations = self.validator.validate(result)
        self.assertFalse(passed)
        self.assertTrue(any("minimum" in v.lower() for v in violations))

    def test_validate_fails_latency(self):
        """Test validation fails on high latency."""
        result = EvalResult(
            status="complete",
            suite_results=[
                SuiteResult(
                    suite_id="suite-001",
                    display_name="Test",
                    scenarios=[
                        ScenarioResult(
                            scenario_id="s1",
                            suite_id="suite-001",
                            outcome="PASS",
                            score=0.9,
                        ),
                        ScenarioResult(
                            scenario_id="s2",
                            suite_id="suite-001",
                            outcome="PASS",
                            score=0.9,
                        ),
                    ],
                    mean_latency_ms=2000,
                ),
            ],
        )

        passed, violations = self.validator.validate(result)
        self.assertFalse(passed)
        self.assertTrue(any("latency" in v.lower() for v in violations))

    def test_validate_fails_regression(self):
        """Test validation fails on regression."""
        result = EvalResult(
            status="complete",
            regression_records=[
                RegressionRecord(
                    suite_id="suite-001",
                    dimension_id="dim-001",
                    current_score=0.75,
                    baseline_score=0.90,
                    delta=-0.15,
                    verdict="REGRESSION",
                ),
            ],
        )

        passed, violations = self.validator.validate(result)
        self.assertFalse(passed)
        self.assertTrue(any("Regression" in v for v in violations))


if __name__ == "__main__":
    unittest.main()
