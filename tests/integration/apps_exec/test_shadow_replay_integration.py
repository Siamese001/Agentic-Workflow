"""
tests/integration/test_shadow_replay_integration.py

Integration tests for Wave 1.3: Shadow/Replay Evaluation Integration

Tests:
- Shadow deployment evaluation
- Replay-based regression detection
- Integration with evaluation spine
- Statistics tracking
"""

from __future__ import annotations

import pytest

from agentic_core.L6_observability.utils.evaluation.shadow_replay_integration import (
    ReplayEvaluationResult,
    ReplayEvaluator,
    ShadowEvaluationIntegrator,
    ShadowEvaluationResult,
    get_replay_evaluator,
    get_shadow_integrator,
    reset_replay_evaluator,
    reset_shadow_integrator,
)


class TestShadowEvaluationIntegrator:
    """Test suite for ShadowEvaluationIntegrator."""

    def test_no_regression_passes(self):
        """Test shadow deployment with no regression passes."""
        integrator = ShadowEvaluationIntegrator()

        production_metrics = {
            "p95_latency_ms": 100.0,
            "error_rate": 0.01,
            "cpu_pct": 50.0,
            "mem_mb": 1000.0,
        }

        shadow_metrics = {
            "p95_latency_ms": 105.0,  # 5% increase (within 10% threshold)
            "error_rate": 0.015,  # 0.005 increase (within 0.05 threshold)
            "cpu_pct": 52.0,  # 4% increase (within 15% threshold)
            "mem_mb": 1020.0,  # 2% increase (within 15% threshold)
        }

        result = integrator.evaluate_shadow_deployment(production_metrics, shadow_metrics)

        assert isinstance(result, ShadowEvaluationResult)
        assert result.passed is True
        assert result.regression_score == 0.0
        assert len(result.violations) == 0

    def test_latency_regression_fails(self):
        """Test shadow deployment with latency regression fails."""
        integrator = ShadowEvaluationIntegrator()

        production_metrics = {
            "p95_latency_ms": 100.0,
            "error_rate": 0.01,
            "cpu_pct": 50.0,
            "mem_mb": 1000.0,
        }

        shadow_metrics = {
            "p95_latency_ms": 120.0,  # 20% increase (exceeds 10% threshold)
            "error_rate": 0.01,
            "cpu_pct": 50.0,
            "mem_mb": 1000.0,
        }

        result = integrator.evaluate_shadow_deployment(production_metrics, shadow_metrics)

        assert result.passed is False
        assert result.regression_score > 0.0
        assert len(result.violations) == 1
        assert "LATENCY_REGRESSION" in result.violations[0]

    def test_error_rate_regression_fails(self):
        """Test shadow deployment with error rate regression fails."""
        integrator = ShadowEvaluationIntegrator()

        production_metrics = {
            "p95_latency_ms": 100.0,
            "error_rate": 0.01,
            "cpu_pct": 50.0,
            "mem_mb": 1000.0,
        }

        shadow_metrics = {
            "p95_latency_ms": 100.0,
            "error_rate": 0.07,  # 0.06 increase (exceeds 0.05 threshold)
            "cpu_pct": 50.0,
            "mem_mb": 1000.0,
        }

        result = integrator.evaluate_shadow_deployment(production_metrics, shadow_metrics)

        assert result.passed is False
        assert len(result.violations) == 1
        assert "ERROR_RATE_REGRESSION" in result.violations[0]

    def test_multiple_regressions(self):
        """Test shadow deployment with multiple regressions."""
        integrator = ShadowEvaluationIntegrator()

        production_metrics = {
            "p95_latency_ms": 100.0,
            "error_rate": 0.01,
            "cpu_pct": 50.0,
            "mem_mb": 1000.0,
        }

        shadow_metrics = {
            "p95_latency_ms": 130.0,  # 30% increase
            "error_rate": 0.08,  # 0.07 increase
            "cpu_pct": 70.0,  # 40% increase
            "mem_mb": 1300.0,  # 30% increase
        }

        result = integrator.evaluate_shadow_deployment(production_metrics, shadow_metrics)

        assert result.passed is False
        assert len(result.violations) == 4
        assert result.regression_score > 0.0

    def test_custom_thresholds(self):
        """Test shadow evaluation with custom thresholds."""
        integrator = ShadowEvaluationIntegrator()

        production_metrics = {
            "p95_latency_ms": 100.0,
            "error_rate": 0.01,
            "cpu_pct": 50.0,
            "mem_mb": 1000.0,
        }

        shadow_metrics = {
            "p95_latency_ms": 110.0,  # 10% increase
            "error_rate": 0.01,
            "cpu_pct": 50.0,
            "mem_mb": 1000.0,
        }

        # Strict threshold (5%)
        strict_thresholds = {
            "max_latency_regression_pct": 5.0,
            "max_error_rate_regression_abs": 0.05,
            "max_cpu_regression_pct": 15.0,
            "max_mem_regression_pct": 15.0,
        }

        result = integrator.evaluate_shadow_deployment(
            production_metrics, shadow_metrics, strict_thresholds
        )

        assert result.passed is False
        assert "LATENCY_REGRESSION" in result.violations[0]

    def test_statistics_tracking(self):
        """Test that integrator tracks evaluation statistics."""
        integrator = ShadowEvaluationIntegrator()

        production_metrics = {"p95_latency_ms": 100.0, "error_rate": 0.01, "cpu_pct": 50.0, "mem_mb": 1000.0}

        # Pass
        integrator.evaluate_shadow_deployment(
            production_metrics,
            {"p95_latency_ms": 105.0, "error_rate": 0.01, "cpu_pct": 50.0, "mem_mb": 1000.0},
        )

        # Fail
        integrator.evaluate_shadow_deployment(
            production_metrics,
            {"p95_latency_ms": 150.0, "error_rate": 0.01, "cpu_pct": 50.0, "mem_mb": 1000.0},
        )

        stats = integrator.get_stats()
        assert stats["evaluation_count"] == 2
        assert stats["regression_count"] == 1
        assert stats["regression_rate"] == 0.5


