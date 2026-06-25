"""Graph-native metric ID helpers for role episode bundle JSON files.

Metric approval is by presence in ``metric_outcome_nodes``. The
``approved_metric_outcome_ids`` JSON object is a review index, not a separate
runtime authority.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.runtime.sections.role_episode_bundle_registry import load_role_episode_bundle_doc


def metric_outcome_nodes_from_doc(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return metric outcome nodes keyed by metric ID."""
    raw = doc.get("metric_outcome_nodes") or {}
    if isinstance(raw, dict):
        return {str(k): v for k, v in raw.items() if isinstance(v, dict)}
    if isinstance(raw, list):
        out: dict[str, dict[str, Any]] = {}
        for row in raw:
            if isinstance(row, dict) and row.get("metric_outcome_id"):
                out[str(row["metric_outcome_id"])] = row
        return out
    return {}


def metric_outcome_nodes_from_path(path: Path) -> dict[str, dict[str, Any]]:
    """Return graph-native metric outcome nodes for an employer graph file."""
    return metric_outcome_nodes_from_doc(load_role_episode_bundle_doc(path))


def approved_metric_outcome_ids_from_doc(doc: dict[str, Any]) -> tuple[str, ...]:
    """Return approved metric IDs from the graph-native metric node surface."""
    return tuple(metric_outcome_nodes_from_doc(doc).keys())


def approved_metric_outcome_ids_from_path(path: Path) -> tuple[str, ...]:
    """Return approved metric IDs from ``metric_outcome_nodes`` in a graph file."""
    return approved_metric_outcome_ids_from_doc(load_role_episode_bundle_doc(path))


def metric_review_index_ids_from_doc(
    doc: dict[str, Any],
    field: str,
) -> tuple[str, ...]:
    """Return IDs from a non-authoritative graph review index."""
    raw = doc.get(field) or {}
    if isinstance(raw, dict):
        return tuple(str(k) for k in raw.keys())
    if isinstance(raw, list):
        return tuple(str(x) for x in raw if str(x).strip())
    return ()


def metric_review_index_ids_from_path(path: Path, field: str) -> tuple[str, ...]:
    """Return IDs from a non-authoritative graph review index in a graph file."""
    return metric_review_index_ids_from_doc(load_role_episode_bundle_doc(path), field)


def linked_metric_outcome_ids_from_doc(doc: dict[str, Any]) -> tuple[str, ...]:
    """Return unique metric IDs linked from role episode bundles, preserving order."""
    ids: list[str] = []
    seen: set[str] = set()
    for bundle in doc.get("bundles") or []:
        if not isinstance(bundle, dict):
            continue
        for raw in bundle.get("linked_metric_outcome_ids") or []:
            mid = str(raw).strip()
            if mid and mid not in seen:
                seen.add(mid)
                ids.append(mid)
    return tuple(ids)


def linked_metric_ids_missing_from_metric_nodes(doc: dict[str, Any]) -> tuple[str, ...]:
    """Return bundle-linked metric IDs absent from graph-native metric nodes."""
    node_ids = set(approved_metric_outcome_ids_from_doc(doc))
    return tuple(mid for mid in linked_metric_outcome_ids_from_doc(doc) if mid not in node_ids)


def review_index_ids_missing_from_metric_nodes(
    doc: dict[str, Any],
    field: str = "approved_metric_outcome_ids",
) -> tuple[str, ...]:
    """Return review-index metric IDs absent from graph-native metric nodes."""
    node_ids = set(approved_metric_outcome_ids_from_doc(doc))
    return tuple(mid for mid in metric_review_index_ids_from_doc(doc, field) if mid not in node_ids)


def _collect_bundle_field(
    ids: list[str],
    bundle_by_id: dict[str, dict[str, Any]],
    field: str,
) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for bundle_id in ids:
        bundle = bundle_by_id.get(bundle_id) or {}
        for raw in bundle.get(field) or []:
            item = str(raw).strip()
            if item and item not in seen:
                seen.add(item)
                out.append(item)
    return out


