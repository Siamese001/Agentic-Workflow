"""Adapter — runtime ADG snapshot → validate_trace input.

Converts a :class:`system_learning.runtime_adg.snapshot.RuntimeADGSnapshot`
into the list-of-dicts shape expected by
:func:`agentic_core.L6_observability.runtime_trace.contract.validate_trace`.

Bridges two vocabularies:

| Runtime ADG edge relation | Contract edge kind   |
|---------------------------|----------------------|
| ``parent_child``          | (used to derive ``parent_name``; not exposed as a span-level edge) |
| ``temporal_sequence``     | (dropped)            |
| ``write_edge``            | ``writes_to``        |
| ``read_edge``             | ``reads_from``       |
| ``dependency``            | ``flows_to``         |
| ``tool_invocation_edge``  | ``emits_side_effect``|
| (others)                  | passed through verbatim |

The adapter is read-only — it never mutates the snapshot.
"""

from __future__ import annotations

import json
from typing import Any

from system_learning.runtime_adg.snapshot import RuntimeADGSnapshot

# Runtime ADG edge → contract edge kind translation.
_EDGE_KIND_TRANSLATION: dict[str, str] = {
    "write_edge": "writes_to",
    "read_edge": "reads_from",
    "dependency": "flows_to",
    "tool_invocation_edge": "emits_side_effect",
}

_DROPPED_RELATIONS: frozenset[str] = frozenset(
    {"parent_child", "temporal_sequence"}
)


def snapshot_to_spans(snapshot: RuntimeADGSnapshot) -> list[dict[str, Any]]:
    """Convert a snapshot to a list of validate_trace-shaped span dicts.

    Each output dict has::

        {
            "name": str,
            "layer": str,
            "parent_name": str | None,
            "attributes": dict,
            "status": str,
            "edges": [{"to": str, "kind": str}, ...],
        }
    """
    # node_id -> name (used to resolve parent_child src and semantic edges
    # whose dst is itself a span_id).
    name_by_id: dict[str, str] = {n.node_id: n.name for n in snapshot.nodes}

    # node_id -> parent name (from parent_child edges).
    parent_name_by_id: dict[str, str | None] = {n.node_id: None for n in snapshot.nodes}
    for edge in snapshot.edges:
        if edge.relation != "parent_child":
            continue
        if edge.src_id.startswith("__"):
            # Root sentinel — child has no real parent.
            continue
        if edge.dst_id in parent_name_by_id and edge.src_id in name_by_id:
            parent_name_by_id[edge.dst_id] = name_by_id[edge.src_id]

    # node_id -> outgoing semantic edges (translated to contract vocab).
    edges_by_id: dict[str, list[dict[str, str]]] = {n.node_id: [] for n in snapshot.nodes}
    for edge in snapshot.edges:
        if edge.relation in _DROPPED_RELATIONS:
            continue
        if edge.src_id not in edges_by_id:
            # Edge whose source is not a node (e.g., synthetic targets) — skip.
            continue
        kind = _EDGE_KIND_TRANSLATION.get(edge.relation, edge.relation)
        # If dst is itself a span node, translate to that span's name; else
        # keep the literal string (the materializer often uses the target
        # identifier directly for write_edge / read_edge).
        target = name_by_id.get(edge.dst_id, edge.dst_id)
        edges_by_id[edge.src_id].append({"to": target, "kind": kind})

    out: list[dict[str, Any]] = []
    for node in snapshot.nodes:
        try:
            attrs = json.loads(node.attributes_json) if node.attributes_json else {}
        except (json.JSONDecodeError, TypeError):
            attrs = {}
        if not isinstance(attrs, dict):
            attrs = {}
        out.append(
            {
                "name": node.name,
                "layer": node.layer,
                "parent_name": parent_name_by_id.get(node.node_id),
                "attributes": attrs,
                "status": node.status,
                "edges": edges_by_id.get(node.node_id, []),
            }
        )
    return out


__all__ = ["snapshot_to_spans"]