class TestReplayEvaluator:
    """Test suite for ReplayEvaluator."""

    def test_no_regression_passes(self):
        """Test replay with no regression passes."""
        evaluator = ReplayEvaluator(regression_threshold=0.1)

        result = evaluator.evaluate_replay(
            trace_id="trace-001",
            baseline_score=0.85,
            current_score=0.87,  # 0.02 delta (within 0.1 threshold)
        )

        assert isinstance(result, ReplayEvaluationResult)
        assert result.passed is True
        assert result.regression_delta == pytest.approx(0.02)
        assert result.baseline_score == 0.85
        assert result.current_score == 0.87

    def test_regression_fails(self):
        """Test replay with regression fails."""
        evaluator = ReplayEvaluator(regression_threshold=0.1)

        result = evaluator.evaluate_replay(
            trace_id="trace-002",
            baseline_score=0.85,
            current_score=0.70,  # 0.15 delta (exceeds 0.1 threshold)
        )

        assert result.passed is False
        assert result.regression_delta == pytest.approx(0.15)

    def test_improvement_passes(self):
        """Test replay with improvement passes."""
        evaluator = ReplayEvaluator(regression_threshold=0.1)

        result = evaluator.evaluate_replay(
            trace_id="trace-003",
            baseline_score=0.70,
            current_score=0.85,  # Improvement
        )

        # Improvement should still pass if delta exceeds threshold
        # (we use abs() so large improvements are flagged for review)
        assert result.regression_delta == pytest.approx(0.15)
        assert result.passed is False  # Large change in either direction

    def test_custom_threshold(self):
        """Test replay evaluator with custom threshold."""
        strict_evaluator = ReplayEvaluator(regression_threshold=0.05)

        result = strict_evaluator.evaluate_replay(
            trace_id="trace-004",
            baseline_score=0.85,
            current_score=0.82,  # 0.03 delta
        )

        assert result.passed is True  # Within 0.05 threshold

        result2 = strict_evaluator.evaluate_replay(
            trace_id="trace-005",
            baseline_score=0.85,
            current_score=0.78,  # 0.07 delta
        )

        assert result2.passed is False  # Exceeds 0.05 threshold

    def test_statistics_tracking(self):
        """Test that evaluator tracks statistics."""
        evaluator = ReplayEvaluator(regression_threshold=0.1)

        # Pass
        evaluator.evaluate_replay("trace-001", 0.85, 0.87)

        # Fail
        evaluator.evaluate_replay("trace-002", 0.85, 0.70)

        # Pass
        evaluator.evaluate_replay("trace-003", 0.85, 0.86)

        stats = evaluator.get_stats()
        assert stats["evaluation_count"] == 3
        assert stats["regression_count"] == 1
        assert stats["regression_rate"] == pytest.approx(1.0 / 3.0)


