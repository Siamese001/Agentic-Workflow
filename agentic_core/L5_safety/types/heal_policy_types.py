"""
Heal Escalation Policy Types and Decision Logic
==============================================

Pure types and decision functions for agent healing escalation policy.
This module contains only stdlib dependencies and deterministic logic.

Score-based routing (replaces legacy confidence-based system):
- S <= 13: DETERMINISTIC  — agent-native logic, no LLM
- S 14-26: QWEN           — Qwen 2.5 14B advises the healing plan
- S > 26:  GEMINI         — Gemini 2.5 Pro handles complex reasoning

Healing always proceeds (proceed=True) once routing dispatches by score.
Confidence is only an intermediate value that contributes factors C, A, F
to the score S. It is never used as a hard gate.

Enums:
- ReasoningTier: LOW (Qwen), HIGH (Gemini)
- ScoreBand: DETERMINISTIC, QWEN, GEMINI
- ConfidenceLevel: alias of ScoreBand for backward compat

Dataclasses:
- HealEscalationInputs: Input parameters — score (canonical), legacy fields kept for compat
- LegacyHealEscalationInputs: Legacy input parameters (backward compat)
- HealEscalationDecision: Output decision with tier, proceed flag, and rationale

Functions:
- classify_score: Map routing score S to ScoreBand
- classify_confidence: DEPRECATED — maps confidence float to ScoreBand (approximation)
- decide_heal_escalation: Score-based escalation, always proceed=True
- decide_reasoning_tier: DEPRECATED legacy function, always proceed=True
"""

import os
from dataclasses import dataclass
from enum import Enum

# Score thresholds matching compute_routing_decision in execute_ssot.py
SCORE_THRESHOLD_DET: int = 13   # S <= 13 → DETERMINISTIC (agent-native)
SCORE_THRESHOLD_QWEN: int = 26  # S <= 26 → QWEN; S > 26 → GEMINI


class ReasoningTier(Enum):
    """LLM reasoning tier for agent healing escalation."""

    LOW = "LOW"   # Qwen 2.5 14B — medium-complexity routing
    HIGH = "HIGH" # Gemini 2.5 Pro — high-complexity routing


class ScoreBand(Enum):
    """Score band classification (replaces ConfidenceLevel)."""

    DETERMINISTIC = "DETERMINISTIC"  # S <= 13: agent-native, no LLM
    QWEN = "QWEN"                    # 14 <= S <= 26: Qwen 2.5 advises
    GEMINI = "GEMINI"                # S > 26: Gemini 2.5 Pro


# Backward-compat alias — old code referencing ConfidenceLevel still works
ConfidenceLevel = ScoreBand


@dataclass(frozen=True)
class HealEscalationInputs:
    """Inputs for heal escalation decision (canonical).

    Attributes:
        score: Routing score S from _route_decision (C+A+F+B+N factors). Primary input.
        enable_llm: Whether LLM escalation is permitted (controls tier activation).
        confidence_value: DEPRECATED — kept for backward compat only, not used for gating.
        task_complexity: DEPRECATED — kept for backward compat only.
        cost_budget: Unused in decision logic.
        latency_budget_ms: Unused in decision logic.
        safety_risk: DEPRECATED — kept for backward compat only.
        prior_failures: DEPRECATED — kept for backward compat only.
    """

    score: int = 0              # canonical routing score S
    enable_llm: bool = False
    confidence_value: float = 0.75  # kept for backward compat, not used for gating
    task_complexity: int = 5    # kept for backward compat
    cost_budget: int = 100
    latency_budget_ms: int = 5000
    safety_risk: int = 0        # kept for backward compat
    prior_failures: int = 0     # kept for backward compat


@dataclass(frozen=True)
class LegacyHealEscalationInputs:
    """Legacy inputs for heal escalation decision (backward compat)."""

    task_complexity: int  # 0..10
    confidence: float  # 0.0..1.0
    safety_risk: int  # 0..10
    retry_count: int  # >=0
    cost_budget: int | None = None
    latency_budget: int | None = None


