"""Tests for GoldenL6Emitter.

Per windsurf rules: test-first discipline, deterministic tests.
"""

from unittest.mock import patch

import pytest

from agentic_core.evaluation.golden.golden_evaluator import GoldenEvalResult
from agentic_core.evaluation.golden.l6_emitter import (
    GoldenL6Emitter,
    emit_golden_batch,
    emit_golden_result,
    get_l6_emitter,
)


@pytest.fixture
def sample_result():
    """Create a sample golden eval result."""
    return GoldenEvalResult(
        case_id="TC001",
        dataset_name="test_cases",
        query="Test query",
        passed=True,
        match_score=0.95,
        expected_contains=["a", "b"],
        actual_contains=["a", "b"],
        missing_spans=[],
        extra_spans=[],
        eval_duration_ms=10.0,
    )


@pytest.fixture
def emitter():
    """Create a fresh L6 emitter."""
    return GoldenL6Emitter()


class TestGoldenL6Emitter:
    """Test GoldenL6Emitter functionality."""

    @patch("agentic_core.evaluation.golden.l6_emitter._emit_captures_evaluation_metric")
    @patch("agentic_core.evaluation.golden.l6_emitter._emit_records_telemetry_event")
    @patch("agentic_core.evaluation.golden.l6_emitter._emit_emits_metric_event")
    def test_emit_single_result(
        self,
        mock_metric_event,
        mock_telemetry,
        mock_eval_metric,
        emitter,
        sample_result,
    ):
        """Test emitting a single golden eval result."""
        emitter.emit_golden_eval_result(sample_result)

        # Should emit 3 signals
        assert mock_eval_metric.call_count == 1
        assert mock_telemetry.call_count == 1
        assert mock_metric_event.call_count == 1

        # Check evaluation metric args (score encoded in metric name)
        mock_eval_metric.assert_called_with(
            "golden_eval",
            "test_cases",
            "match_score_TC001_95",  # Score 0.95 encoded as 95
        )

        # Check telemetry event args
        mock_telemetry.assert_called_with(
            "golden_eval",
            "test_cases",
            {
                "case_id": "TC001",
                "query": "Test query",
                "passed": True,
                "match_score": 0.95,
                "eval_duration_ms": 10.0,
            },
        )

        # Check metric event args
        mock_metric_event.assert_called_with(
            "golden_eval",
            "test_cases",
            {
                "metric_name": "golden_match_test_cases",
                "value": 0.95,
                "case_id": "TC001",
                "passed": True,
            },
        )

    @patch("agentic_core.evaluation.golden.l6_emitter._emit_captures_evaluation_metric")
    @patch("agentic_core.evaluation.golden.l6_emitter._emit_records_telemetry_event")
    @patch("agentic_core.evaluation.golden.l6_emitter._emit_emits_metric_event")
    def test_emit_batch_results(
        self,
        mock_metric_event,
        mock_telemetry,
        mock_eval_metric,
        emitter,
    ):
        """Test emitting batch of results."""
        results = [
            GoldenEvalResult(
                case_id="TC001",
                dataset_name="test_cases",
                query="Query 1",
                passed=True,
                match_score=0.9,
                expected_contains=["a"],
                actual_contains=["a"],
                missing_spans=[],
                extra_spans=[],
                eval_duration_ms=5.0,
            ),
            GoldenEvalResult(
                case_id="TC002",
                dataset_name="test_cases",
                query="Query 2",
                passed=False,
                match_score=0.6,
                expected_contains=["a", "b"],
                actual_contains=["a"],
                missing_spans=["b"],
                extra_spans=[],
                eval_duration_ms=8.0,
            ),
        ]

        summary = emitter.emit_batch_results(results)

        # Should emit metrics for each result + 1 aggregate
        assert mock_eval_metric.call_count == 3  # 2 results + 1 aggregate

        # Check summary
        assert summary["emitted"] == 2
        assert summary["passed"] == 1
        assert summary["failed"] == 1
        assert summary["avg_match_score"] == 0.75  # (0.9 + 0.6) / 2
        assert "test_cases" in summary["datasets"]

    @patch("agentic_core.evaluation.golden.l6_emitter._emit_captures_evaluation_metric")
    @patch("agentic_core.evaluation.golden.l6_emitter._emit_records_telemetry_event")
    @patch("agentic_core.evaluation.golden.l6_emitter._emit_emits_metric_event")
    def test_emit_empty_batch(
        self,
        mock_metric_event,
        mock_telemetry,
        mock_eval_metric,
        emitter,
    ):
        """Test emitting empty batch."""
        summary = emitter.emit_batch_results([])

        assert summary["emitted"] == 0
        assert summary["datasets"] == []

        # Should not emit any metrics
        mock_eval_metric.assert_not_called()
        mock_telemetry.assert_not_called()
        mock_metric_event.assert_not_called()

    def test_get_emit_stats(self, emitter, sample_result):
        """Test emission statistics tracking."""
        with patch("agentic_core.evaluation.golden.l6_emitter._emit_captures_evaluation_metric"), \
             patch("agentic_core.evaluation.golden.l6_emitter._emit_records_telemetry_event"), \
             patch("agentic_core.evaluation.golden.l6_emitter._emit_emits_metric_event"):

            stats_before = emitter.get_emit_stats()
            assert stats_before["total_emits"] == 0

            emitter.emit_golden_eval_result(sample_result)

            stats_after = emitter.get_emit_stats()
            assert stats_after["total_emits"] == 3  # 3 emissions per result


class TestSingletonFunctions:
    """Test module-level singleton functions."""

    def test_get_l6_emitter_singleton(self):
        """Test get_l6_emitter returns singleton."""
        e1 = get_l6_emitter()
        e2 = get_l6_emitter()
        assert e1 is e2

    @patch("agentic_core.evaluation.golden.l6_emitter._emit_captures_evaluation_metric")
    @patch("agentic_core.evaluation.golden.l6_emitter._emit_records_telemetry_event")
    @patch("agentic_core.evaluation.golden.l6_emitter._emit_emits_metric_event")
    def test_emit_golden_result_convenience(
        self,
        mock_metric_event,
        mock_telemetry,
        mock_eval_metric,
        sample_result,
    ):
        """Test emit_golden_result convenience function."""
        emit_golden_result(sample_result)

        # Should emit through singleton
        assert mock_eval_metric.called

    @patch("agentic_core.evaluation.golden.l6_emitter._emit_captures_evaluation_metric")
    @patch("agentic_core.evaluation.golden.l6_emitter._emit_records_telemetry_event")
    @patch("agentic_core.evaluation.golden.l6_emitter._emit_emits_metric_event")
    def test_emit_golden_batch_convenience(
        self,
        mock_metric_event,
        mock_telemetry,
        mock_eval_metric,
    ):
        """Test emit_golden_batch convenience function."""
        results = [
            GoldenEvalResult(
                case_id="TC001",
                dataset_name="test_cases",
                query="Query 1",
                passed=True,
                match_score=0.9,
                expected_contains=["a"],
                actual_contains=["a"],
                missing_spans=[],
                extra_spans=[],
                eval_duration_ms=5.0,
            ),
        ]

        summary = emit_golden_batch(results)

        assert summary["emitted"] == 1
        assert summary["passed"] == 1
