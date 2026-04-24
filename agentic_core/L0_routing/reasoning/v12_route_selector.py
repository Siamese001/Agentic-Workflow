"""v12 §13 — Route Selection Decision Order.

Normative first-match-wins decision tree that maps a ``RouteSignals``
dataclass into a ``V12RouteAnnex``. Pure function — no I/O, no side effects.

This is the reference Python realization of v12 §13; production dispatchers
may wrap additional policy checks (tenant quota, guardrail signals)
around it, but MUST NOT reorder the matches.

Order (first match wins):
  1. Pre-filter fails (tenant/ACL/region/expiry)           → R5_FALLBACK
  2. Classifier confidence < cold_start_threshold          → §7 cold-start override
  3. Exact cache hit                                       → R1A
  4. Semantic cache hit (post R1B.3 policy gates)          → R1B
  5. High-stakes / irreversible action                     → R-HITL
  6. Bounded-reversibility action                          → R4_ACTION
  7. Multi-aspect parallelizable task                      → R-PAR
  8. Qualitative-refinement task (gen-critic-refine)       → R-LOOP
  9. Single-step grounded claim                            → R3_GROUNDED
 10. Ambiguous tier / confidence-varying difficulty        → R-CASC
 11. Multi-hop / cross-step contract change                → R3R4_WORKFLOW
 12. Otherwise                                             → R5_FALLBACK
"""

from __future__ import annotations

from dataclasses import dataclass, field

from agentic_core.L0_routing.config.fallback_chains_loader import (
    get_fallback_chain,
    get_slo_default,
)
from agentic_core.L0_routing.config.routing_calibration import (
    get_v12_threshold,
)
from agentic_core.L0_routing.reasoning.cold_start_safeguard import (
    maybe_override_for_cold_start,
)
from agentic_core.L0_routing.types.route_contract_v12_extensions import (
    CachePolicy,
    CostTier,
    ExecutionForm,
    FallbackEntry,
    FreshnessClass,
    RouteId,
    TenantScope,
    V12RouteAnnex,
    V12RouteContractError,
)


@dataclass(frozen=True)
class RouteSignals:
    """All signals the dispatcher uses to pick a route.

    Populated by upstream stages (ingress pre-filter, classifier, cache
    probes). Each flag's semantics documented inline.
    """

    # Ingress pre-filter result. False → route 1 (R5_FALLBACK).
    ingress_ok: bool
    tenant_scope: TenantScope

    # Classifier output.
    classifier_confidence: float
    top_pick_route: RouteId
    top_pick_tier: CostTier
    classifier_reason_codes: tuple[str, ...] = ()

    # Cache probes.
    exact_cache_hit: bool = False
    semantic_cache_hit: bool = False  # post-gate (R1B.3 already passed)

    # Action signals.
    high_stakes_action: bool = False  # irreversible / sensitive-data mutation
    bounded_reversible_action: bool = False

    # Workflow-shape signals.
    independent_subtasks_ge_2: bool = False
    generator_critic_refiner_applicable: bool = False
    single_step_grounded_sufficient: bool = False
    tier_varying_difficulty: bool = False  # hard to pre-classify difficulty
    cross_step_contract_change: bool = False

    # Freshness + cache preferences.
    freshness_class: FreshnessClass = FreshnessClass.STABLE

    # Telemetry feature-key list — passed through unchanged into the annex.
    telemetry_keys: tuple[str, ...] = field(default_factory=tuple)

    # Base contract id this annex attaches to (existing RoutingContract FK).
    base_contract_id: str = ""


def _cache_policy_for(route_id: RouteId) -> CachePolicy:
    if route_id == RouteId.R1A:
        return CachePolicy.EXACT_ONLY
    if route_id == RouteId.R1B:
        return CachePolicy.SEMANTIC_OK
    if route_id in {RouteId.R4_ACTION, RouteId.R_HITL, RouteId.R5_FALLBACK}:
        return CachePolicy.NO_CACHE
    return CachePolicy.CASCADE_CACHE_FIRST


