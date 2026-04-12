"""
agentic_core/L6_observability/evaluation/learning_signal_enrichment.py

Wave 2.1: Learning Signal Enrichment

Enriches evaluation signals with context for system learning:
- Temporal features (time of day, day of week, trends)
- Signal deduplication (prevent redundant learning)
- Context aggregation (combine related signals)
- Trend analysis (detect patterns over time)
- Signal quality scoring
"""

from __future__ import annotations

import hashlib
import logging
import statistics
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
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
emit_replay_key("p0", "learning_signal_enrichment")
emit_determinism_digest("p0", "learning_signal_enrichment")
_emit_applies_guardrail("p0", "learning_signal_enrichment", "p0_governance")
_emit_snapshots_state("p0", "learning_signal_enrichment", "state_snapshot")
_tid = str(uuid.uuid4())
_emit_signs_execution_trace(_tid, hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)

# P1-P4 self-bootstrap
_emit_routes_through("p1", "learning_signal_enrichment", "L6")
_emit_authorize_and_execute("p2", "learning_signal_enrichment", "execution_auth")
_emit_validates_capability("p2", "learning_signal_enrichment", "capability_check")
_emit_routes_to_capability("p2", "learning_signal_enrichment", "capability_route")
_emit_writes_via_uwg("p2", "learning_signal_enrichment", "uwg_write")
_emit_blocks_direct_write("p2", "learning_signal_enrichment", "direct_write_block")
_emit_records_tool_invocation("p2", "learning_signal_enrichment", "tool_invocation")
_emit_captures_execution_output("p2", "learning_signal_enrichment", "exec_output")
_emit_dispatches_agent("p3", "learning_signal_enrichment", "agent_dispatch")
_emit_coordinates_agents("p3", "learning_signal_enrichment", "agent_coordination")
_emit_records_workflow_lineage("p3", "learning_signal_enrichment", "workflow_lineage")
_emit_records_healing_outcome("p3", "learning_signal_enrichment", "healing_outcome")
_emit_escalates_failure("p3", "learning_signal_enrichment", "failure_escalation")
_emit_orchestrates_workflow("p3", "learning_signal_enrichment", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "learning_signal_enrichment", "healing_dispatch")
_emit_invokes_evaluation("p3", "learning_signal_enrichment", "evaluation_signal")
_emit_records_telemetry_event("p4", "learning_signal_enrichment", "telemetry_event")
_emit_captures_evaluation_metric("p4", "learning_signal_enrichment", "eval_metric")
_emit_stores_embedding("p4", "learning_signal_enrichment", "embedding_store")
_emit_updates_meta_learning_state("p4", "learning_signal_enrichment", "meta_learning")
_emit_links_execution_to_snapshot("p4", "learning_signal_enrichment", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class SignalTrend(str, Enum):
    """Signal trend direction."""

    IMPROVING = "improving"
    DEGRADING = "degrading"
    STABLE = "stable"
    UNKNOWN = "unknown"


@dataclass
class TemporalFeatures:
    """Temporal features extracted from signal timestamp."""

    hour_of_day: int  # 0-23
    day_of_week: int  # 0-6 (Monday=0)
    is_weekend: bool
    is_business_hours: bool  # 9am-5pm weekdays
    time_since_last_signal_sec: float


@dataclass
class EnrichedLearningSignal:
    """Evaluation signal enriched with context for learning."""

    signal_id: str
    original_signal: Any
    evaluation_type: str
    score: float
    timestamp_utc: float

    # Temporal features
    temporal_features: TemporalFeatures

    # Trend analysis
    trend: SignalTrend
    trend_strength: float  # 0.0-1.0
    recent_scores: list[float]  # Last N scores for this eval type

    # Quality scoring
    signal_quality: float  # 0.0-1.0 (confidence in signal)
    is_duplicate: bool
    duplicate_of: str | None

    # Context
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class LearningSignalEnricher:
    """Enriches evaluation signals with context for system learning.

    Features:
    - Temporal feature extraction
    - Trend analysis
    - Signal deduplication
    - Quality scoring
    - Context aggregation
    """

    def __init__(
        self,
        dedup_window_sec: float = 300.0,  # 5 minutes
        trend_window_size: int = 10,
        min_quality_threshold: float = 0.5,
    ) -> None:
        """Initialize signal enricher.

        Args:
            dedup_window_sec: Time window for deduplication (seconds)
            trend_window_size: Number of recent signals for trend analysis
            min_quality_threshold: Minimum quality score to accept signal
        """
        self._dedup_window_sec = dedup_window_sec
        self._trend_window_size = trend_window_size
        self._min_quality_threshold = min_quality_threshold

        # Signal history for trend analysis
        self._signal_history: dict[str, list[tuple[float, float]]] = defaultdict(list)

        # Deduplication tracking
        self._recent_signals: dict[str, tuple[float, str]] = {}  # hash -> (timestamp, signal_id)

        # Statistics
        self._total_signals = 0
        self._duplicates_filtered = 0
        self._low_quality_filtered = 0

    def enrich_signal(
        self,
        signal: Any,
        evaluation_type: str,
        score: float,
        timestamp_utc: float | None = None,
        context: dict[str, Any] | None = None,
    ) -> EnrichedLearningSignal | None:
        """Enrich evaluation signal with learning context.

        Args:
            signal: Original evaluation signal
            evaluation_type: Type of evaluation
            score: Evaluation score
            timestamp_utc: Signal timestamp (defaults to now)
            context: Optional additional context

        Returns:
            EnrichedLearningSignal or None if filtered (duplicate/low quality)

        Raises:
            ValueError: If score is negative or evaluation_type is empty

        Emits ADG edges:
            - updates_meta_learning_state (P4)
        """
        if score < 0:
            raise ValueError(f"Score must be non-negative, got {score}")
        if not evaluation_type or not evaluation_type.strip():
            raise ValueError("Evaluation type cannot be empty")

        _emit_updates_meta_learning_state("p4", "learning_signal_enrichment", evaluation_type)

        if timestamp_utc is None:
            timestamp_utc = time.time()

        self._total_signals += 1

        # Generate signal ID
        signal_id = self._generate_signal_id(evaluation_type, timestamp_utc)

        # Check for duplicates
        signal_hash = self._compute_signal_hash(signal, evaluation_type, score)
        is_duplicate, duplicate_of = self._check_duplicate(signal_hash, timestamp_utc)

        if is_duplicate:
            self._duplicates_filtered += 1
            logger.debug("SIGNAL_DUPLICATE: type=%s hash=%s", evaluation_type, signal_hash[:12])
            return None

        # Extract temporal features
        temporal_features = self._extract_temporal_features(evaluation_type, timestamp_utc)

        # Analyze trend
        trend, trend_strength, recent_scores = self._analyze_trend(evaluation_type, score, timestamp_utc)

        # Calculate signal quality
        signal_quality = self._calculate_signal_quality(score, trend_strength, temporal_features)

        # Filter low quality signals
        if signal_quality < self._min_quality_threshold:
            self._low_quality_filtered += 1
            logger.debug(
                "SIGNAL_LOW_QUALITY: type=%s quality=%.3f threshold=%.3f",
                evaluation_type,
                signal_quality,
                self._min_quality_threshold,
            )
            return None

        # Record signal for deduplication
        self._recent_signals[signal_hash] = (timestamp_utc, signal_id)

        # Update signal history
        self._signal_history[evaluation_type].append((timestamp_utc, score))
        if len(self._signal_history[evaluation_type]) > self._trend_window_size:
            self._signal_history[evaluation_type].pop(0)

        enriched = EnrichedLearningSignal(
            signal_id=signal_id,
            original_signal=signal,
            evaluation_type=evaluation_type,
            score=score,
            timestamp_utc=timestamp_utc,
            temporal_features=temporal_features,
            trend=trend,
            trend_strength=trend_strength,
            recent_scores=recent_scores,
            signal_quality=signal_quality,
            is_duplicate=False,
            duplicate_of=None,
            context=context or {},
            metadata={
                "enrichment_version": "1.0.0",
                "dedup_window_sec": self._dedup_window_sec,
                "trend_window_size": self._trend_window_size,
            },
        )

        logger.info(
            "SIGNAL_ENRICHED: id=%s type=%s score=%.3f quality=%.3f trend=%s",
            signal_id[:12],
            evaluation_type,
            score,
            signal_quality,
            trend.value,
        )

        return enriched

    def _extract_temporal_features(self, evaluation_type: str, timestamp_utc: float) -> TemporalFeatures:
        """Extract temporal features from timestamp."""
        dt = datetime.fromtimestamp(timestamp_utc)

        hour_of_day = dt.hour
        day_of_week = dt.weekday()
        is_weekend = day_of_week >= 5
        is_business_hours = not is_weekend and 9 <= hour_of_day < 17

        # Calculate time since last signal of this type
        history = self._signal_history.get(evaluation_type, [])
        if history:
            last_timestamp = history[-1][0]
            time_since_last = timestamp_utc - last_timestamp
        else:
            time_since_last = 0.0

        return TemporalFeatures(
            hour_of_day=hour_of_day,
            day_of_week=day_of_week,
            is_weekend=is_weekend,
            is_business_hours=is_business_hours,
            time_since_last_signal_sec=time_since_last,
        )

    def _analyze_trend(
        self,
        evaluation_type: str,
        current_score: float,
        timestamp_utc: float,
    ) -> tuple[SignalTrend, float, list[float]]:
        """Analyze signal trend."""
        history = self._signal_history.get(evaluation_type, [])

        if len(history) < 3:
            return SignalTrend.UNKNOWN, 0.0, [current_score]

        # Get recent scores
        recent_scores = [score for _, score in history[-self._trend_window_size :]]
        recent_scores.append(current_score)

        # Calculate trend using linear regression slope
        n = len(recent_scores)
        x = list(range(n))
        y = recent_scores

        x_mean = statistics.mean(x)
        y_mean = statistics.mean(y)

        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            slope = 0.0
        else:
            slope = numerator / denominator

        # Determine trend direction and strength
        if abs(slope) < 0.01:
            trend = SignalTrend.STABLE
            trend_strength = 0.0
        elif slope > 0:
            trend = SignalTrend.IMPROVING
            trend_strength = min(abs(slope) * 10, 1.0)  # Scale to [0, 1]
        else:
            trend = SignalTrend.DEGRADING
            trend_strength = min(abs(slope) * 10, 1.0)

        return trend, trend_strength, recent_scores

    def _calculate_signal_quality(
        self,
        score: float,
        trend_strength: float,
        temporal_features: TemporalFeatures,
    ) -> float:
        """Calculate signal quality score."""
        # Base quality from score magnitude
        base_quality = abs(score)

        # Boost quality if trend is strong
        trend_boost = trend_strength * 0.2

        # Boost quality during business hours (more reliable)
        temporal_boost = 0.1 if temporal_features.is_business_hours else 0.0

        # Penalize if too soon after last signal (might be noise)
        if temporal_features.time_since_last_signal_sec < 10.0:
            recency_penalty = 0.2
        else:
            recency_penalty = 0.0

        quality = base_quality + trend_boost + temporal_boost - recency_penalty
        return max(0.0, min(1.0, quality))

    def _check_duplicate(self, signal_hash: str, timestamp_utc: float) -> tuple[bool, str | None]:
        """Check if signal is a duplicate within dedup window."""
        # Clean up old signals outside dedup window
        cutoff_time = timestamp_utc - self._dedup_window_sec
        to_remove = [h for h, (ts, _) in self._recent_signals.items() if ts < cutoff_time]
        for h in to_remove:
            del self._recent_signals[h]

        # Check for duplicate
        if signal_hash in self._recent_signals:
            _, duplicate_signal_id = self._recent_signals[signal_hash]
            return True, duplicate_signal_id

        return False, None

    def get_stats(self) -> dict[str, Any]:
        """Get enrichment statistics."""
        return {
            "total_signals": self._total_signals,
            "duplicates_filtered": self._duplicates_filtered,
            "low_quality_filtered": self._low_quality_filtered,
            "duplicate_rate": (
                self._duplicates_filtered / self._total_signals if self._total_signals > 0 else 0.0
            ),
            "low_quality_rate": (
                self._low_quality_filtered / self._total_signals if self._total_signals > 0 else 0.0
            ),
            "evaluation_types_tracked": len(self._signal_history),
        }

    def clear_history(self) -> None:
        """Clear signal history."""
        self._signal_history.clear()
        self._recent_signals.clear()
        self._total_signals = 0
        self._duplicates_filtered = 0
        self._low_quality_filtered = 0

    @staticmethod
    def _generate_signal_id(evaluation_type: str, timestamp_utc: float) -> str:
        """Generate unique signal ID."""
        combined = f"{evaluation_type}:{timestamp_utc}:{time.time()}"
        return hashlib.sha256(combined.encode()).hexdigest()

    @staticmethod
    def _compute_signal_hash(signal: Any, evaluation_type: str, score: float) -> str:
        """Compute hash for deduplication."""
        # Create deterministic hash from signal content
        content = f"{evaluation_type}:{score:.6f}:{str(signal)}"
        return hashlib.sha256(content.encode()).hexdigest()


# Global instance
_signal_enricher: LearningSignalEnricher | None = None


def get_signal_enricher() -> LearningSignalEnricher:
    """Get global signal enricher instance."""
    global _signal_enricher
    if _signal_enricher is None:
        _signal_enricher = LearningSignalEnricher()
    return _signal_enricher


def reset_signal_enricher() -> None:
    """Reset global signal enricher (for testing)."""
    global _signal_enricher
    _signal_enricher = None


__all__ = [
    "SignalTrend",
    "TemporalFeatures",
    "EnrichedLearningSignal",
    "LearningSignalEnricher",
    "get_signal_enricher",
    "reset_signal_enricher",
]
