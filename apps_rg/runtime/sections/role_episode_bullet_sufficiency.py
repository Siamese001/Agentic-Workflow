"""Generic role-episode bullet traversal sufficiency receipts.

This helper keeps the bullet-lane evidence modules small by centralizing the
common slot -> bundle -> skill / metric traversal accounting. The receipt shape
mirrors the existing Unify traversal proof so the preflight layer can consume it
without special cases.
"""

from __future__ import annotations

from typing import Any


def _bundle_metric_ids(bundle: dict[str, Any]) -> list[str]:
    for field in (
        "linked_metric_outcome_ids",
        "allowed_metric_outcome_ids",
        "metric_outcome_ids",
        "metric_candidates",
        "held_metrics",
    ):
        raw = bundle.get(field) or []
        if not isinstance(raw, list):
            continue
        metric_ids = [str(item).strip() for item in raw if str(item).strip()]
        if metric_ids:
            return metric_ids
    return []


def _collect(ids: list[str], bundle_by_id: dict[str, dict[str, Any]], field: str) -> list[str]:
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

    selected_skill_ids = _collect(selected_ids, bundle_by_id, "graph_skill_node_ids")
    rejected_skill_ids = _collect(rejected_ids, bundle_by_id, "graph_skill_node_ids")
    selected_metric_ids = _collect(selected_ids, bundle_by_id, "linked_metric_outcome_ids")
    if not selected_metric_ids:
        selected_metric_ids = _collect(selected_ids, bundle_by_id, "allowed_metric_outcome_ids")
    if not selected_metric_ids:
        selected_metric_ids = _collect(selected_ids, bundle_by_id, "metric_candidates")
    if not selected_metric_ids:
        selected_metric_ids = _collect(selected_ids, bundle_by_id, "held_metrics")

    rejected_metric_ids = _collect(rejected_ids, bundle_by_id, "linked_metric_outcome_ids")
    if not rejected_metric_ids:
        rejected_metric_ids = _collect(rejected_ids, bundle_by_id, "allowed_metric_outcome_ids")
    if not rejected_metric_ids:
        rejected_metric_ids = _collect(rejected_ids, bundle_by_id, "metric_candidates")
    if not rejected_metric_ids:
        rejected_metric_ids = _collect(rejected_ids, bundle_by_id, "held_metrics")

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


__all__ = ["build_role_episode_bullet_traversal_sufficiency_receipt"]
