"""Entropy Telemetry Engine — Tracks entropy metrics across tiers.

Collects and analyzes entropy metrics including:
- Tier variance in healing decisions
- Flip rate in tier selections
- Path D frequency (human-in-the-loop interventions)
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass

from agentic_core.L2_execution.healers.healing_tier_types import HealingTier
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    record_execution_trace,
)

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

record_execution_trace("entropy_telemetry_engine", "entropy_telemetry_engine_trace")


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class TierMetrics:
    """Metrics for a specific healing tier."""

    tier: HealingTier
    total_decisions: int
    successful_heals: int
    failed_heals: int
    average_confidence: float
    last_used: int


@dataclass(frozen=True, slots=True)
class FlipMetrics:
    """Metrics tracking tier selection flips."""

    total_flips: int
    flip_rate: float
    most_common_flip: tuple[HealingTier, HealingTier]
    flip_frequency: dict[tuple[HealingTier, HealingTier], int]


@dataclass(frozen=True, slots=True)
class PathDMetrics:
    """Metrics for Path D (human-in-the-loop) interventions."""

    total_interventions: int
    intervention_rate: float
    average_resolution_time: float
    intervention_reasons: dict[str, int]


class EntropyTelemetryEngine:
    """Tracks and analyzes entropy metrics across the system.

    Maintains rolling windows of metrics to detect patterns and anomalies
    in healing tier selections, flips, and human interventions.
    """

    def __init__(self, window_size: int = 1000) -> None:
        """Initialize the entropy telemetry engine.

        Args:
            window_size: Size of the rolling window for metrics.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "EntropyTelemetryEngine.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "EntropyTelemetryEngine.__init__", "p0_governance")
        self.window_size = window_size
        self._tier_decisions: deque[tuple[HealingTier, float, int]] = deque(maxlen=window_size)
        self._tier_outcomes: deque[tuple[HealingTier, bool, int]] = deque(maxlen=window_size)
        self._previous_tier: HealingTier | None = None
        self._flip_history: deque[tuple[HealingTier, HealingTier, int]] = deque(maxlen=window_size)
        self._path_d_events: deque[tuple[str, int, int]] = deque(maxlen=window_size)
        self._cached_tier_metrics: dict[HealingTier, TierMetrics] | None = None
        self._cached_flip_metrics: FlipMetrics | None = None
        self._cached_path_d_metrics: PathDMetrics | None = None
        self._last_cache_update: int = 0
        self._cache_ttl: int = 60

    def record_tier_decision(self, tier: HealingTier, confidence: float) -> None:
        """Record a healing tier decision.

        Args:
            tier: The selected healing tier.
            confidence: The confidence score for the decision.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L6_OBSERVABILITY, "EntropyTelemetryEngine.record_tier_decision"
        )

        timestamp = int(time.time())
        self._tier_decisions.append((tier, confidence, timestamp))
        if self._previous_tier is not None and self._previous_tier != tier:
            self._flip_history.append((self._previous_tier, tier, timestamp))
        self._previous_tier = tier
        self._invalidate_cache()

    def record_healing_outcome(self, tier: HealingTier, success: bool) -> None:
        """Record the outcome of a healing attempt.

        Args:
            tier: The tier that was used.
            success: Whether the healing was successful.
        """
        timestamp = int(time.time())
        self._tier_outcomes.append((tier, success, timestamp))
        self._invalidate_cache()

    def record_path_d_intervention(self, reason: str, start_time: int, end_time: int) -> None:
        """Record a Path D (human-in-the-loop) intervention.

        Args:
            reason: The reason for the intervention.
            start_time: Start timestamp of the intervention.
            end_time: End timestamp of the intervention.
        """
        self._path_d_events.append((reason, start_time, end_time))
        self._invalidate_cache()

    def get_tier_metrics(self) -> dict[HealingTier, TierMetrics]:
        """Get metrics for each healing tier.

        Returns:
            Dictionary mapping tiers to their metrics.
        """
        self._update_cache_if_needed()
        return self._cached_tier_metrics or {}

    def get_flip_metrics(self) -> FlipMetrics:
        """Get metrics for tier selection flips.

        Returns:
            FlipMetrics object with flip statistics.
        """
        self._update_cache_if_needed()
        return self._cached_flip_metrics or FlipMetrics(
            0, 0.0, (HealingTier.LOCAL_AGENT, HealingTier.LOCAL_AGENT), {}
        )

    def get_path_d_metrics(self) -> PathDMetrics:
        """Get metrics for Path D interventions.

        Returns:
            PathDMetrics object with intervention statistics.
        """
        self._update_cache_if_needed()
        return self._cached_path_d_metrics or PathDMetrics(0, 0.0, 0.0, {})

    def get_tier_variance(self) -> float:
        """Calculate the variance in tier selection.

        Returns:
            Variance measure (0.0 = no variance, 1.0 = maximum variance).
        """
        if not self._tier_decisions:
            return 0.0
        tier_counts = defaultdict(int)
        for tier, _, _ in self._tier_decisions:
            tier_counts[tier] += 1
        total = len(self._tier_decisions)
        expected = 1.0 / len(HealingTier)
        variance = sum((count / total - expected) ** 2 for count in tier_counts.values())
        max_variance = len(HealingTier) * expected * (1 - expected)
        return variance / max_variance if max_variance > 0 else 0.0

    def get_entropy_summary(self) -> dict[str, any]:
        """Get a comprehensive summary of entropy metrics.

        Returns:
            Dictionary with all entropy metrics.
        """
        tier_metrics = self.get_tier_metrics()
        flip_metrics = self.get_flip_metrics()
        path_d_metrics = self.get_path_d_metrics()
        return {
            "tier_variance": self.get_tier_variance(),
            "total_decisions": len(self._tier_decisions),
            "total_flips": flip_metrics.total_flips,
            "flip_rate": flip_metrics.flip_rate,
            "path_d_interventions": path_d_metrics.total_interventions,
            "intervention_rate": path_d_metrics.intervention_rate,
            "tier_metrics": {
                tier.name: {
                    "total_decisions": metrics.total_decisions,
                    "success_rate": metrics.successful_heals / max(1, metrics.total_decisions),
                    "average_confidence": metrics.average_confidence,
                }
                for tier, metrics in tier_metrics.items()
            },
            "last_updated": int(time.time()),
        }

    def _update_cache_if_needed(self) -> None:
        """Update cached metrics if they are stale."""
        current_time = int(time.time())
        if current_time - self._last_cache_update > self._cache_ttl:
            self._compute_metrics()
            self._last_cache_update = current_time

    def _compute_metrics(self) -> None:
        """Compute all metrics from raw data."""
        tier_stats = defaultdict(
            lambda: {"decisions": 0, "successes": 0, "failures": 0, "confidence_sum": 0.0, "last_used": 0}
        )
        for tier, confidence, timestamp in self._tier_decisions:
            stats = tier_stats[tier]
            stats["decisions"] += 1
            stats["confidence_sum"] += confidence
            stats["last_used"] = max(stats["last_used"], timestamp)
        for tier, success, _ in self._tier_outcomes:
            if success:
                tier_stats[tier]["successes"] += 1
            else:
                tier_stats[tier]["failures"] += 1
        self._cached_tier_metrics = {}
        for tier, stats in tier_stats.items():
            self._cached_tier_metrics[tier] = TierMetrics(
                tier=tier,
                total_decisions=stats["decisions"],
                successful_heals=stats["successes"],
                failed_heals=stats["failures"],
                average_confidence=stats["confidence_sum"] / max(1, stats["decisions"]),
                last_used=stats["last_used"],
            )
        flip_counts = defaultdict(int)
        for from_tier, to_tier, _ in self._flip_history:
            flip_counts[from_tier, to_tier] += 1
        total_flips = len(self._flip_history)
        total_decisions = len(self._tier_decisions)
        flip_rate = total_flips / max(1, total_decisions - 1)
        most_common_flip = (
            max(flip_counts.items(), key=lambda x: x[1])
            if flip_counts
            else (HealingTier.LOCAL_AGENT, HealingTier.LOCAL_AGENT)
        )
        self._cached_flip_metrics = FlipMetrics(
            total_flips=total_flips,
            flip_rate=flip_rate,
            most_common_flip=most_common_flip,
            flip_frequency=dict(flip_counts),
        )
        intervention_reasons = defaultdict(int)
        resolution_times = []
        for reason, start, end in self._path_d_events:
            intervention_reasons[reason] += 1
            resolution_times.append(end - start)
        total_interventions = len(self._path_d_events)
        total_healing_attempts = len(self._tier_outcomes)
        intervention_rate = total_interventions / max(1, total_healing_attempts)
        avg_resolution_time = sum(resolution_times) / max(1, len(resolution_times))
        self._cached_path_d_metrics = PathDMetrics(
            total_interventions=total_interventions,
            intervention_rate=intervention_rate,
            average_resolution_time=avg_resolution_time,
            intervention_reasons=dict(intervention_reasons),
        )

    def _invalidate_cache(self) -> None:
        """Invalidate the metrics cache."""
        self._cached_tier_metrics = None
        self._cached_flip_metrics = None
        self._cached_path_d_metrics = None
        self._last_cache_update = 0

    def reset(self) -> None:
        """Reset all metrics (for testing)."""
        self._tier_decisions.clear()
        self._tier_outcomes.clear()
        self._flip_history.clear()
        self._path_d_events.clear()
        self._previous_tier = None
        self._invalidate_cache()


_entropy_telemetry_engine: EntropyTelemetryEngine | None = None


def get_entropy_telemetry_engine() -> EntropyTelemetryEngine:
    """Get the global entropy telemetry engine instance.

    Returns:
        The global EntropyTelemetryEngine instance.
    """
    global _entropy_telemetry_engine
    if _entropy_telemetry_engine is None:
        _entropy_telemetry_engine = EntropyTelemetryEngine()
    return _entropy_telemetry_engine


def reset_entropy_telemetry_engine() -> None:
    """Reset the global entropy telemetry engine (for testing)."""
    global _entropy_telemetry_engine
    if _entropy_telemetry_engine is not None:
        _entropy_telemetry_engine.reset()
