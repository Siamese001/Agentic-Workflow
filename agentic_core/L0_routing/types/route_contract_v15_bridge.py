"""v12 ↔ v15 RouteContract bridge.

Lossy-by-design translation between the v12 ``V12RouteAnnex`` shape and the
v15 ``V15RouteContract`` shape. Use this when a v12 producer must hand off
to a v15 consumer (or vice versa) during the migration window.

Design notes
------------

v15 collapses several v12 routes into ``R3R4_MANAGED_WORKFLOW``:

    v12                   -> v15
    -----------------------------------------------------------
    R1A                   -> R1A_EXACT_CACHE
    R1B                   -> R1B_SEMANTIC_CACHE
    R3_GROUNDED           -> R3_SIMPLE_GROUNDED_READ
    R4_ACTION             -> R4_SINGLE_ACTION
    R3R4_WORKFLOW         -> R3R4_MANAGED_WORKFLOW
    R5_FALLBACK           -> R5_FALLBACK
    R_PAR / R_LOOP / R_HITL / R_CASC -> R3R4_MANAGED_WORKFLOW
        (with appropriate reason_codes and TIER_HITL for R-HITL)

v15 has stricter execution-form coherence (only 3 forms), so v12's richer
forms (PARALLEL_FANOUT, ITERATIVE_LOOP, HUMAN_GATED) are absorbed into
``MANAGED_WORKFLOW`` with reason codes that surface the original intent.

The reverse direction (v15 -> v12) is straightforward because v15 is a
strict subset of v12's route id surface for the simple cases.
"""

from __future__ import annotations

from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    CachePolicy as CachePolicyV12,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    CostTier as CostTierV12,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    ExecutionForm as ExecutionFormV12,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    FallbackEntry as FallbackEntryV12,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    FreshnessClass as FreshnessClassV12,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    RouteId as RouteIdV12,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    RouteSLO as RouteSLOV12,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    TenantScope as TenantScopeV12,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    V12RouteAnnex,
)
from agentic_core.L0_routing.types.route_contract_v15 import (
    AuthorityScope,
    CachePolicyV15,
    CapabilityClass,
    CostTierV15,
    ExecutionFormV15,
    FallbackEntryV15,
    FreshnessClassV15,
    ReasonCodeV15,
    RouteIdV15,
    RouteSLOV15,
    SafeResponseType,
    SandboxClass,
    SideEffectClass,
    SignaturesV15,
    SupportTargetV15,
    TelemetryKeysV15,
    V15RouteContract,
    V15RouteContractError,
    WriteAuthority,
    _classify_confidence,
    compute_deterministic_route_digest,
    compute_manifest_hash,
)

# ---------------------------------------------------------------------------
# Forward (v12 -> v15) maps
# ---------------------------------------------------------------------------

_V12_TO_V15_ROUTE: dict[RouteIdV12, RouteIdV15] = {
    RouteIdV12.R1A: RouteIdV15.R1A_EXACT_CACHE,
    RouteIdV12.R1B: RouteIdV15.R1B_SEMANTIC_CACHE,
    RouteIdV12.R3_GROUNDED: RouteIdV15.R3_SIMPLE_GROUNDED_READ,
    RouteIdV12.R4_ACTION: RouteIdV15.R4_SINGLE_ACTION,
    RouteIdV12.R3R4_WORKFLOW: RouteIdV15.R3R4_MANAGED_WORKFLOW,
    RouteIdV12.R5_FALLBACK: RouteIdV15.R5_FALLBACK,
    RouteIdV12.R_PAR: RouteIdV15.R3R4_MANAGED_WORKFLOW,
    RouteIdV12.R_LOOP: RouteIdV15.R3R4_MANAGED_WORKFLOW,
    RouteIdV12.R_HITL: RouteIdV15.R3R4_MANAGED_WORKFLOW,
    RouteIdV12.R_CASC: RouteIdV15.R3R4_MANAGED_WORKFLOW,
}

