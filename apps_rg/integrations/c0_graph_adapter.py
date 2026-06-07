"""apps_rg C0.3 graph adapter — W4N + W10-AG unified spine bind.

W4N invariants:
  - Does not invoke the core graph traversal executor.
  - Does not import L4 state; no answer/route/tool/L4 writes.

W10-AG:
  - Live ``GraphTraversalAdapter`` over ``augmented_skills_graph`` (arsenal ledger).
  - Resolved by ``apps_rg.integrations.c0_graph_adapter`` via core adapter registry.
  - Product spine: ``c0_retrieve_apps_rg`` → ``maybe_run_graph_rag`` → FEC graph refs.
"""

from __future__ import annotations

import hashlib
import json
import re
from functools import lru_cache
from typing import Any, Mapping

from apps_rg.integrations.c0_graph_types import (
    AmbiguousAnchorResolution,
    AclStatus,
    AnchorCandidate,
    AnchorType,
    FreshnessStatus,
    GraphAdapterHealth,
    GraphNeighbor,
    GraphRelationPath,
    GraphTraversalAdapter,
    ProjectionManifest,
    ResolvedGraphAnchor,
    UnresolvedAnchorResolution,
)

_GRAPH_SOURCE = "apps_rg.augmented_skills_graph.v1"
_PROJECTION_VERSION = "v2.0.0"
_WIRING_GATE_LIVE = "LIVE"
_WIRING_GATE_DEFERRED = "GRAPH_TRAVERSE_POLICY_AGENTIC_CORE_REQUIRED"

RG_ALLOWED_RELATION_TYPES: tuple[str, ...] = (
    "DERIVED_FROM",
    "IMPLEMENTS",
    "CONTRADICTS",
    "SOURCE_VERSION",
    "EVIDENCE",
    "SUPPORTS",
    "REQUIRES",
    "RELATED_TO",
)
RG_MAX_HOPS: int = 1
RG_MAX_NODES: int = 32
RG_MAX_EDGES: int = 64
RG_CONTRADICTION_SCAN_ENABLED: bool = True
RG_SUPERSESSION_SCAN_ENABLED: bool = False

_FACT_ID_RE = re.compile(r"(fact_[a-zA-Z0-9_]+)")


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _graph_policy_from_route(route_contract: Any) -> dict[str, Any]:
    if isinstance(route_contract, dict):
        gt = route_contract.get("graph_traverse") or {}
        return gt if isinstance(gt, dict) else {}
    policy = getattr(route_contract, "graph_traverse_policy", None)
    if policy is None:
        return {}
    return {
        "graph_expansion_allowed": bool(getattr(policy, "graph_expansion_allowed", False)),
        "live_wiring_deferred": bool(getattr(policy, "live_wiring_deferred", True)),
        "max_hops": int(getattr(policy, "max_hops", RG_MAX_HOPS)),
        "max_nodes": int(getattr(policy, "max_nodes", RG_MAX_NODES)),
        "max_edges": int(getattr(policy, "max_edges", RG_MAX_EDGES)),
        "allowed_relation_types": list(getattr(policy, "allowed_relation_types", ()) or RG_ALLOWED_RELATION_TYPES),
        "contradiction_scan_enabled": bool(
            getattr(policy, "contradiction_scan_enabled", RG_CONTRADICTION_SCAN_ENABLED)
        ),
        "supersession_scan_enabled": bool(
            getattr(policy, "supersession_scan_enabled", RG_SUPERSESSION_SCAN_ENABLED)
        ),
        "graph_adapter_ref": str(getattr(policy, "graph_adapter_ref", "") or "apps_rg.integrations.c0_graph_adapter"),
    }


