"""
Tests for apps_eval — Evaluation Lab.

All tests are deterministic: no LLM calls, no file I/O in non-dry-run paths.
"""

from __future__ import annotations

import pytest

from apps_eval.types.eval_types import (
    EvalRequest,
    EvalResult,
    EvalRunSummary,
    EvalStatus,
    RegressionRecord,
    RegressionVerdict,
    ScenarioOutcome,
    ScenarioResult,
    ScorecardRow,
    SuiteResult,
)


class TestEvalTypes:
    def test_eval_status_values(self) -> None:
        assert EvalStatus.COMPLETE.value == "complete"
        assert EvalStatus.DRY_RUN.value == "dry_run"
        assert EvalStatus.REGRESSION.value == "regression"

    def test_scenario_outcome_values(self) -> None:
        assert ScenarioOutcome.PASS.value == "PASS"
        assert ScenarioOutcome.FAIL.value == "FAIL"
        assert ScenarioOutcome.TIMEOUT.value == "TIMEOUT"

    def test_regression_verdict_values(self) -> None:
        assert RegressionVerdict.NO_BASELINE.value == "NO_BASELINE"
        assert RegressionVerdict.REGRESSION.value == "REGRESSION"
        assert RegressionVerdict.PASS.value == "PASS"

    def test_scenario_result_frozen(self) -> None:
        result = ScenarioResult(
            scenario_id="s1",
            suite_id="routing",
            outcome=ScenarioOutcome.PASS,
            score=1.0,
        )
        with pytest.raises((AttributeError, TypeError)):
            result.outcome = ScenarioOutcome.FAIL  # type: ignore[misc]

    def test_scorecard_row_frozen(self) -> None:
        row = ScorecardRow(
            dimension_id="correctness",
            display_name="Correctness",
            score=0.85,
            weight=3.0,
            weighted_score=2.55,
            verdict="PASS",
        )
        with pytest.raises((AttributeError, TypeError)):
            row.score = 0.5  # type: ignore[misc]

    def test_suite_result_passed_property(self) -> None:
        suite = SuiteResult(
            suite_id="routing",
            display_name="Routing",
            pass_rate=0.80,
        )
        assert suite.passed is True

    def test_suite_result_failed_property_low_pass_rate(self) -> None:
        suite = SuiteResult(
            suite_id="routing",
            display_name="Routing",
            pass_rate=0.50,
        )
        assert suite.passed is False

    def test_suite_result_failed_property_has_error(self) -> None:
        suite = SuiteResult(
            suite_id="routing",
            display_name="Routing",
            pass_rate=0.90,
            error="module not found",
        )
        assert suite.passed is False

    def test_eval_request_defaults(self) -> None:
        req = EvalRequest()
        assert req.dry_run is False
        assert req.compare_baseline is True
        assert req.suite_ids == []

    def test_eval_result_passed_gate(self) -> None:
        result = EvalResult(
            trace_id="abc",
            status=EvalStatus.COMPLETE,
        )
        assert result.passed_gate is True

    def test_eval_result_failed_gate_with_violations(self) -> None:
        result = EvalResult(
            trace_id="abc",
            status=EvalStatus.COMPLETE,
            gate_violations=["[EVAL_OVERALL_SCORE:BLOCK] score too low"],
        )
        assert result.passed_gate is False

    def test_eval_run_summary_to_dict_keys(self) -> None:
    """Test eval_run_summary_to_dict_keys runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute eval_run_summary_to_dict_keys
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions

        suites = [
            SuiteResult(suite_id="routing_enforcement", display_name="Routing", pass_rate=0.90),
            SuiteResult(suite_id="determinism_contracts", display_name="Determinism", pass_rate=0.85),
        ]
        engine = ScorecardEngine()
        result = engine.compute(suites)
        assert 0.0 <= result.overall_score <= 1.0
        assert result.total_weight > 0

    def test_compute_produces_rows(self) -> None:
        from apps_eval.engines.scorecard_engine import ScorecardEngine
        from apps_eval.types.eval_types import SuiteResult

        suites = [SuiteResult(suite_id="exec_brief_generation", display_name="Exec", pass_rate=1.0)]
        engine = ScorecardEngine()
        result = engine.compute(suites)
        assert len(result.rows) > 0

    def test_compute_empty_suites(self) -> None:
        from apps_eval.engines.scorecard_engine import ScorecardEngine

        engine = ScorecardEngine()
        result = engine.compute([])
        assert result.overall_score == 0.0

    def test_verdict_pass_threshold(self) -> None:
        from apps_eval.engines.scorecard_engine import ScorecardEngine
        from apps_eval.types.eval_types import SuiteResult

        suites = [SuiteResult(suite_id="routing_enforcement", display_name="Routing", pass_rate=1.0)]
        engine = ScorecardEngine()
        result = engine.compute(suites)
        routing_rows = [r for r in result.rows if r.dimension_id == "governance"]
        if routing_rows:
            assert routing_rows[0].verdict in ("PASS", "WARN", "FAIL")


class TestRegressionDetector:
    def test_no_baseline_all_no_baseline_verdict(self, tmp_path) -> None:
        from apps_eval.engines.regression_detector import RegressionDetector
        from apps_eval.types.eval_types import ScorecardRow

        rows = [
            ScorecardRow("correctness", "Correctness", 0.85, 3.0, 2.55, "PASS"),
            ScorecardRow("determinism", "Determinism", 0.90, 3.0, 2.70, "PASS"),
        ]
        detector = RegressionDetector(baseline_dir=str(tmp_path))
        result = detector.detect(rows)
        assert result.baseline_loaded is False
        for rec in result.records:
            assert rec.verdict == RegressionVerdict.NO_BASELINE

    def test_regression_detected_on_score_drop(self, tmp_path) -> None:
        import json

        from apps_eval.engines.regression_detector import RegressionDetector
        from apps_eval.types.eval_types import ScorecardRow

        baseline = {"scores": {"correctness": 0.90, "determinism": 0.90}}
        baseline_file = tmp_path / "eval_baseline.json"
        baseline_file.write_text(json.dumps(baseline), encoding="utf-8")

        rows = [
            ScorecardRow("correctness", "Correctness", 0.70, 3.0, 2.10, "FAIL"),
            ScorecardRow("determinism", "Determinism", 0.88, 3.0, 2.64, "PASS"),
        ]
        detector = RegressionDetector(baseline_dir=str(tmp_path), tolerance_delta=0.05)
        result = detector.detect(rows)
        assert result.baseline_loaded is True
        regressions = [r for r in result.records if r.verdict == RegressionVerdict.REGRESSION]
        assert len(regressions) == 1
        assert regressions[0].dimension_id == "correctness"

    def test_auto_update_baseline_writes_file(self, tmp_path) -> None:
        from apps_eval.engines.regression_detector import RegressionDetector
        from apps_eval.types.eval_types import ScorecardRow

        rows = [ScorecardRow("correctness", "Correctness", 0.85, 3.0, 2.55, "PASS")]
        detector = RegressionDetector(baseline_dir=str(tmp_path))
        detector.detect(rows, trace_id="test123", auto_update=True)
        baseline_file = tmp_path / "eval_baseline.json"
        assert baseline_file.exists()


class TestEvalGateValidator:
    def test_passes_all_suites_above_threshold(self) -> None:
        from apps_eval.validators.eval_gate_validator import EvalGateValidator

        suites = [
            SuiteResult(suite_id="routing_enforcement", display_name="Routing", pass_rate=0.90),
            SuiteResult(suite_id="determinism_contracts", display_name="Determinism", pass_rate=0.85),
        ]
        validator = EvalGateValidator()
        result = validator.validate(suites, [], [], 0.88)
        assert result.passed is True

    def test_fails_low_overall_score(self) -> None:
        from apps_eval.validators.eval_gate_validator import EvalGateValidator

        suites = [SuiteResult(suite_id="s1", display_name="S1", pass_rate=0.50)]
        validator = EvalGateValidator(min_overall_score=0.70)
        result = validator.validate(suites, [], [], 0.50)
        assert result.passed is False

    def test_fails_on_regression(self) -> None:
        from apps_eval.validators.eval_gate_validator import EvalGateValidator

        regressions = [
            RegressionRecord(
                suite_id="",
                dimension_id="correctness",
                current_score=0.70,
                baseline_score=0.90,
                delta=-0.20,
                verdict=RegressionVerdict.REGRESSION,
            )
        ]
        suites = [SuiteResult(suite_id="s1", display_name="S1", pass_rate=0.90)]
        validator = EvalGateValidator(fail_on_regression=True)
        result = validator.validate(suites, [], regressions, 0.85)
        assert result.passed is False


class TestEvalOrchestratorDryRun:
    def test_dry_run_returns_dry_run_status(self) -> None:
        from apps_eval.reasoning.EvalOrchestrator import EvalOrchestrator

        req = EvalRequest(suite_ids=["exec_brief_generation"], dry_run=True)
        orch = EvalOrchestrator(dry_run=True)
        result = orch.run(req)
        assert result.status == EvalStatus.DRY_RUN

    def test_dry_run_no_artifact_paths(self) -> None:
        from apps_eval.reasoning.EvalOrchestrator import EvalOrchestrator

        req = EvalRequest(suite_ids=["exec_brief_generation"], dry_run=True)
        orch = EvalOrchestrator(dry_run=True)
        result = orch.run(req)
        assert result.artifact_paths == []

    def test_dry_run_has_scorecard(self) -> None:
        from apps_eval.reasoning.EvalOrchestrator import EvalOrchestrator

        req = EvalRequest(suite_ids=["exec_brief_generation"], dry_run=True)
        orch = EvalOrchestrator(dry_run=True)
        result = orch.run(req)
        assert len(result.scorecard) > 0

    def test_trace_id_deterministic(self) -> None:
        from apps_eval.reasoning.EvalOrchestrator import EvalOrchestrator

        req1 = EvalRequest(suite_ids=["exec_brief_generation", "routing_enforcement"])
        req2 = EvalRequest(suite_ids=["exec_brief_generation", "routing_enforcement"])
        t1 = EvalOrchestrator._make_trace_id(req1)
        t2 = EvalOrchestrator._make_trace_id(req2)
        assert t1 == t2

    def test_overall_score_in_range(self) -> None:
        from apps_eval.reasoning.EvalOrchestrator import EvalOrchestrator

        req = EvalRequest(suite_ids=["exec_brief_generation"], dry_run=True)
        orch = EvalOrchestrator(dry_run=True)
        result = orch.run(req)
        assert 0.0 <= result.overall_score <= 1.0


class TestEvalConfig:
    def test_load_eval_specs_returns_defaults(self) -> None:
        from apps_eval.config.agent_spec_config import load_eval_specs

        specs = load_eval_specs()
        assert specs is not None
        assert specs.version == "1.0.0"

    def test_benchmark_suites_configured(self) -> None:
        from apps_eval.config.agent_spec_config import load_eval_specs

        specs = load_eval_specs()
        assert len(specs.benchmark_suites) > 0
        assert "exec_brief_generation" in specs.benchmark_suites

    def test_scorecard_dimensions_weights_positive(self) -> None:
        from apps_eval.config.agent_spec_config import load_eval_specs

        specs = load_eval_specs()
        total_weight = sum(d.weight for d in specs.scorecard_dimensions)
        assert total_weight > 0

    def test_reasoning_toggles_defaults(self) -> None:
        from apps_eval.config.reasoning_toggles_config import DEFAULT_TOGGLES

        assert DEFAULT_TOGGLES.enable_scorecard is True
        assert DEFAULT_TOGGLES.enable_regression_detection is True
        assert DEFAULT_TOGGLES.auto_update_baseline is False