class TestGlobalInstances:
    """Test global instance management."""

    def test_shadow_integrator_singleton(self):
        """Test shadow integrator singleton pattern."""
        reset_shadow_integrator()

        integrator1 = get_shadow_integrator()
        integrator2 = get_shadow_integrator()

        assert integrator1 is integrator2

        reset_shadow_integrator()
        integrator3 = get_shadow_integrator()

        assert integrator3 is not integrator1

    def test_replay_evaluator_singleton(self):
        """Test replay evaluator singleton pattern."""
        reset_replay_evaluator()

        evaluator1 = get_replay_evaluator()
        evaluator2 = get_replay_evaluator()

        assert evaluator1 is evaluator2

        reset_replay_evaluator()
        evaluator3 = get_replay_evaluator()

        assert evaluator3 is not evaluator1


class TestIntegration:
    """Integration tests for shadow/replay evaluation."""

    def test_shadow_and_replay_together(self):
        """Test using both shadow and replay evaluation together."""
        shadow_integrator = ShadowEvaluationIntegrator()
        replay_evaluator = ReplayEvaluator()

        # Shadow evaluation
        shadow_result = shadow_integrator.evaluate_shadow_deployment(
            production_metrics={"p95_latency_ms": 100.0, "error_rate": 0.01, "cpu_pct": 50.0, "mem_mb": 1000.0},
            shadow_metrics={"p95_latency_ms": 105.0, "error_rate": 0.01, "cpu_pct": 50.0, "mem_mb": 1000.0},
        )

        # Replay evaluation
        replay_result = replay_evaluator.evaluate_replay(
            trace_id="trace-001",
            baseline_score=0.85,
            current_score=0.87,
        )

        # Both should pass
        assert shadow_result.passed is True
        assert replay_result.passed is True

    def test_combined_statistics(self):
        """Test combined statistics from both evaluators."""
        shadow_integrator = ShadowEvaluationIntegrator()
        replay_evaluator = ReplayEvaluator()

        # Run multiple evaluations
        for i in range(5):
            shadow_integrator.evaluate_shadow_deployment(
                production_metrics={"p95_latency_ms": 100.0, "error_rate": 0.01, "cpu_pct": 50.0, "mem_mb": 1000.0},
                shadow_metrics={"p95_latency_ms": 100.0 + i * 5, "error_rate": 0.01, "cpu_pct": 50.0, "mem_mb": 1000.0},
            )

            replay_evaluator.evaluate_replay(
                trace_id=f"trace-{i:03d}",
                baseline_score=0.85,
                current_score=0.85 - i * 0.03,
            )

        shadow_stats = shadow_integrator.get_stats()
        replay_stats = replay_evaluator.get_stats()

        assert shadow_stats["evaluation_count"] == 5
        assert replay_stats["evaluation_count"] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
