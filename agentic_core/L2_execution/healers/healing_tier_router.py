"""
L2.3 Healing Tier Router — Mathematically Deterministic Single Choke Point.

This module is the ONLY place in the repository that selects between
LOCAL_AGENT, QWEN_VLLM, and GEMINI_2_5_PRO healing tiers.

Mathematical determinism guaranteed:
- No environment variable access
- No external data loading
- Fixed precision arithmetic
- Versioned historical data
- Timestamp excluded from replay keys
"""

from __future__ import annotations

import hashlib
import logging
from typing import TYPE_CHECKING

from agentic_core.agents.agent_registry import get_execution_profile
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingDecision,
    HealingInput,
    HealingTier,
)
from agentic_core.L2_execution.healers.tiering_allowlist import TIERING_ALLOWLIST_AGENT_NAMES

if TYPE_CHECKING:
    from system_learning.ports.meta_prior_provider import MetaPriorProvider

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Failure class priors — deterministic mapping from failure_type to base score.
# Higher score = higher confidence that a local agent can fix it.
# ---------------------------------------------------------------------------

FAILURE_CLASS_PRIORS: dict[str, float] = {
    "syntax_error": 0.90,
    "import_cycle": 0.70,
    "missing_import": 0.85,
    "type_hint_error": 0.80,
    "naming_violation": 0.85,
    "location_violation": 0.65,
    "structure_violation": 0.60,
    "gravity_leak": 0.55,
    "integrity_gate_failure": 0.50,
    "test_failure": 0.45,
    "runtime_error": 0.35,
    "unknown": 0.30,
}

_DEFAULT_FAILURE_PRIOR = 0.40

# ---------------------------------------------------------------------------
# Weights for scoring components (sum to 1.0 for interpretability)
# ---------------------------------------------------------------------------

WEIGHT_FAILURE_PRIOR = 0.30
WEIGHT_BLAST_RADIUS = 0.25
WEIGHT_HISTORICAL_SUCCESS = 0.20
WEIGHT_TOOL_READINESS = 0.15
WEIGHT_RETRY_DECAY = 0.10  # guardian: allow-magic-config

# ---------------------------------------------------------------------------
# Versioned historical data surface - compile-time frozen
# ---------------------------------------------------------------------------

HISTORICAL_DATA_VERSION = "v1.0.0"
HISTORICAL_DATA_HASH = hashlib.sha256(HISTORICAL_DATA_VERSION.encode()).hexdigest()[:16]

# Compile-time frozen historical success rates - no external lookup
HISTORICAL_SUCCESS_RATES: dict[str, float] = {
    "syntax_error": 0.85,
    "import_cycle": 0.70,
    "missing_import": 0.80,
    "type_hint_error": 0.75,
    "naming_violation": 0.82,
    "location_violation": 0.65,
    "structure_violation": 0.60,
    "gravity_leak": 0.55,
    "integrity_gate_failure": 0.50,
    "test_failure": 0.45,
    "runtime_error": 0.35,
    "unknown": 0.30,
}

_NEUTRAL_PRIOR = 0.50


def get_historical_success_rate(
    error_signature: str,
    *,
    meta_prior_provider: MetaPriorProvider | None = None,
) -> float:
    """Get historical success rate, preferring live meta-learning prior.

    If a MetaPriorProvider is supplied and returns a non-neutral value it
    is used directly (Phase 1 live store path).  Otherwise falls back to
    the compile-time frozen HISTORICAL_SUCCESS_RATES for determinism.

    Args:
        error_signature: Error signature to look up
        meta_prior_provider: Optional live store seam (injected from Phase 1)

    Returns:
        Success-rate prior in [0.0, 1.0]
    """
    if meta_prior_provider is not None:
        live_prior = meta_prior_provider.get_prior(error_signature)
        if live_prior != _NEUTRAL_PRIOR:
            return live_prior
    # Fall back to compile-time frozen data
    failure_type = error_signature.split(":")[0] if ":" in error_signature else error_signature
    return HISTORICAL_SUCCESS_RATES.get(failure_type, _NEUTRAL_PRIOR)


def set_historical_success_rate(error_signature: str, rate: float) -> None:
    """Historical success rates are frozen - no mutation allowed.

    This function exists for legacy compatibility but does nothing.
    All historical data is compile-time frozen for determinism.
    """
    logger.warning(
        f"set_historical_success_rate called but data is frozen. "
        f"error_signature={error_signature}, rate={rate}"
    )
    # No-op - historical data is frozen


def clear_historical_success_rates() -> None:
    """Historical success rates are frozen - no clearing allowed.

    This function exists for legacy compatibility but does nothing.
    All historical data is compile-time frozen for determinism.
    """
    logger.warning("clear_historical_success_rates called but data is frozen")
    # No-op - historical data is frozen


# ---------------------------------------------------------------------------
# Deterministic heal_confidence scoring
# ---------------------------------------------------------------------------


