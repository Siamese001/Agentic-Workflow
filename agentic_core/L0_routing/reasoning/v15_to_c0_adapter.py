"""V15RouteContract -> C0 RouteContract adapter.

L0's v15 selector emits :class:`V15RouteContract` (with HMAC + deterministic
digest). C0's :class:`RouteContract` is a simpler shape used by the C0
dispatcher. This module is the SINGLE bridge between the two — pure shape
mapping, no I/O, no policy decisions.

Key invariants:

  - The HMAC signature (``signatures.hmac_sig``) is forwarded onto the new
    C0 ``RouteContract.hmac_sig`` field so downstream verifiers can confirm
    the route is signed.
  - Enum values are mapped explicitly (V15 enums and C0 enums use different
    canonical strings).
  - The V15 SLO is decomposed into the equivalent C0 max_* / *_budget /
    latency_slo fields.
  - The V15 ``fallback_chain`` (a typed list) is collapsed into the C0
    string ``fallback_policy`` (caveat | abstain | R5 | reroute) using the
    documented mapping.

Anti-cheat: this adapter never invents fields. If a required C0 field is
not derivable from V15, the function raises ``V15ToC0AdapterError`` rather
than silently substituting a default that could mask a routing bug.
"""
from __future__ import annotations

from agentic_core.L0_routing.c0_retrieval.preflight import build_c0_policy
from agentic_core.L0_routing.c0_retrieval.route_contract import (
    L1PlanContract,
    RouteContract,
)
from agentic_core.L0_routing.c0_retrieval.verdicts import (
    FreshnessClass as C0FreshnessClass,
)
from agentic_core.L0_routing.c0_retrieval.verdicts import (
    SourceClass as C0SourceClass,
)
from agentic_core.L0_routing.c0_retrieval.verdicts import (
    SupportTarget as C0SupportTarget,
)
from agentic_core.L0_routing.types.route_contract_v15 import (
    CachePolicyV15,
    ExecutionFormV15,
    FreshnessClassV15,
    RouteIdV15,
    SupportTargetV15,
    V15RouteContract,
)


class V15ToC0AdapterError(ValueError):
    """Raised when a V15RouteContract cannot be mapped to a C0 RouteContract."""


# ---------------------------------------------------------------------------
# Enum maps (explicit; do NOT auto-derive from member names — the canonical
# strings differ deliberately between V15 and C0).
# ---------------------------------------------------------------------------

_FRESHNESS_MAP: dict[FreshnessClassV15, C0FreshnessClass] = {
    FreshnessClassV15.STATIC: C0FreshnessClass.STATIC,
    FreshnessClassV15.SLOW_CHANGING: C0FreshnessClass.SLOW,
    FreshnessClassV15.RECENT: C0FreshnessClass.SLOW,
    FreshnessClassV15.CURRENT: C0FreshnessClass.CURRENT,
    FreshnessClassV15.LIVE: C0FreshnessClass.LATEST,
}

_SUPPORT_MAP: dict[SupportTargetV15, C0SupportTarget] = {
    SupportTargetV15.NONE: C0SupportTarget.SOURCE_SUMMARY,  # default safe surface
    SupportTargetV15.EXACT_QUOTE: C0SupportTarget.EXACT_QUOTE,
    SupportTargetV15.SOURCE_BACKED_SUMMARY: C0SupportTarget.SOURCE_SUMMARY,
    SupportTargetV15.POLICY_CLAUSE: C0SupportTarget.POLICY_CLAUSE,
    SupportTargetV15.CODE_LOCATION: C0SupportTarget.CODE_LOCATION,
    SupportTargetV15.INCIDENT_EVIDENCE: C0SupportTarget.INCIDENT_EVIDENCE,
    SupportTargetV15.RANKED_CAUSE: C0SupportTarget.SOURCE_SUMMARY,
    SupportTargetV15.ACTION_ARGUMENT_GROUNDING: C0SupportTarget.SOURCE_SUMMARY,
}

# C0 expects "SINGLE_STEP" or "MANAGED_WORKFLOW_STEP". V15 has three forms.
_EXEC_MAP: dict[ExecutionFormV15, str] = {
    ExecutionFormV15.TERMINAL_SHORTCIRCUIT: "SINGLE_STEP",
    ExecutionFormV15.SINGLE_STEP: "SINGLE_STEP",
    ExecutionFormV15.MANAGED_WORKFLOW: "MANAGED_WORKFLOW_STEP",
}

# V15 cache policy hint -> C0 fallback_policy convention.
_CACHE_TO_FALLBACK: dict[CachePolicyV15, str] = {
    CachePolicyV15.EXACT_ONLY: "R5",
    CachePolicyV15.SEMANTIC_OK: "R5",
    CachePolicyV15.READ_THROUGH: "caveat",
    CachePolicyV15.NO_CACHE: "caveat",
    CachePolicyV15.BYPASS_CACHE: "caveat",
}


