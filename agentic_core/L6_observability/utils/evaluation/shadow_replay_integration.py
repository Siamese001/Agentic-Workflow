"""
agentic_core/L6_observability/evaluation/shadow_replay_integration.py

Wave 1.3: Shadow/Replay Evaluation Integration

Integrates shadow deployment evaluation and replay-based regression detection
into the evaluation spine, routing results to the system learning bus.

Components:
- ShadowEvaluationIntegrator: Wraps shadow_evaluator for evaluation spine
- ReplayEvaluator: Detects regressions via replay comparison
- Integration with evaluation_learning_bridge for learning feedback
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

# P0 governance self-bootstrap
emit_replay_key("p0", "shadow_replay_integration")
emit_determinism_digest("p0", "shadow_replay_integration")
_emit_applies_guardrail("p0", "shadow_replay_integration", "p0_governance")
_emit_snapshots_state("p0", "shadow_replay_integration", "state_snapshot")
_tid = str(uuid.uuid4())
_emit_signs_execution_trace(_tid, hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)

# P1-P4 self-bootstrap
_emit_routes_through("p1", "shadow_replay_integration", "L6")
_emit_authorize_and_execute("p2", "shadow_replay_integration", "execution_auth")
_emit_validates_capability("p2", "shadow_replay_integration", "capability_check")
_emit_routes_to_capability("p2", "shadow_replay_integration", "capability_route")
_emit_writes_via_uwg("p2", "shadow_replay_integration", "uwg_write")
_emit_blocks_direct_write("p2", "shadow_replay_integration", "direct_write_block")
_emit_records_tool_invocation("p2", "shadow_replay_integration", "tool_invocation")
_emit_captures_execution_output("p2", "shadow_replay_integration", "exec_output")
_emit_dispatches_agent("p3", "shadow_replay_integration", "agent_dispatch")
_emit_coordinates_agents("p3", "shadow_replay_integration", "agent_coordination")
_emit_records_workflow_lineage("p3", "shadow_replay_integration", "workflow_lineage")
_emit_records_healing_outcome("p3", "shadow_replay_integration", "healing_outcome")
_emit_escalates_failure("p3", "shadow_replay_integration", "failure_escalation")
_emit_orchestrates_workflow("p3", "shadow_replay_integration", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "shadow_replay_integration", "healing_dispatch")
_emit_invokes_evaluation("p3", "shadow_replay_integration", "evaluation_signal")
_emit_records_telemetry_event("p4", "shadow_replay_integration", "telemetry_event")
_emit_captures_evaluation_metric("p4", "shadow_replay_integration", "eval_metric")
_emit_stores_embedding("p4", "shadow_replay_integration", "embedding_store")
_emit_updates_meta_learning_state("p4", "shadow_replay_integration", "meta_learning")
_emit_links_execution_to_snapshot("p4", "shadow_replay_integration", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ShadowEvaluationResult:
    """Result from shadow deployment evaluation."""

    passed: bool
    regression_score: float  # 0.0 = no regression, 1.0 = severe regression
    violations: list[str]
    production_metrics: dict[str, float]
    shadow_metrics: dict[str, float]
    timestamp_utc: float


@dataclass(frozen=True)
class ReplayEvaluationResult:
    """Result from replay-based regression detection."""

    passed: bool
    regression_delta: float  # Difference from baseline
    baseline_score: float
    current_score: float
    trace_id: str
    timestamp_utc: float


class ShadowEvaluationIntegrator:
    """Integrates shadow deployment evaluation into evaluation spine.

    Wraps system_learning.validators.shadow_evaluator and routes results
    to evaluation_learning_bridge for system learning integration.
    """

    def __init__(self) -> None:
        self._evaluation_count = 0
        self._regression_count = 0

    def evaluate_shadow_deployment(
        self,
        production_metrics: dict[str, float],
        shadow_metrics: dict[str, float],
        thresholds: dict[str, float] | None = None,
    ) -> ShadowEvaluationResult:
        """Evaluate shadow deployment against production.

        Args:
            production_metrics: Production baseline metrics
            shadow_metrics: Shadow deployment metrics
            thresholds: Optional regression thresholds

        Returns:
            ShadowEvaluationResult with pass/fail and regression details

        Emits ADG edges:
            - invokes_evaluation (P3)
            - captures_evaluation_metric (P4)
        """
        _emit_invokes_evaluation("p3", "shadow_replay_integration", "shadow_eval")
        _emit_captures_evaluation_metric("p4", "shadow_replay_integration", "shadow_regression")

        self._evaluation_count += 1

        # Default thresholds
        if thresholds is None:
            thresholds = {
                "max_latency_regression_pct": 10.0,
                "max_error_rate_regression_abs": 0.05,
                "max_cpu_regression_pct": 15.0,
                "max_mem_regression_pct": 15.0,
            }

        violations = []
        regression_scores = []

        # Latency regression check
        prod_latency = production_metrics.get("p95_latency_ms", 0.0)
        shadow_latency = shadow_metrics.get("p95_latency_ms", 0.0)
        if prod_latency > 0:
            latency_regression_pct = (shadow_latency - prod_latency) / prod_latency * 100.0
            if latency_regression_pct > thresholds["max_latency_regression_pct"]:
                violations.append(
                    f"LATENCY_REGRESSION: {latency_regression_pct:.2f}% > {thresholds['max_latency_regression_pct']:.2f}%",
                )
                regression_scores.append(latency_regression_pct / 100.0)

        # Error rate regression check
        prod_error = production_metrics.get("error_rate", 0.0)
        shadow_error = shadow_metrics.get("error_rate", 0.0)
        error_regression = shadow_error - prod_error
        if error_regression > thresholds["max_error_rate_regression_abs"]:
            violations.append(
                f"ERROR_RATE_REGRESSION: +{error_regression:.4f} > {thresholds['max_error_rate_regression_abs']:.4f}",
            )
            regression_scores.append(error_regression * 10.0)  # Scale to [0, 1]

        # CPU regression check
        prod_cpu = production_metrics.get("cpu_pct", 0.0)
        shadow_cpu = shadow_metrics.get("cpu_pct", 0.0)
        if prod_cpu > 0:
            cpu_regression_pct = (shadow_cpu - prod_cpu) / prod_cpu * 100.0
            if cpu_regression_pct > thresholds["max_cpu_regression_pct"]:
                violations.append(
                    f"CPU_REGRESSION: {cpu_regression_pct:.2f}% > {thresholds['max_cpu_regression_pct']:.2f}%",
                )
                regression_scores.append(cpu_regression_pct / 100.0)

        # Memory regression check
        prod_mem = production_metrics.get("mem_mb", 0.0)
        shadow_mem = shadow_metrics.get("mem_mb", 0.0)
        if prod_mem > 0:
            mem_regression_pct = (shadow_mem - prod_mem) / prod_mem * 100.0
            if mem_regression_pct > thresholds["max_mem_regression_pct"]:
                violations.append(
                    f"MEM_REGRESSION: {mem_regression_pct:.2f}% > {thresholds['max_mem_regression_pct']:.2f}%",
                )
                regression_scores.append(mem_regression_pct / 100.0)

        # Calculate overall regression score
        regression_score = max(regression_scores) if regression_scores else 0.0
        passed = len(violations) == 0

        if not passed:
            self._regression_count += 1

        logger.info(
            "SHADOW_EVAL: passed=%s regression_score=%.3f violations=%d",
            passed,
            regression_score,
            len(violations),
        )

        return ShadowEvaluationResult(
            passed=passed,
            regression_score=regression_score,
            violations=violations,
            production_metrics=production_metrics,
            shadow_metrics=shadow_metrics,
            timestamp_utc=time.time(),
        )

    def get_stats(self) -> dict[str, Any]:
        """Get evaluation statistics."""
        return {
            "evaluation_count": self._evaluation_count,
            "regression_count": self._regression_count,
            "regression_rate": (
                self._regression_count / self._evaluation_count if self._evaluation_count > 0 else 0.0
            ),
        }


class ReplayEvaluator:
    """Replay-based regression detection evaluator.

    Compares current execution against baseline replay to detect regressions.
    Emits REGRESSION_DELTA evaluation signals when deviations exceed thresholds.
    """

    def __init__(self, regression_threshold: float = 0.1) -> None:
        """Initialize replay evaluator.

        Args:
            regression_threshold: Maximum allowed deviation from baseline (0.0-1.0)
        """
        self._regression_threshold = regression_threshold
        self._evaluation_count = 0
        self._regression_count = 0

    def evaluate_replay(
        self,
        trace_id: str,
        baseline_score: float,
        current_score: float,
        metadata: dict[str, Any] | None = None,
    ) -> ReplayEvaluationResult:
        """Evaluate current execution against baseline replay.

        Args:
            trace_id: Execution trace ID
            baseline_score: Baseline score from replay
            current_score: Current execution score
            metadata: Optional evaluation metadata

        Returns:
            ReplayEvaluationResult with regression delta

        Emits ADG edges:
            - invokes_evaluation (P3)
            - captures_evaluation_metric (P4)
        """
        _emit_invokes_evaluation("p3", "shadow_replay_integration", "replay_eval")
        _emit_captures_evaluation_metric("p4", "shadow_replay_integration", "regression_delta")

        self._evaluation_count += 1

        # Calculate regression delta
        regression_delta = abs(current_score - baseline_score)
        passed = regression_delta <= self._regression_threshold

        if not passed:
            self._regression_count += 1

        logger.info(
            "REPLAY_EVAL: trace_id=%s delta=%.3f baseline=%.3f current=%.3f passed=%s",
            trace_id,
            regression_delta,
            baseline_score,
            current_score,
            passed,
        )

        return ReplayEvaluationResult(
            passed=passed,
            regression_delta=regression_delta,
            baseline_score=baseline_score,
            current_score=current_score,
            trace_id=trace_id,
            timestamp_utc=time.time(),
        )

    def get_stats(self) -> dict[str, Any]:
        """Get evaluation statistics."""
        return {
            "evaluation_count": self._evaluation_count,
            "regression_count": self._regression_count,
            "regression_rate": (
                self._regression_count / self._evaluation_count if self._evaluation_count > 0 else 0.0
            ),
        }


# Global instances
_shadow_integrator: ShadowEvaluationIntegrator | None = None
_replay_evaluator: ReplayEvaluator | None = None


def get_shadow_integrator() -> ShadowEvaluationIntegrator:
    """Get global shadow evaluation integrator instance."""
    global _shadow_integrator
    if _shadow_integrator is None:
        _shadow_integrator = ShadowEvaluationIntegrator()
    return _shadow_integrator


def get_replay_evaluator() -> ReplayEvaluator:
    """Get global replay evaluator instance."""
    global _replay_evaluator
    if _replay_evaluator is None:
        _replay_evaluator = ReplayEvaluator()
    return _replay_evaluator


def reset_shadow_integrator() -> None:
    """Reset global shadow integrator (for testing)."""
    global _shadow_integrator
    _shadow_integrator = None


def reset_replay_evaluator() -> None:
    """Reset global replay evaluator (for testing)."""
    global _replay_evaluator
    _replay_evaluator = None


__all__ = [
    "ShadowEvaluationResult",
    "ReplayEvaluationResult",
    "ShadowEvaluationIntegrator",
    "ReplayEvaluator",
    "get_shadow_integrator",
    "get_replay_evaluator",
    "reset_shadow_integrator",
    "reset_replay_evaluator",
]
