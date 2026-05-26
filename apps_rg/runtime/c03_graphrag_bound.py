"""Section C0.3 graph binding (module path: c03_graphrag_bound).

Lane-local static JSON graph **incident-edge** binding for ``python -m apps_rg --section *``.
Collects ``graph_edges`` that touch selected proof fact nodes (``graph_expansion_mode=incident_edge_v1``).
**Not** a multi-hop BFS GraphRAG traverse, **not** spine canonical C0.3, **not** spine FinalEvidenceContract.

Receipt vocabulary SSOT: ``apps_rg.runtime.section_spine_terminology``.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Iterable

from apps_rg.fact_inventory.augmented_skills_graph import (
    SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
    graph_version_from_payload,
    load_augmented_skills_graph,
)
from apps_rg.runtime.section_spine_terminology import enrich_section_graph_binding_doc

SUPPORT_STATUS_SUPPORTED = "SUPPORTED"
SUPPORT_STATUS_EMPTY = "EMPTY"
SUPPORT_STATUS_BLOCKED = "BLOCKED"
SUPPORT_STATUS_CONFLICTED = "CONFLICTED"
SUPPORT_STATUS_UNKNOWN = "UNKNOWN"

FORBIDDEN_SUPPORT_FOR_PRODUCT_PROOF = frozenset(
    {SUPPORT_STATUS_EMPTY, SUPPORT_STATUS_BLOCKED, SUPPORT_STATUS_CONFLICTED, SUPPORT_STATUS_UNKNOWN}
)


def _sha256_hex(text: str | bytes) -> str:
    data = text.encode("utf-8") if isinstance(text, str) else text
    return hashlib.sha256(data).hexdigest()


def _fact_node_ids(fact_ids: Iterable[str]) -> set[str]:
    out: set[str] = set()
    for fid in fact_ids:
        s = str(fid or "").strip()
        if not s:
            continue
        base = s.split("_metric_", 1)[0]
        out.add(f"node_fact_{base}")
        out.add(base)
    return out


def _collect_graph_expansion_refs(
    graph: dict[str, Any],
    *,
    selected_fact_ids: set[str],
    max_refs: int = 64,
) -> tuple[str, ...]:
    """Neighbor edge refs touching selected proof fact nodes."""
    node_ids = _fact_node_ids(selected_fact_ids)
    refs: list[str] = []
    for edge in graph.get("graph_edges") or []:
        if not isinstance(edge, dict):
            continue
        eid = str(edge.get("edge_id") or "").strip()
        src = str(edge.get("source_node_id") or edge.get("source") or "")
        tgt = str(edge.get("target_node_id") or edge.get("target") or "")
        if not eid:
            continue
        hit = False
        for nid in (src, tgt):
            if nid in node_ids:
                hit = True
                break
            for fid in selected_fact_ids:
                if fid and fid in nid:
                    hit = True
                    break
        if hit:
            refs.append(f"ref:graph:edge:{eid}")
        if len(refs) >= max_refs:
            break
    if not refs:
        refs.append(f"ref:graph:digest:{_sha256_hex(json.dumps(sorted(selected_fact_ids)))[:16]}")
    return tuple(refs)


def _collect_graph_lineage_refs(
    graph: dict[str, Any],
    *,
    selected_fact_ids: set[str],
    max_refs: int = 32,
) -> tuple[str, ...]:
    refs: list[str] = []
    gver = graph_version_from_payload(graph)
    refs.append(f"ref:graph:version:{gver}")
    meta = graph.get("graph_metadata") if isinstance(graph.get("graph_metadata"), dict) else {}
    if meta.get("node_count") is not None:
        refs.append(f"ref:graph:node_count:{meta.get('node_count')}")
    if meta.get("edge_count") is not None:
        refs.append(f"ref:graph:edge_count:{meta.get('edge_count')}")
    for fid in sorted(selected_fact_ids)[:max_refs]:
        refs.append(f"ref:graph:fact_lineage:{fid}")
    return tuple(refs)


def build_section_c03_graphrag_bound(
    *,
    section_id: str,
    graph: dict[str, Any],
    graph_ref: str,
    graph_digest: str,
    selected_fact_ids: Iterable[str],
    evidence_items: list[dict[str, Any]] | None = None,
    role_family_key: str = "SVP_ENGINEERING_AI_PLATFORM",
    attach_sqlite_context: bool = True,
    repo_root: Any = None,
) -> dict[str, Any]:
    """Lane-local section graph context binding for any apps_rg section (not spine C0.3)."""
    doc = build_executive_summary_c03_graphrag_bound(
        graph=graph,
        graph_ref=graph_ref,
        graph_digest=graph_digest,
        selected_fact_ids=selected_fact_ids,
        evidence_items=evidence_items,
    )
    doc["section_id"] = str(section_id or "").strip() or "executive_summary"
    incident_count = len(doc.get("graph_expansion_refs") or [])
    doc["graph_incident_edge_refs_count"] = incident_count
    if "graph_hop_paths_count" not in doc:
        doc["graph_hop_paths_count"] = incident_count
    non_graph = 0
    for item in doc.get("final_evidence_contract_snapshot", {}).get("evidence_items") or []:
        if isinstance(item, dict) and str(item.get("source_class") or "") != SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH:
            non_graph += 1
    doc["non_graph_evidence_items_count"] = non_graph
    if attach_sqlite_context:
        from apps_rg.runtime.c03_graph_sqlite_context import enrich_c03_bound_with_sqlite_context

        doc = enrich_c03_bound_with_sqlite_context(
            doc,
            role_family_key=role_family_key,
            section_id=doc["section_id"],
            selected_fact_ids=list(selected_fact_ids),
            repo_root=repo_root,
        )
    return doc


def build_executive_summary_c03_graphrag_bound(
    *,
    graph: dict[str, Any],
    graph_ref: str,
    graph_digest: str,
    selected_fact_ids: Iterable[str],
    evidence_items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build lane-local section graph binding (+ FEC-shaped snapshot only, not spine FEC)."""
    fact_set = {str(x).strip() for x in selected_fact_ids if str(x).strip()}
    graph_expansion_refs = _collect_graph_expansion_refs(graph, selected_fact_ids=fact_set)
    graph_lineage_refs = _collect_graph_lineage_refs(graph, selected_fact_ids=fact_set)
    graph_sig = _sha256_hex(f"{graph_digest}:{','.join(sorted(fact_set))}")[:32]

    items = list(evidence_items or [])
    if not items and fact_set:
        for fid in sorted(fact_set):
            items.append(
                {
                    "evidence_id": f"evidence:graph:{fid}",
                    "source": graph_ref,
                    "source_class": "augmented_skills_graph",
                    "graph_node_ref": f"node_fact_{fid.split('_metric_', 1)[0]}",
                    "authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
                }
            )

    support_status = SUPPORT_STATUS_SUPPORTED if items and fact_set else SUPPORT_STATUS_EMPTY
    from apps_rg.runtime.c0.section_support_target import derive_graph_lane_support_target_met

    support_target_met = derive_graph_lane_support_target_met(
        support_status=support_status,
        allowed_fact_ids=fact_set,
        evidence_item_count=len(items),
    )

    ts = datetime.now(timezone.utc).isoformat()
    fec_snapshot = {
        "schema_version": "final_evidence_contract_snapshot_v1",
        "app_id": "apps_rg",
        "source_authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        "support_status": support_status,
        "support_target_met": support_target_met,
        "support_target_derivation": "graph_lane_v1",
        "not_applicable_reason": "",
        "graph_expansion_allowed": True,
        "graph_expansion_refs": list(graph_expansion_refs),
        "graph_lineage_refs": list(graph_lineage_refs),
        "graph_sig": graph_sig,
        "graph_ref": graph_ref,
        "graph_digest": graph_digest,
        "graph_version": graph_version_from_payload(graph),
        "evidence_items": items,
        "evidence_collection_timestamp": ts,
    }

    base = {
        "schema_version": "c03_graphrag_bound_v1",
        "section_id": "executive_summary",
        "generated_at_utc": ts,
        "c03_graphrag_bound_status": "BOUND" if support_status == SUPPORT_STATUS_SUPPORTED else "NOT_BOUND",
        "source_authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        "graph_expansion_allowed": True,
        "graph_expansion_refs": list(graph_expansion_refs),
        "graph_lineage_refs": list(graph_lineage_refs),
        "graph_sig": graph_sig,
        "graph_ref": graph_ref,
        "graph_digest": graph_digest,
        "graph_version": graph_version_from_payload(graph),
        "evidence_items_count": len(items),
        "final_evidence_contract_snapshot": fec_snapshot,
        "support_status": support_status,
        "support_target_met": support_target_met,
        "support_target_derivation": "graph_lane_v1",
    }
    bound = enrich_section_graph_binding_doc(base)
    bound["support_target_met"] = support_target_met
    bound["support_target_derivation"] = "graph_lane_v1"
    if isinstance(bound.get("final_evidence_contract_snapshot"), dict):
        bound["final_evidence_contract_snapshot"]["support_target_met"] = support_target_met
        bound["final_evidence_contract_snapshot"]["support_target_derivation"] = "graph_lane_v1"
    return bound