def build_rg_graph_traverse_input(
    route_contract: Any,
    hydrated_candidates: list[Any],
) -> dict[str, Any]:
    """Build a GraphTraverseInput-compatible dict for apps_rg (W4N shape + W10-AG policy)."""
    graph_policy = _graph_policy_from_route(route_contract)
    live = bool(graph_policy.get("graph_expansion_allowed")) and not bool(
        graph_policy.get("live_wiring_deferred", True)
    )
    return {
        "app_id": "apps_rg",
        "allowed_relation_types": list(
            graph_policy.get("allowed_relation_types", list(RG_ALLOWED_RELATION_TYPES))
        ),
        "max_hops": graph_policy.get("max_hops", RG_MAX_HOPS),
        "max_nodes": graph_policy.get("max_nodes", RG_MAX_NODES),
        "max_edges": graph_policy.get("max_edges", RG_MAX_EDGES),
        "contradiction_scan_enabled": graph_policy.get(
            "contradiction_scan_enabled", RG_CONTRADICTION_SCAN_ENABLED
        ),
        "supersession_scan_enabled": graph_policy.get(
            "supersession_scan_enabled", RG_SUPERSESSION_SCAN_ENABLED
        ),
        "hydrated_candidates": hydrated_candidates,
        "graph_adapter_ref": graph_policy.get("graph_adapter_ref", "apps_rg.integrations.c0_graph_adapter"),
        "live_wiring_deferred": not live,
        "wiring_gate": _WIRING_GATE_LIVE if live else _WIRING_GATE_DEFERRED,
    }


@lru_cache(maxsize=1)
def _load_graph_indexes() -> tuple[
    dict[str, Any],
    dict[str, str],
    dict[str, str],
    dict[str, list[tuple[str, str, str, str]]],
]:
    from apps_rg.fact_inventory.augmented_skills_graph import (
        graph_version_from_payload,
        load_augmented_skills_graph,
    )

    graph = load_augmented_skills_graph()
    fact_to_node: dict[str, str] = {}
    skill_to_node: dict[str, str] = {}
    for node in graph.get("graph_nodes") or []:
        if not isinstance(node, dict):
            continue
        nid = str(node.get("node_id") or "").strip()
        if not nid:
            continue
        ntype = str(node.get("node_type") or "").strip().lower()
        if ntype == "fact":
            fid = str(node.get("fact_id") or nid.replace("node_fact_", "")).strip()
            if fid:
                fact_to_node[fid] = nid
        elif ntype == "skill":
            sid = str(node.get("skill_id") or nid.replace("skill_", "")).strip()
            if sid:
                skill_to_node[sid] = nid

    for row in graph.get("skill_rows") or []:
        if not isinstance(row, dict):
            continue
        sid = str(row.get("skill_id") or "").strip()
        if sid and sid not in skill_to_node:
            skill_to_node[sid] = f"skill_{sid}"
        for fid in row.get("fact_id_links") or []:
            fs = str(fid).strip()
            if fs:
                fact_to_node.setdefault(fs, f"node_fact_{fs}")

    adj: dict[str, list[tuple[str, str, str, str]]] = {}
    for edge in graph.get("graph_edges") or []:
        if not isinstance(edge, dict):
            continue
        eid = str(edge.get("edge_id") or "").strip()
        src = str(edge.get("source_node_id") or edge.get("source") or "").strip()
        tgt = str(edge.get("target_node_id") or edge.get("target") or "").strip()
        rel = str(edge.get("relation_type") or edge.get("relation") or "RELATED_TO").strip()
        if not src or not tgt:
            continue
        adj.setdefault(src, []).append((tgt, rel, eid, "out"))
        adj.setdefault(tgt, []).append((src, rel, eid, "in"))

    meta = {
        "graph_version": graph_version_from_payload(graph),
        "graph_digest": _sha256_hex(json.dumps(graph.get("graph_metadata") or {}, sort_keys=True))[:16],
    }
    return meta, fact_to_node, skill_to_node, adj


def _extract_fact_id(anchor_value: str) -> str | None:
    val = str(anchor_value or "").strip()
    if not val:
        return None
    if val.startswith("evidence:"):
        parts = val.split(":")
        val = parts[-1] if parts else val
    if val.startswith("fact_"):
        return val
    m = _FACT_ID_RE.search(val)
    return m.group(1) if m else None