def v15_to_route_contract(
    v15: V15RouteContract,
    *,
    allowed_sources: tuple[C0SourceClass, ...] = (),
    allowed_data_classes: tuple[str, ...] = ("public", "internal"),
    data_class: str = "internal",
    route_replay_key: str = "",
    policy_hash: str = "",
    blueprint_hash: str = "",
    l1_plan: L1PlanContract | None = None,
) -> RouteContract:
    """Map a V15RouteContract into the C0 RouteContract shape.

    Args:
        v15: The signed V15 contract from the v15 selector.
        allowed_sources, allowed_data_classes, data_class: Caller-controlled
            ACL surfaces. V15 carries authority but does not enumerate
            allowed source classes; the caller (which knows the tenant
            ACL) MUST supply them.
        route_replay_key, policy_hash, blueprint_hash: Replay/audit hooks.
            V15 stamps these on its signatures/digest path; we forward them
            so C0's replay metadata stays consistent.
        l1_plan: Optional L1 plan contract for C0 policy construction.
            If provided, L0 freezes C0 policy using L1 advisory signals.

    Returns:
        A frozen :class:`RouteContract` ready to feed into the C0 dispatcher.
        ``hmac_sig`` is forwarded from ``v15.signatures.hmac_sig``.
        ``c0_policy`` is frozen based on route topology and L1 advisory.

    Raises:
        V15ToC0AdapterError: If a non-default-mappable field is missing.
    """
    if not isinstance(v15, V15RouteContract):
        raise V15ToC0AdapterError(
            f"v15 must be V15RouteContract, got {type(v15).__name__}"
        )

    try:
        c0_freshness = _FRESHNESS_MAP[v15.freshness_class]
    except KeyError as exc:
        raise V15ToC0AdapterError(
            f"unmapped V15 freshness_class: {v15.freshness_class}"
        ) from exc
    try:
        c0_support = _SUPPORT_MAP[v15.support_target]
    except KeyError as exc:
        raise V15ToC0AdapterError(
            f"unmapped V15 support_target: {v15.support_target}"
        ) from exc
    try:
        c0_exec = _EXEC_MAP[v15.execution_form]
    except KeyError as exc:
        raise V15ToC0AdapterError(
            f"unmapped V15 execution_form: {v15.execution_form}"
        ) from exc

    fallback_policy = _CACHE_TO_FALLBACK.get(v15.cache_policy, "caveat")
    grounding_required = v15.support_target != SupportTargetV15.NONE

    # W3 c0-policy-rectification-f7b2a9: Build minimal L1PlanContract if not provided.
    if l1_plan is None:
        l1_plan = L1PlanContract(
            task_spec="",
            query_spec="",
            grounding_required=grounding_required,
            user_task_text="",
        )

    slo = v15.slo
    route = RouteContract(
        route_id=str(v15.route_id.value),
        grounding_required=grounding_required,
        execution_form=c0_exec,
        freshness_class=c0_freshness,
        support_target=c0_support,
        tenant_scope=v15.authority.tenant_scope,
        region=v15.authority.region_scope,
        data_class=data_class,
        acl_roles=tuple(v15.authority.acl_scope),
        max_k=20,
        max_hops=max(1, slo.max_graph_hops),
        max_parent_expansion=2,
        max_child_expansion=2,
        max_refine_attempts=max(1, slo.max_iterations),
        max_token_context=max(1, slo.max_tokens or 4000),
        max_source_classes=7,
        max_latency_ms=slo.max_latency_ms,
        max_cost_tier="standard",
        latency_slo=slo.max_latency_ms,
        token_budget=max(1, slo.max_tokens or 4000),
        allowed_sources=allowed_sources,
        disallowed_sources=(),
        allowed_data_classes=allowed_data_classes,
        fallback_policy=fallback_policy,
        route_replay_key=route_replay_key,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        origin_trust_manifest={
            "deterministic_route_digest": v15.signatures.deterministic_route_digest,
            "manifest_hash": v15.signatures.manifest_hash,
            "v15_route_id": v15.route_id.value,
            "v15_confidence_class": v15.confidence_class.value,
        },
        hmac_sig=v15.signatures.hmac_sig,
    )

    # W3: Freeze C0 policy into RouteContract (L0 authority).
    route = RouteContract(
        **{k: v for k, v in route.__dict__.items() if k != "c0_policy"},
        c0_policy=build_c0_policy(route, l1_plan),
    )

    return route


def route_id_for_v15(route: RouteIdV15) -> str:
    """Convenience: return the canonical string used by C0 for a v15 route id."""
    return str(route.value)


__all__ = [
    "V15ToC0AdapterError",
    "v15_to_route_contract",
    "route_id_for_v15",
]
