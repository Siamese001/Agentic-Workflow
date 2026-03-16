"""Unit tests for system_learning.validators.shadow_evaluator."""

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from system_learning.validators.shadow_evaluator import (
    ShadowMetrics,
    ShadowRegression,
    ShadowThresholds,
    evaluate_shadow,
)

_emit_records_execution_trace("p0", "evidence", "test_shadow_evaluator")
_emit_applies_guardrail("p0", "test_shadow_evaluator", "p0_governance")
_emit_reads_policy_state("p0", "test_shadow_evaluator", "policy_binding")
_emit_snapshots_state("p0", "test_shadow_evaluator", "state_snapshot")
emit_replay_key("p0", "test_shadow_evaluator")
emit_determinism_digest("p0", "test_shadow_evaluator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


class TestShadowEvaluator:
    def test_pass_within_thresholds(self):
        """Shadow metrics within thresholds pass validation."""
        prod = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        shadow = ShadowMetrics(
            p95_latency_ms=105.0,  # 5% regression
            error_rate=0.015,  # 0.005 absolute increase
            safety_violation_count=0,
            cpu_pct=52.0,  # 4% regression
            mem_mb=1020.0,  # 2% regression
        )
        thresholds = ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.01,
            max_cpu_regression_pct=10.0,
            max_mem_regression_pct=10.0,
            forbid_any_safety_violation_increase=True,
        )

        # Should not raise
        evaluate_shadow(prod, shadow, thresholds)

    def test_fail_latency_regression(self):
        """Latency regression beyond threshold raises."""
        prod = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        shadow = ShadowMetrics(
            p95_latency_ms=120.0,  # 20% regression
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        thresholds = ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.05,
            max_cpu_regression_pct=10.0,
            max_mem_regression_pct=10.0,
            forbid_any_safety_violation_increase=True,
        )

        with pytest.raises(ShadowRegression, match="P95_LATENCY_REGRESSION"):
            evaluate_shadow(prod, shadow, thresholds)

    def test_fail_error_rate_regression(self):
        """Error rate regression beyond threshold raises."""
        prod = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        shadow = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.08,  # 0.07 absolute increase
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        thresholds = ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.05,
            max_cpu_regression_pct=10.0,
            max_mem_regression_pct=10.0,
            forbid_any_safety_violation_increase=True,
        )

        with pytest.raises(ShadowRegression, match="ERROR_RATE_REGRESSION"):
            evaluate_shadow(prod, shadow, thresholds)

    def test_fail_safety_violation_increase(self):
        """Any safety violation increase raises when forbidden."""
        prod = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        shadow = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=1,  # Increase from 0 to 1
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        thresholds = ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.05,
            max_cpu_regression_pct=10.0,
            max_mem_regression_pct=10.0,
            forbid_any_safety_violation_increase=True,
        )

        with pytest.raises(ShadowRegression, match="SAFETY_VIOLATION_INCREASE"):
            evaluate_shadow(prod, shadow, thresholds)

    def test_fail_cpu_regression(self):
        """CPU regression beyond threshold raises."""
        prod = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        shadow = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=70.0,  # 40% regression
            mem_mb=1000.0,
        )
        thresholds = ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.05,
            max_cpu_regression_pct=10.0,
            max_mem_regression_pct=10.0,
            forbid_any_safety_violation_increase=True,
        )

        with pytest.raises(ShadowRegression, match="CPU_REGRESSION"):
            evaluate_shadow(prod, shadow, thresholds)

    def test_fail_mem_regression(self):
        """Memory regression beyond threshold raises."""
        prod = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        shadow = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1500.0,  # 50% regression
        )
        thresholds = ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.05,
            max_cpu_regression_pct=10.0,
            max_mem_regression_pct=10.0,
            forbid_any_safety_violation_increase=True,
        )

        with pytest.raises(ShadowRegression, match="MEM_REGRESSION"):
            evaluate_shadow(prod, shadow, thresholds)

    def test_multiple_violations_reported(self):
        """Multiple violations are all reported in error message."""
        prod = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        shadow = ShadowMetrics(
            p95_latency_ms=120.0,  # Latency violation
            error_rate=0.08,  # Error rate violation
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        thresholds = ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.05,
            max_cpu_regression_pct=10.0,
            max_mem_regression_pct=10.0,
            forbid_any_safety_violation_increase=True,
        )

        with pytest.raises(ShadowRegression) as exc_info:
            evaluate_shadow(prod, shadow, thresholds)

        error_msg = str(exc_info.value)
        assert "P95_LATENCY_REGRESSION" in error_msg
        assert "ERROR_RATE_REGRESSION" in error_msg


class TestDeterminism:
    def test_evaluate_shadow_deterministic(self):
        """evaluate_shadow produces consistent results."""
        prod = ShadowMetrics(
            p95_latency_ms=100.0,
            error_rate=0.01,
            safety_violation_count=0,
            cpu_pct=50.0,
            mem_mb=1000.0,
        )
        shadow = ShadowMetrics(
            p95_latency_ms=105.0,
            error_rate=0.015,
            safety_violation_count=0,
            cpu_pct=52.0,
            mem_mb=1020.0,
        )
        thresholds = ShadowThresholds(
            max_p95_latency_regression_pct=10.0,
            max_error_rate_regression_abs=0.01,
            max_cpu_regression_pct=10.0,
            max_mem_regression_pct=10.0,
            forbid_any_safety_violation_increase=True,
        )

        # Should not raise on multiple calls
        evaluate_shadow(prod, shadow, thresholds)
        evaluate_shadow(prod, shadow, thresholds)
        evaluate_shadow(prod, shadow, thresholds)
