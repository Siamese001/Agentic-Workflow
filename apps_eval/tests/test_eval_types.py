"""
Test Eval Types — Pydantic model validation.
"""
import unittest

from pydantic import ValidationError

from apps_eval.types import (
    EvalConfig,
    EvalRequest,
    EvalResult,
    EvalRunSummary,
    RegressionRecord,
    ScenarioResult,
    ScorecardRow,
    SuiteResult,
)


class TestEvalTypes(unittest.TestCase):
    """Test cases for eval Pydantic types."""

    def test_scenario_result_creation(self):
        """Test ScenarioResult creation."""
        result = ScenarioResult(
            scenario_id="test-001",
            suite_id="suite-001",
            outcome="PASS",
            score=0.95,
            latency_ms=100.0,
            message="Test passed",
            evidence="log.txt",
            deterministic=True,
        )
        self.assertEqual(result.scenario_id, "test-001")
        self.assertEqual(result.score, 0.95)

    def test_scenario_result_score_validation(self):
        """Test ScenarioResult score bounds."""
        # Valid score
        result = ScenarioResult(
            scenario_id="test-001",
            suite_id="suite-001",
            outcome="PASS",
            score=0.5,
        )
        self.assertEqual(result.score, 0.5)

        # Invalid score > 1
        with self.assertRaises(ValidationError):
            ScenarioResult(
                scenario_id="test-001",
                suite_id="suite-001",
                outcome="PASS",
                score=1.5,
            )

        # Invalid score < 0
        with self.assertRaises(ValidationError):
            ScenarioResult(
                scenario_id="test-001",
                suite_id="suite-001",
                outcome="FAIL",
                score=-0.1,
            )

    def test_suite_result_passed_property(self):
        """Test SuiteResult.passed property."""
        suite_pass = SuiteResult(
            suite_id="suite-001",
            display_name="Test Suite",
            pass_rate=0.85,
        )
        self.assertTrue(suite_pass.passed)

        suite_fail = SuiteResult(
            suite_id="suite-002",
            display_name="Failing Suite",
            pass_rate=0.50,
        )
        self.assertFalse(suite_fail.passed)

        suite_error = SuiteResult(
            suite_id="suite-003",
            display_name="Error Suite",
            pass_rate=0.85,
            error="Something went wrong",
        )
        self.assertFalse(suite_error.passed)

    def test_suite_result_pass_rate_validation(self):
        """Test SuiteResult pass_rate bounds."""
        with self.assertRaises(ValidationError):
            SuiteResult(
                suite_id="suite-001",
                display_name="Test",
                pass_rate=1.5,
            )

    def test_eval_config_defaults(self):
        """Test EvalConfig default values."""
        config = EvalConfig()
        self.assertEqual(config.min_pass_rate, 0.7)
        self.assertEqual(config.max_latency_ms, 30000)
        self.assertEqual(config.regression_threshold, 0.05)
        self.assertTrue(config.require_deterministic)

    def test_eval_request_defaults(self):
        """Test EvalRequest default values."""
        request = EvalRequest()
        self.assertEqual(request.suite_ids, [])
        self.assertFalse(request.dry_run)
        self.assertTrue(request.compare_baseline)
        self.assertTrue(request.emit_scorecard_csv)

    def test_eval_result_passed_gate(self):
        """Test EvalResult.passed_gate property."""
        result_pass = EvalResult(
            trace_id="trace-001",
            status="complete",
            gate_violations=[],
        )
        self.assertTrue(result_pass.passed_gate)

        result_fail = EvalResult(
            trace_id="trace-002",
            status="complete",
            gate_violations=["violation-1"],
        )
        self.assertFalse(result_fail.passed_gate)

    def test_eval_result_overall_score_validation(self):
        """Test EvalResult overall_score bounds."""
        with self.assertRaises(ValidationError):
            EvalResult(overall_score=1.5)

        with self.assertRaises(ValidationError):
            EvalResult(overall_score=-0.1)

    def test_eval_run_summary_to_dict(self):
        """Test EvalRunSummary.to_dict method."""
        summary = EvalRunSummary(
            trace_id="trace-001",
            app="apps_eval",
            version="1.0.0",
            status="complete",
            suites_run=5,
            scenarios_run=25,
            scenarios_passed=23,
            overall_score=0.92,
        )
        d = summary.to_dict()
        self.assertEqual(d["trace_id"], "trace-001")
        self.assertEqual(d["app"], "apps_eval")
        self.assertEqual(d["overall_score"], 0.92)

    def test_scorecard_row_creation(self):
        """Test ScorecardRow creation."""
        row = ScorecardRow(
            dimension_id="dim-001",
            display_name="Correctness",
            score=0.95,
            weight=0.40,
            weighted_score=0.38,
            verdict="PASS",
        )
        self.assertEqual(row.dimension_id, "dim-001")
        self.assertEqual(row.score, 0.95)

    def test_scorecard_row_weight_validation(self):
        """Test ScorecardRow weight must be positive."""
        with self.assertRaises(ValidationError):
            ScorecardRow(
                dimension_id="dim-001",
                display_name="Test",
                score=0.95,
                weight=0,  # Invalid: must be > 0
                weighted_score=0,
                verdict="PASS",
            )

    def test_regression_record_creation(self):
        """Test RegressionRecord creation."""
        record = RegressionRecord(
            suite_id="suite-001",
            dimension_id="dim-001",
            current_score=0.85,
            baseline_score=0.90,
            delta=-0.05,
            verdict="REGRESSION",
        )
        self.assertEqual(record.verdict, "REGRESSION")
        self.assertEqual(record.delta, -0.05)

    def test_eval_run_summary_suites_run_validation(self):
        """Test EvalRunSummary suites_run must be non-negative."""
        with self.assertRaises(ValidationError):
            EvalRunSummary(suites_run=-1)


if __name__ == "__main__":
    unittest.main()
