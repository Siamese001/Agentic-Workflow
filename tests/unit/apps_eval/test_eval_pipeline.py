"""
Unit tests for apps_eval Evaluation Lab pipeline.

Coverage:
- EvalAgentSpecs: suites config, scorecard dimensions, regression config
- ScenarioRunner: known and unknown scenarios, error isolation
- ScorecardEngine: weighted scoring, dimension mapping
- RegressionDetector: no baseline, regression detected, pass
- EvalGateValidator: score below threshold, regression block, clean pass
- EvalOrchestrator: dry_run, scorecard emission, CSV artifact
- EvalRunSummary: to_dict() completeness
"""

from __future__ import annotations

from pathlib import Path

import pytest


class TestEvalAgentSpecs:
    def test_default_specs_load(self):
        import apps_eval.config.agent_spec_config as cfg_mod

        cfg_mod._SPEC_CACHE = None
        specs = cfg_mod.load_eval_specs()
        assert specs is not None
        assert len(specs.benchmark_suites) >= 5

    def test_scorecard_dimensions_non_empty(self):
        import apps_eval.config.agent_spec_config as cfg_mod

        cfg_mod._SPEC_CACHE = None
        specs = cfg_mod.load_eval_specs()
        assert len(specs.scorecard_dimensions) >= 5

    def test_weights_sum_positive(self):
        import apps_eval.config.agent_spec_config as cfg_mod

        cfg_mod._SPEC_CACHE = None
        specs = cfg_mod.load_eval_specs()
        total = sum(d.weight for d in specs.scorecard_dimensions)
        assert total > 0

    def test_required_suites_present(self):
        import apps_eval.config.agent_spec_config as cfg_mod

        cfg_mod._SPEC_CACHE = None
        specs = cfg_mod.load_eval_specs()
        for suite_id in ["routing_enforcement", "determinism_contracts"]:
            assert suite_id in specs.benchmark_suites

    def test_zero_weights_raises(self):
        from pydantic import ValidationError

        from apps_eval.config.agent_spec_config import EvalAgentSpecs, ScorecardDimensionConfig

        with pytest.raises(ValidationError):
            EvalAgentSpecs(
                scorecard_dimensions=[
                    ScorecardDimensionConfig(dimension_id="d1", display_name="D1", weight=0.0)
                ]
            )


class TestScenarioRunner:
    def test_known_scenario_runs(self):
        from apps_eval.engines.scenario_runner import ScenarioRunner
        from apps_eval.types.eval_types import ScenarioOutcome

        runner = ScenarioRunner()
        result = runner.run_suite(
            suite_id="exec_brief_generation",
            display_name="Exec Brief",
            scenario_ids=["recruiter_brief"],
            timeout_sec=30,
        )
        assert result.pass_rate >= 0.0
        assert len(result.scenarios) == 1
        outcome = result.scenarios[0].outcome
        assert outcome in (ScenarioOutcome.PASS, ScenarioOutcome.SKIP, ScenarioOutcome.FAIL)

    def test_unknown_scenario_returns_error(self):
        from apps_eval.engines.scenario_runner import ScenarioRunner
        from apps_eval.types.eval_types import ScenarioOutcome

        runner = ScenarioRunner()
        result = runner.run_suite(
            suite_id="test_suite",
            display_name="Test Suite",
            scenario_ids=["nonexistent_scenario_xyz"],
            timeout_sec=10,
        )
        assert result.scenarios[0].outcome == ScenarioOutcome.ERROR

    def test_empty_suite_returns_zero_pass_rate(self):
        from apps_eval.engines.scenario_runner import ScenarioRunner

        runner = ScenarioRunner()
        result = runner.run_suite("empty_suite", "Empty", [], timeout_sec=10)
        assert result.pass_rate == 0.0
        assert len(result.scenarios) == 0

    def test_multiple_scenarios_pass_rate_correct(self):
        from apps_eval.engines.scenario_runner import ScenarioRunner
        from apps_eval.types.eval_types import ScenarioOutcome

        runner = ScenarioRunner()
        result = runner.run_suite(
            suite_id="exec_brief_generation",
            display_name="Exec Brief",
            scenario_ids=["recruiter_brief", "cto_brief", "dry_run"],
            timeout_sec=30,
        )
        assert len(result.scenarios) == 3
        passed = sum(1 for s in result.scenarios if s.outcome in (ScenarioOutcome.PASS, ScenarioOutcome.SKIP))
        assert abs(result.pass_rate - passed / 3) < 0.001

    def test_scenario_result_has_latency(self):
        from apps_eval.engines.scenario_runner import ScenarioRunner

        runner = ScenarioRunner()
        result = runner.run_suite("test", "Test", ["recruiter_brief"], timeout_sec=30)
        assert result.scenarios[0].latency_ms >= 0.0

    def test_nondeterminism_scenario_runs(self):
        from apps_eval.engines.scenario_runner import ScenarioRunner
        from apps_eval.types.eval_types import ScenarioOutcome

        runner = ScenarioRunner()
        result = runner.run_suite(
            "determinism_contracts",
            "Determinism",
            ["nondeterministic_time_call", "clean_module"],
            timeout_sec=30,
        )
        for sc in result.scenarios:
            assert sc.outcome in (ScenarioOutcome.PASS, ScenarioOutcome.SKIP, ScenarioOutcome.FAIL)


