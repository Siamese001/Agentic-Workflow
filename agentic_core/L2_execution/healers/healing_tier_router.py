"""
L2.3 Healing Tier Router — Single Choke Point for All Heal Model Selection.

This module is the ONLY place in the repository that selects between
LOCAL_AGENT, QWEN_VLLM, and GEMINI_2_5_PRO healing tiers.

Scoring is fully deterministic:
- failure class prior
- blast radius estimate (bounded 0..1)
- historical success rate lookup (neutral prior if unavailable)
- tool readiness certainty
- retry decay

All components are persisted into the returned HealingDecision for auditability.
"""

from __future__ import annotations

from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingDecision,
    HealingInput,
    HealingTier,
)
from agentic_core.L0_routing.types.guardian_contract import V15HardFailAbort
from agentic_core.agents.agent_registry import get_profile

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
# Historical success rate store (stub — in production backed by L4)
# ---------------------------------------------------------------------------

_HISTORICAL_SUCCESS_RATES: dict[str, float] = {}
_NEUTRAL_PRIOR = 0.50


def get_historical_success_rate(error_signature: str) -> float:
    """Look up historical success rate for an error signature.

    Returns neutral prior (0.50) if no history is available.
    """
    return _HISTORICAL_SUCCESS_RATES.get(error_signature, _NEUTRAL_PRIOR)


def set_historical_success_rate(error_signature: str, rate: float) -> None:
    """Record historical success rate (for testing / L4 integration)."""
    if not (0.0 <= rate <= 1.0):
        raise ValueError(f"rate must be in [0.0, 1.0], got {rate}")
    _HISTORICAL_SUCCESS_RATES[error_signature] = rate


def clear_historical_success_rates() -> None:
    """Clear all historical success rates (for testing)."""
    _HISTORICAL_SUCCESS_RATES.clear()


# ---------------------------------------------------------------------------
# Deterministic heal_confidence scoring
# ---------------------------------------------------------------------------


def compute_heal_confidence(healing_input: HealingInput) -> tuple[float, list[str]]:
    """Compute deterministic heal_confidence from structured failure context.

    Returns:
        (heal_confidence, reason_codes) where heal_confidence is in [0.0, 1.0]
        and reason_codes lists all contributing factors.
    """
    reason_codes: list[str] = []

    # 1. Failure class prior
    failure_prior = FAILURE_CLASS_PRIORS.get(healing_input.failure_type, _DEFAULT_FAILURE_PRIOR)
    reason_codes.append(f"failure_prior={failure_prior:.2f}")

    # 2. Blast radius (inverted: smaller blast = higher confidence)
    blast_component = 1.0 - healing_input.blast_radius_estimate
    reason_codes.append(f"blast_radius_inv={blast_component:.2f}")

    # 3. Historical success rate
    historical_rate = get_historical_success_rate(healing_input.error_signature)
    reason_codes.append(f"historical_success={historical_rate:.2f}")

    # 4. Tool readiness certainty (fraction of required tools available)
    if healing_input.required_tools:
        tool_readiness = 1.0  # Assume all tools available in deterministic mode
    else:
        tool_readiness = 1.0  # No tools required = fully ready
    reason_codes.append(f"tool_readiness={tool_readiness:.2f}")

    # 5. Retry decay (exponential decay with retry count)
    retry_decay = max(0.0, 1.0 - (healing_input.retry_count * 0.25))
    reason_codes.append(f"retry_decay={retry_decay:.2f}")

    # Weighted sum
    heal_confidence = (
        WEIGHT_FAILURE_PRIOR * failure_prior
        + WEIGHT_BLAST_RADIUS * blast_component
        + WEIGHT_HISTORICAL_SUCCESS * historical_rate
        + WEIGHT_TOOL_READINESS * tool_readiness
        + WEIGHT_RETRY_DECAY * retry_decay
    )

    # Clamp to [0.0, 1.0]
    heal_confidence = max(0.0, min(1.0, heal_confidence))
    heal_confidence = round(heal_confidence, 6)

    reason_codes.append(f"heal_confidence={heal_confidence:.6f}")

    return heal_confidence, reason_codes


