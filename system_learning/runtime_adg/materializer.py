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
"""

from __future__ import annotations

import json
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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


def _extract_node(span: dict[str, Any]) -> RuntimeADGNode:
    raw_attrs = span.get("attributes", {})
    if isinstance(raw_attrs, str):
        try:
            raw_attrs = json.loads(raw_attrs)
        except (ValueError, TypeError):
            raw_attrs = {}
    return RuntimeADGNode(
        node_id=str(span.get("span_id", "")),
        name=str(span.get("name", "")),
        kind=str(span.get("kind", "unknown")),
        layer=str(span.get("layer", "")),
        component=str(span.get("component", "")),
        started_at_utc=int(span.get("ts_utc", 0)),
        duration_ms=float(span.get("duration_ms", 0.0)),
        status=str(span.get("status", "ok")),
        attributes_json=attributes_to_json(raw_attrs if isinstance(raw_attrs, dict) else {}),
    )


def _extract_parent_child_edges(spans: list[dict[str, Any]]) -> list[RuntimeADGEdge]:
    edges: list[RuntimeADGEdge] = []
    for span in spans:
        span_id = str(span.get("span_id", ""))
        parent_id = str(span.get("parent_span_id", ""))
        if not span_id:
            continue
        src = parent_id if parent_id else _ROOT_SENTINEL
        edges.append(RuntimeADGEdge(src_id=src, dst_id=span_id, relation="parent_child"))
    return edges


def _extract_temporal_edges(spans: list[dict[str, Any]]) -> list[RuntimeADGEdge]:
    if len(spans) < 2:
        return []
    ordered = sorted(spans, key=lambda s: (int(s.get("ts_utc", 0)), str(s.get("span_id", ""))))
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
        """
        if not spans:
            return create_runtime_adg_snapshot(
                trace_id=trace_id or "",
                mission=mission or "",
                started_at_utc=0,
                ended_at_utc=0,
                nodes=(),
                edges=(),
            )

        resolved_trace_id = trace_id or str(spans[0].get("trace_id", ""))
        resolved_mission = mission or _infer_mission(spans)

        nodes = tuple(_extract_node(s) for s in spans)
        parent_child = _extract_parent_child_edges(spans)
        temporal = _extract_temporal_edges(spans)
        all_edges = tuple(parent_child + temporal)

        started = min(int(s.get("ts_utc", 0)) for s in spans)
        ended = max(int(s.get("ts_utc", 0)) + int(s.get("duration_ms", 0)) for s in spans)

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
