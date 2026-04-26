"""Phase 3.6 — 15 gates that decide accept / reject for every neighbor.

Each gate returns ``GateDecision``. The first gate that returns ``reject`` or
``downgrade`` wins; if all gates pass the neighbor is accepted.

Gates are ordered (G1..G15) but apply_all_gates evaluates them in the order
defined here; this order matches the spec.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Mapping

from .adapter import GraphNeighbor, ProjectionManifest
from .contracts import (
    AclStatus,
    FreshnessClass,
    FreshnessStatus,
    GraphTraversalPlan,
    GraphTraverseInput,
    RejectionReason,
)


class GateName(str, Enum):
    G1_ACL = "C0.3.G1_ACL"
    G2_TENANT = "C0.3.G2_TENANT"
    G3_REGION = "C0.3.G3_REGION"
    G4_DATA_CLASS = "C0.3.G4_DATA_CLASS"
    G5_FRESHNESS = "C0.3.G5_FRESHNESS"
    G6_RELATION_ALLOWLIST = "C0.3.G6_RELATION_ALLOWLIST"
    G7_SOURCE_CLASS = "C0.3.G7_SOURCE_CLASS"
    G8_HOP_BUDGET = "C0.3.G8_HOP_BUDGET"
    G9_SUPPORT_RELEVANCE = "C0.3.G9_SUPPORT_RELEVANCE"
    G10_CONFIDENCE = "C0.3.G10_CONFIDENCE"
    G11_LINEAGE = "C0.3.G11_LINEAGE"
    G12_CITATION = "C0.3.G12_CITATION"
    G13_CONTRADICTION = "C0.3.G13_CONTRADICTION"
    G14_CYCLE = "C0.3.G14_CYCLE"
    G15_PROJECTION_CURRENCY = "C0.3.G15_PROJECTION_CURRENCY"


@dataclass(frozen=True)
class GateDecision:
    accepted: bool
    gate: GateName | None  # which gate fired (None when accepted clean)
    rejection_reason: RejectionReason | None
    note: str = ""
    flag_categories: tuple[str, ...] = ()


_PASS = GateDecision(accepted=True, gate=None, rejection_reason=None)


GateContext = Mapping[str, object]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _acl_value(value: AclStatus | str | None) -> str:
    if value is None:
        return ""
    return value.value if isinstance(value, AclStatus) else str(value)


def _freshness_value(value: FreshnessStatus | str | None) -> str:
    if value is None:
        return ""
    return value.value if isinstance(value, FreshnessStatus) else str(value)


def _freshness_class(value: FreshnessClass | str) -> FreshnessClass:
    if isinstance(value, FreshnessClass):
        return value
    try:
        return FreshnessClass(value)
    except ValueError:
        return FreshnessClass.STATIC


# ---------------------------------------------------------------------------
# gate implementations
# ---------------------------------------------------------------------------


def gate_g1_acl(
    neighbor: GraphNeighbor,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    ctx: GateContext,
) -> GateDecision:
    del plan, ctx
    acl = _acl_value(neighbor.acl_status)
    if acl == AclStatus.DENIED.value:
        return GateDecision(
            accepted=False,
            gate=GateName.G1_ACL,
            rejection_reason=RejectionReason.ACL_FAILED,
            note="acl=denied",
        )
    if inp.acl_scope:
        if acl not in inp.acl_scope:
            return GateDecision(
                accepted=False,
                gate=GateName.G1_ACL,
                rejection_reason=RejectionReason.ACL_FAILED,
                note=f"acl '{acl}' not in scope {inp.acl_scope}",
            )
    return _PASS


def gate_g2_tenant(
    neighbor: GraphNeighbor,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    ctx: GateContext,
) -> GateDecision:
    del plan, ctx
    if not inp.tenant_scope:
        return _PASS
    if neighbor.tenant is None:
        # No tenant on neighbor, but scope demanded — treat as wrong tenant
        # (defensive).
        return GateDecision(
            accepted=False,
            gate=GateName.G2_TENANT,
            rejection_reason=RejectionReason.WRONG_TENANT,
            note="neighbor.tenant is None",
        )
    if neighbor.tenant != inp.tenant_scope:
        return GateDecision(
            accepted=False,
            gate=GateName.G2_TENANT,
            rejection_reason=RejectionReason.WRONG_TENANT,
            note=f"tenant '{neighbor.tenant}' != scope '{inp.tenant_scope}'",
        )
    return _PASS


def gate_g3_region(
    neighbor: GraphNeighbor,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    ctx: GateContext,
) -> GateDecision:
    del plan, ctx
    if not inp.region_scope:
        return _PASS
    if neighbor.region is None:
        return GateDecision(
            accepted=False,
            gate=GateName.G3_REGION,
            rejection_reason=RejectionReason.WRONG_REGION,
            note="neighbor.region is None",
        )
    if neighbor.region != inp.region_scope:
        return GateDecision(
            accepted=False,
            gate=GateName.G3_REGION,
            rejection_reason=RejectionReason.WRONG_REGION,
            note=f"region '{neighbor.region}' != scope '{inp.region_scope}'",
        )
    return _PASS


def gate_g4_data_class(
    neighbor: GraphNeighbor,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    ctx: GateContext,
) -> GateDecision:
    del plan, ctx
    if not inp.data_class_scope:
        return _PASS
    if neighbor.data_class is None:
        return _PASS
    if neighbor.data_class not in inp.data_class_scope:
        return GateDecision(
            accepted=False,
            gate=GateName.G4_DATA_CLASS,
            rejection_reason=RejectionReason.BLOCKED_DATA_CLASS,
            note=f"data_class '{neighbor.data_class}' not in {inp.data_class_scope}",
        )
    return _PASS


def gate_g5_freshness(
    neighbor: GraphNeighbor,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    ctx: GateContext,
) -> GateDecision:
    del plan, ctx
    fc = _freshness_class(inp.freshness_class)
    fs = _freshness_value(neighbor.freshness_status)
    is_stale = fs == FreshnessStatus.STALE.value
    is_historical = fs == FreshnessStatus.HISTORICAL.value
    demands_current = fc in (FreshnessClass.LATEST, FreshnessClass.CURRENT)

    if is_stale and demands_current:
        return GateDecision(
            accepted=False,
            gate=GateName.G5_FRESHNESS,
            rejection_reason=RejectionReason.STALE,
            note=f"stale neighbor under freshness_class={fc.value}",
        )
    if is_historical and demands_current:
        # Historical context allowed but flagged.
        return GateDecision(
            accepted=True,
            gate=None,
            rejection_reason=None,
            note="historical neighbor accepted with flag",
            flag_categories=("historical_context",),
        )
    return _PASS


def gate_g6_relation_allowlist(
    neighbor: GraphNeighbor,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    ctx: GateContext,
) -> GateDecision:
    del ctx
    if neighbor.relation_type in inp.disallowed_relation_types:
        return GateDecision(
            accepted=False,
            gate=GateName.G6_RELATION_ALLOWLIST,
            rejection_reason=RejectionReason.RELATION_TYPE_NOT_ALLOWED,
            note=f"disallowed relation '{neighbor.relation_type}'",
        )
    if plan.allowed_relation_types and neighbor.relation_type not in plan.allowed_relation_types:
        return GateDecision(
            accepted=False,
            gate=GateName.G6_RELATION_ALLOWLIST,
            rejection_reason=RejectionReason.RELATION_TYPE_NOT_ALLOWED,
            note=f"'{neighbor.relation_type}' not in allowed_relation_types",
        )
    return _PASS


def gate_g7_source_class(
    neighbor: GraphNeighbor,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    ctx: GateContext,
) -> GateDecision:
    del plan, ctx
    if inp.disallowed_source_classes and neighbor.source_type in inp.disallowed_source_classes:
        return GateDecision(
            accepted=False,
            gate=GateName.G7_SOURCE_CLASS,
            rejection_reason=RejectionReason.SOURCE_CLASS_NOT_ALLOWED,
            note=f"disallowed source class '{neighbor.source_type}'",
        )
    if inp.allowed_source_classes and neighbor.source_type not in inp.allowed_source_classes:
        return GateDecision(
            accepted=False,
            gate=GateName.G7_SOURCE_CLASS,
            rejection_reason=RejectionReason.SOURCE_CLASS_NOT_ALLOWED,
            note=f"'{neighbor.source_type}' not in allowed_source_classes",
        )
    if inp.disallowed_graph_sources and neighbor.graph_source in inp.disallowed_graph_sources:
        return GateDecision(
            accepted=False,
            gate=GateName.G7_SOURCE_CLASS,
            rejection_reason=RejectionReason.GRAPH_SOURCE_BLOCKED,
            note=f"graph_source '{neighbor.graph_source}' is blocked",
        )
    if inp.allowed_graph_sources and neighbor.graph_source not in inp.allowed_graph_sources:
        return GateDecision(
            accepted=False,
            gate=GateName.G7_SOURCE_CLASS,
            rejection_reason=RejectionReason.GRAPH_SOURCE_BLOCKED,
            note=f"graph_source '{neighbor.graph_source}' not in allowed_graph_sources",
        )
    return _PASS


def gate_g8_hop_budget(
    neighbor: GraphNeighbor,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    ctx: GateContext,
) -> GateDecision:
    del ctx
    if neighbor.hop_distance > inp.max_hops:
        return GateDecision(
            accepted=False,
            gate=GateName.G8_HOP_BUDGET,
            rejection_reason=RejectionReason.MAX_HOPS_EXCEEDED,
            note=f"hop {neighbor.hop_distance} > max_hops {inp.max_hops}",
        )
    rel_cap = plan.max_hops_by_relation_type.get(neighbor.relation_type)
    if rel_cap is not None and neighbor.hop_distance > rel_cap:
        return GateDecision(
            accepted=False,
            gate=GateName.G8_HOP_BUDGET,
            rejection_reason=RejectionReason.MAX_HOPS_EXCEEDED,
            note=f"hop {neighbor.hop_distance} > rel-cap {rel_cap}",
        )
    return _PASS


def gate_g9_support_relevance(
    neighbor: GraphNeighbor,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    ctx: GateContext,
) -> GateDecision:
    del inp
    # A neighbor supports the target if its relation_type is in the
    # plan.relation_priority_order (which is the support-target intersection).
    # Otherwise it's "interesting but not relevant".
    rel = neighbor.relation_type
    if rel in plan.relation_priority_order:
        return _PASS
    if rel in plan.allowed_relation_types:
        # Allowed-but-not-prioritized — treat as background context only when
        # there's at least one positive flag (lineage, ownership, source
        # authority); otherwise reject.
        flag_cats = ctx.get("flag_categories", ()) if isinstance(ctx, Mapping) else ()
        if isinstance(flag_cats, tuple) and any(
            c in flag_cats for c in ("lineage_edge", "ownership_context", "source_authority_context")
        ):
            return _PASS
        return GateDecision(
            accepted=False,
            gate=GateName.G9_SUPPORT_RELEVANCE,
            rejection_reason=RejectionReason.INTERESTING_NOT_RELEVANT,
            note=f"'{rel}' allowed but not prioritized for support_target",
        )
    return GateDecision(
        accepted=False,
        gate=GateName.G9_SUPPORT_RELEVANCE,
        rejection_reason=RejectionReason.SUPPORT_TARGET_MISMATCH,
        note=f"'{rel}' not in priority order or allowlist",
    )


def gate_g10_confidence(
    neighbor: GraphNeighbor,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    ctx: GateContext,
) -> GateDecision:
    del plan, ctx
    if neighbor.confidence < inp.confidence_threshold:
        return GateDecision(
            accepted=False,
            gate=GateName.G10_CONFIDENCE,
            rejection_reason=RejectionReason.LOW_CONFIDENCE,
            note=f"confidence {neighbor.confidence} < threshold {inp.confidence_threshold}",
        )
    return _PASS


def gate_g11_lineage(
    neighbor: GraphNeighbor,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    ctx: GateContext,
) -> GateDecision:
    del inp, plan, ctx
    if neighbor.is_projected and (not neighbor.projection_version or not neighbor.snapshot_pointer):
        return GateDecision(
            accepted=False,
            gate=GateName.G11_LINEAGE,
            rejection_reason=RejectionReason.MISSING_LINEAGE,
            note="projected neighbor missing projection_version or snapshot_pointer",
        )
    if not neighbor.lineage_refs and not neighbor.source_id:
        return GateDecision(
            accepted=False,
            gate=GateName.G11_LINEAGE,
            rejection_reason=RejectionReason.MISSING_LINEAGE,
            note="neighbor has no lineage_refs and no source_id",
        )
    return _PASS


def gate_g12_citation(
    neighbor: GraphNeighbor,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    ctx: GateContext,
) -> GateDecision:
    del plan, ctx
    if not inp.require_citation_anchor:
        return _PASS
    if not neighbor.span_ref:
        return GateDecision(
            accepted=True,
            gate=None,
            rejection_reason=None,
            note="no citation anchor; marked background_only",
            flag_categories=("background_only", "no_citation_anchor"),
        )
    return _PASS


def gate_g13_contradiction(
    neighbor: GraphNeighbor,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    ctx: GateContext,
) -> GateDecision:
    del inp, ctx
    rel = neighbor.relation_type
    if rel == "contradicts" and plan.contradiction_scan_enabled:
        return GateDecision(
            accepted=True,
            gate=None,
            rejection_reason=None,
            note="contradiction preserved",
            flag_categories=("contradiction_candidate",),
        )
    if rel in ("supersedes", "superseded_by") and plan.supersession_scan_enabled:
        return GateDecision(
            accepted=True,
            gate=None,
            rejection_reason=None,
            note="supersession preserved",
            flag_categories=("supersession_candidate",),
        )
    return _PASS


def gate_g14_cycle(
    neighbor: GraphNeighbor,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    ctx: GateContext,
) -> GateDecision:
    del inp, plan
    seen = ctx.get("seen_node_ids") if isinstance(ctx, Mapping) else None
    if isinstance(seen, set) and neighbor.node_id in seen:
        return GateDecision(
            accepted=False,
            gate=GateName.G14_CYCLE,
            rejection_reason=RejectionReason.CYCLE_DETECTED,
            note=f"cycle: {neighbor.node_id} already visited",
        )
    return _PASS


def gate_g15_projection_currency(
    neighbor: GraphNeighbor,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    ctx: GateContext,
) -> GateDecision:
    del plan
    pm: ProjectionManifest | None = None
    if isinstance(ctx, Mapping):
        candidate = ctx.get("projection_manifest")
        if isinstance(candidate, ProjectionManifest):
            pm = candidate
    if pm is None or not pm.is_stale:
        return _PASS
    fc = _freshness_class(inp.freshness_class)
    if fc in (FreshnessClass.LATEST, FreshnessClass.CURRENT):
        return GateDecision(
            accepted=False,
            gate=GateName.G15_PROJECTION_CURRENCY,
            rejection_reason=RejectionReason.PROJECTION_STALE,
            note=f"projection stale; freshness_class={fc.value}",
        )
    # historical / static support: allow but flag
    return GateDecision(
        accepted=True,
        gate=None,
        rejection_reason=None,
        note="projection stale but freshness allows",
        flag_categories=("projection_stale_caveat",),
    )


GateFn = Callable[
    [GraphNeighbor, GraphTraverseInput, GraphTraversalPlan, GateContext],
    GateDecision,
]


GATE_FUNCTIONS: tuple[tuple[GateName, GateFn], ...] = (
    (GateName.G1_ACL, gate_g1_acl),
    (GateName.G2_TENANT, gate_g2_tenant),
    (GateName.G3_REGION, gate_g3_region),
    (GateName.G4_DATA_CLASS, gate_g4_data_class),
    (GateName.G15_PROJECTION_CURRENCY, gate_g15_projection_currency),
    (GateName.G5_FRESHNESS, gate_g5_freshness),
    (GateName.G6_RELATION_ALLOWLIST, gate_g6_relation_allowlist),
    (GateName.G7_SOURCE_CLASS, gate_g7_source_class),
    (GateName.G8_HOP_BUDGET, gate_g8_hop_budget),
    (GateName.G14_CYCLE, gate_g14_cycle),
    (GateName.G13_CONTRADICTION, gate_g13_contradiction),
    (GateName.G9_SUPPORT_RELEVANCE, gate_g9_support_relevance),
    (GateName.G10_CONFIDENCE, gate_g10_confidence),
    (GateName.G11_LINEAGE, gate_g11_lineage),
    (GateName.G12_CITATION, gate_g12_citation),
)


def apply_all_gates(
    neighbor: GraphNeighbor,
    inp: GraphTraverseInput,
    plan: GraphTraversalPlan,
    ctx: GateContext,
) -> GateDecision:
    """Run gates in order. First reject wins; flag categories accumulate."""
    accumulated_flags: list[str] = []
    notes: list[str] = []
    for _name, fn in GATE_FUNCTIONS:
        decision = fn(neighbor, inp, plan, ctx)
        if not decision.accepted:
            return decision
        if decision.flag_categories:
            accumulated_flags.extend(decision.flag_categories)
        if decision.note:
            notes.append(decision.note)
    return GateDecision(
        accepted=True,
        gate=None,
        rejection_reason=None,
        note="; ".join(notes),
        flag_categories=tuple(accumulated_flags),
    )


__all__ = [
    "GATE_FUNCTIONS",
    "GateDecision",
    "GateFn",
    "GateName",
    "apply_all_gates",
    "gate_g1_acl",
    "gate_g2_tenant",
    "gate_g3_region",
    "gate_g4_data_class",
    "gate_g5_freshness",
    "gate_g6_relation_allowlist",
    "gate_g7_source_class",
    "gate_g8_hop_budget",
    "gate_g9_support_relevance",
    "gate_g10_confidence",
    "gate_g11_lineage",
    "gate_g12_citation",
    "gate_g13_contradiction",
    "gate_g14_cycle",
    "gate_g15_projection_currency",
]
