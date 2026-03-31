"""Runtime ADG materializer — converts drained OTel spans into a RuntimeADGSnapshot.

Pipeline:
    tracer.drain_completed_spans()   →  list[dict]
    RuntimeADGMaterializer.materialize(spans, mission)  →  RuntimeADGSnapshot

Node extraction:
    Each span dict becomes one RuntimeADGNode.

Edge extraction:
    parent_child   — span with non-empty parent_span_id gets an edge from parent.
    temporal_sequence — consecutive spans (by ts_utc) within the same trace get
                        an ordered edge so the execution path is reconstructable.

Validation:
    Input validation, span structure validation, and graceful error recovery
    ensure robust operation even with malformed or incomplete span data.
"""

from __future__ import annotations

import json
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)
from system_learning.runtime_adg.snapshot import (
    RuntimeADGEdge,
    RuntimeADGNode,
    RuntimeADGSnapshot,
    attributes_to_json,
    create_runtime_adg_snapshot,
)

emit_determinism_digest("runtime_adg_materializer", "runtime_adg_materializer_digest")
record_execution_trace("runtime_adg_materializer", "runtime_adg_materializer_trace")

_ROOT_SENTINEL = "__root__"


def _extract_node(span: dict[str, Any]) -> RuntimeADGNode | None:
    """Extract RuntimeADGNode from span dict with validation and safe defaults.

    Returns None if span lacks required span_id field.
    """
    # Validate required span_id
    span_id = span.get("span_id", "")
    if not span_id or not isinstance(span_id, str):
        return None

    raw_attrs = span.get("attributes", {})
    if isinstance(raw_attrs, str):
        try:
            raw_attrs = json.loads(raw_attrs)
        except (ValueError, TypeError):
            raw_attrs = {}

    # Safely extract and validate timestamp
    try:
        ts_utc = int(span.get("ts_utc", 0))
    except (ValueError, TypeError):
        ts_utc = 0

    # Safely extract and validate duration
    try:
        duration_ms = float(span.get("duration_ms", 0.0))
        if duration_ms < 0:
            duration_ms = 0.0
    except (ValueError, TypeError):
        duration_ms = 0.0

    # Validate status is one of allowed values
    status = str(span.get("status", "ok"))
    if status not in ("ok", "error"):
        status = "ok"

    return RuntimeADGNode(
        node_id=span_id,
        name=str(span.get("name", ""))[:256],  # Limit name length
        kind=str(span.get("kind", "unknown"))[:64],
        layer=str(span.get("layer", ""))[:8],  # L0-L6 format
        component=str(span.get("component", ""))[:128],
        started_at_utc=ts_utc,
        duration_ms=duration_ms,
        status=status,
        attributes_json=attributes_to_json(raw_attrs if isinstance(raw_attrs, dict) else {}),
    )


def _extract_parent_child_edges(spans: list[dict[str, Any]]) -> list[RuntimeADGEdge]:
    """Extract parent-child edges from spans with validation.

    Each span with a valid span_id gets a parent_child edge:
    - If parent_span_id is present and valid: edge from parent to child
    - Otherwise: edge from __root__ sentinel to child
    """
    edges: list[RuntimeADGEdge] = []
    seen_span_ids: set[str] = set()

    for span in spans:
        span_id = str(span.get("span_id", ""))
        if not span_id:
            continue

        # Skip duplicate span_ids (keep first occurrence)
        if span_id in seen_span_ids:
            continue
        seen_span_ids.add(span_id)

        parent_id = str(span.get("parent_span_id", ""))
        # Use parent if valid and exists in seen spans, otherwise root
        src = parent_id if parent_id and parent_id in seen_span_ids else _ROOT_SENTINEL
        edges.append(RuntimeADGEdge(src_id=src, dst_id=span_id, relation="parent_child"))

    return edges


