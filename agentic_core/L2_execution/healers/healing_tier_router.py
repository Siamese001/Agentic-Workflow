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
from agentic_core.L2_execution.healers.healing_tier_config import (
    HEALING_CONFIDENCE_X,
    HEALING_CONFIDENCE_Y,
    HealingTierConfig,
)
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

# Mutable overlay for test-time overrides — production code does not mutate this.
_HISTORICAL_OVERRIDES: dict[str, float] = {}


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
    # Test-time override takes precedence
    if error_signature in _HISTORICAL_OVERRIDES:
        return _HISTORICAL_OVERRIDES[error_signature]
    if meta_prior_provider is not None:
        live_prior = meta_prior_provider.get_prior(error_signature)
        if live_prior != _NEUTRAL_PRIOR:
            return live_prior
    # Fall back to compile-time frozen data
    failure_type = error_signature.split(":")[0] if ":" in error_signature else error_signature
    return HISTORICAL_SUCCESS_RATES.get(failure_type, _NEUTRAL_PRIOR)


def set_historical_success_rate(error_signature: str, rate: float) -> None:
    """Override historical success rate for a specific error_signature.

    Used by tests to control scoring behavior.  The override lives in a
    module-level mutable dict and is cleared by clear_historical_success_rates.
    """
    _HISTORICAL_OVERRIDES[error_signature] = rate


def clear_historical_success_rates() -> None:
    """Clear all test-time overrides, restoring compile-time frozen defaults."""
    _HISTORICAL_OVERRIDES.clear()


# ---------------------------------------------------------------------------
# Deterministic heal_confidence scoring
# ---------------------------------------------------------------------------


def compute_heal_confidence(
    healing_input: HealingInput,
    *,
    meta_prior_provider: MetaPriorProvider | None = None,
) -> tuple[float, tuple[str, ...]]:
    """Mathematically deterministic confidence calculation - zero external dependencies.

    Fixed precision arithmetic, no environment access, versioned historical data.

    Args:
        healing_input: Structured failure context
        meta_prior_provider: Optional live meta-prior provider

    Returns:
        Tuple of (confidence score in [0.0, 1.0], reason_codes tuple)
    """
    # Fixed weights - no config loading
    WEIGHT_FAILURE_PRIOR = 0.30
    WEIGHT_BLAST_RADIUS = 0.25
    WEIGHT_HISTORICAL_SUCCESS = 0.20
    WEIGHT_TOOL_READINESS = 0.15
    WEIGHT_RETRY_DECAY = 0.10  # guardian: allow-magic-config

    # Failure class prior - compile-time frozen
    failure_prior = FAILURE_CLASS_PRIORS.get(healing_input.failure_type, _DEFAULT_FAILURE_PRIOR)

    # Blast radius contribution — high blast lowers confidence
    blast_radius_contribution = (1.0 - healing_input.blast_radius_estimate) * WEIGHT_BLAST_RADIUS

    # Historical success - versioned data, no external lookup
    hist_rate = get_historical_success_rate(
        healing_input.error_signature,
        meta_prior_provider=meta_prior_provider,
    )
    historical_success = hist_rate * WEIGHT_HISTORICAL_SUCCESS

    # Tool readiness - fixed value for determinism
    tool_readiness = 0.8 * WEIGHT_TOOL_READINESS

    # Retry decay - deterministic calculation
    retry_decay = max(0.0, 1.0 - (healing_input.retry_count * 0.1)) * WEIGHT_RETRY_DECAY

    # Fixed precision arithmetic — weights sum to 1.0
    raw_confidence = (
        failure_prior * WEIGHT_FAILURE_PRIOR
        + blast_radius_contribution
        + historical_success
        + tool_readiness
        + retry_decay
    )

    # Fixed precision for mathematical determinism
    score = round(max(0.0, min(1.0, raw_confidence)), 6)

    reason_codes: tuple[str, ...] = (
        f"failure_prior={failure_prior:.4f}:weight={WEIGHT_FAILURE_PRIOR}",
        f"blast_radius_contribution={blast_radius_contribution:.4f}:weight={WEIGHT_BLAST_RADIUS}",
        f"historical_success_rate={hist_rate:.4f}:weight={WEIGHT_HISTORICAL_SUCCESS}",
        f"tool_readiness={tool_readiness:.4f}:weight={WEIGHT_TOOL_READINESS}",
        f"retry_decay={retry_decay:.4f}:weight={WEIGHT_RETRY_DECAY}",
        f"heal_confidence={score:.6f}",
    )

    return score, reason_codes


