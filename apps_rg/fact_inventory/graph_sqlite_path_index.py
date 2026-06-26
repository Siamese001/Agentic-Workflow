"""Deterministic graph-index projections for the augmented skills SQLite DB.

The JSON ledger remains canonical. This module builds generated helper rows
from materialized graph nodes/edges so SQLite can answer bounded path,
neighborhood, sibling, section-budget, and diagnostic-style graph queries.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from typing import Any

GRAPH_INDEX_SCHEMA_VERSION = "graph_sqlite_path_index_v1"
DEFAULT_MAX_DEPTH = 3
DEFAULT_MAX_EDGES_PER_NODE = 24


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _hash_id(prefix: str, value: str) -> str:
    return f"{prefix}_{hashlib.sha1(value.encode('utf-8')).hexdigest()[:24]}"


def _node_type(node_by_id: dict[str, dict[str, Any]], node_id: str) -> str:
    return str((node_by_id.get(node_id) or {}).get("node_type") or "")


def _edge_weight(edge: dict[str, Any]) -> float:
    try:
        return float(edge.get("weight") or 1.0)
    except (TypeError, ValueError):
        return 1.0


def _path_scores(
    *,
    node_by_id: dict[str, dict[str, Any]],
    edge_path: list[dict[str, Any]],
    node_path: list[str],
) -> tuple[float, float, float]:
    depth = max(1, len(edge_path))
    total_weight = sum(_edge_weight(e) for e in edge_path)
    path_score = round(total_weight / depth, 4)
    edge_type_count = len({str(e.get("edge_type") or "") for e in edge_path})
    novelty_score = round(edge_type_count / depth, 4)
    proof_strength = 0.0
    if any(_node_type(node_by_id, nid) == "fact" for nid in node_path):
        proof_strength += 1.0
    if any(_node_type(node_by_id, nid) == "metric_outcome" for nid in node_path):
        proof_strength += 0.75
    if any(str(e.get("external_claim_policy") or "") for e in edge_path):
        proof_strength += 0.25
    return path_score, novelty_score, round(proof_strength, 4)


def _build_path_rows(
    *,
    node_by_id: dict[str, dict[str, Any]],
    edge_rows: list[dict[str, Any]],
    created_at: str,
    max_depth: int = DEFAULT_MAX_DEPTH,
) -> list[dict[str, Any]]:
    adjacency: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edge_rows:
        src = str(edge.get("source_node_id") or "")
        tgt = str(edge.get("target_node_id") or "")
        if src in node_by_id and tgt in node_by_id:
            adjacency[src].append(edge)
    for edges in adjacency.values():
        edges.sort(
            key=lambda e: (
                str(e.get("edge_type") or ""),
                str(e.get("target_node_id") or ""),
                str(e.get("edge_id") or ""),
            )
        )

    start_types = {
        "role_family",
        "career_track",
        "pillar",
        "capability_domain",
        "skill",
        "fact",
        "metric_outcome",
        "employment",
    }
    rows: dict[str, dict[str, Any]] = {}

    def walk(start: str, current: str, node_path: list[str], edge_path: list[dict[str, Any]]) -> None:
        if edge_path:
            edge_ids = [str(e.get("edge_id") or "") for e in edge_path]
            edge_types = [str(e.get("edge_type") or "") for e in edge_path]
            signature = "->".join(node_path)
            proof_fact_ids = [nid for nid in node_path if _node_type(node_by_id, nid) == "fact"]
            metric_ids = [nid for nid in node_path if _node_type(node_by_id, nid) == "metric_outcome"]
            section_ids = [nid for nid in node_path if _node_type(node_by_id, nid) == "section"]
            path_score, novelty_score, proof_strength = _path_scores(
                node_by_id=node_by_id,
                edge_path=edge_path,
                node_path=node_path,
            )
            path_id = _hash_id("path", signature + "|" + "|".join(edge_ids))
            rows[path_id] = {
                "path_id": path_id,
                "start_node_id": start,
                "end_node_id": current,
                "path_depth": len(edge_path),
                "path_signature": signature,
                "node_path_json": _json(node_path),
                "edge_path_json": _json(edge_ids),
                "edge_types_json": _json(edge_types),
                "proof_fact_ids_json": _json(proof_fact_ids),
                "metric_ids_json": _json(metric_ids),
                "section_ids_json": _json(section_ids),
                "path_score": path_score,
                "novelty_score": novelty_score,
                "proof_strength_score": proof_strength,
                "created_at": created_at,
            }
        if len(edge_path) >= max_depth:
            return
        for edge in adjacency.get(current, [])[:DEFAULT_MAX_EDGES_PER_NODE]:
            nxt = str(edge.get("target_node_id") or "")
            if nxt in node_path:
                continue
            walk(start, nxt, [*node_path, nxt], [*edge_path, edge])

    for node_id, node in sorted(node_by_id.items()):
        if str(node.get("node_type") or "") in start_types:
            walk(node_id, node_id, [node_id], [])
    return sorted(rows.values(), key=lambda r: (r["start_node_id"], r["path_depth"], r["end_node_id"]))


def _build_neighborhood_rows(path_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    chosen: dict[tuple[str, str, int], dict[str, Any]] = {}
    for path in path_rows:
        key = (
            str(path["start_node_id"]),
            str(path["end_node_id"]),
            int(path["path_depth"]),
        )
        row = {
            "center_node_id": key[0],
            "neighbor_node_id": key[1],
            "distance": key[2],
            "connecting_path_json": str(path["node_path_json"]),
            "edge_types_json": str(path["edge_types_json"]),
            "relationship_summary": (
                f"distance={path['path_depth']}; edge_types="
                f"{','.join(json.loads(str(path['edge_types_json'])))}"
            ),
            "neighbor_score": round(
                float(path.get("path_score") or 0.0)
                + float(path.get("novelty_score") or 0.0)
                + float(path.get("proof_strength_score") or 0.0),
                4,
            ),
        }
        prior = chosen.get(key)
        if prior is None or row["neighbor_score"] > prior["neighbor_score"]:
            chosen[key] = row
    return sorted(chosen.values(), key=lambda r: (r["center_node_id"], r["distance"], r["neighbor_node_id"]))


def _upsert_sibling(
    rows: dict[tuple[str, str], dict[str, Any]],
    *,
    node_id: str,
    sibling_node_id: str,
    sibling_reason: str,
    shared_parent_node_id: str,
    shared_edge_type: str,
    sibling_score: float,
) -> None:
    if not node_id or not sibling_node_id or node_id == sibling_node_id:
        return
    key = (node_id, sibling_node_id)
    row = {
        "node_id": node_id,
        "sibling_node_id": sibling_node_id,
        "sibling_reason": sibling_reason,
        "shared_parent_node_id": shared_parent_node_id,
        "shared_edge_type": shared_edge_type,
        "sibling_score": round(sibling_score, 4),
    }
    prior = rows.get(key)
    if prior is None or row["sibling_score"] > float(prior["sibling_score"]):
        rows[key] = row


def _build_sibling_rows(
    *,
    node_by_id: dict[str, dict[str, Any]],
    edge_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    parent_groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    fact_groups: dict[tuple[str, str], list[str]] = defaultdict(list)

    for edge in edge_rows:
        src = str(edge.get("source_node_id") or "")
        tgt = str(edge.get("target_node_id") or "")
        etype = str(edge.get("edge_type") or "")
        if _node_type(node_by_id, tgt) == "skill" and _node_type(node_by_id, src) != "skill":
            parent_groups[(src, etype)].append(tgt)
        if _node_type(node_by_id, src) == "skill" and _node_type(node_by_id, tgt) == "fact":
            fact_groups[(tgt, etype)].append(src)

    rows: dict[tuple[str, str], dict[str, Any]] = {}
    for (parent, etype), skills in sorted(parent_groups.items()):
        uniq = sorted(set(skills))
        for skill in uniq:
            for sibling in uniq:
                _upsert_sibling(
                    rows,
                    node_id=skill,
                    sibling_node_id=sibling,
                    sibling_reason=f"shared_parent:{etype}",
                    shared_parent_node_id=parent,
                    shared_edge_type=etype,
                    sibling_score=1.0,
                )
    for (fact_id, etype), skills in sorted(fact_groups.items()):
        uniq = sorted(set(skills))
        for skill in uniq:
            for sibling in uniq:
                _upsert_sibling(
                    rows,
                    node_id=skill,
                    sibling_node_id=sibling,
                    sibling_reason="shared_fact",
                    shared_parent_node_id=fact_id,
                    shared_edge_type=etype,
                    sibling_score=1.5,
                )
    return sorted(rows.values(), key=lambda r: (r["node_id"], -float(r["sibling_score"]), r["sibling_node_id"]))


def _section_budget_defaults(section_id: str) -> dict[str, Any]:
    normalized = str(section_id or "").lower()
    if normalized == "executive_summary":
        return {
            "max_metric_reuse": 1,
            "max_fact_family_reuse": 2,
            "required_node_types_json": ["skill", "fact"],
            "preferred_edge_types_json": ["skill_supported_by_fact", "skill_allowed_in_section"],
            "preferred_metric_families_json": ["risk_governance", "platform_scale", "business_outcome"],
        }
    if "competenc" in normalized:
        return {
            "max_metric_reuse": 1,
            "max_fact_family_reuse": 3,
            "required_node_types_json": ["skill"],
            "preferred_edge_types_json": ["capability_domain_contains_skill", "pillar_contains_capability_domain"],
            "preferred_metric_families_json": ["breadth", "platform_scale"],
        }
    if "technical" in normalized or "architecture" in normalized:
        return {
            "max_metric_reuse": 1,
            "max_fact_family_reuse": 2,
            "required_node_types_json": ["skill", "fact", "metric_outcome"],
            "preferred_edge_types_json": ["skill_supported_by_fact", "metric_outcome_section_eligible"],
            "preferred_metric_families_json": ["platform_scale", "risk_governance"],
        }
    return {
        "max_metric_reuse": 1,
        "max_fact_family_reuse": 2,
        "required_node_types_json": ["skill", "fact"],
        "preferred_edge_types_json": ["skill_supported_by_fact", "skill_allowed_in_section"],
        "preferred_metric_families_json": [],
    }


def _build_section_budget_rows(
    *,
    node_by_id: dict[str, dict[str, Any]],
    section_rows: list[dict[str, Any]],
    role_family_projection_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    sections = {
        str(nid)
        for nid, row in node_by_id.items()
        if str(row.get("node_type") or "") == "section"
    }
    sections.update(str(r.get("section_id") or "") for r in section_rows if str(r.get("section_id") or ""))
    role_families = [
        str(r.get("projection_role_family_key") or r.get("role_family_id") or "")
        for r in role_family_projection_rows
    ]
    role_families = sorted({rf for rf in role_families if rf})
    rows: list[dict[str, Any]] = []
    for section in sorted(sections):
        defaults = _section_budget_defaults(section)
        for role_family in role_families:
            rows.append(
                {
                    "section_id": section,
                    "role_family_key": role_family,
                    "max_metric_reuse": int(defaults["max_metric_reuse"]),
                    "max_fact_family_reuse": int(defaults["max_fact_family_reuse"]),
                    "required_node_types_json": _json(defaults["required_node_types_json"]),
                    "preferred_edge_types_json": _json(defaults["preferred_edge_types_json"]),
                    "forbidden_metric_ids_json": "[]",
                    "preferred_metric_families_json": _json(defaults["preferred_metric_families_json"]),
                }
            )
    return rows


def build_graph_index_rows(
    *,
    node_rows: list[dict[str, Any]],
    edge_rows: list[dict[str, Any]],
    section_rows: list[dict[str, Any]],
    role_family_projection_rows: list[dict[str, Any]],
    created_at: str,
) -> dict[str, list[dict[str, Any]]]:
    """Build deterministic graph-index helper rows from materialized rows."""
    node_by_id = {str(row.get("node_id") or ""): row for row in node_rows if str(row.get("node_id") or "")}
    normalized_edges = [
        dict(row)
        for row in edge_rows
        if str(row.get("source_node_id") or "") and str(row.get("target_node_id") or "")
    ]
    path_rows = _build_path_rows(
        node_by_id=node_by_id,
        edge_rows=normalized_edges,
        created_at=created_at,
    )
    return {
        "graph_paths": path_rows,
        "graph_neighborhoods": _build_neighborhood_rows(path_rows),
        "graph_sibling_links": _build_sibling_rows(
            node_by_id=node_by_id,
            edge_rows=normalized_edges,
        ),
        "section_evidence_budget": _build_section_budget_rows(
            node_by_id=node_by_id,
            section_rows=section_rows,
            role_family_projection_rows=role_family_projection_rows,
        ),
    }


__all__ = [
    "DEFAULT_MAX_DEPTH",
    "GRAPH_INDEX_SCHEMA_VERSION",
    "build_graph_index_rows",
]

