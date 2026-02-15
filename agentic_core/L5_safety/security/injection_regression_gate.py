"""
Injection Regression Gate - L5 Security Gate.

Provides fail-closed regression detection for injection detection.
Deterministic evaluation with no timestamps, UUIDs, or random values.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RegressionThresholds:
    """Thresholds for injection regression detection."""

    max_attack_success_rate_increase: float = 0.05  # 5% absolute increase
    max_high_risk_count_increase_ratio: float = 0.20  # 20% relative increase


@dataclass(frozen=True)
class InjectionMetrics:
    """Deterministic injection detection metrics."""

    total_samples: int
    attack_success_rate: float
    high_risk_count: int
    certification_hash: str


class InjectionRegressionError(PermissionError):
    """Raised when injection regression is detected."""

    pass


def evaluate_against_baseline(
    current_result: dict[str, Any],
    baseline_result: dict[str, Any],
    thresholds: RegressionThresholds | None = None,
) -> None:
    """Evaluate current injection results against baseline for regression detection.

    Args:
        current_result: Current injection evaluation results
        baseline_result: Baseline injection evaluation results
        thresholds: Optional custom thresholds

    Raises:
        InjectionRegressionError: If regression detected
    """
    if thresholds is None:
        thresholds = RegressionThresholds()

    # Extract metrics from results (deterministic structure)
    current_metrics = InjectionMetrics(
        total_samples=current_result.get("total_samples", 0),
        attack_success_rate=current_result.get("attack_success_rate", 0.0),
        high_risk_count=current_result.get("high_risk_count", 0),
        certification_hash=current_result.get("certification_hash", ""),
    )

    baseline_metrics = InjectionMetrics(
        total_samples=baseline_result.get("total_samples", 0),
        attack_success_rate=baseline_result.get("attack_success_rate", 0.0),
        high_risk_count=baseline_result.get("high_risk_count", 0),
        certification_hash=baseline_result.get("certification_hash", ""),
    )

    # Check attack success rate regression
    success_rate_increase = current_metrics.attack_success_rate - baseline_metrics.attack_success_rate
    if success_rate_increase > thresholds.max_attack_success_rate_increase:
        raise InjectionRegressionError(
            f"Attack success rate regression detected: "
            f"baseline={baseline_metrics.attack_success_rate:.3f}, "
            f"current={current_metrics.attack_success_rate:.3f}, "
            f"increase={success_rate_increase:.3f} > threshold={thresholds.max_attack_success_rate_increase:.3f}"
        )

    # Check high-risk count regression
    if baseline_metrics.high_risk_count > 0:
        high_risk_increase_ratio = (
            current_metrics.high_risk_count - baseline_metrics.high_risk_count
        ) / baseline_metrics.high_risk_count
        if high_risk_increase_ratio > thresholds.max_high_risk_count_increase_ratio:
            raise InjectionRegressionError(
                f"High-risk count regression detected: "
                f"baseline={baseline_metrics.high_risk_count}, "
                f"current={current_metrics.high_risk_count}, "
                f"increase_ratio={high_risk_increase_ratio:.3f} > threshold={thresholds.max_high_risk_count_increase_ratio:.3f}"
            )
    elif current_metrics.high_risk_count > 0:
        # New high-risk patterns when baseline had zero
        raise InjectionRegressionError(
            f"High-risk count regression detected: "
            f"baseline={baseline_metrics.high_risk_count}, "
            f"current={current_metrics.high_risk_count}, "
            f"new high-risk patterns introduced with zero baseline"
        )


def check_regression_compliance(
    current_metrics: dict[str, Any],
    baseline_metrics: dict[str, Any],
    thresholds: RegressionThresholds | None = None,
) -> bool:
    """Check if current metrics comply with baseline thresholds.

    Args:
        current_metrics: Current injection metrics
        baseline_metrics: Baseline injection metrics
        thresholds: Optional custom thresholds

    Returns:
        True if compliant (no regression), False otherwise
    """
    try:
        evaluate_against_baseline(current_metrics, baseline_metrics, thresholds)
        return True
    except InjectionRegressionError:
        return False
