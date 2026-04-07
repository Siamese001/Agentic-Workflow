#!/usr/bin/env python3
"""Minimal runtime ADG test - demonstrates concept without complex imports."""

import asyncio
import json
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class RuntimeSpan:
    """Minimal span representation."""
    span_id: str
    parent_span_id: str
    name: str
    kind: str
    layer: str
    component: str
    ts_utc: int
    duration_ms: float
    status: str
    attributes: dict[str, Any]

@dataclass
class RuntimeNode:
    """Runtime ADG node."""
    node_id: str
    name: str
    kind: str
    layer: str
    component: str
    started_at_utc: int
    duration_ms: float
    status: str
    attributes_json: str

@dataclass
class RuntimeEdge:
    """Runtime ADG edge."""
    src_id: str
    dst_id: str
    relation: str

@dataclass
class RuntimeSnapshot:
    """Runtime ADG snapshot."""
    trace_id: str
    mission: str
    started_at_utc: int
    ended_at_utc: int
    nodes: list[RuntimeNode]
    edges: list[RuntimeEdge]

class MinimalTracer:
    """Minimal tracer implementation."""

    def __init__(self):
        self.spans = []
        self._span_stack = []

    def trace_orchestrator(self, mission: str, metadata: dict[str, Any] = None):
        """Context manager for orchestrator tracing."""
        return _TraceContext(self, "orchestrator", "L3_ORCHESTRATION", mission, metadata)

    def trace_dag_node(self, task_id: str, task_type: str, metadata: dict[str, Any] = None):
        """Context manager for DAG node tracing."""
        return _TraceContext(self, task_id, task_type, task_id, metadata)

    def drain_completed_spans(self) -> list[dict[str, Any]]:
        """Return all completed spans."""
        spans = [asdict(span) for span in self.spans]
        self.spans.clear()
        return spans

class _TraceContext:
    """Context manager for tracing."""

    def __init__(self, tracer: MinimalTracer, name: str, kind: str, layer: str, metadata: dict[str, Any]):
        self.tracer = tracer
        self.name = name
        self.kind = kind
        self.layer = layer
        self.metadata = metadata or {}
        self.start_time = None
        self.span_id = str(uuid.uuid4())

    def __enter__(self):
        self.start_time = int(time.time() * 1000)
        parent_id = self.tracer._span_stack[-1].span_id if self.tracer._span_stack else ""

        span = RuntimeSpan(
            span_id=self.span_id,
            parent_span_id=parent_id,
            name=self.name,
            kind=self.kind,
            layer=self.layer,
            component="test_component",
            ts_utc=self.start_time,
            duration_ms=0,  # Will be set on exit
            status="ok",
            attributes=self.metadata,
        )

        self.tracer.spans.append(span)
        self.tracer._span_stack.append(span)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.tracer._span_stack:
            self.tracer._span_stack.pop()

        # Update duration
        end_time = int(time.time() * 1000)
        for span in self.tracer.spans:
            if span.span_id == self.span_id:
                span.duration_ms = end_time - self.start_time
                if exc_type:
                    span.status = "error"
                break

