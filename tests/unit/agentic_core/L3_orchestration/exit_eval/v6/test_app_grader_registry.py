"""Unit tests for agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry.

Wave 3.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — highest-fan-in
exit_eval module (``app_grader_registry``, fan_in=40). Covers the four pure
grader functions (read_dim_score_from_output, grade_tool_calls,
grade_state_check, grade_transcript), the GRADER_TYPE_DISPATCH table, and the
build_default_app_evaluator factory. Asserts the UNKNOWN-sentinel fail-closed
posture and both branches of every trajectory match-mode.
"""

from __future__ import annotations

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_TYPE_DISPATCH,
    build_default_app_evaluator,
    grade_state_check,
    grade_tool_calls,
    grade_transcript,
    read_dim_score_from_output,
)
from agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator import (
    GRADER_UNKNOWN_SENTINEL,
    AppSpecificEvaluator,
)
from agentic_core.L4_state.contracts.app_domain import ScoreDimension


def _dim(dimension_id: str = "factual_grounding", **overrides: object) -> ScoreDimension:
    base = dict(
        dimension_id=dimension_id,
        description="d",
        weight=1.0,
        grader_type="deterministic",
    )
    base.update(overrides)
    return ScoreDimension(**base)  # type: ignore[arg-type]


class TestReadDimScoreFromOutput:
    def test_reads_present_score(self) -> None:
        ctx = {"output": {"dim_scores": {"factual_grounding": 0.97}}}
        score, evidence = read_dim_score_from_output(_dim(), ctx)
        assert score == 0.97
        assert evidence == []

    def test_reads_evidence_list(self) -> None:
        ctx = {
            "output": {
                "dim_scores": {"factual_grounding": 0.8},
                "dim_evidence": {"factual_grounding": ["profile:abc", "src:1"]},
            }
        }
        score, evidence = read_dim_score_from_output(_dim(), ctx)
        assert score == 0.8
        assert evidence == ["profile:abc", "src:1"]

    def test_scalar_evidence_coerced_to_single_item_list(self) -> None:
        ctx = {
            "output": {
                "dim_scores": {"factual_grounding": 0.5},
                "dim_evidence": {"factual_grounding": "profile:xyz"},
            }
        }
        _, evidence = read_dim_score_from_output(_dim(), ctx)
        assert evidence == ["profile:xyz"]

    def test_missing_output_is_unknown(self) -> None:
        score, evidence = read_dim_score_from_output(_dim(), {})
        assert score == GRADER_UNKNOWN_SENTINEL
        assert evidence == []

    def test_non_mapping_output_is_unknown(self) -> None:
        score, _ = read_dim_score_from_output(_dim(), {"output": ["not", "a", "map"]})
        assert score == GRADER_UNKNOWN_SENTINEL

    def test_missing_dim_score_is_unknown(self) -> None:
        ctx = {"output": {"dim_scores": {"other_dim": 0.9}}}
        score, _ = read_dim_score_from_output(_dim(), ctx)
        assert score == GRADER_UNKNOWN_SENTINEL

    def test_non_numeric_score_is_unknown(self) -> None:
        ctx = {"output": {"dim_scores": {"factual_grounding": "not-a-number"}}}
        score, _ = read_dim_score_from_output(_dim(), ctx)
        assert score == GRADER_UNKNOWN_SENTINEL

    def test_string_numeric_score_coerced(self) -> None:
        ctx = {"output": {"dim_scores": {"factual_grounding": "0.75"}}}
        score, _ = read_dim_score_from_output(_dim(), ctx)
        assert score == 0.75

    def test_non_mapping_dim_scores_is_unknown(self) -> None:
        ctx = {"output": {"dim_scores": ["list"]}}
        score, _ = read_dim_score_from_output(_dim(), ctx)
        assert score == GRADER_UNKNOWN_SENTINEL


class TestGradeToolCalls:
    def _tc_dim(self, mode: str = "") -> ScoreDimension:
        return _dim("tool_selection", grader_type="tool_calls", trajectory_match_mode=mode)

    def test_missing_lists_falls_back_to_reader(self) -> None:
        # No tool_calls/expected_tool_calls but dim_scores present → reader path.
        ctx = {"output": {"dim_scores": {"tool_selection": 0.42}}}
        score, _ = grade_tool_calls(self._tc_dim(), ctx)
        assert score == 0.42

    def test_empty_expected_is_unknown(self) -> None:
        ctx = {"output": {"tool_calls": ["a"], "expected_tool_calls": []}}
        score, _ = grade_tool_calls(self._tc_dim(), ctx)
        assert score == GRADER_UNKNOWN_SENTINEL

    @pytest.mark.parametrize(
        "observed,expected,score",
        [
            (["a", "b"], ["a", "b"], 1.0),
            (["b", "a"], ["a", "b"], 0.0),
        ],
    )
    def test_strict_mode(self, observed: list, expected: list, score: float) -> None:
        ctx = {"output": {"tool_calls": observed, "expected_tool_calls": expected}}
        got, _ = grade_tool_calls(self._tc_dim("strict"), ctx)
        assert got == score

    def test_subset_mode(self) -> None:
        ctx = {"output": {"tool_calls": ["a"], "expected_tool_calls": ["a", "b"]}}
        got, _ = grade_tool_calls(self._tc_dim("subset"), ctx)
        assert got == 1.0
        ctx2 = {"output": {"tool_calls": ["a", "z"], "expected_tool_calls": ["a", "b"]}}
        got2, _ = grade_tool_calls(self._tc_dim("subset"), ctx2)
        assert got2 == 0.0

    def test_superset_mode(self) -> None:
        ctx = {"output": {"tool_calls": ["a", "b", "c"], "expected_tool_calls": ["a", "b"]}}
        got, _ = grade_tool_calls(self._tc_dim("superset"), ctx)
        assert got == 1.0

    def test_unordered_default_overlap_ratio(self) -> None:
        ctx = {"output": {"tool_calls": ["a", "x"], "expected_tool_calls": ["a", "b"]}}
        got, _ = grade_tool_calls(self._tc_dim(), ctx)  # default unordered
        assert got == 0.5

    def test_none_mode_falls_back_to_reader(self) -> None:
        ctx = {
            "output": {
                "tool_calls": ["a"],
                "expected_tool_calls": ["a"],
                "dim_scores": {"tool_selection": 0.33},
            }
        }
        got, _ = grade_tool_calls(self._tc_dim("none"), ctx)
        assert got == 0.33

    def test_non_mapping_output_is_unknown(self) -> None:
        got, _ = grade_tool_calls(self._tc_dim(), {"output": 5})
        assert got == GRADER_UNKNOWN_SENTINEL


