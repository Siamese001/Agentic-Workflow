"""G-16-21: Shadow mode evaluator for System Learning validation.

Pure comparator for evaluating shadow deployments against production metrics.
Enforces regression thresholds and safety violation constraints.

Invariants:
  - No environment access; metrics are inputs
  - Deterministic comparisons only
  - Fail-closed on any regression
"""

from __future__ import annotations

from dataclasses import dataclass


class ShadowRegression(RuntimeError):
    """Raised when shadow deployment shows regression vs production."""


@dataclass(frozen=True, slots=True)
class ShadowMetrics:
    """Performance and safety metrics for a deployment.

    Fields
    ------
    p95_latency_ms : float
        95th percentile latency in milliseconds.
    error_rate : float
        Error rate (0.0 to 1.0).
    safety_violation_count : int
        Number of safety violations detected.
    cpu_pct : float
        CPU usage percentage.
    mem_mb : float
        Memory usage in megabytes.
    """

    p95_latency_ms: float
    error_rate: float
    safety_violation_count: int
    cpu_pct: float
    mem_mb: float


@dataclass(frozen=True, slots=True)
class ShadowThresholds:
    """Regression thresholds for shadow evaluation.

    Fields
    ------
    max_p95_latency_regression_pct : float
        Maximum allowed p95 latency regression as percentage (e.g., 10.0 = 10%).
    max_error_rate_regression_abs : float
        Maximum allowed error rate increase (absolute, e.g., 0.05 = 5pp).
    max_cpu_regression_pct : float
        Maximum allowed CPU regression as percentage.
    max_mem_regression_pct : float
        Maximum allowed memory regression as percentage.
    forbid_any_safety_violation_increase : bool
        If True, any increase in safety violations is rejected.
    """

    max_p95_latency_regression_pct: float
    max_error_rate_regression_abs: float
    max_cpu_regression_pct: float
    max_mem_regression_pct: float
    forbid_any_safety_violation_increase: bool


def evaluate_shadow(production: ShadowMetrics, shadow: ShadowMetrics, thresholds: ShadowThresholds) -> None:
    """Evaluate shadow deployment against production metrics.

    Fail-closed: raises ShadowRegression if any threshold is violated.

    Parameters
    ----------
    production : ShadowMetrics
        Production deployment metrics (baseline).
    shadow : ShadowMetrics
        Shadow deployment metrics (candidate).
    thresholds : ShadowThresholds
        Regression thresholds to enforce.

    Raises
    ------
    ShadowRegression
        If shadow shows regression beyond thresholds.

    Examples
    --------
    >>> prod = ShadowMetrics(p95_latency_ms=100, error_rate=0.01, safety_violation_count=0, cpu_pct=50, mem_mb=1000)
    >>> shadow = ShadowMetrics(p95_latency_ms=105, error_rate=0.015, safety_violation_count=0, cpu_pct=52, mem_mb=1020)
    >>> thresholds = ShadowThresholds(max_p95_latency_regression_pct=10.0, max_error_rate_regression_abs=0.01, max_cpu_regression_pct=10.0, max_mem_regression_pct=10.0, forbid_any_safety_violation_increase=True)
    >>> evaluate_shadow(prod, shadow, thresholds)  # Passes
    """
    violations = []
    if production.p95_latency_ms > 0:
        latency_regression_pct = (
            (shadow.p95_latency_ms - production.p95_latency_ms) / production.p95_latency_ms * 100.0
        )
        if latency_regression_pct > thresholds.max_p95_latency_regression_pct:
            violations.append(
                f"P95_LATENCY_REGRESSION: {latency_regression_pct:.2f}% (threshold: {thresholds.max_p95_latency_regression_pct:.2f}%)",
            )
    error_rate_regression = shadow.error_rate - production.error_rate
    if error_rate_regression > thresholds.max_error_rate_regression_abs:
        violations.append(
            f"ERROR_RATE_REGRESSION: +{error_rate_regression:.4f} (threshold: {thresholds.max_error_rate_regression_abs:.4f})",
        )
    if thresholds.forbid_any_safety_violation_increase:
        if shadow.safety_violation_count > production.safety_violation_count:
            violations.append(
                f"SAFETY_VIOLATION_INCREASE: {shadow.safety_violation_count} > {production.safety_violation_count} (any increase forbidden)",
            )
    if production.cpu_pct > 0:
        cpu_regression_pct = (shadow.cpu_pct - production.cpu_pct) / production.cpu_pct * 100.0
        if cpu_regression_pct > thresholds.max_cpu_regression_pct:
            violations.append(
                f"CPU_REGRESSION: {cpu_regression_pct:.2f}% (threshold: {thresholds.max_cpu_regression_pct:.2f}%)",
            )
    if production.mem_mb > 0:
        mem_regression_pct = (shadow.mem_mb - production.mem_mb) / production.mem_mb * 100.0
        if mem_regression_pct > thresholds.max_mem_regression_pct:
            violations.append(
                f"MEM_REGRESSION: {mem_regression_pct:.2f}% (threshold: {thresholds.max_mem_regression_pct:.2f}%)",
            )
    if violations:
        raise ShadowRegression(
            f"SHADOW_REGRESSION: {len(violations)} threshold(s) violated:\n"
            + "\n".join(f"  - {v}" for v in violations),
        )
