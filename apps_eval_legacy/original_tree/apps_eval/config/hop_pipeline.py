"""apps_eval HOP pipeline topology.

Declares the 6-stage inner DAG for the evaluation lab:
retrieve evaluation corpus -> run scenarios -> compute scorecard ->
judge narratives (LLM-rubric) -> detect regressions -> assess HITL
decision quality.

This substrate adoption is **additive**: the existing imperative
``BaseEvalEngine``-rooted runtime remains primary (driven by
``apps_eval/integrations/eval_ingress_runner.py`` and
``apps_eval/reasoning/EvalOrchestrator.py``). The shared-substrate
entry point documented here lets future callers drive the same 6 stages
declaratively via ``HopPipelineExecutor``.

``base_eval_engine.py`` (abstract base) and ``_taxonomy.py`` (constants)
are intentionally NOT stages — they are infrastructure for the concrete
engines, not pipeline stages.

Plan: .windsurf/plans/apps-hop-substrate-four-apps-b4a2c9.md (Wave 4)
"""

from __future__ import annotations

from apps_shared.orchestration import HopRegistry, HopStageSpec

_STAGE_SPECS: list[HopStageSpec] = [
    HopStageSpec(
        stage_id=1,
        stage_name="evaluation_retrieval",
        engine_module="apps_eval.engines.hop_evaluation_retrieval_engine",
        engine_class="HopEvaluationRetrievalEngine",
        inputs=("eval_request",),
        outputs=("retrieved_evaluations",),
        required=True,
    ),
    HopStageSpec(
        stage_id=2,
        stage_name="scenario_runner",
        engine_module="apps_eval.engines.hop_scenario_runner_engine",
        engine_class="HopScenarioRunnerEngine",
        inputs=("eval_request", "retrieved_evaluations"),
        outputs=("scenario_results",),
        required=True,
    ),
    HopStageSpec(
        stage_id=3,
        stage_name="scorecard",
        engine_module="apps_eval.engines.hop_scorecard_engine",
        engine_class="HopScorecardEngine",
        inputs=("scenario_results",),
        outputs=("scorecard",),
        required=True,
    ),
    HopStageSpec(
        stage_id=4,
        stage_name="narrative_judge",
        engine_module="apps_eval.engines.hop_narrative_judge_engine",
        engine_class="HopNarrativeJudgeEngine",
        inputs=("scenario_results", "scorecard"),
        outputs=("judge_verdicts",),
        required=True,
    ),
    HopStageSpec(
        stage_id=5,
        stage_name="regression_detector",
        engine_module="apps_eval.engines.hop_regression_detector_engine",
        engine_class="HopRegressionDetectorEngine",
        inputs=("scorecard",),
        outputs=("regression_result",),
        required=True,
    ),
    HopStageSpec(
        stage_id=6,
        stage_name="hitl_decision_quality",
        engine_module="apps_eval.engines.hop_hitl_decision_quality_engine",
        engine_class="HopHitlDecisionQualityEngine",
        inputs=("eval_request", "scorecard", "regression_result"),
        outputs=("hitl_quality_report",),
        required=True,
    ),
]


REGISTRY: HopRegistry = HopRegistry("apps_eval").register_all(_STAGE_SPECS)


__all__ = ["REGISTRY"]
