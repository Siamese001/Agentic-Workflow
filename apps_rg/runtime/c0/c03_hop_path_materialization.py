"""Materialize track-weighted graph_hop_path per fact (W4 hop-path parity)."""
from __future__ import annotations

from typing import Any

from apps_rg.fact_inventory.track_weighted_graph_expansion import (
    GRAPH_EXPANSION_MODE_TRACK_WEIGHTED,
)
from apps_rg.runtime.c0.c03_allowlist_coherence import fact_id_base, fact_id_in_allowed_pool
from apps_rg.runtime.section_spine_terminology import (
    GRAPH_EXPANSION_MODE_INCIDENT_EDGE_V1,
    GRAPH_HOP_PATHS_COUNT_SEMANTICS_INCIDENT_EDGE,
    GRAPH_HOP_PATHS_COUNT_SEMANTICS_TRACK_WEIGHTED,
)

DEFAULT_MAX_DOMINANT_FACTS = 12


def _index_expansion_fact_hops(track_expansion: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {}
    for entry in track_expansion.get("selected_facts") or []:
        if not isinstance(entry, dict):
            continue
        fid = str(entry.get("fact_id") or "").strip()
        if not fid:
            continue
        hop = entry.get("graph_hop_path")
        if not isinstance(hop, list) or not hop:
            continue
        steps = [dict(s) for s in hop if isinstance(s, dict)]
        out[fid] = steps
        base = fact_id_base(fid)
        if base not in out:
            out[base] = steps
    return out


def materialize_c03_hop_paths(
    *,
    track_expansion: dict[str, Any] | None,
    allowed_fact_ids: set[str] | None = None,
    max_dominant_facts: int = DEFAULT_MAX_DOMINANT_FACTS,
    incident_edge_refs_count: int | None = None,
) -> dict[str, Any]:
    """Build hop-path receipt fields from track-weighted expansion (competencies-style)."""
    if not isinstance(track_expansion, dict):
        return {
            "graph_expansion_mode": GRAPH_EXPANSION_MODE_INCIDENT_EDGE_V1,
            "graph_hop_paths_by_fact_id": {},
            "graph_hop_paths_sample": [],
            "graph_hop_paths_count": 0,
            "graph_hop_paths_count_semantics": GRAPH_HOP_PATHS_COUNT_SEMANTICS_INCIDENT_EDGE,
            "graph_incident_edge_refs_count": incident_edge_refs_count,
        }

    hop_index = _index_expansion_fact_hops(track_expansion)
    allowed = (
        {str(x).strip() for x in allowed_fact_ids if str(x).strip()}
        if allowed_fact_ids is not None
        else None
    )
    canonical: dict[str, list[dict[str, str]]] = {}
    for fid in sorted(hop_index.keys()):
        key = fact_id_base(fid)
        if key in canonical:
            continue
        if allowed is not None and not fact_id_in_allowed_pool(fid, allowed):
            continue
        canonical[key] = hop_index[fid]
        if len(canonical) >= max_dominant_facts:
            break

    sample = list(canonical.values())[:5]
    hop_count = len([h for h in canonical.values() if h])
    mode = str(track_expansion.get("graph_expansion_mode") or "").strip()
    if hop_count > 0:
        expansion_mode = mode or GRAPH_EXPANSION_MODE_TRACK_WEIGHTED
        semantics = GRAPH_HOP_PATHS_COUNT_SEMANTICS_TRACK_WEIGHTED
    else:
        expansion_mode = GRAPH_EXPANSION_MODE_INCIDENT_EDGE_V1
        semantics = GRAPH_HOP_PATHS_COUNT_SEMANTICS_INCIDENT_EDGE

    return {
        "graph_expansion_mode": expansion_mode,
        "graph_hop_paths_by_fact_id": canonical,
        "graph_hop_paths_sample": sample,
        "graph_hop_paths_count": hop_count,
        "graph_hop_paths_count_semantics": semantics,
        "graph_incident_edge_refs_count": incident_edge_refs_count,
        "c03_graph_hop_paths_count": hop_count,
    }


def attach_track_weighted_hop_paths_to_c03_bound(
    c03_bound: dict[str, Any],
    track_expansion: dict[str, Any] | None,
    *,
    allowed_fact_ids: set[str] | None = None,
    max_dominant_facts: int = DEFAULT_MAX_DOMINANT_FACTS,
) -> dict[str, Any]:
    """Merge materialized hop paths onto lane c03 binding + FEC evidence items."""
    out = dict(c03_bound)
    incident_count = len(out.get("graph_expansion_refs") or [])
    hop_doc = materialize_c03_hop_paths(
        track_expansion=track_expansion,
        allowed_fact_ids=allowed_fact_ids,
        max_dominant_facts=max_dominant_facts,
        incident_edge_refs_count=incident_count,
    )
    out.update(hop_doc)

    by_fact = hop_doc.get("graph_hop_paths_by_fact_id") or {}
    if not by_fact:
        return out

    snap = dict(out.get("final_evidence_contract_snapshot") or {})
    items_in = list(snap.get("evidence_items") or [])
    items_out: list[dict[str, Any]] = []
    for it in items_in:
        if not isinstance(it, dict):
            continue
        row = dict(it)
        fid = str(row.get("source_fact_id") or "").strip()
        if not fid:
            ref = str(row.get("graph_node_ref") or "")
            if ref.startswith("node_fact:"):
                fid = ref.split(":", 1)[1]
            elif ref.startswith("node_fact_"):
                fid = ref[len("node_fact_") :]
        hop = by_fact.get(fid) or by_fact.get(fact_id_base(fid))
        if hop:
            row["graph_hop_path"] = hop
        items_out.append(row)
    snap["evidence_items"] = items_out
    snap["graph_expansion_mode"] = hop_doc.get("graph_expansion_mode")
    snap["graph_hop_paths_count"] = hop_doc.get("graph_hop_paths_count")
    snap["graph_hop_paths_count_semantics"] = hop_doc.get("graph_hop_paths_count_semantics")
    out["final_evidence_contract_snapshot"] = snap
    from apps_rg.runtime.section_spine_terminology import enrich_section_graph_binding_doc

    return enrich_section_graph_binding_doc(out)


__all__ = [
    "DEFAULT_MAX_DOMINANT_FACTS",
    "attach_track_weighted_hop_paths_to_c03_bound",
    "materialize_c03_hop_paths",
]