def _execution_form_for(route_id: RouteId) -> ExecutionForm:
    mapping: dict[RouteId, ExecutionForm] = {
        RouteId.R1A: ExecutionForm.TERMINAL_SHORTCIRCUIT,
        RouteId.R1B: ExecutionForm.TERMINAL_SHORTCIRCUIT,
        RouteId.R5_FALLBACK: ExecutionForm.TERMINAL_SHORTCIRCUIT,
        RouteId.R3_GROUNDED: ExecutionForm.SINGLE_STEP,
        RouteId.R4_ACTION: ExecutionForm.SINGLE_STEP,
        RouteId.R_PAR: ExecutionForm.PARALLEL_FANOUT,
        RouteId.R_LOOP: ExecutionForm.ITERATIVE_LOOP,
        RouteId.R3R4_WORKFLOW: ExecutionForm.MANAGED_WORKFLOW,
        RouteId.R_HITL: ExecutionForm.HUMAN_GATED,
        RouteId.R_CASC: ExecutionForm.SINGLE_STEP,  # same shape as R3 to L2
    }
    return mapping[route_id]


def _pick_tier_for(route_id: RouteId, signals: RouteSignals) -> CostTier:
    # Defaults per v12 §10 budgets table. Callers can post-adjust.
    if route_id in {RouteId.R1A, RouteId.R1B, RouteId.R5_FALLBACK}:
        return CostTier.TIER_S
    if route_id == RouteId.R_HITL:
        return CostTier.TIER_M
    if route_id == RouteId.R3R4_WORKFLOW:
        return CostTier.TIER_L
    if route_id == RouteId.R_CASC:
        return CostTier.TIER_S  # cascade ALWAYS starts at S
    return signals.top_pick_tier


def select_route(signals: RouteSignals) -> V12RouteAnnex:
    """Apply v12 §13 decision order and return a signed-pending annex.

    The returned annex has ``hmac_sig == ""`` — the caller is responsible
    for calling ``.sign(secret_key)`` before persisting or dispatching.
    """
    cold_threshold = get_v12_threshold("cold_start_conservative_threshold")

    # Step 1 — ingress reject.
    if not signals.ingress_ok:
        return _assemble(
            signals,
            route_id=RouteId.R5_FALLBACK,
            cost_tier=CostTier.TIER_S,
            reason_codes=("ingress_reject",),
            chain_prefix=(),
        )

    # Step 3 — exact cache.
    if signals.exact_cache_hit:
        return _assemble(
            signals,
            route_id=RouteId.R1A,
            cost_tier=CostTier.TIER_S,
            reason_codes=("exact_cache_hit",),
            chain_prefix=(),
        )

    # Step 4 — semantic cache hit (policy gates already passed).
    if signals.semantic_cache_hit:
        return _assemble(
            signals,
            route_id=RouteId.R1B,
            cost_tier=CostTier.TIER_S,
            reason_codes=("semantic_cache_hit_postgate",),
            chain_prefix=(),
        )

    # Step 5 — high-stakes action.
    if signals.high_stakes_action:
        return _assemble(
            signals,
            route_id=RouteId.R_HITL,
            cost_tier=CostTier.TIER_M,
            reason_codes=("high_stakes_action",),
            chain_prefix=(),
        )

    # Determine the "natural" top pick under Steps 6..11.
    natural_pick = _natural_top_pick(signals)

    # Step 2 (applied late — after ingress/cache/HITL shortcuts, because those
    # signals dominate classifier confidence per v12 §7 rationale).
    decision = maybe_override_for_cold_start(
        top_pick=natural_pick,
        top_pick_tier=_pick_tier_for(natural_pick, signals),
        classifier_confidence=signals.classifier_confidence,
        cold_start_threshold=cold_threshold,
    )

    merged_reasons = signals.classifier_reason_codes + decision.reason_codes
    return _assemble(
        signals,
        route_id=decision.route_id,
        cost_tier=decision.cost_tier,
        reason_codes=merged_reasons,
        chain_prefix=decision.fallback_chain_prefix,
    )


