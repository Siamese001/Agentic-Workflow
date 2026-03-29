"""
Test Eval Types.
"""
import unittest

from apps_eval.types import (
    EvalStatus,
    ScenarioOutcome,
    RegressionVerdict,
    ScenarioResult,
    SuiteResult,
    ScorecardRow,
    RegressionRecord,
    EvalRequest,
    EvalResult,
    EvalRunSummary,
)


class TestEvalTypes(unittest.TestCase):
    """Test cases for eval types."""

    def test_eval_status_enum(self):
        """Test EvalStatus enum values."""
        self.assertEqual(EvalStatus.PENDING.value, "pending")
        self.assertEqual(EvalStatus.RUNNING.value, "running")
        self.assertEqual(EvalStatus.COMPLETE.value, "complete")
        self.assertEqual(EvalStatus.FAILED.value, "failed")

    def test_scenario_outcome_enum(self):
        """Test ScenarioOutcome enum values."""
        self.assertEqual(ScenarioOutcome.PASS.value, "PASS")
        self.assertEqual(ScenarioOutcome.FAIL.value, "FAIL")
        self.assertEqual(ScenarioOutcome.ERROR.value, "ERROR")

    def test_scenario_result_creation(self):
        """Test ScenarioResult dataclass creation."""
        result = ScenarioResult(
            scenario_id="test-001",
            suite_id="suite-001",
            outcome=ScenarioOutcome.PASS,
            score=0.95,
            latency_ms=100.0,
            message="Test passed",
            evidence="log.txt",
            deterministic=True,
        )
        self.assertEqual(result.scenario_id, "test-001")
        self.assertEqual(result.score, 0.95)
        self.assertTrue(result.deterministic)

    def test_suite_result_passed_property(self):
        """Test SuiteResult.passed property."""
        # High pass rate should pass
        suite_pass = SuiteResult(
            suite_id="suite-001",
            display_name="Test Suite",
            pass_rate=0.85,
        )
        self.assertTrue(suite_pass.passed)

        # Low pass rate should fail
        suite_fail = SuiteResult(
            suite_id="suite-002",
            display_name="Failing Suite",
            pass_rate=0.50,
        )
        self.assertFalse(suite_fail.passed)

        # With error should fail
        suite_error = SuiteResult(
            suite_id="suite-003",
            display_name="Error Suite",
            pass_rate=0.85,
            error="Something went wrong",
        )
        self.assertFalse(suite_error.passed)

    def test_eval_request_defaults(self):
        """Test EvalRequest default values."""
        request = EvalRequest()
        self.assertEqual(request.suite_ids, [])
        self.assertFalse(request.dry_run)
        self.assertEqual(request.trace_id, "")
        self.assertTrue(request.compare_baseline)
        self.assertTrue(request.emit_scorecard_csv)
        self.assertEqual(request.extra, {})

    def test_eval_result_passed_gate(self):
        """Test EvalResult.passed_gate property."""
        # Complete with no violations should pass
        result_pass = EvalResult(
            trace_id="trace-001",
            status=EvalStatus.COMPLETE,
            gate_violations=[],
        )
        self.assertTrue(result_pass.passed_gate)

        # With violations should fail
        result_fail = EvalResult(
            trace_id="trace-002",
            status=EvalStatus.COMPLETE,
            gate_violations=["violation-1"],
        )
        self.assertFalse(result_fail.passed_gate)

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


class TestRegressionTypes(unittest.TestCase):
    """Test cases for regression types."""

    def test_regression_verdict_enum(self):
        """Test RegressionVerdict enum values."""
        self.assertEqual(RegressionVerdict.PASS.value, "PASS")
        self.assertEqual(RegressionVerdict.WARN.value, "WARN")
        self.assertEqual(RegressionVerdict.REGRESSION.value, "REGRESSION")

    def test_regression_record_creation(self):
        """Test RegressionRecord creation."""
        record = RegressionRecord(
            suite_id="suite-001",
            dimension_id="dim-001",
            current_score=0.85,
            baseline_score=0.90,
            delta=-0.05,
            verdict=RegressionVerdict.REGRESSION,
        )
        self.assertEqual(record.verdict, RegressionVerdict.REGRESSION)
        self.assertEqual(record.delta, -0.05)


if __name__ == "__main__":
    unittest.main()
