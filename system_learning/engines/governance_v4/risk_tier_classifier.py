"""L5 Governance v4 — Risk Tier Classifier (G-03).

Assigns ``risk_tier_band`` ∈ {LOW, MODERATE, HIGH} to every governance
packet. The band drives chokepoint depth, HITL requirements, and logging
detail downstream.

Reference
---------
``docs/reference/00_L5_Policy_Plane/risk_tier_bands.md``.

KPI surface
-----------
``RISK_TIER_BAND_COVERAGE`` — ratio of packets that received a band
(must be 1.0 for full coverage).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

logger = logging.getLogger(__name__)


class RiskTierBand(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"


@dataclass(frozen=True)
class RiskAssessment:
    band: RiskTierBand
    score: float  # 0.0..1.0
    rationale: str
    factors: Mapping[str, float]


# Heuristic factor weights. Higher = more risk.
_FACTOR_WEIGHTS: dict[str, float] = {
    "writes_to_canonical_store": 0.35,
    "external_egress": 0.20,
    "cross_principal_data": 0.15,
    "high_value_user_data": 0.20,
    "experimental_provider": 0.10,
    "history_of_drift": 0.10,
    "guard_model_disagreement": 0.15,
}


class RiskTierClassifier:
    """Score a packet and assign a risk tier band."""

    LOW_MAX: float = 0.30
    HIGH_MIN: float = 0.65

    def __init__(self) -> None:
        self._classified: int = 0
        self._total: int = 0

    def classify(
        self, packet_factors: Mapping[str, bool] | Mapping[str, float]
    ) -> RiskAssessment:
        """Classify a packet given a mapping of factor flags or weights.

        Bool factors are treated as 0.0/1.0. Unknown factors are ignored.
        """
        self._total += 1
        weighted: dict[str, float] = {}
        score = 0.0
        for factor, weight in _FACTOR_WEIGHTS.items():
            value = packet_factors.get(factor, 0.0)
            try:
                v = float(bool(value)) if isinstance(value, bool) else float(value)
            except (TypeError, ValueError):
                v = 0.0
            v = max(0.0, min(1.0, v))
            contribution = v * weight
            score += contribution
            if contribution > 0:
                weighted[factor] = contribution

        score = max(0.0, min(1.0, score))

        if score >= self.HIGH_MIN:
            band = RiskTierBand.HIGH
            rationale = (
                f"score={score:.2f} >= HIGH_MIN={self.HIGH_MIN}; "
                "enhanced log + HITL + isolated sandbox required"
            )
        elif score <= self.LOW_MAX:
            band = RiskTierBand.LOW
            rationale = (
                f"score={score:.2f} <= LOW_MAX={self.LOW_MAX}; fast-track"
            )
        else:
            band = RiskTierBand.MODERATE
            rationale = (
                f"score={score:.2f} in (LOW_MAX, HIGH_MIN); "
                "standard guardrails + audit"
            )
        self._classified += 1
        return RiskAssessment(
            band=band,
            score=score,
            rationale=rationale,
            factors=weighted,
        )

    @property
    def counters(self) -> tuple[int, int]:
        return (self._classified, self._total)

    def reset(self) -> None:
        self._classified = 0
        self._total = 0

    def publish_kpi_sample(self, board: Any) -> None:
        try:
            from system_learning.engines.v7_kpi_board import (  # noqa: PLC0415
                V7KPIName,
                V7KPISample,
            )

            ratio = (
                self._classified / self._total if self._total > 0 else 0.0
            )
            board.record(V7KPISample(
                name=V7KPIName.RISK_TIER_BAND_COVERAGE,
                value=ratio,
                timestamp=time.time(),
                source="risk_tier_classifier",
                metadata={"classified": self._classified,
                          "total": self._total},
            ))
        except (ImportError, AttributeError, RuntimeError, ValueError) as exc:  # guardian: allow-specific -- KPI must not break classification
            logger.warning("v7_kpi_risk_tier_band_coverage_failed: %s", exc)


__all__ = ["RiskTierBand", "RiskAssessment", "RiskTierClassifier"]
