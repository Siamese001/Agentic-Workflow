from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RoutingCriteria:
    task_type: str
    complexity: str = "low"  # low | medium | high
    latency_target_ms: int = 2000
    cost_ceiling_usd: float = 0.05
    risk_level: str = "normal"  # normal | strict | high_safety
    model_available: bool = True


@dataclass
class RoutingDecision:
    model: str
    endpoint: str
    rationale: str


def decide_route(criteria: RoutingCriteria) -> RoutingDecision:
    """
    Deterministic routing strategy based on criteria.
    No external calls, no randomness.
    """
    # Simple deterministic mapping:
    if criteria.complexity == "high" or criteria.risk_level == "strict":
        decision = RoutingDecision(
            model="gpt-4o",
            endpoint="default",
            rationale="High complexity or strict risk requires GPT-4o.",
        )
    elif criteria.latency_target_ms < 1000:
        decision = RoutingDecision(
            model="gpt-4o-mini",
            endpoint="fast",
            rationale="Low latency target; use lightweight model.",
        )
    else:
        decision = RoutingDecision(
            model="gpt-4o-mini",
            endpoint="default",
            rationale="Default routing for normal tasks.",
        )

    if not criteria.model_available:
        return RoutingDecision(
            model="gpt-4o-mini",
            endpoint="fast",
            rationale="Primary route unavailable; using fallback fast endpoint.",
        )

    return decision
