"""
Qwen Meta-Learning Protection - Boundary Enforcement

Ensures Qwen metrics only update confidence priors and never modify
routing thresholds or other architectural constants.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# FIXED THRESHOLDS - IMMUTABLE BY META-LEARNING
HEALING_CONFIDENCE_X = 0.75  # Upper threshold - CANNOT BE MODIFIED
HEALING_CONFIDENCE_Y = 0.40  # Lower threshold - CANNOT BE MODIFIED

# Historical success rate store (in production backed by L4)
_historical_success_rates: dict[str, float] = {}
_NEUTRAL_PRIOR = 0.50


def get_historical_success_rate(error_signature: str) -> float:
    """Look up historical success rate for an error signature."""
    return _historical_success_rates.get(error_signature, _NEUTRAL_PRIOR)


def set_historical_success_rate(error_signature: str, rate: float) -> None:
    """Record historical success rate (allowed meta-learning operation)."""
    if not (0.0 <= rate <= 1.0):
        raise ValueError(f"rate must be in [0.0, 1.0], got {rate}")
    _historical_success_rates[error_signature] = rate


def update_qwen_confidence_prior(error_signature: str, success: bool) -> None:
    """
    Qwen metrics may update healer confidence priors ONLY.

    ALLOWED:
    - Historical success rate updates
    - Failure class prior adjustments
    - Tool readiness certainty updates

    FORBIDDEN:
    - HEALING_CONFIDENCE_X modification
    - HEALING_CONFIDENCE_Y modification
    - Routing election logic changes
    - Safety threshold modifications
    - Embedding scoring changes
    - RAG cutoff modifications
    """
    # Update historical success rate (allowed)
    current_rate = get_historical_success_rate(error_signature)
    if success:
        new_rate = min(1.0, current_rate + 0.1)
    else:
        new_rate = max(0.0, current_rate - 0.1)
    set_historical_success_rate(error_signature, new_rate)

    logger.info(f"Updated confidence prior for {error_signature}: {current_rate:.2f} -> {new_rate:.2f}")

    # THRESHOLDS REMAIN IMMUTABLE
    assert HEALING_CONFIDENCE_X == 0.75, "X threshold is immutable"
    assert HEALING_CONFIDENCE_Y == 0.40, "Y threshold is immutable"


def validate_threshold_immutability() -> None:
    """Ensure healing thresholds cannot be modified."""
    # These values must never change
    assert HEALING_CONFIDENCE_X == 0.75, f"X threshold modified: {HEALING_CONFIDENCE_X}"
    assert HEALING_CONFIDENCE_Y == 0.40, f"Y threshold modified: {HEALING_CONFIDENCE_Y}"

    logger.debug("Threshold immutability validated")


def clear_historical_success_rates() -> None:
    """Clear all historical success rates (for testing)."""
    _historical_success_rates.clear()


__all__ = [
    "HEALING_CONFIDENCE_X",
    "HEALING_CONFIDENCE_Y",
    "get_historical_success_rate",
    "set_historical_success_rate",
    "update_qwen_confidence_prior",
    "validate_threshold_immutability",
    "clear_historical_success_rates",
]
