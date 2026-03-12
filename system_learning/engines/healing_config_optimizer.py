"""Healing Config Optimizer - Threshold adjustment proposals.

Phase 6: Consumes healing outcome aggregates to propose threshold adjustments.
All proposals are proposal-only via ChangePackage; no direct config mutation.
W2: Embedding-augmented scoring (C0-only, informational). Final closeout.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
    HealingOutcomeAggregateSnapshot,
)
from system_learning.types.pattern_analysis_types import (
    PatternFindingReport,
)


class HealingConfigOptimizer:
    """Optimizer for healing tier thresholds based on outcome aggregates.

    Consumes HealingOutcomeAggregateSnapshot and produces deterministic
    threshold adjustment proposals. All changes are proposal-only.
    """

    # guardian: allow-magic-config
    def __init__(
        self,
        min_sample_size: int = 20,
        low_success_rate_threshold: float = 0.5,
        escalation_delta: float = 0.1,
        max_threshold: float = 2.0,
        max_delta: float = 0.2,  # Maximum delta per run for bounded adjustments
    ) -> None:
        """Initialize optimizer with deterministic parameters.

        Args:
            min_sample_size: Minimum sample size for reliable statistics.
            low_success_rate_threshold: Success rate below which escalation is considered.
            escalation_delta: Fixed delta to add to threshold when escalating.
            max_threshold: Maximum allowed threshold value.
            max_delta: Maximum delta per run for bounded adjustments.
        """
        if min_sample_size < 1:
            raise ValueError("min_sample_size must be >= 1")
        if not 0.0 <= low_success_rate_threshold <= 1.0:
            raise ValueError("low_success_rate_threshold must be in [0.0, 1.0]")
        if escalation_delta <= 0:
            raise ValueError("escalation_delta must be > 0")
        if max_threshold <= 0:
            raise ValueError("max_threshold must be > 0")
        if max_delta <= 0:
            raise ValueError("max_delta must be > 0")

        self._min_sample_size = min_sample_size
        self._low_success_rate_threshold = low_success_rate_threshold
        self._escalation_delta = escalation_delta
        self._max_threshold = max_threshold
        self._max_delta = max_delta

    def create_snapshot_from_intake(self, intake_record, created_utc: int) -> HealingOutcomeAggregateSnapshot:
        """Create aggregate snapshot from healing outcome intake record.

        Args:
            intake_record: Healing outcome intake record.
            created_utc: Timestamp for the snapshot.

        Returns:
            Aggregate snapshot for threshold optimization.
        """
        # Convert intake snapshot to aggregate format
        aggregate_pairs = []

        if hasattr(intake_record, "snapshot"):
            for stats in intake_record.snapshot:
                key = HealingOutcomeAggregateKey(
                    healer_name=stats.healer_id, tier=stats.tier, failure_type=stats.failure_type
                )
                aggregate = HealingOutcomeAggregate(
                    success_count=stats.success_count,
                    failure_count=stats.failure_count,
                    total_count=stats.total_count,
                )
                aggregate_pairs.append((key, aggregate))

        # Sort deterministically
        aggregate_pairs.sort(key=lambda pair: (pair[0].healer_name, pair[0].tier, pair[0].failure_type))

        # Create temporary snapshot to compute hash
        temp_snapshot = HealingOutcomeAggregateSnapshot(
            version_id="temp",  # Temporary value
            created_utc=created_utc,
            aggregates=tuple(aggregate_pairs),
        )

        # Compute version_id as hash of content
        version_id = temp_snapshot.content_hash()

        # Create final snapshot with correct version_id
        snapshot = HealingOutcomeAggregateSnapshot(
            version_id=version_id, created_utc=created_utc, aggregates=tuple(aggregate_pairs)
        )

        return snapshot

    def propose_threshold_adjustments(
        self,
        snapshot: HealingOutcomeAggregateSnapshot,
        embedding_metadata: dict[str, Any] | None = None,
    ) -> ThresholdAdjustmentProposal:
        """Analyze snapshot and propose threshold adjustments.

        Args:
            snapshot: Healing outcome aggregate snapshot.

        Returns:
            Proposal with threshold adjustments (proposal-only).
        """
        adjustments = []

        for key, aggregate in snapshot.aggregates:
            # Check if we have enough data
            if aggregate.total_count < self._min_sample_size:
                continue

            # Check if success rate is below threshold
            if aggregate.success_rate < self._low_success_rate_threshold:
                # Propose escalation
                current_threshold = self._get_current_threshold(key)
                new_threshold = min(current_threshold + self._escalation_delta, self._max_threshold)

                if new_threshold != current_threshold:
                    adjustment = ThresholdAdjustment(
                        healer_name=key.healer_name,
                        tier=key.tier,
                        failure_type=key.failure_type,
                        current_threshold=current_threshold,
                        proposed_threshold=new_threshold,
                        reason=(
                            f"Success rate {aggregate.success_rate:.4f} "
                            f"< {self._low_success_rate_threshold} "
                            f"with {aggregate.total_count} samples"
                        ),
                        confidence=self._compute_confidence(aggregate),
                    )
                    adjustments.append(adjustment)

        # Sort adjustments deterministically
        adjustments.sort(key=lambda a: (a.healer_name, a.tier, a.failure_type, a.proposed_threshold))

        return ThresholdAdjustmentProposal(
            snapshot_version_id=snapshot.version_id,
            created_utc=snapshot.created_utc,
            adjustments=tuple(adjustments),
        )

    def propose_threshold_adjustments_with_patterns(
        self,
        snapshot: HealingOutcomeAggregateSnapshot,
        pattern_report: PatternFindingReport | None = None,
        embedding_metadata: dict[str, Any] | None = None,
    ) -> ThresholdAdjustmentProposal:
        """Analyze snapshot with pattern findings and propose threshold adjustments.

        Args:
            snapshot: Healing outcome aggregate snapshot.
            pattern_report: Optional pattern analysis report.
            embedding_metadata: Optional embedding metadata for W2 integration.

        Returns:
            Proposal with threshold adjustments (proposal-only).
        """
        # If embedding metadata is provided, use the embedding-aware method
        if embedding_metadata:
            return self.propose_threshold_adjustments_with_embeddings(
                snapshot, pattern_report, embedding_metadata
            )

        # Otherwise, use the original pattern-only logic
        base_proposal = self.propose_threshold_adjustments(snapshot)
        adjustments = list(base_proposal.adjustments)

        # Apply pattern-based adjustments
        if pattern_report:
            pattern_adjustments = self._apply_pattern_findings(pattern_report)
            adjustments.extend(pattern_adjustments)

        # Sort deterministically and apply bounds
        adjustments.sort(key=lambda a: (a.healer_name, a.tier, a.failure_type, a.proposed_threshold))
        bounded_adjustments = self._apply_bounded_constraints(adjustments)

        return ThresholdAdjustmentProposal(
            snapshot_version_id=snapshot.version_id,
            created_utc=snapshot.created_utc,
            adjustments=tuple(bounded_adjustments),
        )

    def _apply_pattern_findings(self, pattern_report: PatternFindingReport) -> list[ThresholdAdjustment]:
        """Apply pattern findings to generate adjustments."""
        adjustments = []

        for finding in pattern_report.findings:
            if finding.key.label == "UNDERPERFORMING_HEALER_TIER":
                # Increase escalation aggressiveness
                component = finding.key.component
                # Map component to healer/tier (simplified)
                healer_name = component.split("_")[0] if "_" in component else component
                tier = "LOCAL_AGENT"  # Default tier

                current_threshold = self._get_current_threshold_for_healer(healer_name, tier)
                # Apply bounded delta based on severity
                delta = min(self._escalation_delta * finding.severity, self._max_delta)
                new_threshold = min(current_threshold + delta, self._max_threshold)

                if new_threshold != current_threshold:
                    adjustment = ThresholdAdjustment(
                        healer_name=healer_name,
                        tier=tier,
                        failure_type="pattern_based",
                        current_threshold=current_threshold,
                        proposed_threshold=new_threshold,
                        reason=f"Pattern finding: {finding.key.label} (severity={finding.severity:.3f})",
                        confidence=finding.severity,
                    )
                    adjustments.append(adjustment)

            elif finding.key.label == "ROUTING_DRIFT_HIGH":
                # Tighten thresholds for components with high drift
                component = finding.key.component
                healer_name = component.split("_")[0] if "_" in component else component
                tier = "LOCAL_AGENT"

                current_threshold = self._get_current_threshold_for_healer(healer_name, tier)
                # Decrease threshold to be more strict (but not below minimum)
                delta = min(self._escalation_delta * finding.severity * 0.5, self._max_delta)
                new_threshold = max(current_threshold - delta, 0.1)

                if new_threshold != current_threshold:
                    adjustment = ThresholdAdjustment(
                        healer_name=healer_name,
                        tier=tier,
                        failure_type="drift_based",
                        current_threshold=current_threshold,
                        proposed_threshold=new_threshold,
                        reason=f"Pattern finding: {finding.key.label} (severity={finding.severity:.3f})",
                        confidence=finding.severity,
                    )
                    adjustments.append(adjustment)

        return adjustments

    def _apply_bounded_constraints(self, adjustments: list[ThresholdAdjustment]) -> list[ThresholdAdjustment]:
        """Apply bounded delta constraints to adjustments."""
        bounded_adjustments = []

        # Group by healer_name and tier
        grouped = {}
        for adj in adjustments:
            key = (adj.healer_name, adj.tier)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(adj)

        # Apply constraints per group
        for (healer_name, tier), group_adj in grouped.items():
            # Get current threshold
            current_threshold = self._get_current_threshold_for_healer(healer_name, tier)

            # Calculate total delta
            total_delta = 0.0
            for adj in group_adj:
                total_delta += adj.proposed_threshold - current_threshold

            # Clamp to max_delta
            if abs(total_delta) > self._max_delta:
                # Scale down all adjustments proportionally
                scale = self._max_delta / abs(total_delta)
                for adj in group_adj:
                    scaled_delta = (adj.proposed_threshold - current_threshold) * scale
                    adj = ThresholdAdjustment(
                        healer_name=adj.healer_name,
                        tier=adj.tier,
                        failure_type=adj.failure_type,
                        current_threshold=current_threshold,
                        proposed_threshold=current_threshold + scaled_delta,
                        reason=adj.reason + f" (scaled to max_delta={self._max_delta})",
                        confidence=adj.confidence,
                    )
                    bounded_adjustments.append(adj)
            else:
                bounded_adjustments.extend(group_adj)

        return bounded_adjustments

    def _get_current_threshold_for_healer(self, healer_name: str, tier: str) -> float:
        """Get current threshold for a healer and tier."""
        # Use existing method with a temporary key
        from system_learning.types.healing_outcome_learning_types import HealingOutcomeAggregateKey

        key = HealingOutcomeAggregateKey(healer_name=healer_name, tier=tier, failure_type="generic")
        return self._get_current_threshold(key)

    def _get_current_threshold(self, key: HealingOutcomeAggregateKey) -> float:
        """Get current threshold for a key.

        In practice, this would query the current config.
        For now, returns deterministic defaults.
        """
        # Default thresholds by tier
        tier_defaults = {
            "LOCAL_AGENT": 0.5,
            "REMOTE_AGENT": 0.6,
            "CLOUD_SERVICE": 0.7,
        }
        return tier_defaults.get(key.tier, 0.5)

    def _compute_confidence(self, aggregate: HealingOutcomeAggregate) -> float:
        """Compute confidence in the proposed adjustment.

        Args:
            aggregate: Aggregate statistics.

        Returns:
            Confidence score (0.0 to 1.0).
        """
        # Simple confidence based on sample size
        # More samples = higher confidence
        # guardian: allow-magic-config
        max_samples = 1000
        normalized_samples = min(aggregate.total_count, max_samples) / max_samples

        # Also consider how far below threshold the success rate is
        rate_gap = self._low_success_rate_threshold - aggregate.success_rate
        normalized_gap = min(rate_gap / self._low_success_rate_threshold, 1.0)

        # Combine factors
        confidence = (normalized_samples * 0.6) + (normalized_gap * 0.4)
        return round(confidence + 1e-10, 4)  # Round-half-up

    # guardian: allow-magic-config
    def propose_threshold_adjustments_with_embeddings(
        self,
        snapshot: HealingOutcomeAggregateSnapshot,
        pattern_report: Any = None,
        embedding_metadata: dict[str, Any] | None = None,
        embedding_influence_cap: float = 0.25,
        min_sample_threshold: int = 20,
    ) -> ThresholdAdjustmentProposal:
        """Analyze snapshot with embedding influence and propose threshold adjustments.

        This is W2 implementation: embeddings provide C0 informational context
        and contribute to scoring with bounded influence.

        Args:
            snapshot: Healing outcome aggregate snapshot.
            pattern_report: Optional pattern analysis report.
            embedding_metadata: Embedding retrieval metadata for C0 context.
            embedding_influence_cap: Maximum influence of embeddings (<= 0.25).
            min_sample_threshold: Minimum samples for embedding influence.

        Returns:
            Proposal with threshold adjustments (proposal-only).
        """
        # Get base adjustments from snapshot
        base_proposal = self.propose_threshold_adjustments(snapshot)
        adjustments = list(base_proposal.adjustments)

        # Apply pattern-based adjustments if available
        if pattern_report:
            pattern_adjustments = self._apply_pattern_findings(pattern_report)
            adjustments.extend(pattern_adjustments)

        # Apply embedding-influenced scoring if enabled and guard passes
        if embedding_metadata and embedding_metadata.get("embedding_enabled_at_time", False):
            # Calculate total sample size across all aggregates
            total_samples = sum(agg.total_count for _, agg in snapshot.aggregates)

            # Small-N guard: if insufficient samples, embedding_weight = 0.0
            if total_samples >= min_sample_threshold:
                # Apply embedding influence to confidence scores
                embedding_weight = min(embedding_influence_cap, 0.25)

                # Get embedding scores for aggregation
                embedding_scores = embedding_metadata.get("embedding_topk_scores_round6", [])
                embedding_score = self._aggregate_embedding_scores(embedding_scores)

                # Update adjustments with embedding-influenced confidence
                embedding_influenced_adjustments = []
                for adj in adjustments:
                    # Combine statistical confidence with embedding score
                    statistical_confidence = adj.confidence
                    embedding_confidence = embedding_score

                    # Bounded combination: statistical remains dominant
                    final_confidence = (
                        1.0 - embedding_weight
                    ) * statistical_confidence + embedding_weight * embedding_confidence

                    # Round to 6 decimal places for determinism
                    final_confidence = round(final_confidence + 1e-10, 6)

                    # Create new adjustment with embedding-influenced confidence
                    influenced_adj = ThresholdAdjustment(
                        healer_name=adj.healer_name,
                        tier=adj.tier,
                        failure_type=adj.failure_type,
                        current_threshold=adj.current_threshold,
                        proposed_threshold=adj.proposed_threshold,
                        reason=(
                            adj.reason + f" (embedding_influenced: weight={embedding_weight:.3f}, "
                            f"score={embedding_score:.6f})"
                        ),
                        confidence=final_confidence,
                    )
                    embedding_influenced_adjustments.append(influenced_adj)

                adjustments = embedding_influenced_adjustments

        # Sort deterministically and apply bounds
        adjustments.sort(key=lambda a: (a.healer_name, a.tier, a.failure_type, a.proposed_threshold))
        bounded_adjustments = self._apply_bounded_constraints(adjustments)

        return ThresholdAdjustmentProposal(
            snapshot_version_id=snapshot.version_id,
            created_utc=snapshot.created_utc,
            adjustments=tuple(bounded_adjustments),
        )

    def _aggregate_embedding_scores(self, scores: list[float]) -> float:
        """Aggregate embedding scores deterministically.

        Args:
            scores: List of similarity scores (rounded to 6 decimals).

        Returns:
            Aggregated score (0.0 to 1.0).
        """
        if not scores:
            return 0.0

        # Use max for deterministic aggregation (most relevant context)
        # Could also use mean of top-3, but max is simpler and deterministic
        return max(scores) if scores else 0.0


# Data structures for proposals
@dataclass(frozen=True, slots=True)
class ThresholdAdjustment:
    """Proposal to adjust a healing threshold."""

    healer_name: str
    tier: str
    failure_type: str
    current_threshold: float
    proposed_threshold: float
    reason: str
    confidence: float

    def canonical_bytes(self) -> bytes:
        """Generate canonical byte representation."""
        data = {
            "healer_name": self.healer_name,
            "tier": self.tier,
            "failure_type": self.failure_type,
            "current_threshold": self.current_threshold,
            "proposed_threshold": self.proposed_threshold,
            "reason": self.reason,
            "confidence": self.confidence,
        }
        import json

        json_str = json.dumps(data, separators=(",", ":"), sort_keys=True)
        return json_str.encode("utf-8")

    def content_hash(self) -> str:
        """Generate SHA-256 hash."""
        import hashlib

        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class ThresholdAdjustmentProposal:
    """Proposal-only container for threshold adjustments."""

    snapshot_version_id: str
    created_utc: int
    adjustments: tuple[ThresholdAdjustment, ...] = field(default_factory=tuple)

    def canonical_bytes(self) -> bytes:
        """Generate canonical byte representation."""
        adjustments_data = []
        for adj in self.adjustments:
            adjustments_data.append(
                {
                    "healer_name": adj.healer_name,
                    "tier": adj.tier,
                    "failure_type": adj.failure_type,
                    "current_threshold": adj.current_threshold,
                    "proposed_threshold": adj.proposed_threshold,
                    "reason": adj.reason,
                    "confidence": adj.confidence,
                }
            )

        data = {
            "snapshot_version_id": self.snapshot_version_id,
            "created_utc": self.created_utc,
            "adjustments": adjustments_data,
        }

        import json

        json_str = json.dumps(data, separators=(",", ":"), sort_keys=True)
        return json_str.encode("utf-8")

    def content_hash(self) -> str:
        """Generate SHA-256 hash."""
        import hashlib

        return hashlib.sha256(self.canonical_bytes()).hexdigest()


__all__ = [
    "HealingConfigOptimizer",
    "ThresholdAdjustment",
    "ThresholdAdjustmentProposal",
]