def _extract_temporal_edges(spans: list[dict[str, Any]]) -> list[RuntimeADGEdge]:
    """Extract temporal sequence edges from spans with validation.

    Orders spans by timestamp and span_id, then creates edges between consecutive spans.
    """
    if len(spans) < 2:
        return []

    def safe_ts_utc(s: dict[str, Any]) -> int:
        """Safely extract timestamp, returning 0 for invalid values."""
        try:
            val = s.get("ts_utc", 0)
            return int(val)
        except (ValueError, TypeError):
            return 0

    ordered = sorted(spans, key=lambda s: (safe_ts_utc(s), str(s.get("span_id", ""))))
    edges: list[RuntimeADGEdge] = []
    for prev, curr in zip(ordered, ordered[1:]):
        src_id = str(prev.get("span_id", ""))
        dst_id = str(curr.get("span_id", ""))
        if src_id and dst_id and src_id != dst_id:
            edges.append(RuntimeADGEdge(src_id=src_id, dst_id=dst_id, relation="temporal_sequence"))
    return edges


class RuntimeADGMaterializer:
    """Converts a list of drained OTel span dicts into a ``RuntimeADGSnapshot``.

    Usage::

        spans = tracer.drain_completed_spans()
        snapshot = RuntimeADGMaterializer().materialize(spans, mission="campaign-run-001")
    """

    def materialize(
        self,
        spans: list[dict[str, Any]],
        mission: str = "",
        trace_id: str = "",
    ) -> RuntimeADGSnapshot:
        """Materialise a ``RuntimeADGSnapshot`` from drained span records.

        Parameters
        ----------
        spans:
            Span dicts as returned by ``OpenTelemetryTracingAdapter.drain_completed_spans()``.
        mission:
            Human-readable mission label. Falls back to root span name if empty.
        trace_id:
            Explicit trace ID. Falls back to first span's trace_id if empty.

        Returns
        -------
        RuntimeADGSnapshot
            Immutable, content-addressed snapshot.

        Validation:
            - Empty spans: returns empty snapshot with zero timestamps
            - Missing fields: safe defaults applied
            - Invalid types: coerced or set to defaults
            - Duplicate span_ids: first occurrence kept
        """
        # Validate and sanitize mission
        mission = str(mission)[:256] if mission else ""

        if not spans:
            return create_runtime_adg_snapshot(
                trace_id=str(trace_id)[:128] if trace_id else "",
                mission=mission,
                started_at_utc=0,
                ended_at_utc=0,
                nodes=(),
                edges=(),
            )

        resolved_trace_id = str(trace_id)[:128] if trace_id else str(spans[0].get("trace_id", ""))[:128]
        resolved_mission = mission or _infer_mission(spans)

        # Extract nodes with validation
        nodes_list: list[RuntimeADGNode] = []
        for span in spans:
            node = _extract_node(span)
            if node is not None:
                nodes_list.append(node)

        nodes = tuple(nodes_list)

        # Extract edges
        parent_child = _extract_parent_child_edges(spans)
        temporal = _extract_temporal_edges(spans)
        all_edges = tuple(parent_child + temporal)

        # Calculate time bounds with validation
        if nodes_list:
            started = min(n.started_at_utc for n in nodes_list)
            ended = max(n.started_at_utc + int(n.duration_ms) for n in nodes_list)
        else:
            started = 0
            ended = 0

        return create_runtime_adg_snapshot(
            trace_id=resolved_trace_id,
            mission=resolved_mission,
            started_at_utc=started,
            ended_at_utc=ended,
            nodes=nodes,
            edges=all_edges,
        )


def _infer_mission(spans: list[dict[str, Any]]) -> str:
    root_candidates = [s for s in spans if not s.get("parent_span_id", "")]
    if root_candidates:
        attrs = root_candidates[0].get("attributes", {})
        if isinstance(attrs, dict) and "mission" in attrs:
            return str(attrs["mission"])
        return str(root_candidates[0].get("name", ""))
    return str(spans[0].get("name", "")) if spans else ""
