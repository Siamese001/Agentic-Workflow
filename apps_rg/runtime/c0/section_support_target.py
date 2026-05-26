"""Graph-lane support_target_met derivation (apps_rg section CLI).

Section graph proof pools use ``proof_pool:<fact_id>`` retrieval sources — not the
full multi-prefix target used for integrated spine runs with ledger+SRFS.
"""
from __future__ import annotations

from typing import Any, Iterable

from agentic_core.runtime.c0.evidence_metrics_extractor import SupportTarget
from agentic_core.runtime.contracts.final_evidence_contract import (
    SUPPORT_STATUS_PASS,
    SUPPORT_STATUS_WEAK_WITH_CAVEATS,
)

_GRAPH_LANE_PASS_STATUSES = frozenset(
    {
        SUPPORT_STATUS_PASS,
        SUPPORT_STATUS_WEAK_WITH_CAVEATS,
        "SUPPORTED",
        "PASS",
    }
)


def graph_lane_proof_support_target() -> SupportTarget:
    """Support target for ``python -m apps_rg --section *`` graph proof pools."""
    return SupportTarget.from_prefix_list(
        ("proof_pool",),
        label="apps_rg_graph_lane_proof_pool",
    )


def proof_pool_retrieval_sources(
    allowed_fact_ids: Iterable[str],
    *,
    proof_source: str = "augmented_skills_graph",
) -> tuple[str, ...]:
    """Canonical retrieval_sources entries for graph-lane FEC → c0_metrics."""
    sources: set[str] = set()
    auth = str(proof_source or "").strip()
    if auth:
        sources.add(auth)
    for fid in allowed_fact_ids:
        base = str(fid or "").strip().split("_metric_", 1)[0]
        if base:
            sources.add(f"proof_pool:{base}")
    return tuple(sorted(sources))


def derive_graph_lane_support_target_met(
    *,
    support_status: str,
    allowed_fact_ids: Iterable[str],
    evidence_item_count: int,
) -> bool:
    """True when graph lane has PASS-class status, allowed facts, and evidence items."""
    allowed = [str(x).strip() for x in allowed_fact_ids if str(x).strip()]
    status = str(support_status or "").strip()
    if not allowed or evidence_item_count <= 0:
        return False
    if status not in _GRAPH_LANE_PASS_STATUSES:
        return False
    return True


def align_support_target_met_fields(
    doc: dict[str, Any],
    *,
    support_status: str,
    allowed_fact_ids: Iterable[str],
    evidence_item_count: int | None = None,
) -> dict[str, Any]:
    """Stamp consistent support_target_met on FEC-shaped dicts (c03 bound, bridge snap)."""
    out = dict(doc)
    count = evidence_item_count
    if count is None:
        snap = out.get("final_evidence_contract_snapshot")
        if isinstance(snap, dict):
            count = int(snap.get("evidence_items_count") or len(snap.get("evidence_items") or []))
        else:
            count = int(out.get("evidence_items_count") or len(out.get("evidence_items") or []))
    met = derive_graph_lane_support_target_met(
        support_status=str(out.get("support_status") or support_status),
        allowed_fact_ids=allowed_fact_ids,
        evidence_item_count=int(count or 0),
    )
    out["support_target_met"] = met
    out["support_target_derivation"] = "graph_lane_v1"
    snap = out.get("final_evidence_contract_snapshot")
    if isinstance(snap, dict):
        snap_out = dict(snap)
        snap_out["support_target_met"] = met
        snap_out["support_target_derivation"] = "graph_lane_v1"
        out["final_evidence_contract_snapshot"] = snap_out
    return out


__all__ = [
    "align_support_target_met_fields",
    "derive_graph_lane_support_target_met",
    "graph_lane_proof_support_target",
    "proof_pool_retrieval_sources",
]
