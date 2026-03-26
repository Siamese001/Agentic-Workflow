"""
apps_eval integration tests — ml_metrics_validation suite.

ADG coverage targets:
  - apps_eval/engines/scenario_runner.py   → ml_metrics_validation scenario fns
  - apps_eval/config/agent_spec_config.py  → ml_metrics_validation suite config
  - apps_eval/engines/scorecard_engine.py  → ml_metric_correctness dimension

These tests run the ScenarioRunner directly (no LLM, no external deps)
and assert that all ml_metrics_validation scenarios PASS with score >= 0.9.
"""

from __future__ import annotations

import pytest

#  # MOVED: from apps_eval.config.agent_spec_config import EvalAgentSpecs, load_eval_specs
#  # MOVED: from apps_eval.engines.scenario_runner import ScenarioRunner
#  # MOVED: from apps_eval.engines.scorecard_engine import _SUITE_TO_DIMENSION, ScorecardEngine
#  # MOVED: from apps_eval.types.eval_types import ScenarioOutcome

_ML_METRICS_SUITE_ID = "ml_metrics_validation"
_ML_SCENARIO_IDS = [
    "binary_precision_perfect",
    "binary_recall_perfect",
    "binary_f1_harmonic_mean",
    "multiclass_macro_f1",
    "multiclass_weighted_f1",
    "confusion_matrix_invariants",
]


# ---------------------------------------------------------------------------
# Suite config registration
# ---------------------------------------------------------------------------


class TestMlMetricsSuiteConfig:
    def test_suite_registered_in_default_specs(self):
        from apps_eval.config.agent_spec_config import EvalAgentSpecs, load_eval_specs
        from apps_eval.engines.scenario_runner import ScenarioRunner
        from apps_eval.engines.scorecard_engine import _SUITE_TO_DIMENSION, ScorecardEngine
        from apps_eval.types.eval_types import ScenarioOutcome
        import apps_eval.config.agent_spec_config as _cfg
        from apps_eval.types.eval_types import SuiteResult
        from apps_eval.types.eval_types import SuiteResult
        specs = EvalAgentSpecs()
        assert _ML_METRICS_SUITE_ID in specs.benchmark_suites

    def test_suite_has_all_scenarios(self):
        specs = EvalAgentSpecs()
        suite = specs.benchmark_suites[_ML_METRICS_SUITE_ID]
        for scenario_id in _ML_SCENARIO_IDS:
            assert scenario_id in suite.scenario_ids, f"Missing scenario: {scenario_id}"

    def test_suite_target_module(self):
        specs = EvalAgentSpecs()
        suite = specs.benchmark_suites[_ML_METRICS_SUITE_ID]
        assert "classification" in suite.target_module

    def test_ml_metric_correctness_dimension_registered(self):
        specs = EvalAgentSpecs()
        dim_ids = [d.dimension_id for d in specs.scorecard_dimensions]
        assert "ml_metric_correctness" in dim_ids

    def test_ml_metric_correctness_weight(self):
        specs = EvalAgentSpecs()
        dim = next(d for d in specs.scorecard_dimensions if d.dimension_id == "ml_metric_correctness")
        assert dim.weight == 2.0

    def test_ml_metric_correctness_threshold(self):
        specs = EvalAgentSpecs()
        dim = next(d for d in specs.scorecard_dimensions if d.dimension_id == "ml_metric_correctness")
        assert dim.threshold_pass >= 0.90

    def test_load_eval_specs_includes_suite(self):
#  # MOVED: import apps_eval.config.agent_spec_config as _cfg

        _cfg._SPEC_CACHE = None
        specs = load_eval_specs()
        assert _ML_METRICS_SUITE_ID in specs.benchmark_suites


# ---------------------------------------------------------------------------
# ScenarioRunner — individual scenarios
# ---------------------------------------------------------------------------


