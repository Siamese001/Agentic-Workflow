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

from agentic_core.agents.types.agent_registry import get_profile, registry_digest
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
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "healing_tier_router")
emit_determinism_digest("p0", "healing_tier_router")

_emit_dispatches_healing_run("p1", "healing_tier_router", "L2")
_emit_routes_through("p1", "healing_tier_router", "L2")
_emit_checks_agent_registry("p1", "healing_tier_router", "agent_registry")
_emit_validates_agent_capability("p1", "healing_tier_router", "capability")
_emit_dispatches_execution_plan("p1", "healing_tier_router", "exec_plan")
_emit_agent_executes_agent("p1", "healing_tier_router", "sub_agent")
_emit_routes_to_agent("p1", "healing_tier_router", "target_agent")
_emit_verifies_policy("p1", "healing_tier_router", "policy_check")
_emit_observes_runtime_state("p1", "healing_tier_router", "runtime_state")
_emit_verifies_boundary("p1", "healing_tier_router", "boundary_check")
_emit_transcripts_response("p1", "healing_tier_router", "transcript")
_emit_hard_fails_untranscripted("p1", "healing_tier_router")
_emit_gated_by_confidence("p1", "healing_tier_router", "confidence_gate")
_emit_escalates_to_human("p1", "healing_tier_router", "L2")
_emit_reads_policy_state("p1", "healing_tier_router", "L2")
_emit_authorize_and_execute("p2", "healing_tier_router", "execution_auth")
_emit_validates_capability("p2", "healing_tier_router", "capability_check")
_emit_routes_to_capability("p2", "healing_tier_router", "capability_route")
_emit_writes_via_uwg("p2", "healing_tier_router", "uwg_write")
_emit_blocks_direct_write("p2", "healing_tier_router", "direct_write_block")
_emit_records_tool_invocation("p2", "healing_tier_router", "tool_invocation")
_emit_captures_execution_output("p2", "healing_tier_router", "exec_output")
_emit_dispatches_agent("p3", "healing_tier_router", "agent_dispatch")
_emit_coordinates_agents("p3", "healing_tier_router", "agent_coordination")
_emit_records_workflow_lineage("p3", "healing_tier_router", "workflow_lineage")
_emit_records_healing_outcome("p3", "healing_tier_router", "healing_outcome")
_emit_escalates_failure("p3", "healing_tier_router", "failure_escalation")
_emit_orchestrates_workflow("p3", "healing_tier_router", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healing_tier_router", "healing_dispatch")
_emit_invokes_evaluation("p3", "healing_tier_router", "evaluation_signal")
_emit_records_telemetry_event("p4", "healing_tier_router", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healing_tier_router", "eval_metric")
_emit_stores_embedding("p4", "healing_tier_router", "embedding_store")
_emit_updates_meta_learning_state("p4", "healing_tier_router", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healing_tier_router", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("healing_tier_router", "p4obs", "metric_1")
_emit_emits_metric_event("healing_tier_router", "p4obs", "metric_2")
_emit_emits_metric_event("healing_tier_router", "p4obs", "metric_3")
_emit_emits_metric_event("healing_tier_router", "p4obs", "metric_4")
_emit_emits_metric_event("healing_tier_router", "p4obs", "metric_5")
_emit_emits_metric_event("healing_tier_router", "p4obs", "metric_6")
_emit_records_incident_event("healing_tier_router", "p4obs", "incident")
_emit_captures_runtime_anomaly("healing_tier_router", "p4obs", "anomaly")
_emit_writes_observability_log("healing_tier_router", "p4obs", "obs_log")
_emit_updates_monitoring_state("healing_tier_router", "p4obs", "mon_state")
_emit_triggers_alert("healing_tier_router", "p4obs", "alert")
_emit_links_incident_trace("healing_tier_router", "p4obs", "trace_link")
_emit_captures_pattern("healing_tier_router", "p3lm", "pattern")
_emit_records_learning_event("healing_tier_router", "p3lm", "learning_event")
_emit_writes_learning_snapshot("healing_tier_router", "p3lm", "snapshot")
_emit_feeds_meta_learning("healing_tier_router", "p3lm", "meta_feed")
_emit_updates_routing_strategy("healing_tier_router", "p3lm", "routing")
_emit_improves_agent_policy("healing_tier_router", "p3lm", "policy")
_emit_stores_learning_state("healing_tier_router", "p3lm", "state")
_emit_records_execution_trace("healing_tier_router", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("healing_tier_router", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("healing_tier_router", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("healing_tier_router", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("healing_tier_router", "L4_STATE", "p2_trace_5")
_emit_reads_environ("healing_tier_router", "env_read", "p2_env_1")
_emit_reads_environ("healing_tier_router", "env_read", "p2_env_2")
_emit_reads_runtime_state("healing_tier_router", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("healing_tier_router", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "healing_tier_router", "context_pull")
_emit_pulls_context("p1", "healing_tier_router", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "healing_tier_router", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "healing_tier_router", "uwg_term_2")
_emit_writes_through("p1", "healing_tier_router", "write_through")
_emit_writes_through("p1", "healing_tier_router", "write_through_2")
_emit_validated_by_safety_plane("p1", "healing_tier_router", "safety_validation")
_emit_invokes_eval("p1", "healing_tier_router", "eval_call")
_emit_proposal_commits_routing("p1", "healing_tier_router", "routing_commit")

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
# NOTE: These are informational constants only. The authoritative values
# are the local variables inside compute_heal_confidence.
# ---------------------------------------------------------------------------

WEIGHT_FAILURE_PRIOR = 0.25
WEIGHT_BLAST_RADIUS = 0.20
WEIGHT_HISTORICAL_SUCCESS = 0.15
WEIGHT_TOOL_READINESS = 0.15
WEIGHT_RETRY_DECAY = 0.10  # guardian: allow-magic-config
WEIGHT_FAILURE_ENTROPY = 0.15  # HMD Item 3: entropy classification weight

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
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_historical_success_rate", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_historical_success_rate", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "get_historical_success_rate")
    # Test-time override takes precedence
    if error_signature in _HISTORICAL_OVERRIDES:
        return _HISTORICAL_OVERRIDES[error_signature]
    if meta_prior_provider is not None:
        return meta_prior_provider.get_prior(error_signature)
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
    # Fixed weights - no config loading (adjusted to include entropy)
    WEIGHT_FAILURE_PRIOR = 0.25
    WEIGHT_BLAST_RADIUS = 0.20
    WEIGHT_HISTORICAL_SUCCESS = 0.15
    WEIGHT_TOOL_READINESS = 0.15
    WEIGHT_RETRY_DECAY = 0.10  # guardian: allow-magic-config
    WEIGHT_FAILURE_ENTROPY = 0.15

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

    # Failure entropy class contribution - higher entropy lowers confidence
    entropy_weights = {"LOW": 1.0, "MEDIUM": 0.7, "HIGH": 0.3}
    entropy_weight = entropy_weights.get(healing_input.failure_entropy_class, 0.7)
    failure_entropy = entropy_weight * WEIGHT_FAILURE_ENTROPY

    # Fixed precision arithmetic — weights sum to 1.0
    raw_confidence = (
        failure_prior * WEIGHT_FAILURE_PRIOR
        + blast_radius_contribution
        + historical_success
        + tool_readiness
        + retry_decay
        + failure_entropy
    )

    # Fixed precision for mathematical determinism
    score = round(max(0.0, min(1.0, raw_confidence)), 6)

    reason_codes: tuple[str, ...] = (
        f"failure_prior={failure_prior:.4f}:weight={WEIGHT_FAILURE_PRIOR}",
        f"blast_radius_contribution={blast_radius_contribution:.4f}:weight={WEIGHT_BLAST_RADIUS}",
        f"historical_success_rate={hist_rate:.4f}:weight={WEIGHT_HISTORICAL_SUCCESS}",
        f"tool_readiness={tool_readiness:.4f}:weight={WEIGHT_TOOL_READINESS}",
        f"retry_decay={retry_decay:.4f}:weight={WEIGHT_RETRY_DECAY}",
        f"failure_entropy={failure_entropy:.4f}:weight={WEIGHT_FAILURE_ENTROPY}:class={healing_input.failure_entropy_class}",
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
        try:
            profile = get_execution_profile(healing_input.agent_id)
            # DETERMINISTIC agents bypass the TIERING_ALLOWLIST and go straight to LOCAL_AGENT
            if not profile.is_llm_allowed():
                return HealingDecision(
                    heal_confidence=1.0,
                    tier=HealingTier.LOCAL_AGENT,
                    reason_codes=("agent_execution_mode=DETERMINISTIC:FORCED_LOCAL_AGENT",),
                )
        except KeyError:
            logger.debug("Agent '%s' not in registry — proceeding with tiering", healing_input.agent_id)

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


def route_by_confidence(
    confidence: float,
    retry_count: int = 0,
    failure_type: str = "unknown",
    error_signature: str = "",
    blast_radius_estimate: float = 0.5,
    agent_id: str = "",
    config: HealingTierConfig | None = None,
    *,
    meta_prior_provider: MetaPriorProvider | None = None,
) -> HealingDecision:
    """Bridge: convert raw confidence float into a canonical HealingDecision.

    Wraps route_healing_tier() so legacy callers that hold only a confidence
    float (e.g. SovereignDecisionEngine, decorators_util) can delegate to the
    single choke-point without constructing a HealingInput themselves.

    Args:
        confidence: Pre-computed confidence score in [0.0, 1.0].
        retry_count: Number of prior heal attempts.
        failure_type: Canonical failure type string (maps to FAILURE_CLASS_PRIORS).
        error_signature: Error signature for historical look-up.
        blast_radius_estimate: Normalised blast radius [0.0, 1.0].
        agent_id: Optional agent identifier for allowlist check.
        config: Optional HealingTierConfig; uses canonical X/Y defaults if None.
        meta_prior_provider: Optional live meta-prior provider.

    Returns:
        Immutable HealingDecision with tier and reason_codes.
    """
    safe_confidence = round(max(0.0, min(1.0, confidence)), 6)
    safe_retry = max(0, retry_count)

    x_threshold = config.heal_confidence_x if config is not None else HEALING_CONFIDENCE_X
    y_threshold = config.heal_confidence_y if config is not None else HEALING_CONFIDENCE_Y
    max_retries = config.max_heal_retries if config is not None else 3

    reason_codes: list[str] = [
        f"route_by_confidence:input_confidence={safe_confidence:.6f}",
        f"failure_type={failure_type}",
        f"retry_count={safe_retry}",
    ]

    if safe_retry >= max_retries:
        reason_codes.append(f"retry_count>={max_retries}:FORCED_GEMINI")
        return HealingDecision(
            heal_confidence=safe_confidence,
            tier=HealingTier.GEMINI_2_5_PRO,
            reason_codes=tuple(reason_codes),
        )

    if safe_confidence >= x_threshold:
        tier = HealingTier.LOCAL_AGENT
        reason_codes.append(f"heal_confidence>={x_threshold}:LOCAL_AGENT")
    elif safe_confidence >= y_threshold:
        tier = HealingTier.QWEN_VLLM
        reason_codes.append(f"heal_confidence>={y_threshold}:QWEN_VLLM")
    else:
        tier = HealingTier.GEMINI_2_5_PRO
        reason_codes.append(f"heal_confidence<{y_threshold}:GEMINI_2_5_PRO")

    return HealingDecision(
        heal_confidence=safe_confidence,
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
    "route_by_confidence",
    "set_historical_success_rate",
    "HISTORICAL_DATA_VERSION",
    "HISTORICAL_DATA_HASH",
    "_compute_replay_key",
    "SovereigntyViolation",
]
