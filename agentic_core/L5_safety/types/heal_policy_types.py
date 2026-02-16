"""
Heal Escalation Policy Types and Decision Logic
==============================================

Pure types and decision functions for agent healing escalation policy.
This module contains only stdlib dependencies and deterministic logic.

Canonical reference: execute_ssot.py AutonomousDecisionEngine/SovereignDecisionEngine
- High confidence (>0.75): proceed deterministically, no LLM
- Medium confidence (0.50..0.75): LLM LOW tier only when enable_llm=True AND judicious gate
- Low confidence (<0.50): LLM HIGH tier only when enable_llm=True AND judicious gate

Enums:
- ReasoningTier: LOW, HIGH
- ConfidenceLevel: LOW, MEDIUM, HIGH

Dataclasses:
- HealEscalationInputs: Input parameters for escalation decision (canonical)
- LegacyHealEscalationInputs: Legacy input parameters (backward compat)
- HealEscalationDecision: Output decision with tier, proceed flag, and rationale

Functions:
- classify_confidence: Map confidence float to ConfidenceLevel
- decide_heal_escalation: Canonical escalation decision matching execute_ssot semantics
- decide_reasoning_tier: Legacy decision function (backward compat)
"""

import os
from dataclasses import dataclass
from enum import Enum


def _get_high_threshold() -> float:
    """SOVEREIGN_HIGH_CONFIDENCE env var, default 0.75."""
    return float(os.getenv("SOVEREIGN_HIGH_CONFIDENCE", "0.75"))


def _get_medium_threshold() -> float:
    """SOVEREIGN_MEDIUM_CONFIDENCE env var, default 0.50."""
    return float(os.getenv("SOVEREIGN_MEDIUM_CONFIDENCE", "0.50"))


class ReasoningTier(Enum):
    """Reasoning tier for agent healing escalation."""

    LOW = "LOW"
    HIGH = "HIGH"


