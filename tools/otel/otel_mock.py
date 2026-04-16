from __future__ import annotations

import time
from typing import Any


def create_mock_trace(trace_id: str) -> dict[str, Any]:
    """Create mock trace data when explicitly enabled for local testing."""
    now_ms = int(time.time()) * 1000
    mock_spans = [
        {
            "span_id": "span_1",
            "parent_span_id": None,
            "name": "orchestrator.execute",
            "kind": "orchestrator",
            "layer": "L3_Orchestration",
            "component": "NervousSystem",
            "started_at_utc": now_ms,
            "duration_ms": 5000.0,
            "status": "ok",
        },
        {
            "span_id": "span_2",
            "parent_span_id": "span_1",
            "name": "cognitive.think",
            "kind": "cognitive",
            "layer": "L1_Cognition",
            "component": "CognitivePlane",
            "started_at_utc": now_ms + 1000,
            "duration_ms": 2000.0,
            "status": "ok",
        },
        {
            "span_id": "span_3",
            "parent_span_id": "span_2",
            "name": "tool.search",
            "kind": "tool",
            "layer": "L2_Execution",
            "component": "SearchTool",
            "started_at_utc": now_ms + 2000,
            "duration_ms": 1500.0,
            "status": "ok",
        },
    ]

    adg_edges: list[dict[str, Any]] = []
    for span in mock_spans:
        if not span["parent_span_id"]:
            continue
        parent_span = next((item for item in mock_spans if item["span_id"] == span["parent_span_id"]), None)
        if parent_span is None:
            continue
        adg_edges.append(
            {
                "source": parent_span["name"],
                "target": span["name"],
                "relation_type": "parent_child",
                "edge_kind": "temporal",
                "layer": span["layer"],
                "component": span["component"],
                "timestamp": span["started_at_utc"],
                "attributes": {
                    "span_id": span["span_id"],
                    "parent_span_id": span["parent_span_id"],
                    "status": span["status"],
                    "duration_ms": span["duration_ms"],
                },
            }
        )

    return {
        "trace_id": trace_id,
        "snapshot_id": f"mock_snapshot_{trace_id}",
        "timestamp": int(time.time()),
        "node_count": len(mock_spans),
        "edge_count": len(adg_edges),
        "adg_edges": adg_edges,
        "source": "mock_data",
    }