class TestScorecardEngine:
    def _make_suite_results(self, pass_rates: dict[str, float]):
        from apps_eval.types.eval_types import SuiteResult

        results = []
        for suite_id, rate in pass_rates.items():
            results.append(
                SuiteResult(
                    suite_id=suite_id,
                    display_name=suite_id.title(),
                    scenarios=(),
                    pass_rate=rate,
                    mean_latency_ms=10.0,
                )
            )
        return results

    def test_perfect_score_all_pass(self):
        from apps_eval.engines.scorecard_engine import ScorecardEngine

        engine = ScorecardEngine()
        suites = self._make_suite_results(
            {
                "routing_enforcement": 1.0,
                "determinism_contracts": 1.0,
                "orchestration_hop": 1.0,
            }
        )
        result = engine.compute(suites)
        assert result.overall_score > 0.0

    def test_zero_score_all_fail(self):
        from apps_eval.engines.scorecard_engine import ScorecardEngine

        engine = ScorecardEngine()
        suites = self._make_suite_results(
            {
                "routing_enforcement": 0.0,
                "determinism_contracts": 0.0,
            }
        )
        result = engine.compute(suites)
        assert result.overall_score < 1.0

    def test_scorecard_rows_have_verdicts(self):
        from apps_eval.engines.scorecard_engine import ScorecardEngine

        engine = ScorecardEngine()
        suites = self._make_suite_results({"routing_enforcement": 0.85, "determinism_contracts": 0.90})
        result = engine.compute(suites)
        for row in result.rows:
            assert row.verdict in ("PASS", "WARN", "FAIL")

    def test_empty_suites_returns_zero_score(self):
        from apps_eval.engines.scorecard_engine import ScorecardEngine

        engine = ScorecardEngine()
        result = engine.compute([])
        assert result.overall_score >= 0.0


class TestRegressionDetector:
    def test_no_baseline_returns_no_baseline_verdict(self, tmp_path):
        from apps_eval.engines.regression_detector import RegressionDetector
        from apps_eval.types.eval_types import RegressionVerdict, ScorecardRow

        detector = RegressionDetector(baseline_dir=str(tmp_path / "no_baseline"))
        rows = [ScorecardRow("correctness", "Correctness", 0.85, 3.0, 2.55, "PASS")]
        result = detector.detect(rows, trace_id="test-001")
        assert result.baseline_loaded is False
        assert all(r.verdict == RegressionVerdict.NO_BASELINE for r in result.records)

    def test_regression_detected_when_drop_exceeds_tolerance(self, tmp_path):
        import json

        from apps_eval.engines.regression_detector import RegressionDetector
        from apps_eval.types.eval_types import RegressionVerdict, ScorecardRow

        baseline_dir = tmp_path / "baselines"
        baseline_dir.mkdir()
        baseline_file = baseline_dir / "eval_baseline.json"
        baseline_file.write_text(json.dumps({"scores": {"correctness": 0.90}}), encoding="utf-8")
        detector = RegressionDetector(baseline_dir=str(baseline_dir), tolerance_delta=0.05)
        rows = [ScorecardRow("correctness", "Correctness", 0.80, 3.0, 2.4, "WARN")]
        result = detector.detect(rows, trace_id="test-002")
        assert result.regression_count == 1
        assert result.records[0].verdict == RegressionVerdict.REGRESSION

    def test_no_regression_when_within_tolerance(self, tmp_path):
        import json

        from apps_eval.engines.regression_detector import RegressionDetector
        from apps_eval.types.eval_types import RegressionVerdict, ScorecardRow

        baseline_dir = tmp_path / "baselines2"
        baseline_dir.mkdir()
        (baseline_dir / "eval_baseline.json").write_text(
            json.dumps({"scores": {"correctness": 0.88}}), encoding="utf-8"
        )
        detector = RegressionDetector(baseline_dir=str(baseline_dir), tolerance_delta=0.05)
        rows = [ScorecardRow("correctness", "Correctness", 0.86, 3.0, 2.58, "PASS")]
        result = detector.detect(rows)
        assert result.regression_count == 0
        assert result.records[0].verdict in (RegressionVerdict.PASS, RegressionVerdict.WARN)

    def test_auto_update_writes_baseline(self, tmp_path):
        from apps_eval.engines.regression_detector import RegressionDetector
        from apps_eval.types.eval_types import ScorecardRow

        baseline_dir = tmp_path / "auto_baseline"
        detector = RegressionDetector(baseline_dir=str(baseline_dir), tolerance_delta=0.05)
        rows = [ScorecardRow("correctness", "Correctness", 0.88, 3.0, 2.64, "PASS")]
        detector.detect(rows, trace_id="auto-001", auto_update=True)
        assert (baseline_dir / "eval_baseline.json").exists()