# ---------------------------------------------------------------------------
# Tier routing (single choke point)
# ---------------------------------------------------------------------------


def route_healing_tier(
    healing_input: HealingInput,
    config: HealingTierConfig,
) -> HealingDecision:
    """Route a healing request to the appropriate tier.

    This is the SINGLE CHOKE POINT for all healing model selection.
    No other module may select between LOCAL_AGENT, QWEN_VLLM, GEMINI_2_5_PRO.

    Phase 5-G: Enforces agent execution profile restrictions.

    Args:
        healing_input: Structured failure context.
        config: Validated healing tier configuration.

    Returns:
        Immutable HealingDecision with tier, heal_confidence, and reason_codes.
    """
    # Phase 5-G: Agent execution profile enforcement
    try:
        profile = get_profile(healing_input.agent_id)
    except KeyError as e:
        raise V15HardFailAbort(
            f"§AgentProfile: Agent '{healing_input.agent_id}' not found in registry: {e}"
        )

    # Enforce execution mode - deterministic agents cannot escalate to LLM tiers
    if not profile.is_llm_allowed():
        # Deterministic agents can ONLY use LOCAL_AGENT tier
        reason_codes = [f"agent_execution_mode=DETERMINISTIC:FORCED_LOCAL_AGENT"]
        return HealingDecision(
            heal_confidence=1.0,  # Maximum confidence for local agents
            tier=HealingTier.LOCAL_AGENT,
            reason_codes=tuple(reason_codes),
        )

    heal_confidence, reason_codes = compute_heal_confidence(healing_input)

    # Force GEMINI_2_5_PRO if max retries exceeded
    if healing_input.retry_count >= config.max_heal_retries:
        # For LLM agents, validate that GEMINI_2_5_PRO is allowed
        if not profile.can_use_model("gemini-2.5-pro"):
            raise V15HardFailAbort(
                f"§AgentProfile: Agent '{healing_input.agent_id}' not allowed to use model 'gemini-2.5-pro' for forced escalation. Allowed models: {profile.allowed_models}"
            )
        reason_codes.append(
            f"retry_count={healing_input.retry_count}>="
            f"max_heal_retries={config.max_heal_retries}:FORCED_GEMINI"
        )
        return HealingDecision(
            heal_confidence=heal_confidence,
            tier=HealingTier.GEMINI_2_5_PRO,
            reason_codes=tuple(reason_codes),
        )

    # Route by X/Y bands with model validation (fail-closed)
    if heal_confidence >= config.heal_confidence_x:
        tier = HealingTier.LOCAL_AGENT
        reason_codes.append(f"heal_confidence>={config.heal_confidence_x}:LOCAL_AGENT")
    elif heal_confidence >= config.heal_confidence_y:
        # QWEN_VLLM tier - validate model access (fail-closed)
        if not profile.can_use_model("qwen-vllm"):
            raise V15HardFailAbort(
                f"§AgentProfile: Agent '{healing_input.agent_id}' not allowed to use model 'qwen-vllm'. "
                f"Allowed models: {profile.allowed_models}"
            )
        tier = HealingTier.QWEN_VLLM
        reason_codes.append(
            f"{config.heal_confidence_y}<=heal_confidence<{config.heal_confidence_x}:QWEN_VLLM"
        )
    else:
        # GEMINI_2_5_PRO tier - validate model access (fail-closed)
        if not profile.can_use_model("gemini-2.5-pro"):
            raise V15HardFailAbort(
                f"§AgentProfile: Agent '{healing_input.agent_id}' not allowed to use model 'gemini-2.5-pro'. "
                f"Allowed models: {profile.allowed_models}"
            )
        tier = HealingTier.GEMINI_2_5_PRO
        reason_codes.append(f"heal_confidence<{config.heal_confidence_y}:GEMINI_2_5_PRO")

    return HealingDecision(
        heal_confidence=heal_confidence,
        tier=tier,
        reason_codes=tuple(reason_codes),
    )


__all__ = [
    "clear_historical_success_rates",
    "compute_heal_confidence",
    "route_healing_tier",
    "set_historical_success_rate",
]
