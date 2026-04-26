"""Phase 3.4 — build a deterministic ``GraphTraversalPlan`` from the input.

The plan reflects:
  * the intersection of input ``allowed_relation_types`` with the
    support-target's recommended relation policy,
  * recommended max_hops per support_target,
  * which scans (contradiction / supersession / dependency / lineage / runtime
    / definition / owner / source_authority) are enabled for the target.

Determinism property: same ``GraphTraverseInput`` + same start_nodes ordering
+ same projection manifest -> same plan, byte-for-byte.
"""

from __future__ import annotations

import hashlib
from typing import Mapping

from .contracts import (
    GraphBudget,
    GraphTraversalPlan,
    GraphTraverseInput,
    SupportTarget,
)


# Per-support-target relation policy.
#
# Each entry is:
#   recommended_relations, recommended_max_hops, scans
#
# scans is a dict of:
#   contradiction, supersession, dependency, lineage, runtime, definition,
#   owner, source_authority -> bool
SUPPORT_TARGET_POLICY: Mapping[
    SupportTarget,
    tuple[tuple[str, ...], int, dict[str, bool]],
] = {
    SupportTarget.EXACT_QUOTE: (
        ("parent_of", "child_of", "source_version", "supersedes", "duplicates"),
        1,
        {
            "contradiction": True,
            "supersession": True,
            "dependency": False,
            "lineage": True,
            "runtime": False,
            "definition": True,
            "owner": False,
            "source_authority": True,
        },
    ),
    SupportTarget.SOURCE_SUMMARY: (
        ("references", "defines", "parent_of", "child_of", "supersedes", "contradicts"),
        2,
        {
            "contradiction": True,
            "supersession": True,
            "dependency": False,
            "lineage": True,
            "runtime": False,
            "definition": True,
            "owner": True,
            "source_authority": True,
        },
    ),
    SupportTarget.POLICY_CLAUSE: (
        ("governed_by", "supersedes", "contradicts", "source_version"),
        2,
        {
            "contradiction": True,
            "supersession": True,
            "dependency": False,
            "lineage": True,
            "runtime": False,
            "definition": True,
            "owner": True,
            "source_authority": True,
        },
    ),
    SupportTarget.CODE_LOCATION: (
        ("defines", "imports", "calls", "implements", "tested_by"),
        2,
        {
            "contradiction": True,
            "supersession": False,
            "dependency": True,
            "lineage": True,
            "runtime": False,
            "definition": True,
            "owner": True,
            "source_authority": False,
        },
    ),
    SupportTarget.INCIDENT_EVIDENCE: (
        ("observed_in", "triggered_by", "remediated_by", "trace", "deployment", "ticket"),
        2,
        {
            "contradiction": True,
            "supersession": False,
            "dependency": True,
            "lineage": True,
            "runtime": True,
            "definition": False,
            "owner": True,
            "source_authority": False,
        },
    ),
    SupportTarget.ROOT_CAUSE_RANKING: (
        (
            "depends_on",
            "depended_on_by",
            "calls",
            "observed_in",
            "remediated_by",
            "contradicts",
        ),
        3,
        {
            "contradiction": True,
            "supersession": False,
            "dependency": True,
            "lineage": True,
            "runtime": True,
            "definition": False,
            "owner": True,
            "source_authority": False,
        },
    ),
    SupportTarget.COMPARISON: (
        (
            "references",
            "defines",
            "parent_of",
            "child_of",
            "depends_on",
            "supersedes",
            "contradicts",
        ),
        2,
        {
            "contradiction": True,
            "supersession": True,
            "dependency": True,
            "lineage": True,
            "runtime": False,
            "definition": True,
            "owner": True,
            "source_authority": True,
        },
    ),
    SupportTarget.CLAIM_CHECK: (
        ("references", "contradicts", "supersedes", "source_authority", "evidence"),
        2,
        {
            "contradiction": True,
            "supersession": True,
            "dependency": False,
            "lineage": True,
            "runtime": False,
            "definition": False,
            "owner": False,
            "source_authority": True,
        },
    ),
    SupportTarget.ARCHITECTURE_BOUNDARY: (
        ("owns", "depends_on", "governed_by", "violates", "implements", "calls"),
        2,
        {
            "contradiction": True,
            "supersession": False,
            "dependency": True,
            "lineage": True,
            "runtime": False,
            "definition": True,
            "owner": True,
            "source_authority": True,
        },
    ),
    SupportTarget.BLAST_RADIUS: (
        ("depends_on", "depended_on_by", "imports", "calls"),
        2,
        {
            "contradiction": False,
            "supersession": False,
            "dependency": True,
            "lineage": True,
            "runtime": False,
            "definition": False,
            "owner": True,
            "source_authority": False,
        },
    ),
    SupportTarget.GOVERNANCE_DECISION: (
        (
            "governed_by",
            "approved_by",
            "requires",
            "prohibits",
            "exception_to",
            "evidence",
        ),
        2,
        {
            "contradiction": True,
            "supersession": True,
            "dependency": False,
            "lineage": True,
            "runtime": False,
            "definition": False,
            "owner": True,
            "source_authority": True,
        },
    ),
}