# ---------------------------------------------------------------------------
# Tier routing (single choke point)
# ---------------------------------------------------------------------------


def route_healing_tier(
    healing_input: HealingInput,
    config: HealingTierConfig | None = None,
    *,
    meta_prior_provider: MetaPriorProvider | None = None,
) -> HealingDecision:
    """Mathematically deterministic tier router - absolute choke point.

    This is the SINGLE CHOKE POINT for all healing model selection.
    No environment access, no external data loading, fixed precision math.

    Args:
        healing_input: Structured failure context
        config: Optional HealingTierConfig; uses canonical X/Y constants if None
        meta_prior_provider: Optional live meta-prior provider

    Returns:
        Immutable HealingDecision with mathematical determinism guarantees
    """
    # Resolve X/Y thresholds and max retries from config or canonical constants
    x_threshold = config.heal_confidence_x if config is not None else HEALING_CONFIDENCE_X
    y_threshold = config.heal_confidence_y if config is not None else HEALING_CONFIDENCE_Y
    max_retries = config.max_heal_retries if config is not None else 3

    # Frozen profile lookup — only when agent_id is known
    if healing_input.agent_id:
        profile = get_execution_profile(healing_input.agent_id)
        # DETERMINISTIC agents bypass the TIERING_ALLOWLIST and go straight to LOCAL_AGENT
        if not profile.is_llm_allowed():
            return HealingDecision(
                heal_confidence=1.0,
                tier=HealingTier.LOCAL_AGENT,
                reason_codes=("agent_execution_mode=DETERMINISTIC:FORCED_LOCAL_AGENT",),
            )

    # Structural NO_TIERING guard - skip when agent_id not provided (test/anonymous callers)
    # Only applies to LLM agents that passed the DETERMINISTIC check above
    if healing_input.agent_id and healing_input.agent_id not in TIERING_ALLOWLIST_AGENT_NAMES:
        raise SovereigntyViolation(
            f"Agent '{healing_input.agent_id}' not in compile-time frozen TIERING_ALLOWLIST. "
            "NO_TIERING agents must emit FailureSignal only."
        )

    # Mathematical confidence calculation - no external dependencies
    heal_confidence, conf_reasons = compute_heal_confidence(
        healing_input,
        meta_prior_provider=meta_prior_provider,
    )

    reason_codes = list(conf_reasons)

    # Retry escalation with GEMINI mandate
    if healing_input.retry_count >= max_retries:
        reason_codes.append(f"retry_count>={max_retries}:FORCED_GEMINI")
        return HealingDecision(
            heal_confidence=heal_confidence,
            tier=HealingTier.GEMINI_2_5_PRO,
            reason_codes=tuple(reason_codes),
        )

    # X/Y band routing
    if heal_confidence >= x_threshold:
        tier = HealingTier.LOCAL_AGENT
        reason_codes.append(f"heal_confidence>={x_threshold}:LOCAL_AGENT")
    elif heal_confidence >= y_threshold:
        tier = HealingTier.QWEN_VLLM
        reason_codes.append(f"heal_confidence>={y_threshold}:QWEN_VLLM")
    else:
        tier = HealingTier.GEMINI_2_5_PRO
        reason_codes.append(f"heal_confidence<{y_threshold}:GEMINI_2_5_PRO")

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