def load_graph_and_build_c03_bound(
    *,
    repo_root: Any,
    selected_fact_ids: Iterable[str],
) -> dict[str, Any]:
    graph = load_augmented_skills_graph(repo_root=repo_root)
    from apps_rg.fact_inventory.augmented_skills_graph import augmented_skills_graph_path_explicit

    path = augmented_skills_graph_path_explicit(None, repo_root=repo_root)
    try:
        ref = str(path.resolve().relative_to(repo_root.resolve()))
    except ValueError:
        ref = str(path)
    digest = _sha256_hex(json.dumps(graph, sort_keys=True, ensure_ascii=False, separators=(",", ":")))
    return build_executive_summary_c03_graphrag_bound(
        graph=graph,
        graph_ref=ref,
        graph_digest=digest,
        selected_fact_ids=selected_fact_ids,
    )


__all__ = [
    "FORBIDDEN_SUPPORT_FOR_PRODUCT_PROOF",
    "SUPPORT_STATUS_BLOCKED",
    "SUPPORT_STATUS_CONFLICTED",
    "SUPPORT_STATUS_EMPTY",
    "SUPPORT_STATUS_SUPPORTED",
    "SUPPORT_STATUS_UNKNOWN",
    "build_executive_summary_c03_graphrag_bound",
    "build_section_c03_graphrag_bound",
    "load_graph_and_build_c03_bound",
]
