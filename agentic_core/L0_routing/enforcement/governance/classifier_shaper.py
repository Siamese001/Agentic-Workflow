"""C0 G5: CLASSIFY + SHAPE - Route categorization and shaping.

10C-REQ-114: Classify route categorize shape output bundle
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class RouteCategory(Enum):
    """Categories for route classification."""
    CACHE_HIT = auto()
    RAG_GROUNDED = auto()
    TOOL_CALL = auto()
    MODEL_GENERATION = auto()
    HITL_REQUIRED = auto()
    FALLBACK_SAFE = auto()


class RiskTier(Enum):
    """Risk tiers for routing."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass
class ShapedBundle:
    """Output bundle after classification and shaping."""
    category: RouteCategory
    risk_tier: RiskTier
    route_target: str
    requires_governance: bool
    shaped_payload: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class ClassifierShaper:
    """C0 G5: Classifier and shaper.

    10C-REQ-114: Classify route categorize shape output bundle.
    """

    def __init__(self) -> None:
        self._category_rules: list[tuple[callable, RouteCategory]] = []
        self._risk_thresholds: dict[RiskTier, float] = {
            RiskTier.LOW: 0.3,
            RiskTier.MEDIUM: 0.5,
            RiskTier.HIGH: 0.7,
            RiskTier.CRITICAL: 0.9,
        }

    def classify_and_shape(
        self,
        request: dict[str, Any],
        risk_score: float = 0.0,
    ) -> ShapedBundle:
        """Classify request and shape output bundle."""
        # Determine category
        category = self._classify(request)

        # Determine risk tier
        risk_tier = self._assess_risk_tier(risk_score, category)

        # Determine route target
        route_target = self._select_route(category, risk_tier)

        # Shape payload
        shaped = self._shape_payload(request, category)

        # Check governance requirement
        needs_governance = risk_tier in (RiskTier.HIGH, RiskTier.CRITICAL)

        return ShapedBundle(
            category=category,
            risk_tier=risk_tier,
            route_target=route_target,
            requires_governance=needs_governance,
            shaped_payload=shaped,
            metadata={
                "original_operation": request.get("operation"),
                "risk_score": risk_score,
            },
        )

    def _classify(self, request: dict[str, Any]) -> RouteCategory:
        """Classify request to category."""
        operation = request.get("operation", "").lower()

        # Check for cache indicators
        if request.get("cache_hit") or "cache" in operation:
            return RouteCategory.CACHE_HIT

        # Check for RAG/retrieval indicators
        if any(x in operation for x in ["rag", "retrieve", "evidence", "search"]):
            return RouteCategory.RAG_GROUNDED

        # Check for tool indicators
        if any(x in operation for x in ["tool", "execute", "invoke"]):
            return RouteCategory.TOOL_CALL

        # Check for model indicators
        if any(x in operation for x in ["model", "llm", "generate", "completion"]):
            return RouteCategory.MODEL_GENERATION

        # Check for HITL indicators
        if request.get("confidence", 1.0) < 0.5 or "hitl" in operation:
            return RouteCategory.HITL_REQUIRED

        return RouteCategory.FALLBACK_SAFE

    def _assess_risk_tier(self, risk_score: float, category: RouteCategory) -> RiskTier:
        """Assess risk tier from score and category."""
        # Category adjustments
        if category == RouteCategory.HITL_REQUIRED:
            risk_score = max(risk_score, 0.7)
        elif category == RouteCategory.TOOL_CALL:
            risk_score = max(risk_score, 0.5)

        for tier, threshold in sorted(self._risk_thresholds.items(), key=lambda x: x[1]):
            if risk_score <= threshold:
                return tier

        return RiskTier.CRITICAL

    def _select_route(self, category: RouteCategory, risk_tier: RiskTier) -> str:
        """Select route target based on category and risk."""
        routes = {
            RouteCategory.CACHE_HIT: "L0_cache",
            RouteCategory.RAG_GROUNDED: "C0_retrieval",
            RouteCategory.TOOL_CALL: "L2_execution",
            RouteCategory.MODEL_GENERATION: "L2_model_invoke",
            RouteCategory.HITL_REQUIRED: "L5_HITL",
            RouteCategory.FALLBACK_SAFE: "L0_fallback",
        }
        return routes.get(category, "L0_default")

    def _shape_payload(self, request: dict[str, Any], category: RouteCategory) -> dict[str, Any]:
        """Shape payload for routing."""
        shaped = dict(request)
        shaped["governance_category"] = category.name
        shaped["shaped_at"] = "g5_classifier"
        return shaped

    def set_risk_threshold(self, tier: RiskTier, threshold: float) -> None:
        """Set risk threshold for tier."""
        self._risk_thresholds[tier] = max(0.0, min(1.0, threshold))
