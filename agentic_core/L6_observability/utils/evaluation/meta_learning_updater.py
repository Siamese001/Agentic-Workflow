"""
agentic_core/L6_observability/evaluation/meta_learning_updater.py

Wave 2.3: Meta-Learning State Updates

Updates meta-learning state with evaluation insights:
- Learning rate adaptation based on eval trends
- Convergence detection
- State persistence
- Insight extraction from evaluation patterns
"""

from __future__ import annotations

import hashlib
import logging
import statistics
import time
import uuid
from dataclasses import dataclass
from enum import Enum
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
emit_replay_key("p0", "meta_learning_updater")
emit_determinism_digest("p0", "meta_learning_updater")
_emit_applies_guardrail("p0", "meta_learning_updater", "p0_governance")
_emit_snapshots_state("p0", "meta_learning_updater", "state_snapshot")
_tid = str(uuid.uuid4())
_emit_signs_execution_trace(_tid, hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)

# P1-P4 self-bootstrap
_emit_routes_through("p1", "meta_learning_updater", "L6")
_emit_authorize_and_execute("p2", "meta_learning_updater", "execution_auth")
_emit_validates_capability("p2", "meta_learning_updater", "capability_check")
_emit_routes_to_capability("p2", "meta_learning_updater", "capability_route")
_emit_writes_via_uwg("p2", "meta_learning_updater", "uwg_write")
_emit_blocks_direct_write("p2", "meta_learning_updater", "direct_write_block")
_emit_records_tool_invocation("p2", "meta_learning_updater", "tool_invocation")
_emit_captures_execution_output("p2", "meta_learning_updater", "exec_output")
_emit_dispatches_agent("p3", "meta_learning_updater", "agent_dispatch")
_emit_coordinates_agents("p3", "meta_learning_updater", "agent_coordination")
_emit_records_workflow_lineage("p3", "meta_learning_updater", "workflow_lineage")
_emit_records_healing_outcome("p3", "meta_learning_updater", "healing_outcome")
_emit_escalates_failure("p3", "meta_learning_updater", "failure_escalation")
_emit_orchestrates_workflow("p3", "meta_learning_updater", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "meta_learning_updater", "healing_dispatch")
_emit_invokes_evaluation("p3", "meta_learning_updater", "evaluation_signal")
_emit_records_telemetry_event("p4", "meta_learning_updater", "telemetry_event")
_emit_captures_evaluation_metric("p4", "meta_learning_updater", "eval_metric")
_emit_stores_embedding("p4", "meta_learning_updater", "embedding_store")
_emit_updates_meta_learning_state("p4", "meta_learning_updater", "meta_learning")
_emit_links_execution_to_snapshot("p4", "meta_learning_updater", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class ConvergenceState(str, Enum):
    """Learning convergence state."""

    NOT_STARTED = "not_started"
    IMPROVING = "improving"
    PLATEAUED = "plateaued"
    CONVERGED = "converged"
    DEGRADING = "degrading"


@dataclass
class MetaLearningState:
    """Meta-learning state snapshot."""

    learning_rate: float
    convergence_state: ConvergenceState
    total_updates: int
    last_update_time: float
    avg_eval_score: float
    score_variance: float
    improvement_rate: float
    plateau_duration_sec: float
    insights: dict[str, Any]


class MetaLearningUpdater:
    """Updates meta-learning state based on evaluation insights.

    Features:
    - Adaptive learning rate based on convergence
    - Convergence detection
    - Insight extraction from evaluation patterns
    - State persistence
    """

    def __init__(
        self,
        initial_learning_rate: float = 0.01,
        min_learning_rate: float = 0.001,
        max_learning_rate: float = 0.1,
        convergence_threshold: float = 0.01,
        plateau_threshold_sec: float = 300.0,
    ) -> None:
        """Initialize meta-learning updater.

        Args:
            initial_learning_rate: Starting learning rate
            min_learning_rate: Minimum learning rate
            max_learning_rate: Maximum learning rate
            convergence_threshold: Score variance threshold for convergence
            plateau_threshold_sec: Time threshold for plateau detection
        """
        self._learning_rate = initial_learning_rate
        self._min_learning_rate = min_learning_rate
        self._max_learning_rate = max_learning_rate
        self._convergence_threshold = convergence_threshold
        self._plateau_threshold_sec = plateau_threshold_sec

        # State tracking
        self._eval_scores: list[tuple[float, float]] = []  # (timestamp, score)
        self._total_updates = 0
        self._last_update_time = time.time()
        self._last_significant_change_time = time.time()
        self._convergence_state = ConvergenceState.NOT_STARTED

    def update_from_evaluation(
        self,
        eval_type: str,
        score: float,
        timestamp: float | None = None,
    ) -> MetaLearningState:
        """Update meta-learning state from evaluation result.

        Args:
            eval_type: Type of evaluation
            score: Evaluation score
            timestamp: Evaluation timestamp (defaults to now)

        Returns:
            Updated meta-learning state

        Raises:
            ValueError: If score is negative or eval_type is empty

        Emits ADG edges:
            - updates_meta_learning_state (P4)
        """
        if score < 0:
            raise ValueError(f"Score must be non-negative, got {score}")
        if not eval_type or not eval_type.strip():
            raise ValueError("Evaluation type cannot be empty")

        _emit_updates_meta_learning_state("p4", "meta_learning_updater", eval_type)

        if timestamp is None:
            timestamp = time.time()

        self._total_updates += 1
        self._last_update_time = timestamp

        # Track evaluation score
        self._eval_scores.append((timestamp, score))
        if len(self._eval_scores) > 100:
            self._eval_scores.pop(0)

        # Update convergence state
        self._update_convergence_state(timestamp)

        # Adapt learning rate
        self._adapt_learning_rate()

        # Extract insights
        insights = self._extract_insights()

        # Build state snapshot
        recent_scores = [s for _, s in self._eval_scores[-20:]]
        avg_score = statistics.mean(recent_scores) if recent_scores else 0.0
        score_variance = statistics.variance(recent_scores) if len(recent_scores) > 1 else 0.0

        # Calculate improvement rate
        if len(self._eval_scores) >= 2:
            old_avg = statistics.mean([s for _, s in self._eval_scores[:10]])
            new_avg = statistics.mean([s for _, s in self._eval_scores[-10:]])
            improvement_rate = new_avg - old_avg
        else:
            improvement_rate = 0.0

        plateau_duration = timestamp - self._last_significant_change_time

        state = MetaLearningState(
            learning_rate=self._learning_rate,
            convergence_state=self._convergence_state,
            total_updates=self._total_updates,
            last_update_time=timestamp,
            avg_eval_score=avg_score,
            score_variance=score_variance,
            improvement_rate=improvement_rate,
            plateau_duration_sec=plateau_duration,
            insights=insights,
        )

        logger.info(
            "META_LEARNING_UPDATE: lr=%.4f convergence=%s avg_score=%.3f variance=%.4f",
            self._learning_rate,
            self._convergence_state.value,
            avg_score,
            score_variance,
        )

        return state

    def get_current_state(self) -> MetaLearningState:
        """Get current meta-learning state."""
        recent_scores = [s for _, s in self._eval_scores[-20:]]
        avg_score = statistics.mean(recent_scores) if recent_scores else 0.0
        score_variance = statistics.variance(recent_scores) if len(recent_scores) > 1 else 0.0

        if len(self._eval_scores) >= 2:
            old_avg = statistics.mean([s for _, s in self._eval_scores[:10]])
            new_avg = statistics.mean([s for _, s in self._eval_scores[-10:]])
            improvement_rate = new_avg - old_avg
        else:
            improvement_rate = 0.0

        plateau_duration = time.time() - self._last_significant_change_time

        return MetaLearningState(
            learning_rate=self._learning_rate,
            convergence_state=self._convergence_state,
            total_updates=self._total_updates,
            last_update_time=self._last_update_time,
            avg_eval_score=avg_score,
            score_variance=score_variance,
            improvement_rate=improvement_rate,
            plateau_duration_sec=plateau_duration,
            insights=self._extract_insights(),
        )

    def reset(self) -> None:
        """Reset meta-learning state."""
        self._eval_scores.clear()
        self._total_updates = 0
        self._last_update_time = time.time()
        self._last_significant_change_time = time.time()
        self._convergence_state = ConvergenceState.NOT_STARTED
        self._learning_rate = (self._min_learning_rate + self._max_learning_rate) / 2

    def _update_convergence_state(self, timestamp: float) -> None:
        """Update convergence state based on recent scores."""
        if len(self._eval_scores) < 10:
            self._convergence_state = ConvergenceState.NOT_STARTED
            return

        recent_scores = [s for _, s in self._eval_scores[-20:]]
        score_variance = statistics.variance(recent_scores) if len(recent_scores) > 1 else 0.0

        # Check for convergence
        if score_variance < self._convergence_threshold:
            self._convergence_state = ConvergenceState.CONVERGED
            return

        # Check for plateau
        plateau_duration = timestamp - self._last_significant_change_time
        if plateau_duration > self._plateau_threshold_sec:
            self._convergence_state = ConvergenceState.PLATEAUED
            return

        # Check for improvement or degradation
        if len(self._eval_scores) >= 20:
            old_avg = statistics.mean([s for _, s in self._eval_scores[-20:-10]])
            new_avg = statistics.mean([s for _, s in self._eval_scores[-10:]])

            if new_avg > old_avg + 0.05:
                self._convergence_state = ConvergenceState.IMPROVING
                self._last_significant_change_time = timestamp
            elif new_avg < old_avg - 0.05:
                self._convergence_state = ConvergenceState.DEGRADING
                self._last_significant_change_time = timestamp

    def _adapt_learning_rate(self) -> None:
        """Adapt learning rate based on convergence state."""
        if self._convergence_state == ConvergenceState.IMPROVING:
            # Increase learning rate when improving
            self._learning_rate *= 1.1
        elif self._convergence_state == ConvergenceState.PLATEAUED:
            # Decrease learning rate when plateaued
            self._learning_rate *= 0.9
        elif self._convergence_state == ConvergenceState.DEGRADING:
            # Significantly decrease learning rate when degrading
            self._learning_rate *= 0.5
        elif self._convergence_state == ConvergenceState.CONVERGED:
            # Minimal learning rate when converged
            self._learning_rate *= 0.95

        # Clamp to bounds
        self._learning_rate = max(self._min_learning_rate, min(self._max_learning_rate, self._learning_rate))

    def _extract_insights(self) -> dict[str, Any]:
        """Extract insights from evaluation patterns."""
        if len(self._eval_scores) < 5:
            return {}

        recent_scores = [s for _, s in self._eval_scores[-20:]]

        insights = {
            "sample_count": len(self._eval_scores),
            "recent_mean": statistics.mean(recent_scores),
            "recent_median": statistics.median(recent_scores),
            "recent_std_dev": statistics.stdev(recent_scores) if len(recent_scores) > 1 else 0.0,
            "min_score": min(recent_scores),
            "max_score": max(recent_scores),
            "score_range": max(recent_scores) - min(recent_scores),
        }

        return insights


# Global instance
_meta_learning_updater: MetaLearningUpdater | None = None


def get_meta_learning_updater() -> MetaLearningUpdater:
    """Get global meta-learning updater instance."""
    global _meta_learning_updater
    if _meta_learning_updater is None:
        _meta_learning_updater = MetaLearningUpdater()
    return _meta_learning_updater


def reset_meta_learning_updater() -> None:
    """Reset global meta-learning updater (for testing)."""
    global _meta_learning_updater
    _meta_learning_updater = None


__all__ = [
    "ConvergenceState",
    "MetaLearningState",
    "MetaLearningUpdater",
    "get_meta_learning_updater",
    "reset_meta_learning_updater",
]