class TestMlMetricsScenariosPass:
    """Each ml_metrics_validation scenario should PASS (or SKIP if import unavailable)."""

    def _run(self, scenario_id: str):
        runner = ScenarioRunner()
        result = runner._run_scenario(scenario_id, _ML_METRICS_SUITE_ID, timeout_sec=10)
        return result

    @pytest.mark.parametrize("scenario_id", _ML_SCENARIO_IDS)
    def test_scenario_not_error(self, scenario_id):
        result = self._run(scenario_id)
        assert result.outcome != ScenarioOutcome.ERROR, f"{scenario_id} returned ERROR: {result.message}"

    @pytest.mark.parametrize("scenario_id", _ML_SCENARIO_IDS)
    def test_scenario_pass_or_skip(self, scenario_id):
        result = self._run(scenario_id)
        assert result.outcome in (ScenarioOutcome.PASS, ScenarioOutcome.SKIP), (
            f"{scenario_id} outcome={result.outcome.value} score={result.score} msg={result.message}"
        )

    @pytest.mark.parametrize("scenario_id", _ML_SCENARIO_IDS)
    def test_scenario_score_non_negative(self, scenario_id):
        result = self._run(scenario_id)
        assert result.score >= 0.0

    def test_binary_precision_perfect_score_is_one(self):
        result = self._run("binary_precision_perfect")
        if result.outcome == ScenarioOutcome.SKIP:

        assert result.score == 1.0

    def test_binary_recall_perfect_score_is_one(self):
        result = self._run("binary_recall_perfect")
        if result.outcome == ScenarioOutcome.SKIP:

        assert result.score == 1.0

    def test_binary_f1_harmonic_mean_score_is_one(self):
        result = self._run("binary_f1_harmonic_mean")
        if result.outcome == ScenarioOutcome.SKIP:

        assert result.score == 1.0

    def test_multiclass_macro_f1_score_is_one(self):
        result = self._run("multiclass_macro_f1")
        if result.outcome == ScenarioOutcome.SKIP:

        assert result.score == 1.0

    def test_multiclass_weighted_f1_score_is_one(self):
        result = self._run("multiclass_weighted_f1")
        if result.outcome == ScenarioOutcome.SKIP:

        assert result.score >= 0.9

    def test_confusion_matrix_invariants_score_is_one(self):
        result = self._run("confusion_matrix_invariants")
        if result.outcome == ScenarioOutcome.SKIP:

        assert result.score == 1.0


# ---------------------------------------------------------------------------
# ScenarioRunner.run_suite integration
# ---------------------------------------------------------------------------


class TestMlMetricsSuiteRunSuite:
    def test_run_suite_returns_suite_result(self):
        runner = ScenarioRunner()
        result = runner.run_suite(
            suite_id=_ML_METRICS_SUITE_ID,
            display_name="ML Evaluation Metrics Validation",
            scenario_ids=_ML_SCENARIO_IDS,
        )
        assert result.suite_id == _ML_METRICS_SUITE_ID
        assert len(result.scenarios) == len(_ML_SCENARIO_IDS)

    def test_run_suite_pass_rate_gte_threshold(self):
        runner = ScenarioRunner()
        result = runner.run_suite(
            suite_id=_ML_METRICS_SUITE_ID,
            display_name="ML Evaluation Metrics Validation",
            scenario_ids=_ML_SCENARIO_IDS,
        )
        assert result.pass_rate >= 0.9, f"ml_metrics_validation pass_rate={result.pass_rate:.2f} < 0.90"

    def test_run_suite_no_error_outcomes(self):
        runner = ScenarioRunner()
        result = runner.run_suite(
            suite_id=_ML_METRICS_SUITE_ID,
            display_name="ML Evaluation Metrics Validation",
            scenario_ids=_ML_SCENARIO_IDS,
        )
        errors = [r for r in result.scenarios if r.outcome == ScenarioOutcome.ERROR]
        assert errors == [], f"ERROR outcomes: {[(e.scenario_id, e.message) for e in errors]}"

    def test_run_suite_mean_latency_present(self):
        runner = ScenarioRunner()
        result = runner.run_suite(
            suite_id=_ML_METRICS_SUITE_ID,
            display_name="ML Evaluation Metrics Validation",
            scenario_ids=_ML_SCENARIO_IDS,
        )
        assert result.mean_latency_ms >= 0.0


# ---------------------------------------------------------------------------
# ScorecardEngine — ml_metric_correctness dimension
# ---------------------------------------------------------------------------


class TestScorecardEngineMlDimension:
    def test_suite_to_dimension_mapping(self):
        assert _SUITE_TO_DIMENSION.get(_ML_METRICS_SUITE_ID) == "ml_metric_correctness"

    def test_scorecard_includes_ml_metric_correctness(self):
#  # MOVED: from apps_eval.types.eval_types import SuiteResult

        suite_result = SuiteResult(
            suite_id=_ML_METRICS_SUITE_ID,
            display_name="ML Evaluation Metrics Validation",
            scenarios=(),
            pass_rate=1.0,
            mean_latency_ms=5.0,
        )
        specs = EvalAgentSpecs()
        engine = ScorecardEngine(dimension_configs=specs.scorecard_dimensions)
        scorecard = engine.compute([suite_result])
        dim_ids = [r.dimension_id for r in scorecard.rows]
        assert "ml_metric_correctness" in dim_ids

    def test_scorecard_ml_metric_correctness_score_from_pass_rate(self):
#  # MOVED: from apps_eval.types.eval_types import SuiteResult

        suite_result = SuiteResult(
            suite_id=_ML_METRICS_SUITE_ID,
            display_name="ML Evaluation Metrics Validation",
            scenarios=(),
            pass_rate=1.0,
            mean_latency_ms=5.0,
        )
        specs = EvalAgentSpecs()
        engine = ScorecardEngine(dimension_configs=specs.scorecard_dimensions)
        scorecard = engine.compute([suite_result])
        ml_row = next(r for r in scorecard.rows if r.dimension_id == "ml_metric_correctness")
        assert ml_row.score == 1.0
        assert ml_row.verdict == "PASS"