_V12_TO_V15_FRESHNESS: dict[FreshnessClassV12, FreshnessClassV15] = {
    FreshnessClassV12.REALTIME: FreshnessClassV15.LIVE,
    FreshnessClassV12.FRESH: FreshnessClassV15.CURRENT,
    FreshnessClassV12.STABLE: FreshnessClassV15.SLOW_CHANGING,
    FreshnessClassV12.ARCHIVAL: FreshnessClassV15.STATIC,
}

_V12_TO_V15_COST: dict[CostTierV12, CostTierV15] = {
    CostTierV12.TIER_S: CostTierV15.TIER_S,
    CostTierV12.TIER_M: CostTierV15.TIER_M,
    CostTierV12.TIER_L: CostTierV15.TIER_L,
}

_V12_TO_V15_REASON_FOR_ROUTE: dict[RouteIdV12, tuple[str, ...]] = {
    RouteIdV12.R_PAR: (ReasonCodeV15.MULTI_STEP_REQUIRED.value,),
    RouteIdV12.R_LOOP: (ReasonCodeV15.MULTI_STEP_REQUIRED.value,),
    RouteIdV12.R_HITL: (
        ReasonCodeV15.HITL_REQUIRED.value,
        ReasonCodeV15.ACTION_HIGH_RISK.value,
    ),
    RouteIdV12.R_CASC: (ReasonCodeV15.MULTI_STEP_REQUIRED.value,),
}

# ---------------------------------------------------------------------------
# Reverse (v15 -> v12) maps
# ---------------------------------------------------------------------------

_V15_TO_V12_ROUTE: dict[RouteIdV15, RouteIdV12] = {
    RouteIdV15.R1A_EXACT_CACHE: RouteIdV12.R1A,
    RouteIdV15.R1B_SEMANTIC_CACHE: RouteIdV12.R1B,
    RouteIdV15.R3_SIMPLE_GROUNDED_READ: RouteIdV12.R3_GROUNDED,
    RouteIdV15.R4_SINGLE_ACTION: RouteIdV12.R4_ACTION,
    RouteIdV15.R3R4_MANAGED_WORKFLOW: RouteIdV12.R3R4_WORKFLOW,
    RouteIdV15.R5_FALLBACK: RouteIdV12.R5_FALLBACK,
}

_V15_TO_V12_FRESHNESS: dict[FreshnessClassV15, FreshnessClassV12] = {
    FreshnessClassV15.LIVE: FreshnessClassV12.REALTIME,
    FreshnessClassV15.CURRENT: FreshnessClassV12.FRESH,
    FreshnessClassV15.RECENT: FreshnessClassV12.FRESH,
    FreshnessClassV15.SLOW_CHANGING: FreshnessClassV12.STABLE,
    FreshnessClassV15.STATIC: FreshnessClassV12.ARCHIVAL,
}

_V15_TO_V12_COST: dict[CostTierV15, CostTierV12] = {
    CostTierV15.TIER_S: CostTierV12.TIER_S,
    CostTierV15.TIER_M: CostTierV12.TIER_M,
    CostTierV15.TIER_L: CostTierV12.TIER_L,
    # v12 has no TIER_HITL; downshift to TIER_M (the de-facto HITL tier in v12).
    CostTierV15.TIER_HITL: CostTierV12.TIER_M,
}


def _v15_to_v12_cache_policy(policy: CachePolicyV15) -> CachePolicyV12:
    """Best-effort policy downgrade. v12 has 4 values, v15 has 5."""
    if policy == CachePolicyV15.EXACT_ONLY:
        return CachePolicyV12.EXACT_ONLY
    if policy == CachePolicyV15.SEMANTIC_OK:
        return CachePolicyV12.SEMANTIC_OK
    if policy in {CachePolicyV15.READ_THROUGH, CachePolicyV15.BYPASS_CACHE}:
        return CachePolicyV12.CASCADE_CACHE_FIRST
    return CachePolicyV12.NO_CACHE


def _translate_fallback_chain(
    v12_chain: tuple[FallbackEntryV12, ...],
) -> list[FallbackEntryV15]:
    """Map a v12 fallback chain to v15; drop entries with no v15 mapping."""
    out: list[FallbackEntryV15] = []
    for entry in v12_chain:
        v15_route = _V12_TO_V15_ROUTE.get(entry.route_id)
        if v15_route is None:
            continue
        cost = _V12_TO_V15_COST[entry.cost_tier]
        out.append(FallbackEntryV15(route_id=v15_route, cost_tier=cost, provider=entry.provider))
    return out


