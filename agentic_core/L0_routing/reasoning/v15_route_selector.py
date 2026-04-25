"""v15 §FIXED DECISION ORDER — normative L0 dispatcher.

Pure function. No I/O, no side effects, no hidden state. Maps a
``RouteSignalsV15`` dataclass into a fully-populated ``V15RouteContract``
with a deterministic route digest, a manifest hash, and an empty
``hmac_sig`` (caller signs after construction via
:meth:`V15RouteContract.sign`).

The decision order is exactly the one in v15:

    0. Invalid envelope / scope fail / unsafe request   -> R5_FALLBACK [RET]
    1. Exact reusable answer with valid freshness       -> R1A_EXACT_CACHE [RET]
    2. Reuse-safe semantic match with calibrated conf.  -> R1B_SEMANTIC_CACHE [RET]
    3. High-risk / irreversible / ambiguous mutation    -> HITL posture
                                                          (R3R4_MANAGED, TIER_HITL)
    4. Low-risk reversible action (one bounded action)  -> R4_SINGLE_ACTION
    5. Factual/document/code/policy answer w/ support   -> R3_SIMPLE_GROUNDED_READ
    6. Multi-hop with deps / changing step contract     -> R3R4_MANAGED_WORKFLOW
    7. No safe/grounded/reusable path                   -> R5_FALLBACK [RET]

Cold-start rule (v15 §COLD-START RULE) is applied before steps 4-6:
when classifier confidence is weak and grounding is needed, the
selector prefers R3 (grounded read) over R4/managed; if the request
is underspecified, prefers R5 clarify.

This module deliberately depends only on stdlib + the v15 type module
so it stays testable without spinning up cache infra.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from agentic_core.L0_routing.types.route_contract_v15 import (
    AuthorityScope,
    CachePolicyV15,
    ConfidenceClass,
    CostTierV15,
    ExecutionFormV15,
    FallbackEntryV15,
    FreshnessClassV15,
    ReasonCodeV15,
    RouteIdV15,
    RouteSLOV15,
    SignaturesV15,
    SupportTargetV15,
    TelemetryKeysV15,
    V15RouteContract,
    V15RouteContractError,
    _classify_confidence,
    compute_deterministic_route_digest,
    compute_manifest_hash,
)

Logger = logging.getLogger(__name__)

# Cold-start threshold: below this, the selector refuses to pick R4 / managed
# workflows and downshifts to R3 grounded read (or R5 clarify when there is
# no signal at all).
COLD_START_CONFIDENCE_THRESHOLD = 0.50

# Default per-route SLO when caller omits one. Conservative bounds; production
# dispatchers SHOULD inject route-specific SLOs from
# config/routing_thresholds.yaml.
_DEFAULT_SLO_BY_ROUTE: dict[RouteIdV15, RouteSLOV15] = {
    RouteIdV15.R1A_EXACT_CACHE: RouteSLOV15(
        max_latency_ms=500,
        max_cost=0.0,
        max_tokens=0,
        max_retrieval_passes=0,
        max_graph_hops=0,
        max_tool_calls=0,
        max_iterations=0,
        reserve_for_exit_eval=0,
    ),
    RouteIdV15.R1B_SEMANTIC_CACHE: RouteSLOV15(
        max_latency_ms=1500,
        max_cost=0.0,
        max_tokens=0,
        max_retrieval_passes=0,
        max_graph_hops=0,
        max_tool_calls=0,
        max_iterations=0,
        reserve_for_exit_eval=0,
    ),
    RouteIdV15.R3_SIMPLE_GROUNDED_READ: RouteSLOV15(
        max_latency_ms=15_000,
        max_cost=0.05,
        max_tokens=8_000,
        max_retrieval_passes=2,
        max_graph_hops=2,
        max_tool_calls=0,
        max_iterations=0,
        reserve_for_exit_eval=512,
    ),
    RouteIdV15.R4_SINGLE_ACTION: RouteSLOV15(
        max_latency_ms=10_000,
        max_cost=0.02,
        max_tokens=4_000,
        max_retrieval_passes=0,
        max_graph_hops=0,
        max_tool_calls=1,
        max_iterations=0,
        reserve_for_exit_eval=512,
    ),
    RouteIdV15.R3R4_MANAGED_WORKFLOW: RouteSLOV15(
        max_latency_ms=120_000,
        max_cost=1.00,
        max_tokens=64_000,
        max_retrieval_passes=8,
        max_graph_hops=8,
        max_tool_calls=16,
        max_iterations=4,
        reserve_for_exit_eval=2_048,
    ),
    RouteIdV15.R5_FALLBACK: RouteSLOV15(
        max_latency_ms=2_000,
        max_cost=0.0,
        max_tokens=512,
        max_retrieval_passes=0,
        max_graph_hops=0,
        max_tool_calls=0,
        max_iterations=0,
        reserve_for_exit_eval=0,
    ),
}


# ---------------------------------------------------------------------------
# Input signal bundle
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RouteSignalsV15:
    """All signals the v15 dispatcher consumes.

    Populated by upstream stages: ingress pre-filter, L1 plan classifier,
    cache probes, mutation-intent flagger. Each flag's semantics inline.
    """

    # Ingress pre-filter result. False -> step 0 (R5_FALLBACK).
    ingress_ok: bool

    # Authority scope captured at ingress time (tenant/ACL/region/etc.).
    authority: AuthorityScope

    # Provenance bound to L1 plan + policy snapshot.
    policy_hash: str
    blueprint_hash: str
    snapshot_id: str

    # Telemetry identity (from L1 / trace context).
    trace_root: str
    route_span_id: str
    replay_key: str
    route_telemetry_event_id: str

    # Classifier output.
    classifier_confidence: float

    # Cache probes (D1/D2 already executed).
    exact_cache_hit: bool = False
    semantic_cache_hit: bool = False

    # Mutation-intent / action signals.
    high_risk_action: bool = False  # irreversible / sensitive — needs HITL
    low_risk_reversible_action: bool = False
    action_args_need_grounding: bool = False  # maps to ACTION_ARGUMENT_GROUNDING

    # Grounded-read signals.
    grounding_required: bool = False
    support_target: SupportTargetV15 = SupportTargetV15.NONE

    # Workflow-shape signals.
    multi_step_required: bool = False
    cross_step_contract_change: bool = False
    parallel_safe_shards: bool = False
    iterative_refinement_needed: bool = False
    needs_hitl_pause: bool = False

    # Freshness preference (drives cache eligibility too).
    freshness_class: FreshnessClassV15 = FreshnessClassV15.SLOW_CHANGING

    # Underspecified / ambiguous request — drives R5 clarify per cold-start rule.
    underspecified: bool = False
    unsafe: bool = False  # explicit unsafe flag (independent of confidence)

    # Per-call HITL pause point identifiers (used only if needs_hitl_pause).
    hitl_pause_points: tuple[str, ...] = field(default_factory=tuple)

    # Workflow blueprint id (required for managed workflow).
    workflow_blueprint_id: str | None = None

    # Plan FK for traceability.
    base_contract_id: str = ""


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def select_route_v15(signals: RouteSignalsV15) -> V15RouteContract:
    """Apply v15 §FIXED DECISION ORDER and return an unsigned contract.

    The returned contract has ``signatures.hmac_sig == ""``. The caller is
    responsible for signing via :meth:`V15RouteContract.sign` before
    persistence or downstream dispatch.

    Raises:
        V15RouteContractError: when ``signals`` violates a v15 invariant
            (e.g., managed-workflow path requested without a blueprint id).
    """
    _validate_signals(signals)

    # ---- step 0: ingress reject / unsafe ----
    if not signals.ingress_ok or signals.unsafe:
        reason = (
            ReasonCodeV15.SCOPE_FAIL.value
            if not signals.ingress_ok
            else ReasonCodeV15.POLICY_BLOCK.value
        )
        return _build(
            signals,
            route_id=RouteIdV15.R5_FALLBACK,
            cache_policy=CachePolicyV15.NO_CACHE,
            support_target=SupportTargetV15.NONE,
            cost_tier=CostTierV15.TIER_S,
            reason_codes=(reason, ReasonCodeV15.FALLBACK_SELECTED.value),
            confidence_class=ConfidenceClass.UNSAFE,
            confidence_score=0.0,
            fallback_chain=(),
        )

    # ---- step 1: exact cache hit ----
    if signals.exact_cache_hit:
        return _build(
            signals,
            route_id=RouteIdV15.R1A_EXACT_CACHE,
            cache_policy=CachePolicyV15.EXACT_ONLY,
            support_target=SupportTargetV15.NONE,
            cost_tier=CostTierV15.TIER_S,
            reason_codes=(ReasonCodeV15.EXACT_CACHE_HIT.value,),
            confidence_class=ConfidenceClass.EXACT,
            confidence_score=1.0,
            fallback_chain=(),
        )

    # ---- step 2: semantic cache hit ----
    if signals.semantic_cache_hit:
        # v15 §R1B GUARDS: semantic cache cannot answer LIVE/CURRENT freshness.
        if signals.freshness_class in {
            FreshnessClassV15.LIVE,
            FreshnessClassV15.CURRENT,
        }:
            # Fall through; semantic cache is invalid for this freshness class.
            # Emit a reason code so downstream sees the rejection.
            Logger.debug(
                "select_route_v15: semantic_cache_hit ignored due to freshness=%s",
                signals.freshness_class.value,
            )
        else:
            return _build(
                signals,
                route_id=RouteIdV15.R1B_SEMANTIC_CACHE,
                cache_policy=CachePolicyV15.SEMANTIC_OK,
                support_target=SupportTargetV15.NONE,
                cost_tier=CostTierV15.TIER_S,
                reason_codes=(ReasonCodeV15.SEMANTIC_CACHE_HIT.value,),
                confidence_class=_classify_confidence(signals.classifier_confidence),
                confidence_score=signals.classifier_confidence,
                fallback_chain=(),
            )

    # ---- step 3: high-risk mutation -> HITL posture ----
    if signals.high_risk_action:
        # HITL is realized as a managed workflow with TIER_HITL and explicit
        # pause point. v15 §EDGE CASE #5 — HITL is not sovereign authority.
        return _build(
            signals,
            route_id=RouteIdV15.R3R4_MANAGED_WORKFLOW,
            cache_policy=CachePolicyV15.NO_CACHE,
            support_target=SupportTargetV15.ACTION_ARGUMENT_GROUNDING,
            cost_tier=CostTierV15.TIER_HITL,
            reason_codes=(
                ReasonCodeV15.ACTION_HIGH_RISK.value,
                ReasonCodeV15.HITL_REQUIRED.value,
            ),
            confidence_class=_classify_confidence(signals.classifier_confidence),
            confidence_score=signals.classifier_confidence,
            fallback_chain=_default_fallback_for(RouteIdV15.R3R4_MANAGED_WORKFLOW),
            require_blueprint=True,
            hitl_pause_points=(
                signals.hitl_pause_points
                if signals.hitl_pause_points
                else ("HITL_PRECOMMIT",)
            ),
        )

    # ---- cold-start rule (v15 §COLD-START RULE) ----
    cold_start = signals.classifier_confidence < COLD_START_CONFIDENCE_THRESHOLD
    if cold_start:
        if signals.underspecified:
            # Underspecified + low confidence -> R5 clarify.
            # Score zeroed so INSUFFICIENT_SUPPORT class agrees with score
            # under v15's class-vs-score coherence rule.
            return _build(
                signals,
                route_id=RouteIdV15.R5_FALLBACK,
                cache_policy=CachePolicyV15.NO_CACHE,
                support_target=SupportTargetV15.NONE,
                cost_tier=CostTierV15.TIER_S,
                reason_codes=(
                    ReasonCodeV15.SUPPORT_WEAK.value,
                    ReasonCodeV15.FALLBACK_SELECTED.value,
                ),
                confidence_class=ConfidenceClass.INSUFFICIENT_SUPPORT,
                confidence_score=0.0,
                fallback_chain=(),
            )
        # If grounding is needed, prefer R3 over any action/managed path.
        if signals.grounding_required:
            return _build_r3(signals, cold_start=True)

    # ---- step 4: low-risk reversible action ----
    if signals.low_risk_reversible_action:
        # If the action requires argument grounding, the canonical v15
        # answer is "R3 + R4 single step" (Route Selection Matrix). For our
        # SSOT one-route-per-contract model we surface that as R4 with
        # support_target=ACTION_ARGUMENT_GROUNDING; downstream stages run
        # the single grounded retrieval pass before L2.
        support = (
            SupportTargetV15.ACTION_ARGUMENT_GROUNDING
            if signals.action_args_need_grounding
            else SupportTargetV15.NONE
        )
        return _build(
            signals,
            route_id=RouteIdV15.R4_SINGLE_ACTION,
            cache_policy=CachePolicyV15.NO_CACHE,
            support_target=support,
            cost_tier=CostTierV15.TIER_M,
            reason_codes=(ReasonCodeV15.ACTION_LOW_RISK.value,),
            confidence_class=_classify_confidence(signals.classifier_confidence),
            confidence_score=signals.classifier_confidence,
            fallback_chain=_default_fallback_for(RouteIdV15.R4_SINGLE_ACTION),
        )

    # ---- step 5: simple grounded read ----
    if signals.grounding_required and not signals.multi_step_required:
        return _build_r3(signals, cold_start=False)

    # ---- step 6: managed workflow ----
    if signals.multi_step_required or signals.cross_step_contract_change or (
        signals.parallel_safe_shards or signals.iterative_refinement_needed
    ):
        reason_codes_list: list[str] = [ReasonCodeV15.MULTI_STEP_REQUIRED.value]
        if signals.cross_step_contract_change:
            reason_codes_list.append(ReasonCodeV15.DEPENDENCY_BRANCHING_REQUIRED.value)
        if signals.grounding_required:
            reason_codes_list.append(ReasonCodeV15.GROUNDING_REQUIRED.value)
        if signals.needs_hitl_pause:
            reason_codes_list.append(ReasonCodeV15.HITL_REQUIRED.value)
        return _build(
            signals,
            route_id=RouteIdV15.R3R4_MANAGED_WORKFLOW,
            cache_policy=CachePolicyV15.READ_THROUGH if signals.grounding_required else CachePolicyV15.NO_CACHE,
            support_target=signals.support_target if signals.grounding_required else SupportTargetV15.NONE,
            cost_tier=CostTierV15.TIER_L,
            reason_codes=tuple(reason_codes_list),
            confidence_class=_classify_confidence(signals.classifier_confidence),
            confidence_score=signals.classifier_confidence,
            fallback_chain=_default_fallback_for(RouteIdV15.R3R4_MANAGED_WORKFLOW),
            require_blueprint=True,
            hitl_pause_points=signals.hitl_pause_points if signals.needs_hitl_pause else (),
        )

    # ---- step 7: no safe path ----
    # Score is reset to 0.0 because the routing layer cannot satisfy the
    # request — the class INSUFFICIENT_SUPPORT must agree with the score
    # under the v15 contract's class-vs-score coherence rule.
    return _build(
        signals,
        route_id=RouteIdV15.R5_FALLBACK,
        cache_policy=CachePolicyV15.NO_CACHE,
        support_target=SupportTargetV15.NONE,
        cost_tier=CostTierV15.TIER_S,
        reason_codes=(ReasonCodeV15.FALLBACK_SELECTED.value,),
        confidence_class=ConfidenceClass.INSUFFICIENT_SUPPORT,
        confidence_score=0.0,
        fallback_chain=(),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_r3(
    signals: RouteSignalsV15,
    *,
    cold_start: bool,
) -> V15RouteContract:
    """Compose the R3_SIMPLE_GROUNDED_READ contract."""
    reason_codes_list = [ReasonCodeV15.GROUNDING_REQUIRED.value]
    if signals.freshness_class in {
        FreshnessClassV15.CURRENT,
        FreshnessClassV15.LIVE,
    }:
        reason_codes_list.append(ReasonCodeV15.FRESHNESS_REQUIRED.value)
    if cold_start:
        reason_codes_list.append(ReasonCodeV15.SUPPORT_WEAK.value)
    return _build(
        signals,
        route_id=RouteIdV15.R3_SIMPLE_GROUNDED_READ,
        cache_policy=CachePolicyV15.READ_THROUGH,
        support_target=(
            signals.support_target
            if signals.support_target != SupportTargetV15.NONE
            else SupportTargetV15.SOURCE_BACKED_SUMMARY
        ),
        cost_tier=CostTierV15.TIER_M,
        reason_codes=tuple(reason_codes_list),
        confidence_class=_classify_confidence(signals.classifier_confidence),
        confidence_score=signals.classifier_confidence,
        fallback_chain=_default_fallback_for(RouteIdV15.R3_SIMPLE_GROUNDED_READ),
    )


def _default_fallback_for(
    route_id: RouteIdV15,
) -> tuple[FallbackEntryV15, ...]:
    """Default fallback chains for non-terminal routes (R5 always last)."""
    if route_id == RouteIdV15.R3_SIMPLE_GROUNDED_READ:
        return (
            FallbackEntryV15(RouteIdV15.R3_SIMPLE_GROUNDED_READ, CostTierV15.TIER_L),
            FallbackEntryV15(RouteIdV15.R5_FALLBACK, CostTierV15.TIER_S),
        )
    if route_id == RouteIdV15.R4_SINGLE_ACTION:
        return (
            FallbackEntryV15(RouteIdV15.R3R4_MANAGED_WORKFLOW, CostTierV15.TIER_HITL),
            FallbackEntryV15(RouteIdV15.R5_FALLBACK, CostTierV15.TIER_S),
        )
    if route_id == RouteIdV15.R3R4_MANAGED_WORKFLOW:
        return (
            FallbackEntryV15(RouteIdV15.R3_SIMPLE_GROUNDED_READ, CostTierV15.TIER_M),
            FallbackEntryV15(RouteIdV15.R5_FALLBACK, CostTierV15.TIER_S),
        )
    return ()


def _validate_signals(signals: RouteSignalsV15) -> None:
    """Type-and-range checks the dataclass cannot express on its own."""
    if not isinstance(signals.classifier_confidence, (int, float)):
        raise V15RouteContractError(
            "classifier_confidence must be numeric",
        )
    if not 0.0 <= float(signals.classifier_confidence) <= 1.0:
        raise V15RouteContractError(
            f"classifier_confidence out of range [0,1]: {signals.classifier_confidence}",
        )
    if not isinstance(signals.authority, AuthorityScope):
        raise V15RouteContractError("signals.authority must be AuthorityScope")
    if not isinstance(signals.support_target, SupportTargetV15):
        raise V15RouteContractError(
            "signals.support_target must be SupportTargetV15",
        )
    if not isinstance(signals.freshness_class, FreshnessClassV15):
        raise V15RouteContractError(
            "signals.freshness_class must be FreshnessClassV15",
        )


def _build(
    signals: RouteSignalsV15,
    *,
    route_id: RouteIdV15,
    cache_policy: CachePolicyV15,
    support_target: SupportTargetV15,
    cost_tier: CostTierV15,
    reason_codes: tuple[str, ...],
    confidence_class: ConfidenceClass,
    confidence_score: float,
    fallback_chain: tuple[FallbackEntryV15, ...],
    require_blueprint: bool = False,
    hitl_pause_points: tuple[str, ...] = (),
) -> V15RouteContract:
    """Assemble the final V15RouteContract with deterministic digest."""
    # Managed-workflow guard.
    workflow_blueprint_id: str | None = None
    if require_blueprint or route_id == RouteIdV15.R3R4_MANAGED_WORKFLOW:
        if not signals.workflow_blueprint_id:
            raise V15RouteContractError(
                "signals.workflow_blueprint_id required for R3R4_MANAGED_WORKFLOW",
            )
        workflow_blueprint_id = signals.workflow_blueprint_id

    # Compute deterministic digest BEFORE constructing the contract.
    digest = compute_deterministic_route_digest(
        route_id=route_id,
        execution_form=_canonical_execution_form(route_id),
        cache_policy=cache_policy,
        freshness_class=signals.freshness_class,
        support_target=support_target,
        cost_tier=cost_tier,
        reason_codes=reason_codes,
        fallback_chain=fallback_chain,
        authority=signals.authority,
        policy_hash=signals.policy_hash,
        blueprint_hash=signals.blueprint_hash,
        snapshot_id=signals.snapshot_id,
    )
    manifest_hash = compute_manifest_hash(
        contract_version="v15.0.0",
        route_digest=digest,
        policy_hash=signals.policy_hash,
        blueprint_hash=signals.blueprint_hash,
        snapshot_id=signals.snapshot_id,
    )

    telemetry = TelemetryKeysV15(
        trace_root=signals.trace_root,
        route_span_id=signals.route_span_id,
        route_digest=digest,
        policy_hash=signals.policy_hash,
        blueprint_hash=signals.blueprint_hash,
        snapshot_id=signals.snapshot_id,
        replay_key=signals.replay_key,
        route_telemetry_event_id=signals.route_telemetry_event_id,
    )
    signatures = SignaturesV15(
        manifest_hash=manifest_hash,
        deterministic_route_digest=digest,
        hmac_sig="",
    )

    slo = _DEFAULT_SLO_BY_ROUTE[route_id]

    return V15RouteContract(
        contract_version="v15.0.0",
        route_id=route_id,
        execution_form=_canonical_execution_form(route_id),
        confidence_score=float(confidence_score),
        confidence_class=confidence_class,
        reason_codes=reason_codes,
        freshness_class=signals.freshness_class,
        cache_policy=cache_policy,
        support_target=support_target,
        cost_tier=cost_tier,
        fallback_chain=fallback_chain,
        slo=slo,
        authority=signals.authority,
        telemetry_keys=telemetry,
        signatures=signatures,
        base_contract_id=signals.base_contract_id,
        hitl_pause_points=hitl_pause_points,
        workflow_blueprint_id=workflow_blueprint_id,
    )


def _canonical_execution_form(route_id: RouteIdV15) -> ExecutionFormV15:
    """v15 has only 3 execution forms; one per route family."""
    if route_id in {
        RouteIdV15.R1A_EXACT_CACHE,
        RouteIdV15.R1B_SEMANTIC_CACHE,
        RouteIdV15.R5_FALLBACK,
    }:
        return ExecutionFormV15.TERMINAL_SHORTCIRCUIT
    if route_id in {
        RouteIdV15.R3_SIMPLE_GROUNDED_READ,
        RouteIdV15.R4_SINGLE_ACTION,
    }:
        return ExecutionFormV15.SINGLE_STEP
    return ExecutionFormV15.MANAGED_WORKFLOW


__all__ = [
    "COLD_START_CONFIDENCE_THRESHOLD",
    "RouteSignalsV15",
    "select_route_v15",
]