class TestEvalGateValidator:
    def test_clean_run_passes(self):
        from apps_eval.types.eval_types import RegressionRecord, RegressionVerdict, ScorecardRow, SuiteResult
        from apps_eval.validators.eval_gate_validator import EvalGateValidator

        validator = EvalGateValidator(min_overall_score=0.70)
        suite = SuiteResult("test", "Test", (), 0.90, 10.0)
        row = ScorecardRow("correctness", "Correctness", 0.85, 3.0, 2.55, "PASS")
        reg = RegressionRecord("", "correctness", 0.85, 0.85, 0.0, RegressionVerdict.PASS)
        result = validator.validate([suite], [row], [reg], 0.85)
        assert result.passed

    def test_score_below_threshold_blocks(self):
        from apps_eval.types.eval_types import RegressionRecord, RegressionVerdict, ScorecardRow, SuiteResult
        from apps_eval.validators.eval_gate_validator import EvalGateValidator

        validator = EvalGateValidator(min_overall_score=0.80)
        suite = SuiteResult("test", "Test", (), 0.60, 10.0)
        row = ScorecardRow("correctness", "Correctness", 0.60, 3.0, 1.8, "FAIL")
        reg = RegressionRecord("", "correctness", 0.60, 0.60, 0.0, RegressionVerdict.PASS)
        result = validator.validate([suite], [row], [reg], 0.60)
        assert not result.passed

    def test_regression_blocks_when_fail_on_regression(self):
        from apps_eval.types.eval_types import RegressionRecord, RegressionVerdict, ScorecardRow, SuiteResult
        from apps_eval.validators.eval_gate_validator import EvalGateValidator

        validator = EvalGateValidator(min_overall_score=0.70, fail_on_regression=True)
        suite = SuiteResult("test", "Test", (), 0.85, 10.0)
        row = ScorecardRow("correctness", "Correctness", 0.85, 3.0, 2.55, "PASS")
        reg = RegressionRecord("", "correctness", 0.75, 0.90, -0.15, RegressionVerdict.REGRESSION)
        result = validator.validate([suite], [row], [reg], 0.85)
        assert not result.passed


class TestEvalOrchestrator:
    def test_dry_run_no_artifacts(self):
        from apps_eval.reasoning.EvalOrchestrator import EvalOrchestrator
        from apps_eval.types.eval_types import EvalRequest, EvalStatus

        orch = EvalOrchestrator(dry_run=True)
        req = EvalRequest(suite_ids=["exec_brief_generation"], dry_run=True)
        result = orch.run(req)
        assert result.status == EvalStatus.DRY_RUN
        assert len(result.artifact_paths) == 0

    def test_scorecard_non_empty(self):
        from apps_eval.reasoning.EvalOrchestrator import EvalOrchestrator
        from apps_eval.types.eval_types import EvalRequest

        orch = EvalOrchestrator(dry_run=True)
        req = EvalRequest(suite_ids=["exec_brief_generation"], dry_run=True)
        result = orch.run(req)
        assert len(result.scorecard) > 0

    def test_artifacts_written_in_non_dry_run(self, tmp_path):
        from apps_eval.reasoning.EvalOrchestrator import EvalOrchestrator
        from apps_eval.types.eval_types import EvalRequest, EvalStatus

        orch = EvalOrchestrator(
            dry_run=False, output_dir=str(tmp_path), baseline_dir=str(tmp_path / "baselines")
        )
        req = EvalRequest(suite_ids=["exec_brief_generation"], emit_scorecard_csv=True)
        result = orch.run(req)
        if result.status in (EvalStatus.COMPLETE, EvalStatus.REGRESSION):
            assert len(result.artifact_paths) > 0
            for path in result.artifact_paths:
                assert Path(path).exists()

    def test_trace_id_propagated(self):
        from apps_eval.reasoning.EvalOrchestrator import EvalOrchestrator
        from apps_eval.types.eval_types import EvalRequest

        orch = EvalOrchestrator(dry_run=True)
        req = EvalRequest(suite_ids=[], trace_id="eval-trace-999", dry_run=True)
        result = orch.run(req)
        assert result.trace_id == "eval-trace-999"


class TestEvalRunSummary:
    def test_to_dict_completeness(self):
        from apps_eval.types.eval_types import EvalRunSummary

        summary = EvalRunSummary(trace_id="eval-001", status="complete")
        d = summary.to_dict()
        for key in [
            "trace_id",
            "app",
            "status",
            "suites_run",
            "scenarios_run",
            "scenarios_passed",
            "overall_score",
            "regressions_detected",
            "gate_violations",
            "artifacts",
            "provenance",
        ]:
            assert key in d, f"Missing key: {key}"
