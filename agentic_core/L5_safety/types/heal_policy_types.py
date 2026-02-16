"""
Heal Escalation Policy Types and Decision Logic
==============================================

Pure types and decision functions for agent healing escalation policy.
This module contains only stdlib dependencies and deterministic logic.

Enums:
- ReasoningTier: LOW, HIGH
- ConfidenceLevel: LOW, MEDIUM, HIGH, VERY_HIGH

Dataclasses:
- HealEscalationInputs: Input parameters for escalation decision
- HealEscalationDecision: Output decision with tier and rationale

Functions:
- classify_confidence: Map confidence float to ConfidenceLevel
- decide_reasoning_tier: Pure decision function for reasoning tier
"""

from dataclasses import dataclass
from enum import Enum


class ReasoningTier(Enum):
    """Reasoning tier for agent healing escalation."""

    LOW = "LOW"
    HIGH = "HIGH"


class ConfidenceLevel(Enum):
    """Confidence level classification."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


@dataclass(frozen=True)
class HealEscalationInputs:
    """Inputs for heal escalation decision."""

    task_complexity: int  # 0..10
    confidence: float  # 0.0..1.0
    safety_risk: int  # 0..10
    retry_count: int  # >=0
    cost_budget: int | None = None  # Optional; not used in decision logic
    latency_budget: int | None = None  # Optional; not used in decision logic


@dataclass(frozen=True)
class HealEscalationDecision:
    """Decision result for heal escalation."""

    tier: ReasoningTier
    rationale: str
    threshold_used: str  # Short, deterministic token


def classify_confidence(confidence: float) -> ConfidenceLevel:
    """Classify confidence value into discrete levels.

    Args:
        confidence: Confidence value between 0.0 and 1.0

    Returns:
        ConfidenceLevel classification

    Raises:
        ValueError: If confidence is not in [0.0, 1.0]
    """
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(f"Confidence must be in [0.0, 1.0], got {confidence}")

    if confidence >= 0.85:
        return ConfidenceLevel.VERY_HIGH
    elif confidence >= 0.70:
        return ConfidenceLevel.HIGH
    elif confidence >= 0.50:
        return ConfidenceLevel.MEDIUM
    else:
        return ConfidenceLevel.LOW


def decide_reasoning_tier(inputs: HealEscalationInputs) -> HealEscalationDecision:
    """Pure decision function for reasoning tier escalation.

    Decision rules (deterministic, ordered):
    A) Validate input ranges
    B) Trivial no-escalation rule
    C) Escalate to HIGH if ANY condition met
    D) Otherwise LOW

    Args:
        inputs: Heal escalation inputs

    Returns:
        HealEscalationDecision with tier and rationale

    Raises:
        ValueError: If any input validation fails
    """
    # A) Validate inputs
    if not 0 <= inputs.task_complexity <= 10:
        raise ValueError(f"task_complexity must be in 0..10, got {inputs.task_complexity}")
    if not 0 <= inputs.safety_risk <= 10:
        raise ValueError(f"safety_risk must be in 0..10, got {inputs.safety_risk}")
    if inputs.retry_count < 0:
        raise ValueError(f"retry_count must be >= 0, got {inputs.retry_count}")

    # B) Trivial no-escalation rule
    if inputs.task_complexity < 3 and inputs.safety_risk < 7 and inputs.retry_count <= 2:
        return HealEscalationDecision(
            tier=ReasoningTier.LOW,
            rationale="Task is trivial: low complexity, low safety risk, few retries",
            threshold_used="TRIVIAL",
        )

    # C) Escalate to HIGH if ANY condition met
    if inputs.confidence < 0.70:
        return HealEscalationDecision(
            tier=ReasoningTier.HIGH,
            rationale="Low confidence triggers escalation",
            threshold_used="CONF_LT_0.70",
        )

    if inputs.task_complexity >= 8:
        return HealEscalationDecision(
            tier=ReasoningTier.HIGH,
            rationale="High task complexity triggers escalation",
            threshold_used="COMPLEXITY_GE_8",
        )

    if inputs.safety_risk >= 7:
        return HealEscalationDecision(
            tier=ReasoningTier.HIGH,
            rationale="High safety risk triggers escalation",
            threshold_used="SAFETY_GE_7",
        )

    if inputs.retry_count > 2:
        return HealEscalationDecision(
            tier=ReasoningTier.HIGH,
            rationale="Multiple retries trigger escalation",
            threshold_used="RETRY_GT_2",
        )

    # D) Otherwise LOW
    return HealEscalationDecision(
        tier=ReasoningTier.LOW,
        rationale="No escalation triggers met; default to low tier",
        threshold_used="DEFAULT_LOW",
    )
