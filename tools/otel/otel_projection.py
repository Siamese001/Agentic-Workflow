from __future__ import annotations

from typing import Any


def convert_snapshot_to_adg_edges(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    """Convert runtime ADG snapshot payload into projected ADG edges."""
    edges: list[dict[str, Any]] = []
    nodes = snapshot.get("nodes", [])

    for node in nodes:
        parent_span_id = node.get("parent_span_id")
        if not parent_span_id:
            continue
        parent_node = next((item for item in nodes if item.get("span_id") == parent_span_id), None)
        if parent_node is None:
            continue
        edges.append(
            {
                "source": parent_node.get("name", "unknown"),
                "target": node.get("name", "unknown"),
                "relation_type": "parent_child",
                "edge_kind": "temporal",
                "layer": node.get("layer", "unknown"),
                "component": node.get("component", "unknown"),
                "timestamp": node.get("started_at_utc", 0),
                "attributes": {
                    "span_id": node.get("span_id"),
                    "parent_span_id": parent_span_id,
                    "status": node.get("status"),
                    "duration_ms": node.get("duration_ms"),
                },
            }
        )
    return edges
