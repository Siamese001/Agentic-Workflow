"""Spine C0.3 graph authority helpers — W10-AG / deferred follow-on DS-11."""
from __future__ import annotations

from typing import Any

from apps_rg.runtime.bindings.c0_binding import C0_GRAPH_LANE_NA_REF


def spine_graph_refs_live(refs: tuple[str, ...] | list[str] | None) -> bool:
    """True when spine FEC carries non-deferred graph expansion refs."""
    if not refs:
        return False
    for ref in refs:
        s = str(ref or "").strip()
        if not s or s == C0_GRAPH_LANE_NA_REF:
            continue
        if "graphrag_deferred_phase1" in s:
            continue
        if s.startswith("ref:graph:"):
            return True
    return False


def spine_retrieve_graph_live(receipt: dict[str, Any]) -> bool:
    """Classify spine retrieve receipt as live C0.3 graph (not NA deferral)."""
    if bool(receipt.get("canonical_c0_3_graph_claimed")):
        return True
    if bool(receipt.get("canonical_c0_3_graph_rag_claimed")):
        return True
    refs = receipt.get("graph_expansion_refs") or ()
    return spine_graph_refs_live(refs if isinstance(refs, (list, tuple)) else (refs,))


def overlay_spine_graph_authority_on_bridge(
    bridge_doc: dict[str, Any],
    *,
    spine_graph_expansion_refs: list[str],
    spine_graph_lineage_refs: list[str] | None = None,
) -> dict[str, Any]:
    """When spine graph is LIVE, make bridge + embedded c03 reflect spine authority (DS-11)."""
    if not spine_graph_refs_live(spine_graph_expansion_refs):
        return bridge_doc
    out = dict(bridge_doc)
    exp = list(spine_graph_expansion_refs)
    lin = list(spine_graph_lineage_refs or out.get("graph_lineage_refs") or [])
    out["graph_expansion_refs"] = exp
    out["graph_lineage_refs"] = lin
    out["citation_lineage_refs"] = lin + exp
    out["canonical_c0_3_claimed"] = True
    out["canonical_c0_3_graph_claimed"] = True
    out["proof_pool_shim_only"] = False
    out["binding_kind"] = "spine_c0_retrieve_apps_rg"
    pa = dict(out.get("pa_proof_authority_metadata") or {})
    pa["binding_kind"] = "spine_c0_retrieve_apps_rg"
    pa["canonical_c0_path"] = True
    pa["spine_graph_authority"] = True
    c03 = dict(pa.get("c03_graphrag_bound") or out.get("c03_graphrag_bound") or {})
    if c03:
        c03 = dict(c03)
        c03["graph_expansion_refs"] = exp
        c03["graph_lineage_refs"] = lin
        c03["c03_graphrag_bound_status"] = "BOUND"
        c03["binding_kind"] = "spine_c0_retrieve_apps_rg"
        c03["spine_fec_overlay"] = True
        pa["c03_graphrag_bound"] = c03
        pa["c03_graphrag_bound_status"] = "BOUND"
    out["pa_proof_authority_metadata"] = pa
    explicit = list(out.get("explicit_non_claims") or [])
    out["explicit_non_claims"] = [
        x
        for x in explicit
        if "not canonical C0.3" not in str(x).lower()
    ]
    return out


__all__ = [
    "overlay_spine_graph_authority_on_bridge",
    "spine_graph_refs_live",
    "spine_retrieve_graph_live",
]