class TestGradeStateCheck:
    def _sc_dim(self) -> ScoreDimension:
        return _dim("state_truth", grader_type="state_check")

    def test_all_assertions_satisfied(self) -> None:
        ctx = {
            "output": {"expected_state": {"state_truth": {"counter.value": 5}}},
            "state_diff": {"counter": {"value": 5}},
        }
        score, _ = grade_state_check(self._sc_dim(), ctx)
        assert score == 1.0

    def test_mismatch_scores_zero(self) -> None:
        ctx = {
            "output": {"expected_state": {"state_truth": {"counter.value": 5}}},
            "state_diff": {"counter": {"value": 9}},
        }
        score, evidence = grade_state_check(self._sc_dim(), ctx)
        assert score == 0.0
        assert any("mismatch" in e for e in evidence)

    def test_missing_path_scores_zero(self) -> None:
        ctx = {
            "output": {"expected_state": {"state_truth": {"a.b.c": True}}},
            "state_diff": {"a": {"x": 1}},
        }
        score, _ = grade_state_check(self._sc_dim(), ctx)
        assert score == 0.0

    def test_no_expected_for_dim_is_unknown(self) -> None:
        ctx = {"output": {"expected_state": {"other": {"k": 1}}}, "state_diff": {}}
        score, _ = grade_state_check(self._sc_dim(), ctx)
        assert score == GRADER_UNKNOWN_SENTINEL

    def test_missing_expected_state_is_unknown(self) -> None:
        ctx = {"output": {}, "state_diff": {"k": 1}}
        score, _ = grade_state_check(self._sc_dim(), ctx)
        assert score == GRADER_UNKNOWN_SENTINEL


class TestGradeTranscript:
    def _t_dim(self) -> ScoreDimension:
        return _dim("verbosity", grader_type="transcript")

    def test_reads_metric(self) -> None:
        ctx = {"output": {"transcript_metrics": {"verbosity": 0.6}}}
        score, evidence = grade_transcript(self._t_dim(), ctx)
        assert score == 0.6
        assert evidence == ["transcript_metric=0.6"]

    def test_missing_metrics_is_unknown(self) -> None:
        score, _ = grade_transcript(self._t_dim(), {"output": {}})
        assert score == GRADER_UNKNOWN_SENTINEL

    def test_missing_dim_metric_is_unknown(self) -> None:
        ctx = {"output": {"transcript_metrics": {"other": 1.0}}}
        score, _ = grade_transcript(self._t_dim(), ctx)
        assert score == GRADER_UNKNOWN_SENTINEL

    def test_non_numeric_metric_is_unknown(self) -> None:
        ctx = {"output": {"transcript_metrics": {"verbosity": object()}}}
        score, _ = grade_transcript(self._t_dim(), ctx)
        assert score == GRADER_UNKNOWN_SENTINEL


class TestDispatchTable:
    def test_expected_keys(self) -> None:
        assert set(GRADER_TYPE_DISPATCH) == {
            "deterministic",
            "hybrid",
            "llm_as_judge",
            "tool_calls",
            "trajectory_match",
            "state_check",
            "transcript",
        }

    @pytest.mark.parametrize(
        "key,fn",
        [
            ("deterministic", read_dim_score_from_output),
            ("hybrid", read_dim_score_from_output),
            ("llm_as_judge", read_dim_score_from_output),
            ("tool_calls", grade_tool_calls),
            ("trajectory_match", grade_tool_calls),
            ("state_check", grade_state_check),
            ("transcript", grade_transcript),
        ],
    )
    def test_dispatch_maps_to_correct_grader(self, key: str, fn: object) -> None:
        assert GRADER_TYPE_DISPATCH[key] is fn


class TestBuildDefaultAppEvaluator:
    def test_returns_app_specific_evaluator(self) -> None:
        ev = build_default_app_evaluator()
        assert isinstance(ev, AppSpecificEvaluator)

    def test_default_grader_is_reader(self) -> None:
        ev = build_default_app_evaluator()
        assert ev._default_grader is read_dim_score_from_output

    def test_extra_graders_registered(self) -> None:
        def _custom(dim, ctx):  # noqa: ANN001, ANN202
            return 1.0, []

        ev = build_default_app_evaluator(extra_graders={"my_dim": _custom})
        assert ev._graders["my_dim"] is _custom
