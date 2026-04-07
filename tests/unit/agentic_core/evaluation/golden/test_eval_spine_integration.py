"""Tests for GoldenEvalIntegration with Eval Spine.

Per windsurf rules: test-first discipline, deterministic tests.
"""

import time
from concurrent.futures import wait
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.adg.runtime.eval_spine import EvalSpine
from agentic_core.evaluation.golden.eval_spine_integration import (
    GoldenEvalIntegration,
    attach_golden_eval,
)
from agentic_core.evaluation.golden.golden_evaluator import GoldenEvalResult


@pytest.fixture
def eval_spine():
    """Create a test EvalSpine."""
    return EvalSpine(agent_id="test_agent", run_id="test_run_001")


@pytest.fixture
def integration(eval_spine):
    """Create GoldenEvalIntegration with mocked evaluator."""
    mock_evaluator = MagicMock()
    mock_evaluator.evaluate_against_test_cases.return_value = [
        GoldenEvalResult(
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
        ),
    ]
    mock_evaluator.list_available_datasets.return_value = ["test_cases"]

    integration = GoldenEvalIntegration(eval_spine, evaluator=mock_evaluator, max_workers=1)
    yield integration
    integration.shutdown()


class TestGoldenEvalIntegration:
    """Test GoldenEvalIntegration functionality."""

    def test_initialization(self, eval_spine):
        """Test integration initialization."""
        integration = GoldenEvalIntegration(eval_spine)

        assert integration.eval_spine == eval_spine
        assert integration.evaluator is not None
        assert integration._executor._max_workers == 2  # Default

    def test_evaluate_query_async(self, integration, eval_spine):
        """Test async query evaluation."""
        future = integration.evaluate_query_async(
            query="Test query",
            actual_output="Test output",
        )

        # Wait for completion
        wait([future], timeout=5.0)

        assert future.done()
        results = future.result()
        assert len(results) == 1
        assert results[0].case_id == "TC001"

    def test_evaluate_retrieval_async(self, integration, eval_spine):
        """Test async retrieval evaluation."""
        mock_result = GoldenEvalResult(
            case_id="RGT001",
            dataset_name="retrieval_ground_truth",
            query="Retrieval query",
            passed=True,
            match_score=1.0,
            expected_contains=["span1"],
            actual_contains=["span1"],
            missing_spans=[],
            extra_spans=[],
            eval_duration_ms=5.0,
        )
        integration.evaluator.evaluate_retrieval_ground_truth.return_value = [mock_result]

        future = integration.evaluate_retrieval_async(
            query="Retrieval query",
            retrieved_doc_ids=["doc_001"],
            generated_answer="Answer with span1",
        )

        wait([future], timeout=5.0)

        assert future.done()
        results = future.result()
        assert len(results) == 1

    def test_emit_golden_metrics(self, integration, eval_spine):
        """Test metrics emission to Eval Spine."""
        results = [
            GoldenEvalResult(
                case_id="TC001",
                dataset_name="test_cases",
                query="Test",
                passed=True,
                match_score=0.95,
                expected_contains=["a"],
                actual_contains=["a"],
                missing_spans=[],
                extra_spans=[],
                eval_duration_ms=10.0,
            ),
        ]

        integration.emit_golden_metrics(results)

        # Check metric was recorded
        assert len(eval_spine.report.metrics) == 1
        metric = eval_spine.report.metrics[0]
        assert metric.metric_name == "golden_match_test_cases"
        assert metric.value == 0.95
        assert metric.metadata["case_id"] == "TC001"

    def test_emit_drift_alert_low_score(self, integration, eval_spine):
        """Test drift alert emission for low match scores."""
        results = [
            GoldenEvalResult(
                case_id="TC002",
                dataset_name="test_cases",
                query="Test",
                passed=False,
                match_score=0.3,  # Low score triggers drift alert
                expected_contains=["a", "b", "c"],
                actual_contains=["a"],
                missing_spans=["b", "c"],
                extra_spans=[],
                eval_duration_ms=10.0,
            ),
        ]

        integration.emit_golden_metrics(results)

        # Check drift alert was emitted
        assert len(eval_spine.report.drift_alerts) == 1
        alert = eval_spine.report.drift_alerts[0]
        assert alert.metric_name == "golden_match_test_cases"
        assert alert.current_value == 0.3
        assert alert.baseline_value == 1.0

    def test_process_pending(self, integration, eval_spine):
        """Test processing pending evaluations."""
        # Submit async evaluation
        future = integration.evaluate_query_async(
            query="Test query",
            actual_output="Test output",
        )

        # Process all pending
        results = integration.process_pending(timeout=5.0)

        assert len(results) == 1
        assert len(eval_spine.report.metrics) == 1  # Metrics emitted

    def test_get_summary(self, integration):
        """Test summary generation."""
        summary = integration.get_summary()

        assert "pending_evaluations" in summary
        assert "datasets_available" in summary
        assert "eval_spine_metrics" in summary
        assert summary["datasets_available"] == ["test_cases"]

    def test_shutdown(self, integration, eval_spine):
        """Test graceful shutdown."""
        # Submit some work
        integration.evaluate_query_async("q1", "out1")
        integration.evaluate_query_async("q2", "out2")

        # Shutdown
        integration.shutdown()

        # Executor should be shut down
        assert integration._executor._shutdown

    def test_non_blocking_execution(self, eval_spine):
        """Verify evaluation is truly non-blocking."""
        # Create slow evaluator
        slow_evaluator = MagicMock()

        def slow_eval(*args, **kwargs):
            time.sleep(0.5)
            return []

        slow_evaluator.evaluate_against_test_cases.side_effect = slow_eval

        integration = GoldenEvalIntegration(eval_spine, evaluator=slow_evaluator, max_workers=1)

        start = time.time()
        future = integration.evaluate_query_async("query", "output")
        elapsed = time.time() - start

        # Should return immediately (< 0.1s even with thread startup)
        assert elapsed < 0.1
        assert not future.done()  # Still running

        integration.shutdown()