class AppsRgGraphAdapter:
    """Live augmented-skills-graph adapter for core C0.3 traversal."""

    def resolve_anchor(
        self,
        anchor_candidate: AnchorCandidate,
        scope: Mapping[str, object],
    ) -> ResolvedGraphAnchor | AmbiguousAnchorResolution | UnresolvedAnchorResolution:
        _ = scope
        meta, fact_to_node, skill_to_node, _adj = _load_graph_indexes()
        val = str(anchor_candidate.anchor_value or "").strip()
        fid = _extract_fact_id(val)
        node_id = ""
        anchor_type = anchor_candidate.anchor_type
        if fid and fid in fact_to_node:
            node_id = fact_to_node[fid]
            anchor_type = AnchorType.DOCUMENT
        elif val in skill_to_node:
            node_id = skill_to_node[val]
            anchor_type = AnchorType.SERVICE
        elif val in fact_to_node:
            node_id = fact_to_node[val]
            anchor_type = AnchorType.DOCUMENT
        else:
            return UnresolvedAnchorResolution(
                candidate=anchor_candidate,
                reason=f"apps_rg graph: no node for anchor={val!r}",
            )
        return ResolvedGraphAnchor(
            anchor_id=f"anchor:{node_id}",
            original_evidence_id=anchor_candidate.original_evidence_id,
            anchor_type=anchor_type,
            anchor_value=val,
            resolved_node_id=node_id,
            graph_source=_GRAPH_SOURCE,
            source_id=anchor_candidate.hint_source_id or node_id,
            source_version=meta.get("graph_version", "unknown"),
            confidence=max(float(anchor_candidate.confidence), 0.55),
            resolution_reason="apps_rg.augmented_skills_graph exact match",
            acl_status=AclStatus.CLEARED,
        )

    def get_neighbors(
        self,
        node_id: str,
        relation_types: tuple[str, ...],
        scope: Mapping[str, object],
        limit: int,
    ) -> tuple[GraphNeighbor, ...]:
        _ = scope
        meta, _fact_to_node, _skill_to_node, adj = _load_graph_indexes()
        allowed = {str(r).strip().upper() for r in relation_types if str(r).strip()}
        if not allowed:
            allowed = {r.upper() for r in RG_ALLOWED_RELATION_TYPES}
        out: list[GraphNeighbor] = []
        for nb_id, rel, eid, _dir in adj.get(node_id, []):
            rel_u = rel.upper()
            if rel_u not in allowed and allowed:
                continue
            out.append(
                GraphNeighbor(
                    node_id=nb_id,
                    node_type="skill" if nb_id.startswith("skill_") else "fact",
                    source_id=nb_id,
                    source_type=_GRAPH_SOURCE,
                    source_version=str(meta.get("graph_version", "unknown")),
                    relation_type=rel,
                    relation_path=(node_id, rel, nb_id),
                    hop_distance=1,
                    tenant=None,
                    region=None,
                    data_class="EVIDENCE_DATA_ONLY",
                    acl_status=AclStatus.CLEARED,
                    freshness_status=FreshnessStatus.CURRENT,
                    candidate_text_or_payload="",
                )
            )
            if len(out) >= max(1, limit):
                break
        return tuple(out)

    def get_relation_path(
        self,
        start_node_id: str,
        neighbor_node_id: str,
    ) -> GraphRelationPath:
        return GraphRelationPath(
            start_node_id=start_node_id,
            end_node_id=neighbor_node_id,
            relations=(),
            nodes=(start_node_id, neighbor_node_id),
        )

    def get_projection_manifest(self) -> ProjectionManifest:
        meta, _f, _s, _a = _load_graph_indexes()
        digest = str(meta.get("graph_digest", "unknown"))
        return ProjectionManifest(
            graph_source=_GRAPH_SOURCE,
            projection_version=_PROJECTION_VERSION,
            snapshot_pointer=f"apps_rg::augmented_skills_graph::{digest}",
            snapshot_built_at="live",
            canonical_source_hash=digest,
            is_stale=False,
        )

    def health_check(self) -> GraphAdapterHealth:
        try:
            _load_graph_indexes()
            return GraphAdapterHealth(
                healthy=True,
                backend=_GRAPH_SOURCE,
                latency_p50_ms=1.0,
                latency_p95_ms=5.0,
            )
        except (OSError, ValueError, TypeError) as exc:
            return GraphAdapterHealth(
                healthy=False,
                backend=_GRAPH_SOURCE,
                latency_p50_ms=0.0,
                latency_p95_ms=0.0,
                last_error=str(exc),
            )


def get_graph_adapter() -> GraphTraversalAdapter:
    """Entry-point for ``resolve_graph_adapter('apps_rg.integrations.c0_graph_adapter')``."""
    return AppsRgGraphAdapter()


__all__ = [
    "AppsRgGraphAdapter",
    "RG_ALLOWED_RELATION_TYPES",
    "RG_MAX_EDGES",
    "RG_MAX_HOPS",
    "RG_MAX_NODES",
    "build_rg_graph_traverse_input",
    "get_graph_adapter",
]