@dataclass(frozen=True)
class HealEscalationDecision:
    """Decision result for heal escalation.

    Attributes:
        proceed: Whether healing should proceed
        tier: Reasoning tier (None if proceed=False or no LLM needed)
        rationale: Human-readable explanation
        threshold_used: Short deterministic token for debugging
    """

    proceed: bool
    tier: ReasoningTier | None
    rationale: str
    threshold_used: str  # Short, deterministic token


def classify_score(score: int) -> ScoreBand:
    """Classify routing score S into score band.

    Args:
        score: Routing score S from _route_decision.

    Returns:
        ScoreBand: DETERMINISTIC, QWEN, or GEMINI.
    """
    if score <= SCORE_THRESHOLD_DET:
        return ScoreBand.DETERMINISTIC
    elif score <= SCORE_THRESHOLD_QWEN:
        return ScoreBand.QWEN
    else:
        return ScoreBand.GEMINI


def classify_confidence(confidence: float) -> ScoreBand:
    """DEPRECATED: approximate mapping from confidence float to ScoreBand.

    Use classify_score(score) for new code.
    High confidence → low score → DETERMINISTIC.
    """
    if confidence > 0.75:
        return ScoreBand.DETERMINISTIC
    elif confidence >= 0.50:
        return ScoreBand.QWEN
    else:
        return ScoreBand.GEMINI


def decide_heal_escalation(inputs: HealEscalationInputs) -> HealEscalationDecision:
    """Score-based escalation decision. Healing always proceeds (proceed=True).

    Routing rules (by score S):
    - S <= 13: DETERMINISTIC — agent-native logic, no LLM needed
    - S 14-26: QWEN tier    — Qwen 2.5 14B advises the healing plan
    - S > 26:  GEMINI tier  — Gemini 2.5 Pro handles complex reasoning

    Args:
        inputs: Heal escalation inputs (score is the canonical field).

    Returns:
        HealEscalationDecision with proceed=True and appropriate tier.
    """
    score = inputs.score
    band = classify_score(score)

    if band == ScoreBand.DETERMINISTIC:
        return HealEscalationDecision(
            proceed=True,
            tier=None,
            rationale=f"Score S={score} <= {SCORE_THRESHOLD_DET}: agent-native logic governs, no LLM needed",
            threshold_used="SCORE_DET",
        )
    elif band == ScoreBand.QWEN:
        return HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.LOW,
            rationale=f"Score S={score} in [{SCORE_THRESHOLD_DET + 1},{SCORE_THRESHOLD_QWEN}]: Qwen 2.5 14B advises healing plan",
            threshold_used="SCORE_QWEN",
        )
    else:
        return HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.HIGH,
            rationale=f"Score S={score} > {SCORE_THRESHOLD_QWEN}: Gemini 2.5 Pro handles complex reasoning",
            threshold_used="SCORE_GEMINI",
        )


def decide_reasoning_tier(inputs: LegacyHealEscalationInputs) -> HealEscalationDecision:
    """DEPRECATED legacy function. Always proceeds; routes by complexity.

    Use decide_heal_escalation() with score for new code.
    """
    if not 0 <= inputs.task_complexity <= 10:
        raise ValueError(f"task_complexity must be in 0..10, got {inputs.task_complexity}")
    if not 0 <= inputs.safety_risk <= 10:
        raise ValueError(f"safety_risk must be in 0..10, got {inputs.safety_risk}")
    if inputs.retry_count < 0:
        raise ValueError(f"retry_count must be >= 0, got {inputs.retry_count}")

    if inputs.task_complexity < 3 and inputs.safety_risk < 7 and inputs.retry_count <= 2:
        return HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.LOW,
            rationale="Task is trivial: low complexity, low safety risk, few retries",
            threshold_used="TRIVIAL",
        )

    if inputs.task_complexity >= 8 or inputs.safety_risk >= 7 or inputs.retry_count > 2:
        return HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.HIGH,
            rationale="High complexity/risk/retries: Gemini escalation",
            threshold_used="LEGACY_HIGH",
        )

    return HealEscalationDecision(
        proceed=True,
        tier=ReasoningTier.LOW,
        rationale="No escalation triggers met; default to Qwen tier",
        threshold_used="LEGACY_LOW",
    )