class ConfidenceLevel(Enum):
    """Confidence level classification."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class HealEscalationInputs:
    """Inputs for heal escalation decision (canonical).

    Attributes:
        confidence_value: Confidence score 0.0..1.0
        enable_llm: Whether LLM escalation is permitted
        task_complexity: Task complexity 0..10
        cost_budget: Cost budget (unused in decision logic)
        latency_budget_ms: Latency budget in ms (unused in decision logic)
        safety_risk: Safety risk 0..10
        prior_failures: Number of prior healing failures (>=0)
    """

    confidence_value: float  # 0.0..1.0
    enable_llm: bool
    task_complexity: int  # 0..10
    cost_budget: int = 100
    latency_budget_ms: int = 5000
    safety_risk: int = 0  # 0..10
    prior_failures: int = 0  # >=0


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


def classify_confidence(confidence: float) -> ConfidenceLevel:
    """Classify confidence value into discrete levels.

    Uses environment-sourced thresholds:
    - HIGH: confidence > SOVEREIGN_HIGH_CONFIDENCE (default 0.75)
    - MEDIUM: SOVEREIGN_MEDIUM_CONFIDENCE <= confidence <= SOVEREIGN_HIGH_CONFIDENCE
    - LOW: confidence < SOVEREIGN_MEDIUM_CONFIDENCE (default 0.50)

    Args:
        confidence: Confidence value between 0.0 and 1.0

    Returns:
        ConfidenceLevel classification

    Raises:
        ValueError: If confidence is not in [0.0, 1.0]
    """
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(f"Confidence must be in [0.0, 1.0], got {confidence}")

    high_threshold = _get_high_threshold()
    medium_threshold = _get_medium_threshold()

    if confidence > high_threshold:
        return ConfidenceLevel.HIGH
    elif confidence >= medium_threshold:
        return ConfidenceLevel.MEDIUM
    else:
        return ConfidenceLevel.LOW


def decide_heal_escalation(inputs: HealEscalationInputs) -> HealEscalationDecision:
    """Canonical escalation decision matching execute_ssot.py semantics.

    Decision rules (deterministic, ordered):
    1. Validate input ranges
    2. High confidence (>0.75): proceed=True, tier=None (no LLM)
    3. Medium confidence (0.50..0.75):
       - proceed=True only if enable_llm AND task_complexity >= 5 (judicious gate)
       - tier=LOW when proceeding
    4. Low confidence (<0.50):
       - proceed=True only if enable_llm AND (task_complexity >= 7 OR prior_failures >= 1)
       - tier=HIGH when proceeding
    5. Otherwise proceed=False with explicit rationale

    Args:
        inputs: Heal escalation inputs

    Returns:
        HealEscalationDecision with proceed, tier, and rationale

    Raises:
        ValueError: If any input validation fails
    """
    if not 0.0 <= inputs.confidence_value <= 1.0:
        raise ValueError(f"confidence_value must be in [0.0, 1.0], got {inputs.confidence_value}")
    if not 0 <= inputs.task_complexity <= 10:
        raise ValueError(f"task_complexity must be in 0..10, got {inputs.task_complexity}")
    if not 0 <= inputs.safety_risk <= 10:
        raise ValueError(f"safety_risk must be in 0..10, got {inputs.safety_risk}")
    if inputs.prior_failures < 0:
        raise ValueError(f"prior_failures must be >= 0, got {inputs.prior_failures}")

    high_threshold = _get_high_threshold()
    medium_threshold = _get_medium_threshold()
    confidence = inputs.confidence_value

    if confidence > high_threshold:
        return HealEscalationDecision(
            proceed=True,
            tier=None,
            rationale=f"High confidence ({confidence:.2f} > {high_threshold}): sovereign auto-proceed",
            threshold_used="HIGH_CONF_AUTO",
        )

    if confidence >= medium_threshold:
        if inputs.enable_llm and inputs.task_complexity >= 5:
            return HealEscalationDecision(
                proceed=True,
                tier=ReasoningTier.LOW,
                rationale=f"Medium confidence ({confidence:.2f}): LLM LOW tier, complexity={inputs.task_complexity}",
                threshold_used="MEDIUM_CONF_LLM_LOW",
            )
        elif not inputs.enable_llm:
            return HealEscalationDecision(
                proceed=False,
                tier=None,
                rationale=f"Medium confidence ({confidence:.2f}) requires LLM arbitration (disabled)",
                threshold_used="MEDIUM_CONF_LLM_DISABLED",
            )
        else:
            return HealEscalationDecision(
                proceed=False,
                tier=None,
                rationale=f"Medium confidence ({confidence:.2f}): task_complexity={inputs.task_complexity} < 5 (judicious gate)",
                threshold_used="MEDIUM_CONF_JUDICIOUS_BLOCK",
            )

    judicious_low_gate = inputs.task_complexity >= 7 or inputs.prior_failures >= 1
    if inputs.enable_llm and judicious_low_gate:
        return HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.HIGH,
            rationale=f"Low confidence ({confidence:.2f}): LLM HIGH tier, complexity={inputs.task_complexity}, failures={inputs.prior_failures}",
            threshold_used="LOW_CONF_LLM_HIGH",
        )
    elif not inputs.enable_llm:
        return HealEscalationDecision(
            proceed=False,
            tier=None,
            rationale=f"Low confidence ({confidence:.2f}) requires advanced reasoning (LLM disabled)",
            threshold_used="LOW_CONF_LLM_DISABLED",
        )
    else:
        return HealEscalationDecision(
            proceed=False,
            tier=None,
            rationale=f"Low confidence ({confidence:.2f}): judicious gate not met (complexity={inputs.task_complexity}, failures={inputs.prior_failures})",
            threshold_used="LOW_CONF_JUDICIOUS_BLOCK",
        )


def decide_reasoning_tier(inputs: LegacyHealEscalationInputs) -> HealEscalationDecision:
    """Legacy decision function for reasoning tier escalation.

    DEPRECATED: Use decide_heal_escalation() for new code.

    Decision rules (deterministic, ordered):
    A) Validate input ranges
    B) Trivial no-escalation rule
    C) Escalate to HIGH if ANY condition met
    D) Otherwise LOW

    Args:
        inputs: Legacy heal escalation inputs

    Returns:
        HealEscalationDecision with tier and rationale

    Raises:
        ValueError: If any input validation fails
    """
    if not 0 <= inputs.task_complexity <= 10:
        raise ValueError(f"task_complexity must be in 0..10, got {inputs.task_complexity}")
    if not 0 <= inputs.safety_risk <= 10:
        raise ValueError(f"safety_risk must be in 0..10, got {inputs.safety_risk}")
    if inputs.retry_count < 0:
        raise ValueError(f"retry_count must be >= 0, got {inputs.retry_count}")

    high_threshold = _get_high_threshold()

    if inputs.task_complexity < 3 and inputs.safety_risk < 7 and inputs.retry_count <= 2:
        return HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.LOW,
            rationale="Task is trivial: low complexity, low safety risk, few retries",
            threshold_used="TRIVIAL",
        )

    if inputs.confidence < high_threshold:
        return HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.HIGH,
            rationale=f"Low confidence ({inputs.confidence:.2f} < {high_threshold}) triggers escalation",
            threshold_used=f"CONF_LT_{high_threshold}",
        )

    if inputs.task_complexity >= 8:
        return HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.HIGH,
            rationale="High task complexity triggers escalation",
            threshold_used="COMPLEXITY_GE_8",
        )

    if inputs.safety_risk >= 7:
        return HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.HIGH,
            rationale="High safety risk triggers escalation",
            threshold_used="SAFETY_GE_7",
        )

    if inputs.retry_count > 2:
        return HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.HIGH,
            rationale="Multiple retries trigger escalation",
            threshold_used="RETRY_GT_2",
        )

    return HealEscalationDecision(
        proceed=True,
        tier=ReasoningTier.LOW,
        rationale="No escalation triggers met; default to low tier",
        threshold_used="DEFAULT_LOW",
    )