def _collect_bundle_metric_ids(
    ids: list[str],
    bundle_by_id: dict[str, dict[str, Any]],
) -> list[str]:
    for field in (
        "linked_metric_outcome_ids",
        "allowed_metric_outcome_ids",
        "metric_outcome_ids",
        "metric_candidates",
        "held_metrics",
    ):
        metric_ids = _collect_bundle_field(ids, bundle_by_id, field)
        if metric_ids:
            return metric_ids
    return []


def build_role_episode_bullet_traversal_sufficiency_receipt(
    *,
    section_id: str,
    slot_ids: tuple[str, ...] | list[str],
    slot_bundle_map: dict[str, str],
    packet: dict[str, Any],
    employer_label: str,
) -> dict[str, Any]:
    """Receipt proving bullet slots traverse a bundle -> skill -> metric frontier."""
    bundles = [
        bundle
        for bundle in (packet.get("role_episode_bundles") or [])
        if isinstance(bundle, dict) and bundle.get("role_episode_bundle_id")
    ]
    bundle_by_id = {str(bundle["role_episode_bundle_id"]): bundle for bundle in bundles}
    eligible_ids = [str(bundle["role_episode_bundle_id"]) for bundle in bundles]

    selected_ids: list[str] = []
    for slot_id in slot_ids:
        bundle_id = str(slot_bundle_map.get(str(slot_id)) or "").strip()
        if bundle_id and bundle_id not in selected_ids:
            selected_ids.append(bundle_id)
    rejected_ids = [bundle_id for bundle_id in eligible_ids if bundle_id not in selected_ids]
    unexplained_ids = [bundle_id for bundle_id in selected_ids if bundle_id not in bundle_by_id]

    selected_skill_ids = _collect_bundle_field(selected_ids, bundle_by_id, "graph_skill_node_ids")
    rejected_skill_ids = _collect_bundle_field(rejected_ids, bundle_by_id, "graph_skill_node_ids")
    selected_metric_ids = _collect_bundle_metric_ids(selected_ids, bundle_by_id)
    rejected_metric_ids = _collect_bundle_metric_ids(rejected_ids, bundle_by_id)

    candidate_conservation_pass = not unexplained_ids and (
        set(selected_ids) | set(rejected_ids)
    ) == set(eligible_ids)

    return {
        "receipt_schema": "role_episode_bullet_traversal_sufficiency_v1",
        "section_id": section_id,
        "employer_label": employer_label,
        "slot_bundle_map_resolved": dict(slot_bundle_map),
        "selected_role_episode_bundle_ids": selected_ids,
        "rejected_sibling_role_episode_bundle_ids": rejected_ids,
        "selected_role_episode_root_count": len(selected_ids),
        "selected_unique_leaf_skill_count": len(selected_skill_ids),
        "selected_unique_metric_count": len(selected_metric_ids),
        "rejected_sibling_skill_count": len(rejected_skill_ids),
        "rejected_sibling_metric_count": len(rejected_metric_ids),
        "selected_leaf_skill_ids": selected_skill_ids,
        "rejected_sibling_skill_ids": rejected_skill_ids,
        "selected_metric_outcome_ids": selected_metric_ids,
        "rejected_sibling_metric_ids": rejected_metric_ids,
        "frontier_size_by_hop_depth": {
            "hop_0_role_episode_roots": len(selected_ids),
            "hop_1_graph_skill_nodes": len(selected_skill_ids),
            "hop_2_metric_outcome_nodes": len(selected_metric_ids),
            "rejected_hop_0_sibling_roots": len(rejected_ids),
            "rejected_hop_1_sibling_skill_nodes": len(rejected_skill_ids),
            "rejected_hop_2_sibling_metric_nodes": len(rejected_metric_ids),
        },
        "candidate_conservation": {
            "eligible_role_episode_root_count": len(eligible_ids),
            "selected_role_episode_root_count": len(selected_ids),
            "rejected_role_episode_root_count": len(rejected_ids),
            "unexplained_selected_role_episode_bundle_ids": unexplained_ids,
            "pass": candidate_conservation_pass,
        },
    }