class MinimalRuntimeADG:
    """Minimal runtime ADG implementation."""

    def __init__(self):
        self.snapshots = []

    def materialize(self, spans: list[dict[str, Any]], mission: str = "", trace_id: str = "") -> RuntimeSnapshot:
        """Materialize spans into a runtime ADG snapshot."""
        if not spans:
            return RuntimeSnapshot(
                trace_id=trace_id or "empty",
                mission=mission or "empty",
                started_at_utc=0,
                ended_at_utc=0,
                nodes=[],
                edges=[],
            )

        # Extract nodes
        nodes = []
        for span in spans:
            node = RuntimeNode(
                node_id=span["span_id"],
                name=span["name"],
                kind=span["kind"],
                layer=span["layer"],
                component=span["component"],
                started_at_utc=span["ts_utc"],
                duration_ms=span["duration_ms"],
                status=span["status"],
                attributes_json=json.dumps(span.get("attributes", {})),
            )
            nodes.append(node)

        # Extract edges (parent-child + temporal)
        edges = []
        span_map = {s["span_id"]: s for s in spans}

        # Parent-child edges
        for span in spans:
            if span.get("parent_span_id") and span["parent_span_id"] in span_map:
                edge = RuntimeEdge(
                    src_id=span["parent_span_id"],
                    dst_id=span["span_id"],
                    relation="parent_child",
                )
                edges.append(edge)

        # Temporal edges
        sorted_spans = sorted(spans, key=lambda s: (s["ts_utc"], s["span_id"]))
        for prev, curr in zip(sorted_spans, sorted_spans[1:]):
            edge = RuntimeEdge(
                src_id=prev["span_id"],
                dst_id=curr["span_id"],
                relation="temporal_sequence",
            )
            edges.append(edge)

        # Create snapshot
        started = min(s["ts_utc"] for s in spans)
        ended = max(s["ts_utc"] + s["duration_ms"] for s in spans)

        snapshot = RuntimeSnapshot(
            trace_id=trace_id or spans[0].get("trace_id", "unknown"),
            mission=mission,
            started_at_utc=started,
            ended_at_utc=ended,
            nodes=nodes,
            edges=edges,
        )

        return snapshot

    def persist(self, snapshot: RuntimeSnapshot, output_dir: Path = None) -> str:
        """Persist snapshot to disk."""
        if output_dir is None:
            output_dir = Path("artifacts/runtime_adg")

        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate version ID
        version_id = f"runtime_adg_{int(time.time())}"

        # Save snapshot
        snapshot_file = output_dir / f"{version_id}.json"
        snapshot_data = asdict(snapshot)
        snapshot_file.write_text(json.dumps(snapshot_data, indent=2))

        print(f"[RUNTIME ADG] Persisted snapshot: {snapshot_file}")
        print(f"  - Nodes: {len(snapshot.nodes)}")
        print(f"  - Edges: {len(snapshot.edges)}")
        print(f"  - Duration: {snapshot.ended_at_utc - snapshot.started_at_utc}ms")

        return version_id

async def test_minimal_runtime_adg():
    """Test minimal runtime ADG."""
    print("[TEST] Starting minimal runtime ADG test...")

    try:
        # Initialize tracer and runtime ADG
        tracer = MinimalTracer()
        runtime_adg = MinimalRuntimeADG()

        # Simulate orchestration execution
        mission_id = "test-mission-001"

        with tracer.trace_orchestrator(mission_id, {"mode": "test"}):
            # Simulate workflow steps
            with tracer.trace_dag_node("step1", "validation"):
                await asyncio.sleep(0.01)  # Simulate work

            with tracer.trace_dag_node("step2", "agent_call"):
                await asyncio.sleep(0.02)  # Simulate work

            with tracer.trace_dag_node("step3", "post_processing"):
                await asyncio.sleep(0.01)  # Simulate work

        # Drain spans
        spans = tracer.drain_completed_spans()
        print(f"[TEST] Generated {len(spans)} spans")

        # Materialize snapshot
        snapshot = runtime_adg.materialize(spans, mission=mission_id, trace_id=mission_id)

        # Persist snapshot
        version_id = runtime_adg.persist(snapshot)

        # Verify snapshot
        assert snapshot.nodes, "Should have nodes"
        assert snapshot.edges, "Should have edges"
        assert len(snapshot.nodes) == 4, "Should have 4 nodes (orchestrator + 3 steps)"

        # Check for parent-child edges
        parent_edges = [e for e in snapshot.edges if e.relation == "parent_child"]
        assert len(parent_edges) == 3, "Should have 3 parent-child edges"

        # Check for temporal edges
        temporal_edges = [e for e in snapshot.edges if e.relation == "temporal_sequence"]
        assert len(temporal_edges) == 3, "Should have 3 temporal edges"

        print("[TEST] Minimal runtime ADG test completed successfully!")
        return True

    except Exception as e:
        print(f"[TEST] Minimal runtime ADG test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_minimal_runtime_adg())
