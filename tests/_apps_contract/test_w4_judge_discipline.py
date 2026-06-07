"""W4 verification — retry-on-low + OTEL domain attrs + tracked_metrics.

Plan: ``docs/archive/windsurf/legacy-tree/plans/apps-eval-harness-deferred-e4a1b7.md`` W4.P1-P4.

Proves:

- Retry-on-low only fires when grader_type=llm_as_judge AND
  judge_retry_on_low=True AND raw_score < min_required_score.
- Retry takes the higher of the two scores (never worse than original).
- Retry budget: 1 call max per dim per run.
- Pipeline OTEL span exit.app_specific_eval carries dim counts + optional
  tracked_metrics keys.
"""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator import (
    GRADER_UNKNOWN_SENTINEL,
    AppSpecificEvaluator,
)
from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    build_default_app_evaluator,
)
from agentic_core.L4_state.contracts.app_domain import (
    AppEvalRubricRecord,
    AppThresholdProfileRecord,
    ScoreDimension,
)


class TestRetryOnLow:
    def _setup(self, *, judge_scores: list[float], grader_type: str = "llm_as_judge"):
        """Build an evaluator whose single grader yields successive scores."""
        calls = {"n": 0}

        def flaky_grader(dim, ctx):
            i = calls["n"]
            calls["n"] += 1
            return judge_scores[min(i, len(judge_scores) - 1)], [f"call={i}"]

        evaluator = AppSpecificEvaluator(default_grader=flaky_grader)

        dim = ScoreDimension(
            dimension_id="exec_pos", description="t", weight=1.0,
            grader_type=grader_type, min_required_score=0.70,
            evidence_required=False, fail_closed_if_unknown=False,
        )
        rubric = AppEvalRubricRecord(
            eval_rubric_id="aer::test::t::v1",
            app_id="apps_eval",
            task_class="eval_self",
            version="1.0",
            status="active",
            policy_hash="p",
            score_dimensions=(dim,),
        )
        threshold = AppThresholdProfileRecord(
            threshold_profile_id="atp::test::t::v1",
            app_id="apps_eval",
            task_class="eval_self",
            version="1.0",
            status="active",
            overall_pass_threshold=0.60,
        )
        return evaluator, rubric, threshold, calls

    def test_retry_fires_on_low_when_enabled(self) -> None:
        evaluator, rubric, threshold, calls = self._setup(judge_scores=[0.50, 0.85])
        result = evaluator._score_against_rubric(
            app_id="apps_eval", task_class="eval_self",
            rubric=rubric, threshold=threshold,
            run_context={"judge_retry_on_low": True},
        )
        # Retry happened (2 calls) and higher score was taken
        assert calls["n"] == 2
        assert result.dimensions[0].score == 0.85

    def test_retry_not_fired_when_flag_absent(self) -> None:
        evaluator, rubric, threshold, calls = self._setup(judge_scores=[0.50, 0.90])
        _result = evaluator._score_against_rubric(
            app_id="apps_eval", task_class="eval_self",
            rubric=rubric, threshold=threshold,
            run_context={},  # no judge_retry_on_low
        )
        assert calls["n"] == 1

    def test_retry_not_fired_for_deterministic_grader(self) -> None:
        evaluator, rubric, threshold, calls = self._setup(
            judge_scores=[0.50, 0.90], grader_type="deterministic",
        )
        _result = evaluator._score_against_rubric(
            app_id="apps_eval", task_class="eval_self",
            rubric=rubric, threshold=threshold,
            run_context={"judge_retry_on_low": True},
        )
        # Deterministic grader MUST NOT be retried — only 1 call.
        assert calls["n"] == 1

    def test_retry_keeps_original_if_retry_is_lower(self) -> None:
        evaluator, rubric, threshold, calls = self._setup(judge_scores=[0.60, 0.40])
        result = evaluator._score_against_rubric(
            app_id="apps_eval", task_class="eval_self",
            rubric=rubric, threshold=threshold,
            run_context={"judge_retry_on_low": True},
        )
        assert calls["n"] == 2
        # Original 0.60 kept (higher than 0.40 retry)
        assert result.dimensions[0].score == 0.60

    def test_retry_budget_max_one(self) -> None:
        """Retry budget: at most 1 extra call per dim, even if result is
        still below min_required_score after the retry."""
        evaluator, rubric, threshold, calls = self._setup(
            judge_scores=[0.30, 0.35, 0.40],  # all below min=0.70
        )
        _result = evaluator._score_against_rubric(
            app_id="apps_eval", task_class="eval_self",
            rubric=rubric, threshold=threshold,
            run_context={"judge_retry_on_low": True},
        )
        # Exactly 2 calls — original + 1 retry
        assert calls["n"] == 2


class TestOtelAttrsAndTrackedMetrics:
    def test_pipeline_span_emits_tracked_metric_keys(self) -> None:
        """Structural check: pipeline.py emits the canonical tracked_metrics
        OTEL keys. Full integration is tested in the v6 pipeline tests."""
        from pathlib import Path
        src = Path(__file__).resolve().parents[2] / "agentic_core" / "L3_orchestration" / "exit_eval" / "v6" / "pipeline.py"
        text = src.read_text(encoding="utf-8")
        for key in ("ttft_ms", "ttlt_ms", "output_tokens_per_sec", "n_total_tokens", "cost_usd"):
            assert key in text, f"pipeline.py must emit OTEL attr {key}"
        # W4.P3 dim counts
        for key in ("dim_pass_count", "dim_fail_count", "dim_unknown_count"):
            assert key in text, f"pipeline.py must emit OTEL attr {key}"