def _v15_to_v12_execution_form(
    form: ExecutionFormV15,
    route_id: RouteIdV15,
) -> ExecutionFormV12:
    """v15 form -> v12 form. Managed workflow stays managed."""
    if form == ExecutionFormV15.TERMINAL_SHORTCIRCUIT:
        return ExecutionFormV12.TERMINAL_SHORTCIRCUIT
    if form == ExecutionFormV15.SINGLE_STEP:
        return ExecutionFormV12.SINGLE_STEP
    # Managed workflow — pass through.
    if route_id == RouteIdV15.R3R4_MANAGED_WORKFLOW:
        return ExecutionFormV12.MANAGED_WORKFLOW
    return ExecutionFormV12.MANAGED_WORKFLOW


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def v12_to_v15(
    annex: V12RouteAnnex,
    *,
    blueprint_hash: str,
    snapshot_id: str,
    trace_root: str,
    route_span_id: str,
    replay_key: str,
    route_telemetry_event_id: str,
    workflow_blueprint_id: str | None = None,
    capability_class: CapabilityClass = CapabilityClass.READ_ONLY,
    side_effect_class: SideEffectClass = SideEffectClass.PURE,
    sandbox_class: SandboxClass = SandboxClass.NO_SANDBOX,
    support_target: SupportTargetV15 = SupportTargetV15.NONE,
    freshness_class: FreshnessClassV15 | None = None,
) -> V15RouteContract:
    """Translate a v12 ``V12RouteAnnex`` into an unsigned v15 contract.

    The ``hmac_sig`` is intentionally empty in the returned contract — call
    :meth:`V15RouteContract.sign` after translation.

    Parameters that v12 does not carry (blueprint_hash, snapshot_id, trace
    identity) MUST be supplied by the caller. ``workflow_blueprint_id`` is
    required when ``annex.route_id`` maps to ``R3R4_MANAGED_WORKFLOW``.

    Raises:
        V15RouteContractError: when the source annex maps to an
            unrepresentable v15 contract (missing blueprint id, etc.).
    """
    if not isinstance(annex, V12RouteAnnex):
        raise V15RouteContractError(
            f"v12_to_v15 expects V12RouteAnnex, got {type(annex).__name__}",
        )
    v15_route = _V12_TO_V15_ROUTE.get(annex.route_id)
    if v15_route is None:
        raise V15RouteContractError(
            f"v12 route {annex.route_id.value} has no v15 mapping",
        )

    # Translate fallback chain — drop entries that map to UNKNOWN routes.
    v15_chain = _translate_fallback_chain(annex.fallback_chain)
    # Ensure non-terminal route has R5 last (the v15 contract enforces this).
    terminal = {
        RouteIdV15.R1A_EXACT_CACHE,
        RouteIdV15.R1B_SEMANTIC_CACHE,
        RouteIdV15.R5_FALLBACK,
    }
    if v15_route not in terminal:
        if not v15_chain or v15_chain[-1].route_id != RouteIdV15.R5_FALLBACK:
            v15_chain.append(
                FallbackEntryV15(RouteIdV15.R5_FALLBACK, CostTierV15.TIER_S),
            )

    fresh_v15 = (
        freshness_class if freshness_class is not None else _V12_TO_V15_FRESHNESS[annex.freshness_class]
    )

    # v15 cache_policy is whitelisted per route. Pick a safe default per route.
    if v15_route == RouteIdV15.R1A_EXACT_CACHE:
        v15_cache = CachePolicyV15.EXACT_ONLY
    elif v15_route == RouteIdV15.R1B_SEMANTIC_CACHE:
        v15_cache = CachePolicyV15.SEMANTIC_OK
    elif v15_route == RouteIdV15.R3_SIMPLE_GROUNDED_READ:
        v15_cache = CachePolicyV15.READ_THROUGH
    elif v15_route in {RouteIdV15.R4_SINGLE_ACTION, RouteIdV15.R5_FALLBACK}:
        v15_cache = CachePolicyV15.NO_CACHE
    else:  # managed workflow
        v15_cache = CachePolicyV15.NO_CACHE

    # Cost tier — special-case R-HITL.
    if annex.route_id == RouteIdV12.R_HITL:
        v15_cost = CostTierV15.TIER_HITL
    else:
        v15_cost = _V12_TO_V15_COST[annex.cost_tier]

    # Authority — synthesize from v12 tenant_scope.
    authority = AuthorityScope(
        tenant_scope=annex.tenant_scope.tenant_id,
        acl_scope=annex.tenant_scope.acl_bounds,
        region_scope=annex.tenant_scope.region,
        capability_class=capability_class,
        side_effect_class=side_effect_class,
        sandbox_class=sandbox_class,
        write_authority=WriteAuthority.NONE_UNTIL_UWG,
    )

    # Map SLO 1:1 (units already align, plus zero defaults for v15-only fields).
    v15_slo = RouteSLOV15(
        max_latency_ms=annex.slo.latency_budget_ms,
        max_cost=annex.slo.cost_cap_usd,
        max_tokens=annex.slo.token_budget_in + annex.slo.token_budget_out,
        max_retrieval_passes=2 if v15_route == RouteIdV15.R3_SIMPLE_GROUNDED_READ else 0,
        max_graph_hops=2 if v15_route == RouteIdV15.R3_SIMPLE_GROUNDED_READ else 0,
        max_tool_calls=1 if v15_route == RouteIdV15.R4_SINGLE_ACTION else 0,
        max_iterations=4 if v15_route == RouteIdV15.R3R4_MANAGED_WORKFLOW else 0,
        reserve_for_exit_eval=512 if v15_route != RouteIdV15.R5_FALLBACK else 0,
    )

    # Reason codes — preserve original v12 codes plus add archetype reasons.
    v12_archetype_reasons = _V12_TO_V15_REASON_FOR_ROUTE.get(annex.route_id, ())
    # v12 reason_codes are free-form; only keep those in the v15 closed vocabulary.
    known_v15 = {r.value for r in ReasonCodeV15}
    preserved = tuple(c for c in annex.reason_codes if c in known_v15)
    # Ensure R5 selects a fallback reason code.
    if v15_route == RouteIdV15.R5_FALLBACK and not any(
        c == ReasonCodeV15.FALLBACK_SELECTED.value for c in preserved
    ):
        preserved = (*preserved, ReasonCodeV15.FALLBACK_SELECTED.value)
    reason_codes = tuple(dict.fromkeys((*preserved, *v12_archetype_reasons)))
    if not reason_codes:
        # Fall back to a generic reason so we never emit an empty tuple.
        reason_codes = (ReasonCodeV15.FALLBACK_SELECTED.value,)

    # Confidence — v12 is numeric only; derive class via the v15 mapper.
    confidence_class = _classify_confidence(annex.confidence)

    # Workflow blueprint id required for managed workflow.
    if v15_route == RouteIdV15.R3R4_MANAGED_WORKFLOW and not workflow_blueprint_id:
        raise V15RouteContractError(
            "v12_to_v15: workflow_blueprint_id required when target route is R3R4_MANAGED_WORKFLOW",
        )

    # Compute deterministic digest.
    digest = compute_deterministic_route_digest(
        route_id=v15_route,
        execution_form=_canonical_form(v15_route),
        cache_policy=v15_cache,
        freshness_class=fresh_v15,
        support_target=support_target,
        cost_tier=v15_cost,
        reason_codes=reason_codes,
        fallback_chain=tuple(v15_chain),
        authority=authority,
        policy_hash=annex.base_contract_id or "policy:unknown",
        blueprint_hash=blueprint_hash,
        snapshot_id=snapshot_id,
    )
    manifest_hash = compute_manifest_hash(
        contract_version="v15.0.0",
        route_digest=digest,
        policy_hash=annex.base_contract_id or "policy:unknown",
        blueprint_hash=blueprint_hash,
        snapshot_id=snapshot_id,
    )

    telemetry = TelemetryKeysV15(
        trace_root=trace_root,
        route_span_id=route_span_id,
        route_digest=digest,
        policy_hash=annex.base_contract_id or "policy:unknown",
        blueprint_hash=blueprint_hash,
        snapshot_id=snapshot_id,
        replay_key=replay_key,
        route_telemetry_event_id=route_telemetry_event_id,
    )
    signatures = SignaturesV15(
        manifest_hash=manifest_hash,
        deterministic_route_digest=digest,
        hmac_sig="",
    )

    return V15RouteContract(
        contract_version="v15.0.0",
        route_id=v15_route,
        execution_form=_canonical_form(v15_route),
        confidence_score=annex.confidence,
        confidence_class=confidence_class,
        reason_codes=reason_codes,
        freshness_class=fresh_v15,
        cache_policy=v15_cache,
        support_target=support_target,
        cost_tier=v15_cost,
        fallback_chain=tuple(v15_chain),
        slo=v15_slo,
        authority=authority,
        telemetry_keys=telemetry,
        signatures=signatures,
        base_contract_id=annex.base_contract_id,
        hitl_pause_points=(("HITL_PRECOMMIT",) if annex.route_id == RouteIdV12.R_HITL else ()),
        workflow_blueprint_id=workflow_blueprint_id,
        safe_response_type=(SafeResponseType.ABSTAIN if v15_route == RouteIdV15.R5_FALLBACK else None),
    )