def _support_target_enum(value: SupportTarget | str) -> SupportTarget:
    if isinstance(value, SupportTarget):
        return value
    try:
        return SupportTarget(value)
    except ValueError:
        return SupportTarget.SOURCE_SUMMARY  # safest default


def build_traversal_plan(
    *,
    inp: GraphTraverseInput,
    start_nodes: tuple[str, ...],
    projection_version: str,
) -> GraphTraversalPlan:
    """Phase 3.4 entrypoint.

    Intersect the input's ``allowed_relation_types`` with the support-target
    recommended relations. The intersection is honored as the priority order;
    relations not in the intersection but explicitly allowed by the input are
    appended in input-declared order.

    Determinism:
      hash(input.policy_hash || input.support_target || projection_version ||
           sorted(allowed_relation_types) || sorted(start_nodes))
      drives ``replay_metadata`` and the per-relation hop budget seed.
    """
    target = _support_target_enum(inp.support_target)
    recommended, recommended_hops, scan_flags = SUPPORT_TARGET_POLICY[target]

    input_allowed = tuple(inp.allowed_relation_types)
    # Reject any relation that is in disallowed.
    disallowed = set(inp.disallowed_relation_types)
    input_allowed = tuple(r for r in input_allowed if r not in disallowed)

    intersection = tuple(r for r in recommended if r in input_allowed)
    extras = tuple(r for r in input_allowed if r not in intersection)
    priority_order = intersection + extras

    if not priority_order:
        priority_order = input_allowed  # may be empty if max_hops == 0

    # Per-relation hop budget — start at min(input.max_hops, recommended).
    base_hops = min(inp.max_hops, recommended_hops) if inp.max_hops > 0 else 0
    max_hops_by_relation: dict[str, int] = {}
    for r in input_allowed:
        # Heavy fan-out relations (calls/imports/depends_on) get a slightly
        # tighter budget for blast-radius safety.
        if r in {"calls", "imports", "depends_on", "depended_on_by"}:
            max_hops_by_relation[r] = max(1, base_hops - 0)
        else:
            max_hops_by_relation[r] = base_hops

    budget = GraphBudget(
        max_hops=inp.max_hops,
        max_nodes=inp.max_nodes,
        max_edges=inp.max_edges,
        max_neighbors_by_anchor=max(1, inp.max_parent_expansion + inp.max_child_expansion),
        max_latency_ms=inp.max_latency_ms,
        max_token_budget_for_graph_context=inp.max_token_budget_for_graph_context,
    )

    stop_conditions: tuple[str, ...] = (
        "max_hops_reached",
        "max_nodes_reached",
        "max_edges_reached",
        "max_latency_ms_reached",
        "all_branches_rejected",
    )

    seed_payload = "|".join(
        [
            inp.policy_hash,
            str(target.value if isinstance(target, SupportTarget) else target),
            projection_version,
            ",".join(sorted(input_allowed)),
            ",".join(sorted(start_nodes)),
        ]
    )
    replay_seed = hashlib.sha256(seed_payload.encode("utf-8")).hexdigest()
    # Heterogeneous typed map; Any covers the list[str] entry.
    from typing import Any as _Any

    replay_metadata: dict[str, _Any] = {
        "support_target": target.value,
        "projection_version": projection_version,
        "policy_hash": inp.policy_hash,
        "blueprint_hash": inp.blueprint_hash,
        "route_replay_key": inp.route_replay_key,
        "seed": replay_seed,
        # Recommended ∩ input_allowed — used by pipeline to label support
        # contribution as primary vs secondary vs background.
        "primary_relations": list(intersection),
    }

    return GraphTraversalPlan(
        start_nodes=start_nodes,
        allowed_relation_types=input_allowed,
        relation_priority_order=priority_order,
        max_hops_by_relation_type=max_hops_by_relation,
        max_neighbors_by_anchor=budget.max_neighbors_by_anchor,
        contradiction_scan_enabled=scan_flags["contradiction"],
        supersession_scan_enabled=scan_flags["supersession"],
        dependency_scan_enabled=scan_flags["dependency"],
        lineage_scan_enabled=scan_flags["lineage"],
        runtime_scan_enabled=scan_flags["runtime"],
        definition_scan_enabled=scan_flags["definition"],
        owner_scan_enabled=scan_flags["owner"],
        source_authority_scan_enabled=scan_flags["source_authority"],
        graph_budget=budget,
        stop_conditions=stop_conditions,
        replay_metadata=replay_metadata,
    )


__all__ = ["SUPPORT_TARGET_POLICY", "build_traversal_plan"]
