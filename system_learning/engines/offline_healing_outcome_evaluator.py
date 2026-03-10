"""Offline evaluator for healing outcome proposals.

Phase 3: Deterministic scoring engine for shadow mode evaluation.
No IO except optional store; no config/routing/L4 writes.
"""

from __future__ import annotations

from system_learning.types.healing_outcome_intake_types import HealingOutcomeIntakeRecord
from system_learning.types.healing_outcome_scoring_types import (
    ScoredRecommendation,
    ScoringReport,
    ScoringWeights,
    _stable_round,
)
from system_learning.types.healing_outcome_types import HealingOutcomeProposal


class OfflineHealingOutcomeEvaluator:
    """Deterministic offline evaluator for healing outcome proposals.

    Evaluates proposals against intake records using pure functions.
    No wall-clock reads; all timestamps are explicit.
    """

    def __init__(self, weights: ScoringWeights) -> None:
        """Initialize evaluator with scoring weights."""
        self.weights = weights

    def evaluate(
        self,
        intake: HealingOutcomeIntakeRecord,
        created_utc: int,
        candidates: tuple[HealingOutcomeProposal, ...],
    ) -> ScoringReport:
        """Evaluate candidate proposals deterministically.

        Args:
            intake: Healing outcome intake record with snapshot stats
            created_utc: Explicit timestamp (no wall-clock reads)
            candidates: Proposals to evaluate (order-independent)

        Returns:
            Deterministic scoring report with sorted recommendations
        """
        # Compute aggregate success rate from intake snapshot
        total_success = sum(stat.success_count for stat in intake.snapshot)
        total_events = sum(stat.total_count for stat in intake.snapshot)
        aggregate_success_rate = total_success / total_events if total_events > 0 else 0.0

        # Sample size is total events (deterministic formula)
        sample_size = total_events

        # Compute risk tier penalty (higher tiers get higher penalty)
        # Tier penalty: LOCAL_AGENT=0, REMOTE_AGENT=0.1, CLOUD_SERVICE=0.2
        tier_penalties = {
            "LOCAL_AGENT": 0.0,
            "REMOTE_AGENT": 0.1,
            "CLOUD_SERVICE": 0.2,
        }

        # Aggregate risk tier penalty from snapshot
        risk_penalty = 0.0
        for stat in intake.snapshot:
            tier_penalty = tier_penalties.get(stat.tier, 0.3)  # Default penalty for unknown tiers
            # Weight by proportion of events
            weight = stat.total_count / total_events if total_events > 0 else 0.0
            risk_penalty += tier_penalty * weight

        # Evaluate each candidate
        recommendations = []
        rejected_reasons = []

        for i, candidate in enumerate(candidates):
            proposer_id = f"proposer_{i}"  # Generic proposer ID since proposals don't carry it
            target_surface = "healing_outcome_policy"  # Generic target surface

            # Apply deterministic validation filters
            # Filter 1: Minimum sample size (require at least 10 events)
            if sample_size < 10:
                rejected_reasons.append(f"Candidate {i}: Insufficient sample size ({sample_size} < 10)")
                continue

            # Filter 2: Minimum success rate (require at least 50%)
            if aggregate_success_rate < 0.5:
                rejected_reasons.append(
                    f"Candidate {i}: Low success rate ({aggregate_success_rate:.4f} < 0.5)"
                )
                continue

            # Filter 3: Risk tier threshold (reject if average penalty > 0.15)
            if risk_penalty > 0.15:
                rejected_reasons.append(f"Candidate {i}: High risk tier penalty ({risk_penalty:.4f} > 0.15)")
                continue

            # Compute deterministic score
            # Score = success_rate_weight * success_rate
            #        - stability_penalty_weight * risk_penalty
            #        + sample_size_weight * log(sample_size + 1) / log(1000)
            #        - risk_tier_penalty_weight * risk_penalty

            import math

            sample_size_normalized = math.log(sample_size + 1) / math.log(1000)  # 0 to 1 scale

            raw_score = (
                self.weights.success_rate_weight * aggregate_success_rate
                - self.weights.stability_penalty_weight * risk_penalty
                + self.weights.sample_size_weight * sample_size_normalized
                - self.weights.risk_tier_penalty_weight * risk_penalty
            )

            # Apply deterministic rounding (round-half-up to 4 decimals)
            score = _stable_round(max(0.0, raw_score))  # Clamp to non-negative

            # Generate deterministic reasons
            reasons = [
                f"Success rate: {aggregate_success_rate:.4f}",
                f"Sample size: {sample_size}",
                f"Risk penalty: {risk_penalty:.4f}",
                f"Actions: {len(candidate.recommended_actions)}",
            ]

            recommendation = ScoredRecommendation(
                proposer_id=proposer_id,
                target_surface=target_surface,
                recommended_actions=candidate.recommended_actions,
                score=score,
                reasons=tuple(reasons),
            )
            recommendations.append(recommendation)

        # Sort recommendations deterministically by (-score, proposer_id, target_surface)
        recommendations.sort(key=lambda r: (-r.score, r.proposer_id, r.target_surface))

        # Sort rejected reasons deterministically
        rejected_reasons = tuple(sorted(rejected_reasons))

        return ScoringReport(
            created_utc=created_utc,
            intake_record=intake,
            weights=self.weights,
            recommendations=tuple(recommendations),
            rejected_reasons=rejected_reasons,
        )