def v15_to_v12(
    contract: V15RouteContract,
    *,
    secret_key: bytes | None = None,
) -> V12RouteAnnex:
    """Translate a v15 contract back to a v12 annex.

    Use only when a v15 producer must hand off to a strictly-v12 consumer.
    The resulting annex has ``hmac_sig=""``; call ``annex.sign(key)``
    afterwards if required, or pass ``secret_key`` to sign in-place.

    Raises:
        V12RouteContractError: when the resulting annex would violate v12
            invariants (e.g., ``execution_form`` mismatch).
    """
    if not isinstance(contract, V15RouteContract):
        raise V15RouteContractError(
            f"v15_to_v12 expects V15RouteContract, got {type(contract).__name__}",
        )

    v12_route = _V15_TO_V12_ROUTE[contract.route_id]
    v12_freshness = _V15_TO_V12_FRESHNESS[contract.freshness_class]
    v12_cost = _V15_TO_V12_COST[contract.cost_tier]
    v12_cache = _v15_to_v12_cache_policy(contract.cache_policy)
    v12_form = _v15_to_v12_execution_form(contract.execution_form, contract.route_id)

    # Translate fallback chain.
    v12_chain: list[FallbackEntryV12] = []
    for v15_entry in contract.fallback_chain:
        v12_chain.append(
            FallbackEntryV12(
                route_id=_V15_TO_V12_ROUTE[v15_entry.route_id],
                cost_tier=_V15_TO_V12_COST[v15_entry.cost_tier],
                provider=v15_entry.provider,
            ),
        )

    # v12 SLO has no retrieval/graph/tool/iteration fields — drop them.
    v12_slo = RouteSLOV12(
        latency_budget_ms=contract.slo.max_latency_ms,
        token_budget_in=contract.slo.max_tokens // 2,
        token_budget_out=contract.slo.max_tokens - (contract.slo.max_tokens // 2),
        cost_cap_usd=contract.slo.max_cost,
    )

    tenant = TenantScopeV12(
        tenant_id=contract.authority.tenant_scope,
        region=contract.authority.region_scope,
        acl_bounds=contract.authority.acl_scope,
    )

    annex = V12RouteAnnex(
        contract_version="1.0.0",
        base_contract_id=contract.base_contract_id or "v15-bridge",
        route_id=v12_route,
        confidence=contract.confidence_score,
        reason_codes=contract.reason_codes,
        freshness_class=v12_freshness,
        cache_policy=v12_cache,
        execution_form=v12_form,
        cost_tier=v12_cost,
        fallback_chain=tuple(v12_chain),
        slo=v12_slo,
        telemetry_keys=(),
        tenant_scope=tenant,
        hmac_sig="",
    )
    if secret_key is not None:
        annex = annex.sign(secret_key)
    return annex


def _canonical_form(route_id: RouteIdV15) -> ExecutionFormV15:
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
    "v12_to_v15",
    "v15_to_v12",
]