def _natural_top_pick(signals: RouteSignals) -> RouteId:
    # Step 6
    if signals.bounded_reversible_action:
        return RouteId.R4_ACTION
    # Step 7
    if signals.independent_subtasks_ge_2:
        return RouteId.R_PAR
    # Step 8
    if signals.generator_critic_refiner_applicable:
        return RouteId.R_LOOP
    # Step 9
    if signals.single_step_grounded_sufficient:
        return RouteId.R3_GROUNDED
    # Step 10
    if signals.tier_varying_difficulty:
        return RouteId.R_CASC
    # Step 11
    if signals.cross_step_contract_change:
        return RouteId.R3R4_WORKFLOW
    # Step 12 — no viable route.
    return RouteId.R5_FALLBACK


def _assemble(
    signals: RouteSignals,
    *,
    route_id: RouteId,
    cost_tier: CostTier,
    reason_codes: tuple[str, ...],
    chain_prefix: tuple[FallbackEntry, ...],
) -> V12RouteAnnex:
    try:
        default_chain = get_fallback_chain(route_id)
    except V12RouteContractError:
        # Malformed YAML chain for this route — degrade gracefully to an
        # R5-only chain so the dispatcher can still return a valid contract.
        default_chain = (FallbackEntry(RouteId.R5_FALLBACK, CostTier.TIER_S),)
    full_chain = chain_prefix + default_chain
    # Merge dedup — keep first occurrence order, strip duplicate (route_id, cost_tier).
    # Also drop any entry that matches the primary (route_id, cost_tier) — that
    # would trip V12RouteAnnex's self-reference guard.
    primary_key = (route_id.value, cost_tier.value)
    seen: set[tuple[str, str]] = set()
    deduped: list[FallbackEntry] = []
    for entry in full_chain:
        key = (entry.route_id.value, entry.cost_tier.value)
        if key == primary_key:
            continue
        if key in seen:
            continue
        seen.add(key)
        deduped.append(entry)
    # Guarantee R5 is last if present.
    if any(e.route_id == RouteId.R5_FALLBACK for e in deduped):
        non_r5 = [e for e in deduped if e.route_id != RouteId.R5_FALLBACK]
        r5_entry = next(e for e in deduped if e.route_id == RouteId.R5_FALLBACK)
        deduped = [*non_r5, r5_entry]
    # Enforce hard depth cap at assembly time.
    _ASSEMBLY_MAX = 8
    if len(deduped) > _ASSEMBLY_MAX:
        deduped = deduped[:_ASSEMBLY_MAX]
        # If truncation removed R5, re-append it (truncation should never
        # leave a non-terminal chain without its safety net).
        if not any(e.route_id == RouteId.R5_FALLBACK for e in deduped):
            deduped[-1] = FallbackEntry(RouteId.R5_FALLBACK, CostTier.TIER_S)
    # Non-terminal routes require non-empty chain.
    _terminal = {RouteId.R1A, RouteId.R1B, RouteId.R5_FALLBACK}
    if route_id not in _terminal and not deduped:
        deduped = [FallbackEntry(RouteId.R5_FALLBACK, CostTier.TIER_S)]

    try:
        slo = get_slo_default(route_id, cost_tier)
    except V12RouteContractError:
        # No tier-specific default for this (route_id, cost_tier) cell —
        # fall through to R5_FALLBACK's SLO (documented in v12 §10 as the
        # floor envelope for any degenerate dispatch).
        slo = get_slo_default(RouteId.R5_FALLBACK)

    return V12RouteAnnex(
        contract_version="1.0.0",
        base_contract_id=signals.base_contract_id,
        route_id=route_id,
        confidence=signals.classifier_confidence,
        reason_codes=reason_codes,
        freshness_class=signals.freshness_class,
        cache_policy=_cache_policy_for(route_id),
        execution_form=_execution_form_for(route_id),
        cost_tier=cost_tier,
        fallback_chain=tuple(deduped),
        slo=slo,
        telemetry_keys=signals.telemetry_keys,
        tenant_scope=signals.tenant_scope,
        hmac_sig="",
    )
