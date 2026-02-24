"""Healing Config Optimizer - Threshold adjustment proposals.

Phase 6: Consumes healing outcome aggregates to propose threshold adjustments.
All proposals are proposal-only via ChangePackage; no direct config mutation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

from system_learning.types.healing_outcome_learning_types import (
    HealingOutcomeAggregate,
    HealingOutcomeAggregateKey,
    HealingOutcomeAggregateSnapshot,
)


class HealingConfigOptimizer:
    """Optimizer for healing tier thresholds based on outcome aggregates.

    Consumes HealingOutcomeAggregateSnapshot and produces deterministic
    threshold adjustment proposals. All changes are proposal-only.
    """

    def __init__(
        self,
        min_sample_size: int = 20,
        low_success_rate_threshold: float = 0.5,
        escalation_delta: float = 0.1,
        max_threshold: float = 2.0
    ) -> None:
        """Initialize optimizer with deterministic parameters.

        Args:
            min_sample_size: Minimum sample size for reliable statistics.
            low_success_rate_threshold: Success rate below which escalation is considered.
            escalation_delta: Fixed delta to add to threshold when escalating.
            max_threshold: Maximum allowed threshold value.
        """
        if min_sample_size < 1:
            raise ValueError("min_sample_size must be >= 1")
        if not 0.0 <= low_success_rate_threshold <= 1.0:
            raise ValueError("low_success_rate_threshold must be in [0.0, 1.0]")
        if escalation_delta <= 0:
            raise ValueError("escalation_delta must be > 0")
        if max_threshold <= 0:
            raise ValueError("max_threshold must be > 0")

        self._min_sample_size = min_sample_size
        self._low_success_rate_threshold = low_success_rate_threshold
        self._escalation_delta = escalation_delta
        self._max_threshold = max_threshold

    def create_snapshot_from_intake(
        self,
        intake_record,
        created_utc: int
    ) -> HealingOutcomeAggregateSnapshot:
        """Create aggregate snapshot from healing outcome intake record.

        Args:
            intake_record: Healing outcome intake record.
            created_utc: Timestamp for the snapshot.

        Returns:
            Aggregate snapshot for threshold optimization.
        """
        # Convert intake snapshot to aggregate format
        aggregate_pairs = []

        if hasattr(intake_record, 'snapshot'):
            for stats in intake_record.snapshot:
                key = HealingOutcomeAggregateKey(
                    healer_name=stats.healer_id,
                    tier=stats.tier,
                    failure_type=stats.failure_type
                )
                aggregate = HealingOutcomeAggregate(
                    success_count=stats.success_count,
                    failure_count=stats.failure_count,
                    total_count=stats.total_count
                )
                aggregate_pairs.append((key, aggregate))

        # Sort deterministically
        aggregate_pairs.sort(key=lambda pair: (
            pair[0].healer_name,
            pair[0].tier,
            pair[0].failure_type
        ))

        # Create temporary snapshot to compute hash
        temp_snapshot = HealingOutcomeAggregateSnapshot(
            version_id="temp",  # Temporary value
            created_utc=created_utc,
            aggregates=tuple(aggregate_pairs)
        )

        # Compute version_id as hash of content
        version_id = temp_snapshot.content_hash()

        # Create final snapshot with correct version_id
        snapshot = HealingOutcomeAggregateSnapshot(
            version_id=version_id,
            created_utc=created_utc,
            aggregates=tuple(aggregate_pairs)
        )

        return snapshot

    def propose_threshold_adjustments(
        self,
        snapshot: HealingOutcomeAggregateSnapshot
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
                new_threshold = min(
                    current_threshold + self._escalation_delta,
                    self._max_threshold
                )

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
                        confidence=self._compute_confidence(aggregate)
                    )
                    adjustments.append(adjustment)

        # Sort adjustments deterministically
        adjustments.sort(key=lambda a: (
            a.healer_name,
            a.tier,
            a.failure_type,
            a.proposed_threshold
        ))

        return ThresholdAdjustmentProposal(
            snapshot_version_id=snapshot.version_id,
            created_utc=snapshot.created_utc,
            adjustments=tuple(adjustments)
        )

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
        max_samples = 1000
        normalized_samples = min(aggregate.total_count, max_samples) / max_samples

        # Also consider how far below threshold the success rate is
        rate_gap = self._low_success_rate_threshold - aggregate.success_rate
        normalized_gap = min(rate_gap / self._low_success_rate_threshold, 1.0)

        # Combine factors
        confidence = (normalized_samples * 0.6) + (normalized_gap * 0.4)
        return round(confidence + 1e-10, 4)  # Round-half-up


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
        return json_str.encode('utf-8')

    def content_hash(self) -> str:
        """Generate SHA-256 hash."""
        import hashlib
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True, slots=True)
class ThresholdAdjustmentProposal:
    """Proposal-only container for threshold adjustments."""

    snapshot_version_id: str
    created_utc: int
    adjustments: Tuple[ThresholdAdjustment, ...] = field(default_factory=tuple)

    def canonical_bytes(self) -> bytes:
        """Generate canonical byte representation."""
        adjustments_data = []
        for adj in self.adjustments:
            adjustments_data.append({
                "healer_name": adj.healer_name,
                "tier": adj.tier,
                "failure_type": adj.failure_type,
                "current_threshold": adj.current_threshold,
                "proposed_threshold": adj.proposed_threshold,
                "reason": adj.reason,
                "confidence": adj.confidence,
            })

        data = {
            "snapshot_version_id": self.snapshot_version_id,
            "created_utc": self.created_utc,
            "adjustments": adjustments_data,
        }

        import json
        json_str = json.dumps(data, separators=(",", ":"), sort_keys=True)
        return json_str.encode('utf-8')

    def content_hash(self) -> str:
        """Generate SHA-256 hash."""
        import hashlib
        return hashlib.sha256(self.canonical_bytes()).hexdigest()




__all__ = [
    "HealingConfigOptimizer",
    "ThresholdAdjustment",
    "ThresholdAdjustmentProposal",
]
