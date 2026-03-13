"""
W4-D Policy Recommendation Engine

Converts W4-C DriftSummary outputs into deterministic, bounded policy recommendations.
Advisory only - does not mutate active RetrievalProfile.
"""

import hashlib
import json
from dataclasses import dataclass

from system_learning.engines.retrieval_profile import RetrievalProfile
from system_learning.engines.shadow_drift_analyzer import DriftSummary


@dataclass(frozen=True, slots=True)
class PolicyRecommendation:
    """Advisory policy recommendation based on drift analysis."""

    profile_id: str
    recommended_changes: dict[str, float]
    rationale: str
    confidence_score: float
    deterministic_digest: str

    def emit_digest(self) -> None:
        """Print the recommendation digest for determinism verification."""
        print(f"W4D-RECOMMEND-DIGEST: {self.deterministic_digest}")

    def to_canonical_json(self) -> str:
        """Convert to canonical JSON for deterministic serialization."""
        data = {
            "profile_id": self.profile_id,
            "recommended_changes": {k: round(v, 6) for k, v in self.recommended_changes.items()},
            "rationale": self.rationale,
            "confidence_score": round(self.confidence_score, 6),
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":"))


class PolicyRecommendationEngine:
    """Generates deterministic, bounded policy recommendations from drift analysis."""

    def generate_recommendation(
        self, *, drift_summary: DriftSummary, active_profile: RetrievalProfile, now_utc: int
    ) -> PolicyRecommendation:
        """Generate policy recommendation based on drift analysis.

        Args:
            drift_summary: Drift analysis from W4-C
            active_profile: Current active RetrievalProfile
            now_utc: Current timestamp

        Returns:
            PolicyRecommendation with deterministic digest
        """
        if drift_summary.drift_flag:
            recommended_changes = {}
            rationale_parts = []
            max_cutoff_reduction = min(0.02, drift_summary.drift_score * 0.05)
            if max_cutoff_reduction > 1e-06:
                new_cutoff = max(0.1, round(active_profile.similarity_cutoff - max_cutoff_reduction, 6))
                recommended_changes["similarity_cutoff"] = new_cutoff
                rationale_parts.append(
                    f"Lower similarity_cutoff from {active_profile.similarity_cutoff:.6f} to {new_cutoff:.6f} (drift_score={drift_summary.drift_score:.6f})"
                )
            max_cap_increase = min(0.01, drift_summary.drift_score * 0.02)
            if max_cap_increase > 1e-06:
                new_cap = min(1.0, round(active_profile.influence_cap + max_cap_increase, 6))
                recommended_changes["influence_cap"] = new_cap
                rationale_parts.append(
                    f"Increase influence_cap from {active_profile.influence_cap:.6f} to {new_cap:.6f} (drift_score={drift_summary.drift_score:.6f})"
                )
            rationale = "Drift detected: " + "; ".join(rationale_parts)
            confidence_score = min(1.0, drift_summary.drift_score * 2.0)
        else:
            recommended_changes = {}
            rationale = f"No drift detected (p95_cosine={drift_summary.p95_cosine:.6f} >= 0.92)"
            confidence_score = 0.95
        deterministic_digest = self._compute_digest(
            profile_id=active_profile.profile_id,
            drift_summary=drift_summary,
            recommended_changes=recommended_changes,
            rationale=rationale,
            confidence_score=confidence_score,
            now_utc=now_utc,
        )
        return PolicyRecommendation(
            profile_id=active_profile.profile_id,
            recommended_changes=recommended_changes,
            rationale=rationale,
            confidence_score=round(confidence_score, 6),
            deterministic_digest=deterministic_digest,
        )

    def _compute_digest(
        self,
        *,
        profile_id: str,
        drift_summary: DriftSummary,
        recommended_changes: dict[str, float],
        rationale: str,
        confidence_score: float,
        now_utc: int,
    ) -> str:
        """Compute deterministic SHA-256 digest of recommendation data."""
        data = {
            "profile_id": profile_id,
            "drift_summary": {
                "profile_id": drift_summary.profile_id,
                "batch_size": drift_summary.batch_size,
                "mean_cosine": round(drift_summary.mean_cosine, 6),
                "p95_cosine": round(drift_summary.p95_cosine, 6),
                "drift_flag": drift_summary.drift_flag,
                "drift_score": round(drift_summary.drift_score, 6),
            },
            "recommended_changes": {k: round(v, 6) for k, v in sorted(recommended_changes.items())},
            "rationale": rationale,
            "confidence_score": round(confidence_score, 6),
            "now_utc": now_utc,
            "engine_version": "W4-D-v1.0",
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class MemoryAwarePolicyRecommendationEngine(PolicyRecommendationEngine):
    """PolicyRecommendationEngine that persists recommendations to Memory MCP.

    Drop-in replacement. Every call to ``generate_recommendation`` is
    automatically persisted to the Memory MCP knowledge graph, building a
    cross-session recommendation history for drift trend analysis.
    """

    def generate_recommendation(
        self, *, drift_summary: DriftSummary, active_profile: RetrievalProfile, now_utc: int
    ) -> PolicyRecommendation:
        recommendation = super().generate_recommendation(
            drift_summary=drift_summary, active_profile=active_profile, now_utc=now_utc
        )
        try:
            from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

            get_sl_memory_bridge().persist_policy_recommendation(recommendation, ts=str(now_utc))
        # guardian: allow-silent-swallow
        except Exception:
            pass
        return recommendation


__all__ = ["PolicyRecommendationEngine", "MemoryAwarePolicyRecommendationEngine", "PolicyRecommendation"]
