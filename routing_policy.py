from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class RoutingCriteria:
    task_type: str
    complexity: str = "low"  # low | medium | high
    latency_target_ms: int = 2000
    cost_ceiling_usd: float = 0.05
    risk_level: str = "normal"  # normal | strict | high_safety


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
        return RoutingDecision(
            model="gpt-4o",
            endpoint="default",
            rationale="High complexity or strict risk requires GPT-4o.",
        )

    if criteria.latency_target_ms < 1000:
        return RoutingDecision(
            model="gpt-4o-mini",
            endpoint="fast",
            rationale="Low latency target; use lightweight model.",
        )

    return RoutingDecision(
        model="gpt-4o-mini",
        endpoint="default",
        rationale="Default routing for normal tasks.",
    )