class TestAttachGoldenEval:
    """Test attach_golden_eval convenience function."""

    def test_attach_creates_integration(self, eval_spine):
        """Test attach function creates proper integration."""
        integration = attach_golden_eval(eval_spine)

        assert isinstance(integration, GoldenEvalIntegration)
        assert integration.eval_spine == eval_spine

        integration.shutdown()

    def test_attach_logs_info(self, eval_spine):
        """Test attach logs attachment info."""
        with patch("agentic_core.evaluation.golden.eval_spine_integration.Logger") as mock_logger:
            integration = attach_golden_eval(eval_spine)

            mock_logger.info.assert_called_once()
            assert "Golden eval attached" in mock_logger.info.call_args[0][0]

            integration.shutdown()


class TestErrorHandling:
    """Test error handling in integration."""

    def test_evaluation_exception_caught(self, eval_spine):
        """Test exceptions during evaluation are caught and logged."""
        mock_evaluator = MagicMock()
        mock_evaluator.evaluate_against_test_cases.side_effect = RuntimeError("Eval failed")

        integration = GoldenEvalIntegration(eval_spine, evaluator=mock_evaluator, max_workers=1)

        # Should not raise
        future = integration.evaluate_query_async("query", "output")
        wait([future], timeout=5.0)

        results = future.result()
        assert results == []  # Empty list on error

        integration.shutdown()

    def test_process_pending_exception_handling(self, integration):
        """Test exceptions during result processing are caught."""
        # Create a future that will raise when result() called
        mock_future = MagicMock()
        mock_future.done.return_value = True
        mock_future.result.side_effect = RuntimeError("Result processing failed")

        integration._pending = [mock_future]

        # Should not raise
        results = integration.process_pending()
        assert results == []
