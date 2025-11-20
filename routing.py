# FILE: routing.py
"""
Unified Routing Policy (v10_10) — MODEL SELECTION ENGINE

This module implements Pillar 11 (Cost & Optimization).
It acts as the "Traffic Controller" for the agent, deciding WHICH model
to use based on Task Complexity, Cost Sensitivity, and Meta-Biases.

It is PURE DECISION LOGIC. It does not execute network calls.

Responsibilities:
    1. Model Selection: Map (Task + Complexity) -> (Model ID).
    2. Provider Routing: Select OpenAI vs Anthropic based on availability.
    3. Parameter Tuning: Adjust temperature/tokens based on reasoning mode.
    4. Meta-Adaptation: React to 'bias_routing_fast' signals.
"""

from __future__ import annotations

from typing import Dict, Any
from models import (
    RoutingRequest, 
    RoutingDecision, 
    MetaProfile, 
    ReasoningStrategy
)

# =============================================================================
# ROUTING CONSTANTS
# =============================================================================

# Tier definitions for clear separation of concerns
MODEL_TIERS = {
    "reasoning_heavy": {
        "primary": "gpt-4-turbo",
        "fallback": "claude-3-opus",
        "cost": "high"
    },
    "balanced": {
        "primary": "gpt-4o",
        "fallback": "claude-3-sonnet",
        "cost": "medium"
    },
    "fast": {
        "primary": "gpt-3.5-turbo",
        "fallback": "claude-3-haiku",
        "cost": "low"
    }
}

# =============================================================================
# ROUTING ENGINE
# =============================================================================

class RoutingEngine:
    """
    Determines the optimal model configuration for a given task.
    """

    def decide(
        self, 
        request: RoutingRequest, 
        meta_profile: MetaProfile
    ) -> RoutingDecision:
        """
        The core routing logic.
        """
        
        # 1. Determine Tier based on Complexity & Task
        tier = self._resolve_tier(request, meta_profile)
        
        # 2. Select Provider/Model
        # (In a real system, we'd check health status here)
        selection = MODEL_TIERS[tier]
        model_id = selection["primary"]
        
        # 3. Tune Parameters (Temperature / Tokens)
        # Strategy tasks need higher temp for creativity? 
        # Actually, Strategy needs reasoning (lower temp usually better for coherence).
        temperature = 0.7
        if request.task_type == "strategy":
            temperature = 0.2 # Deterministic reasoning
        elif request.task_type == "drafting":
            temperature = 0.7 # Creative flow
        elif request.task_type == "safety":
            temperature = 0.0 # Strict adherence

        # 4. Construct Decision
        return RoutingDecision(
            model_id=model_id,
            provider="openai" if "gpt" in model_id else "anthropic",
            max_tokens=4096,
            temperature=temperature,
            reasoning_effort=tier,
            rationale=f"Selected {tier} tier for {request.complexity} {request.task_type} task."
        )

    def _resolve_tier(self, request: RoutingRequest, meta: MetaProfile) -> str:
        """
        Applies Heuristics + Meta-Biases to choose the tier.
        """
        # RULE 1: Meta-Bias Override (Self-Correction)
        # If the agent realizes it's too slow, FORCE fast mode.
        if meta.bias_routing_fast:
            return "fast"

        # RULE 2: Safety is always Reasoning-Heavy or Balanced
        # Never trust a 'fast' model with safety.
        if request.task_type == "safety":
            return "balanced"

        # RULE 3: High Complexity Strategy = Reasoning Heavy
        if request.task_type == "strategy" and request.complexity == "high":
            return "reasoning_heavy"

        # RULE 4: Drafting is usually Balanced (unless low complexity)
        if request.task_type == "drafting":
            if request.complexity == "low":
                return "fast"
            return "balanced"

        # Default
        return "balanced"

# Global Singleton
ROUTER = RoutingEngine()