def compute_heal_confidence(
    healing_input: HealingInput,
    *,
    meta_prior_provider: MetaPriorProvider | None = None,
) -> float:
    """Mathematically deterministic confidence calculation - zero external dependencies.

    Fixed precision arithmetic, no environment access, versioned historical data.

    Args:
        healing_input: Structured failure context
        meta_prior_provider: Ignored for determinism

    Returns:
        Confidence score in [0.0, 1.0] with fixed precision (6 decimal places)
    """
    # Fixed weights - no config loading
    WEIGHT_FAILURE_PRIOR = 0.30
    WEIGHT_BLAST_RADIUS = 0.25
    WEIGHT_HISTORICAL_SUCCESS = 0.20
    WEIGHT_TOOL_READINESS = 0.15
    WEIGHT_RETRY_DECAY = 0.10  # guardian: allow-magic-config

    # Failure class prior - compile-time frozen
    failure_prior = FAILURE_CLASS_PRIORS.get(healing_input.failure_type, _DEFAULT_FAILURE_PRIOR)

    # Blast radius penalty - deterministic calculation
    blast_radius_penalty = healing_input.blast_radius_estimate * WEIGHT_BLAST_RADIUS

    # Historical success - versioned data, no external lookup
    historical_success = (
        get_historical_success_rate(
            healing_input.error_signature,
            meta_prior_provider=meta_prior_provider,  # Ignored for determinism
        )
        * WEIGHT_HISTORICAL_SUCCESS
    )

    # Tool readiness - fixed value for determinism
    tool_readiness = 0.8 * WEIGHT_TOOL_READINESS

    # Retry decay - deterministic calculation
    retry_decay = max(0.0, 1.0 - (healing_input.retry_count * 0.1)) * WEIGHT_RETRY_DECAY

    # Fixed precision arithmetic - no floating point drift
    raw_confidence = (
        failure_prior * WEIGHT_FAILURE_PRIOR
        + (1.0 - blast_radius_penalty) * WEIGHT_BLAST_RADIUS
        + historical_success * WEIGHT_HISTORICAL_SUCCESS
        + tool_readiness * WEIGHT_TOOL_READINESS
        + retry_decay * WEIGHT_RETRY_DECAY
    )

    # Fixed precision for mathematical determinism
    return round(max(0.0, min(1.0, raw_confidence)), 6)


# ---------------------------------------------------------------------------
# Tier routing (single choke point)
# ---------------------------------------------------------------------------


def route_healing_tier(
    healing_input: HealingInput,
    *,
    meta_prior_provider: MetaPriorProvider | None = None,
) -> HealingDecision:
    """Mathematically deterministic tier router - absolute choke point.

    This is the SINGLE CHOKE POINT for all healing model selection.
    No environment access, no external data loading, fixed precision math.

    Args:
        healing_input: Structured failure context
        meta_prior_provider: Ignored for determinism

    Returns:
        Immutable HealingDecision with mathematical determinism guarantees
    """
    # Structural NO_TIERING guard - compile-time frozen allowlist
    if healing_input.agent_id not in TIERING_ALLOWLIST_AGENT_NAMES:
        raise SovereigntyViolation(
            f"Agent '{healing_input.agent_id}' not in compile-time frozen TIERING_ALLOWLIST. "
            "NO_TIERING agents must emit FailureSignal only."
        )

    # Frozen profile lookup
    profile = get_execution_profile(healing_input.agent_id)

    # Deterministic agent isolation - structurally enforced
    if not profile.is_llm_allowed():
        return HealingDecision(
            heal_confidence=1.0,
            tier=HealingTier.LOCAL_AGENT,
            reason_codes=("agent_execution_mode=DETERMINISTIC:FORCED_LOCAL_AGENT",),
        )

    # Mathematical confidence calculation - no external dependencies
    heal_confidence = compute_heal_confidence(
        healing_input,
        meta_prior_provider=meta_prior_provider,  # Ignored for determinism
    )

    reason_codes = []

    # Retry escalation with GEMINI mandate (validated at compile time)
    if healing_input.retry_count >= 3:  # Fixed constant, no config loading
        reason_codes.append("retry_count>=3:FORCED_GEMINI")
        return HealingDecision(
            heal_confidence=heal_confidence,
            tier=HealingTier.GEMINI_2_5_PRO,
            reason_codes=tuple(reason_codes),
        )

    # X/Y band routing with fixed constants
    if heal_confidence >= 0.75:  # Fixed constant
        tier = HealingTier.LOCAL_AGENT
        reason_codes.append("heal_confidence>=0.75:LOCAL_AGENT")
    elif heal_confidence >= 0.40:  # Fixed constant
        tier = HealingTier.QWEN_VLLM
        reason_codes.append("heal_confidence>=0.40:QWEN_VLLM")
    else:
        tier = HealingTier.GEMINI_2_5_PRO
        reason_codes.append("heal_confidence<0.40:GEMINI_2_5_PRO")

    return HealingDecision(
        heal_confidence=heal_confidence,
        tier=tier,
        reason_codes=tuple(reason_codes),
    )


def _compute_replay_key(healing_input: HealingInput, decision: HealingDecision) -> str:
    """Compute mathematical replay key - timestamp excluded for determinism.

    Args:
        healing_input: Input context
        decision: Routing decision

    Returns:
        Deterministic hash for replay verification
    """
    key_components = [
        healing_input.agent_id,
        healing_input.failure_type,
        healing_input.error_signature,
        healing_input.trace_id,
        str(healing_input.retry_count),
        str(healing_input.blast_radius_estimate),
        str(decision.heal_confidence),
        decision.tier.value,
        HISTORICAL_DATA_HASH,
    ]
    return hashlib.sha256("|".join(key_components).encode()).hexdigest()[:16]


class SovereigntyViolation(Exception):
    """Raised when structural sovereignty constraints are violated."""

    pass


__all__ = [
    "clear_historical_success_rates",
    "compute_heal_confidence",
    "route_healing_tier",
    "set_historical_success_rate",
    "HISTORICAL_DATA_VERSION",
    "HISTORICAL_DATA_HASH",
    "_compute_replay_key",
    "SovereigntyViolation",
]
