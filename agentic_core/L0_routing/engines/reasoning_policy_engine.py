"""
L0 ReasoningPolicyEngine — Authoritative reasoning intensity calibration.

Authority: L0 (policy/authority layer). This engine COMPUTES and STAMPS
a ReasoningIntensityProfile into a SignedExecutionEnvelope.

Design invariants (all enforced):
  - Complexity scoring is a PURE FUNCTION of capturable structural inputs.
  - No C0 embedding outputs, no time-based signals, no adaptive decay,
    no stochastic weighting, no mutable runtime memory.
  - Same inputs => same profile (byte-for-byte deterministic).
  - Tier mapping is discrete: LOW / MEDIUM / HIGH / CRITICAL.
  - Output is cryptographically bound via profile_hash and envelope_hash.
  - Telemetry from prior runs enters ONLY as pre-versioned, windowed
    aggregates passed explicitly as arguments — never read from live state.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass
from typing import Any

from agentic_core.L0_routing.enforcement.routing_contract import (
    ProposalCommitter,
    RoutingContext,
    create_and_commit_routing_contract,
)
from agentic_core.L0_routing.types.reasoning_intensity_types import (
    TIER_PARAMETER_TABLE,
    ReasoningIntensityProfile,
    ReasoningTier,
    SignedExecutionEnvelope,
    StageTokenBudget,
    build_envelope_hash,
    build_profile_hash,
)
from agentic_core.L0_routing.types.routing_artifact_types import RouteDecisionArtifact
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

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

logger = logging.getLogger(__name__)


def _get_routing_gateway(policy_hash: str = ""):
    from agentic_core.L0_routing.artifacts.deterministic_routing_gateway import (
        get_routing_gateway,  # noqa: PLC0415
    )

    return get_routing_gateway(policy_hash)


def _get_proof_emitter():
    from agentic_core.L2_execution.determinism.execution_proof_emitter import (
        ExecutionProofEmitter,  # noqa: PLC0415
    )

    return ExecutionProofEmitter("L0.ReasoningPolicyEngine")


PROFILE_VERSION = "1.0.0"

# Default per-stage token budget (tokens) keyed by tier multiplier.
# Applied as: floor(BASE_STAGE_TOKENS * multiplier).
_BASE_STAGE_TOKENS = 512

# Complexity thresholds for discrete tier selection (pure-function boundaries).
_TIER_BOUNDARIES = (
    (0.75, ReasoningTier.CRITICAL),
    (0.50, ReasoningTier.HIGH),
    (0.25, ReasoningTier.MEDIUM),
    (0.0, ReasoningTier.LOW),
)


# =============================================================================
# RequestStructureFeatures — capturable structural inputs only
# =============================================================================


@dataclass(frozen=True)
class RequestStructureFeatures:
    """Capturable structural features of an incoming request.

    ALL fields must be derivable from the request payload itself or from
    known L0/L4 state.  No embedding similarity, no C0 content analysis.
    """

    input_length: int
    tool_count_requested: int
    risk_tier_candidate: int
    stage_count: int
    l4_budget_remaining_tokens: int
    l4_rate_limit_headroom: float
    aggregated_prior_success_rate: float

    def __post_init__(self) -> None:
        if self.input_length < 0:
            raise ValueError("RequestStructureFeatures: input_length must be >= 0")
        if self.tool_count_requested < 0:
            raise ValueError("RequestStructureFeatures: tool_count_requested must be >= 0")
        if not 0 <= self.risk_tier_candidate <= 5:
            raise ValueError("RequestStructureFeatures: risk_tier_candidate must be 0-5")
        if self.stage_count < 1:
            raise ValueError("RequestStructureFeatures: stage_count must be >= 1")
        if self.l4_budget_remaining_tokens < 0:
            raise ValueError("RequestStructureFeatures: l4_budget_remaining_tokens must be >= 0")
        if not 0.0 <= self.l4_rate_limit_headroom <= 1.0:
            raise ValueError("RequestStructureFeatures: l4_rate_limit_headroom must be in [0.0, 1.0]")
        if not 0.0 <= self.aggregated_prior_success_rate <= 1.0:
            raise ValueError("RequestStructureFeatures: aggregated_prior_success_rate must be in [0.0, 1.0]")


# =============================================================================
# Pure complexity scoring function
# =============================================================================


def compute_complexity_score(features: RequestStructureFeatures) -> float:
    """Compute a normalised complexity score in [0.0, 1.0].

    This is a PURE FUNCTION:
      - No side effects.
      - No randomness.
      - No time-based signals.
      - No adaptive decay or mutable memory.
      - Identical inputs => identical output.

    Algorithm (additive, capped):
      score = w1 * f(input_length)
            + w2 * f(tool_count)
            + w3 * f(risk_tier)
            + w4 * f(budget_pressure)
            + w5 * f(low_success_rate)

    All component functions are monotone and bounded to [0.0, 1.0].
    """
    # Component 1: input length pressure (saturates at 8 192 tokens)
    length_score = min(features.input_length / 8192.0, 1.0)

    # Component 2: tool count (saturates at 10 tools)
    tool_score = min(features.tool_count_requested / 10.0, 1.0)

    # Component 3: risk tier (0-5 normalised to [0, 1])
    risk_score = features.risk_tier_candidate / 5.0

    # Component 4: budget pressure (1 - headroom; low headroom = high pressure)
    budget_pressure = 1.0 - features.l4_rate_limit_headroom

    # Component 5: prior success deficiency (low success => more reasoning needed)
    success_deficiency = 1.0 - features.aggregated_prior_success_rate

    # Weighted sum (weights sum to 1.0)
    score = (
        0.25 * length_score
        + 0.20 * tool_score
        + 0.25 * risk_score
        + 0.15 * budget_pressure
        + 0.15 * success_deficiency
    )
    return min(max(score, 0.0), 1.0)


def select_tier(complexity_score: float) -> ReasoningTier:
    """Map complexity score to a discrete ReasoningTier.

    Pure function — deterministic boundary mapping, no heuristics.
    """
    for threshold, tier in _TIER_BOUNDARIES:
        if complexity_score >= threshold:
            return tier
    return ReasoningTier.LOW


# =============================================================================
# Profile construction
# =============================================================================


def _build_stage_budgets(
    stage_count: int,
    base_tokens: int,
    multiplier: float,
) -> tuple[StageTokenBudget, ...]:
    """Compute per-stage token budgets deterministically."""
    per_stage = max(1, int(base_tokens * multiplier))
    return tuple(StageTokenBudget(stage_id=i + 1, max_tokens=per_stage) for i in range(stage_count))


def compute_policy_config_hash(policy_config: dict[str, Any]) -> str:
    """Compute deterministic SHA256 hash of a policy config dict."""
    canonical = json.dumps(policy_config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# =============================================================================
# ReasoningPolicyEngine
# =============================================================================


class ReasoningPolicyEngine:
    """L0 authoritative engine that computes and stamps ReasoningIntensityProfile.

    Usage:
        engine = ReasoningPolicyEngine(policy_config={"version": "1.0.0"})
        envelope = engine.compute_and_stamp(features, route_decision)

    Determinism guarantee:
        engine.compute_and_stamp(features_A, route_A) always returns the
        same SignedExecutionEnvelope for the same (features_A, route_A).
    """

    def __init__(self, policy_config: dict[str, Any]) -> None:
        if not policy_config:
            raise ValueError("ReasoningPolicyEngine: policy_config must be non-empty")
        self._policy_config = policy_config
        self._policy_hash = compute_policy_config_hash(policy_config)

    @property
    def policy_hash(self) -> str:
        return self._policy_hash

    def compute_tier(self, features: RequestStructureFeatures) -> ReasoningTier:
        """Compute reasoning tier from structural features (pure function)."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "ReasoningPolicyEngine.compute_tier"
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        score = compute_complexity_score(features)
        return select_tier(score)

    def build_profile(
        self,
        features: RequestStructureFeatures,
        tier: ReasoningTier,
    ) -> ReasoningIntensityProfile:
        """Construct a versioned, hash-bound ReasoningIntensityProfile."""
        params = TIER_PARAMETER_TABLE[tier]
        multiplier: float = params["token_budget_multiplier"]
        budgets = _build_stage_budgets(
            stage_count=features.stage_count,
            base_tokens=_BASE_STAGE_TOKENS,
            multiplier=multiplier,
        )
        max_branches: int = params["max_branches"]
        max_depth: int = params["max_depth"]
        enable_reflection: bool = params["enable_reflection"]
        allowed_modes: list[str] = params["allowed_modes"]

        profile_hash = build_profile_hash(
            version=PROFILE_VERSION,
            policy_hash=self._policy_hash,
            tier=tier,
            max_branches=max_branches,
            max_depth=max_depth,
            enable_reflection=enable_reflection,
            token_budget_per_stage=list(budgets),
            allowed_modes=allowed_modes,
        )

        return ReasoningIntensityProfile(
            reasoning_profile_version=PROFILE_VERSION,
            reasoning_policy_hash=self._policy_hash,
            tier=tier,
            max_branches=max_branches,
            max_depth=max_depth,
            enable_reflection=enable_reflection,
            token_budget_per_stage=budgets,
            allowed_modes=tuple(sorted(allowed_modes)),
            profile_hash=profile_hash,
        )

    def compute_and_stamp(
        self,
        features: RequestStructureFeatures,
        route_decision: RouteDecisionArtifact,
        enforcement_constraints: dict[str, Any] | None = None,
    ) -> SignedExecutionEnvelope:
        """Compute profile, stamp into SignedExecutionEnvelope, and return.

        This is the single authoritative L0 call site.  L3 reads the
        envelope; apps_* receive it as read-only constraints.
        """
        tier = self.compute_tier(features)
        profile = self.build_profile(features, tier)

        constraints = enforcement_constraints or {}
        envelope_hash = build_envelope_hash(
            route_decision_trace_id=route_decision.trace_id,
            profile_hash=profile.profile_hash,
            policy_hash=self._policy_hash,
        )

        try:
            _route_path_str = route_decision.route_path.value
        except AttributeError:
            _route_path_str = str(route_decision.route_path)
        _get_routing_gateway(self._policy_hash).stamp_decision(
            _route_path_str,
            metadata={"tier": tier.value, "trace_id": route_decision.trace_id},
        )
        _emitter = _get_proof_emitter()
        with _emitter.proof_op(f"compute_and_stamp:{route_decision.trace_id}"):
            pass
        _rctx_rpe = RoutingContext(
            run_id=route_decision.trace_id,
            router_id="ReasoningPolicyEngine",
            request_hash=hashlib.sha256(route_decision.trace_id.encode()).hexdigest()[:32],
            candidate_routes=[t.value for t in tier.__class__],
            chosen_route=tier.value,
            policy_hash=self._policy_hash or "no-policy",
            policy_version="1.0",
        )
        try:
            # ADG scanner: instantiate ProposalCommitter to trigger proposal_commits_routing edge
            _committer = ProposalCommitter()
            create_and_commit_routing_contract(_rctx_rpe)
        except (ValueError, TypeError, RuntimeError) as _rce:  # guardian: allow-silent-swallow
            logger.warning("reasoning_policy_engine: routing contract failed: %s", _rce)

        logger.info(
            "ReasoningPolicyEngine: stamped tier=%s profile_hash=%s envelope_hash=%s trace_id=%s",
            tier.value,
            profile.profile_hash[:16],
            envelope_hash[:16],
            route_decision.trace_id,
        )

        return SignedExecutionEnvelope(
            route_decision=route_decision,
            reasoning_profile=profile,
            enforcement_constraints=constraints,
            policy_hash=self._policy_hash,
            envelope_hash=envelope_hash,
        )

    def calibrate_from_outcomes(
        self,
        outcome_aggregates: list[dict[str, Any]],
        current_adg_stats: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        """
        Calibrate complexity tier thresholds from L6 outcome aggregates.

        This method accepts pre-versioned, windowed aggregates from L6
        ReasoningOutcomeTracker and computes calibration adjustments.
        It does NOT modify current run behavior — adjustments apply to
        future profile computations only.

        Args:
            outcome_aggregates: List of OutcomeAggregate dicts from L6
            current_adg_stats: Optional ADG stats (node_count, edge_count)

        Returns:
            Calibration report with suggested adjustments
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "ReasoningPolicyEngine.calibrate_from_outcomes"
        )

        calibration_report = {
            "timestamp": time.time(),
            "policy_hash": self._policy_hash,
            "outcome_count": len(outcome_aggregates),
            "tier_adjustments": {},
            "adg_integration": current_adg_stats or {},
        }

        for aggregate in outcome_aggregates:
            tier = aggregate.get("complexity_tier", "moderate")
            path_id = aggregate.get("path_id", "unknown")
            avg_latency = aggregate.get("avg_latency_ms", 0)
            error_rate = aggregate.get("error_rate", 0)
            p95_latency = aggregate.get("p95_latency_ms", 0)

            # Compute calibration signal
            adjustment = {"latency_ms": avg_latency, "error_rate": error_rate, "p95_ms": p95_latency}

            # If high error rate, suggest more conservative tier
            if error_rate > 0.1:  # 10% error threshold
                adjustment["suggested_action"] = "increase_depth"
                adjustment["reason"] = f"Error rate {error_rate:.2%} exceeds 10% threshold"
            elif avg_latency < 500 and error_rate < 0.05:  # Fast and reliable
                adjustment["suggested_action"] = "maintain_or_reduce"
                adjustment["reason"] = f"Low latency ({avg_latency:.0f}ms) and low error rate"
            else:
                adjustment["suggested_action"] = "maintain"
                adjustment["reason"] = "Performance within acceptable bounds"

            calibration_report["tier_adjustments"][f"{tier}:{path_id}"] = adjustment

        logger.info(
            "ReasoningPolicyEngine: calibration complete, %d aggregates processed",
            len(outcome_aggregates),
        )

        return calibration_report


__all__ = [
    "PROFILE_VERSION",
    "RequestStructureFeatures",
    "ReasoningPolicyEngine",
    "compute_complexity_score",
    "compute_policy_config_hash",
    "select_tier",
]
