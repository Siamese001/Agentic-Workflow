# FILE: v10_9_clean/l5/model_routing.py
"""
L5 — Model Routing Policy (v10_9)

Determines which model + endpoint to use based on:
    • task complexity
    • latency target
    • cost ceiling
    • risk/safety level
    • META_PROFILE routing biases

This replaces the 10_7/10_8 routing.py functionality and belongs
in the L5 policy layer (not orchestration).
"""

from __future__ import annotations
from typing import Any, Dict
from dataclasses import dataclass

from shared.constants import CANONICAL_MODEL_DEFAULT
from l1.meta_profile import META_PROFILE


@dataclass
class RoutingCriteria:
    task_type: str
    complexity: str = "low"         # low | medium | high
    latency_target_ms: int = 2000
    cost_ceiling_usd: float = 0.05
    risk_level: str = "normal"      # normal | strict | high_safety
    model_available: bool = True


@dataclass
class RoutingDecision:
    model: str
    endpoint: str
    rationale: str


def select_model(criteria: RoutingCriteria) -> RoutingDecision:
    """
    Deterministic v10_9 routing logic.
    """

    # High complexity OR high risk → strong model
    if criteria.complexity == "high" or criteria.risk_level in ("strict", "high_safety"):
        decision = RoutingDecision(
            model="gpt-4.1",
            endpoint="standard",
            rationale="High complexity or risk → strong model required.",
        )

    # Low latency → lightweight model
    elif criteria.latency_target_ms < 1000:
        decision = RoutingDecision(
            model="gpt-4.1-mini",
            endpoint="fast",
            rationale="Low latency target → lightweight model.",
        )

    else:
        decision = RoutingDecision(
            model="gpt-4.1-mini",
            endpoint="standard",
            rationale="Default path for normal tasks.",
        )

    # Unavailable model fallback
    if not criteria.model_available:
        decision = RoutingDecision(
            model="gpt-4.1-mini",
            endpoint="fast",
            rationale="Primary route unavailable → fallback fast endpoint.",
        )

    # META_PROFILE override
    if META_PROFILE.routing_bias.get("prefer_fast"):
        decision.endpoint = "fast"

    return decision
