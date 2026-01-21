"""
EvaluateResumeEffectiveness.py - Scoring Module

Domain: resume
Generated: 2025-12-07T13:28:54.223993
"""

import logging

from shared.result_types import ScoreResult

Logger = logging.getLogger(__name__)


class EvaluateResumeEffectiveness:
    """Scorer for resume domain."""

    def __init__(self, config: dict[str, object] | None = None):
        self.config = config or {}
        self.weights = self.config.get("weights", {})
        Logger.info(f"Initialized {self.__class__.__name__}")

    def score(self, data: dict[str, object]) -> ScoreResult:
        """Compute score for data."""
        factors = self._extract_factors(data)
        raw_score = self._compute_weighted(factors)
        confidence = self._compute_confidence(factors)
        return ScoreResult(score=max(0, min(1, raw_score)), confidence=confidence, factors=factors)

    def _extract_factors(self, data: dict[str, object]) -> dict[str, float]:
        """Extract scoring factors."""
        factors = {}
        for k, v in data.items():
            if isinstance(v, (int, float)):
                factors[k] = float(v)
            elif isinstance(v, str):
                factors[f"{k}_len"] = min(1.0, len(v) / 100)
        return factors

    def _compute_weighted(self, factors: dict[str, float]) -> float:
        """Compute weighted score."""
        if not factors:
            return 0.5
        total_w = sum(self.weights.get(k, 1.0) for k in factors)
        weighted = sum(v * self.weights.get(k, 1.0) for k, v in factors.items())
        return weighted / total_w if total_w else 0.5

    def _compute_confidence(self, factors: dict[str, float]) -> float:
        """Compute confidence."""
        return min(1.0, len(factors) / 5)


def compute_score(data: dict[str, object], config: dict | None = None) -> ScoreResult:
    """Compute relevance score based on input parameters."""
    return EvaluateResumeEffectiveness(config).score(data)
