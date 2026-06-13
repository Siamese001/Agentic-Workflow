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
