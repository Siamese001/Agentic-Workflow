"""Runtime ADG snapshot — per-execution-trace immutable graph artifact.

Design: snapshot-based runtime ADG.
  - One snapshot per OTel trace (natural execution boundary).
  - Nodes = span records (agents, tools, reasoning steps).
  - Edges = parent-child span relationships + temporal ordering.
  - Content-addressed: snapshot_id = SHA-256 of canonical_bytes().
  - Persists via FileBackedVersionStore (L4) — no new storage subsystem.

Anchor rule: if it requires execution to observe → runtime ADG.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    emit_determinism_digest,
    record_execution_trace,
)

emit_determinism_digest("runtime_adg_snapshot", "runtime_adg_snapshot_digest")
record_execution_trace("runtime_adg_snapshot", "runtime_adg_snapshot_trace")


@dataclass(frozen=True, slots=True)
class RuntimeADGNode:
    """A single span captured as a node in the runtime ADG.

    Fields
    ------
    node_id : str
        Span ID — unique within a trace.
    name : str
        Span name (e.g. ``orchestrator.execute``, ``tool.search``).
    kind : str
        Span kind (orchestrator / cognitive / action / tool / dag_node / reasoning).
    layer : str
        Architecture layer (L0–L6).
    component : str
        Component class / service name.
    started_at_utc : int
        Span start time (Unix milliseconds).
    duration_ms : float
        Span duration in milliseconds.
    status : str
        ``ok`` or ``error``.
    attributes_json : str
        Span attributes serialised as compact sorted JSON.
    """

    node_id: str
    name: str
    kind: str
    layer: str
    component: str
    started_at_utc: int
    duration_ms: float
    status: str
    attributes_json: str


@dataclass(frozen=True, slots=True)
class RuntimeADGEdge:
    """A directed edge in the runtime ADG.

    Fields
    ------
    src_id : str
        Source node ID (parent span ID, or ``__root__`` for root spans).
    dst_id : str
        Destination node ID (child span ID).
    relation : str
        Relation type: ``parent_child`` | ``temporal_sequence``.
    """

    src_id: str
    dst_id: str
    relation: str


@dataclass(frozen=True, slots=True)
class RuntimeADGSnapshot:
    """Immutable, content-addressed runtime ADG for one execution trace.

    Fields
    ------
    snapshot_id : str
        Content-addressed ID — SHA-256 of ``canonical_bytes()``.
    trace_id : str
        OTel trace ID.
    mission : str
        Mission / run label (from root span attributes or caller).
    started_at_utc : int
        Trace start (Unix milliseconds).
    ended_at_utc : int
        Trace end (Unix milliseconds).
    nodes : tuple[RuntimeADGNode, ...]
        Span nodes sorted deterministically.
    edges : tuple[RuntimeADGEdge, ...]
        Edges sorted deterministically.
    snapshot_hash : str
        SHA-256 hex digest (same value as snapshot_id).
    """

    snapshot_id: str
    trace_id: str
    mission: str
    started_at_utc: int
    ended_at_utc: int
    nodes: tuple[RuntimeADGNode, ...]
    edges: tuple[RuntimeADGEdge, ...]
    snapshot_hash: str

    def canonical_bytes(self) -> bytes:
        """Return deterministic bytes for content-addressed storage.

        Compatible with ``FileBackedVersionStore.commit_change_package()``.
        """
        return _canonical_bytes(self)

    def node_count(self) -> int:
        return len(self.nodes)

    def edge_count(self) -> int:
        return len(self.edges)

    def validate(self) -> dict[str, Any]:
        """Validate snapshot integrity and return validation report.

        Wave 2: Validates snapshot structure and edge types.

        Returns:
            Dictionary with validation results:
            - is_valid: Overall validation status
            - errors: List of validation errors
            - warnings: List of validation warnings
            - stats: Snapshot statistics
            - edge_types: Count of each edge type
        """
        errors: list[str] = []
        warnings: list[str] = []
        edge_type_counts: dict[str, int] = {}

        # Validate basic structure
        if not self.snapshot_id:
            errors.append("Missing snapshot_id")

        if not self.trace_id:
            errors.append("Missing trace_id")

        # Validate hash consistency
        if self.snapshot_id != self.snapshot_hash:
            errors.append(
                f"Hash mismatch: snapshot_id={self.snapshot_id[:16]}... vs snapshot_hash={self.snapshot_hash[:16]}..."
            )

        # Validate timestamps
        if self.started_at_utc < 0:
            errors.append(f"Invalid started_at_utc: {self.started_at_utc}")
        if self.ended_at_utc < 0:
            errors.append(f"Invalid ended_at_utc: {self.ended_at_utc}")
        if self.ended_at_utc < self.started_at_utc:
            warnings.append(f"Time inversion: ended ({self.ended_at_utc}) < started ({self.started_at_utc})")

        # Validate nodes
        if not self.nodes:
            warnings.append("Empty nodes list")
        else:
            # Check for duplicate node IDs
            node_ids = [n.node_id for n in self.nodes]
            if len(node_ids) != len(set(node_ids)):
                errors.append("Duplicate node IDs detected")

            # Validate each node
            for node in self.nodes:
                if not node.node_id:
                    errors.append("Node with empty node_id")
                if node.duration_ms < 0:
                    errors.append(f"Negative duration for node {node.node_id[:16]}: {node.duration_ms}")

        # Validate edges and count types
        valid_relations = frozenset(
            {
                "parent_child",
                "temporal_sequence",
                "actor",
                "action",
                "target",
                "dependency",
                "read_edge",
                "write_edge",
                "tool_invocation_edge",
                "orchestration_handoff_edge",
                "retry_edge",
                "evaluation_edge",
                "policy_validation_edge",
                "human_escalation_edge",
                "failure_propagation_edge",
                "outcome_edge",
            }
        )

        for edge in self.edges:
            # Count edge types
            edge_type_counts[edge.relation] = edge_type_counts.get(edge.relation, 0) + 1

            # Validate edge relation
            if edge.relation not in valid_relations:
                warnings.append(f"Unknown edge relation: {edge.relation}")

            # Check for dangling edges (referencing non-existent nodes)
            if self.nodes:
                node_ids = {n.node_id for n in self.nodes}
                if edge.src_id not in node_ids and not edge.src_id.startswith("__"):
                    warnings.append(f"Dangling edge src: {edge.src_id[:32]}...")
                if edge.dst_id not in node_ids and not edge.dst_id.startswith("__"):
                    warnings.append(f"Dangling edge dst: {edge.dst_id[:32]}...")

        # Calculate statistics
        stats = {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "edge_type_count": len(edge_type_counts),
            "semantic_edge_count": sum(
                count
                for rel, count in edge_type_counts.items()
                if rel not in ("parent_child", "temporal_sequence")
            ),
            "duration_ms": self.ended_at_utc - self.started_at_utc
            if self.ended_at_utc >= self.started_at_utc
            else 0,
        }

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "stats": stats,
            "edge_types": edge_type_counts,
        }

    def to_dict(self) -> dict:
        return {
            "snapshot_id": self.snapshot_id,
            "trace_id": self.trace_id,
            "mission": self.mission,
            "started_at_utc": self.started_at_utc,
            "ended_at_utc": self.ended_at_utc,
            "node_count": self.node_count(),
            "edge_count": self.edge_count(),
            "nodes": [
                {
                    "node_id": n.node_id,
                    "name": n.name,
                    "kind": n.kind,
                    "layer": n.layer,
                    "component": n.component,
                    "started_at_utc": n.started_at_utc,
                    "duration_ms": n.duration_ms,
                    "status": n.status,
                    "attributes_json": n.attributes_json,
                }
                for n in self.nodes
            ],
            "edges": [{"src_id": e.src_id, "dst_id": e.dst_id, "relation": e.relation} for e in self.edges],
            "snapshot_hash": self.snapshot_hash,
        }


def _canonical_bytes(snapshot: RuntimeADGSnapshot) -> bytes:
    """Deterministic serialisation for hashing.

    Field order is fixed. Nodes and edges are sorted by their natural keys.
    """
    sorted_nodes = sorted(
        snapshot.nodes,
        key=lambda n: (n.started_at_utc, n.node_id, n.name),
    )
    sorted_edges = sorted(
        snapshot.edges,
        key=lambda e: (e.src_id, e.dst_id, e.relation),
    )
    node_parts = [
        b"\x1e".join(
            [
                n.node_id.encode(),
                n.name.encode(),
                n.kind.encode(),
                n.layer.encode(),
                n.component.encode(),
                str(n.started_at_utc).encode(),
                str(round(n.duration_ms, 3)).encode(),
                n.status.encode(),
                n.attributes_json.encode(),
            ],
        )
        for n in sorted_nodes
    ]
    edge_parts = [
        b"\x1e".join([e.src_id.encode(), e.dst_id.encode(), e.relation.encode()]) for e in sorted_edges
    ]
    header = b"\x1f".join(
        [
            snapshot.trace_id.encode(),
            snapshot.mission.encode(),
            str(snapshot.started_at_utc).encode(),
            str(snapshot.ended_at_utc).encode(),
        ],
    )
    return header + b"\x1f" + b"\x1f".join(node_parts + edge_parts)


def _compute_snapshot_hash(snapshot: RuntimeADGSnapshot) -> str:
    return hashlib.sha256(_canonical_bytes(snapshot)).hexdigest()


def create_runtime_adg_snapshot(
    trace_id: str,
    mission: str,
    started_at_utc: int,
    ended_at_utc: int,
    nodes: tuple[RuntimeADGNode, ...],
    edges: tuple[RuntimeADGEdge, ...],
) -> RuntimeADGSnapshot:
    """Create a content-addressed ``RuntimeADGSnapshot``.

    Parameters
    ----------
    trace_id:
        OTel trace ID for this execution.
    mission:
        Human-readable mission or run label.
    started_at_utc:
        Trace start (Unix ms).
    ended_at_utc:
        Trace end (Unix ms).
    nodes:
        Span nodes — will be sorted deterministically.
    edges:
        Graph edges — will be sorted deterministically.

    Returns
    -------
    RuntimeADGSnapshot
        Immutable, content-addressed snapshot.
    """
    sorted_nodes = tuple(sorted(nodes, key=lambda n: (n.started_at_utc, n.node_id, n.name)))
    sorted_edges = tuple(sorted(edges, key=lambda e: (e.src_id, e.dst_id, e.relation)))
    temp = RuntimeADGSnapshot(
        snapshot_id="",
        trace_id=trace_id,
        mission=mission,
        started_at_utc=started_at_utc,
        ended_at_utc=ended_at_utc,
        nodes=sorted_nodes,
        edges=sorted_edges,
        snapshot_hash="",
    )
    h = _compute_snapshot_hash(temp)
    return RuntimeADGSnapshot(
        snapshot_id=h,
        trace_id=trace_id,
        mission=mission,
        started_at_utc=started_at_utc,
        ended_at_utc=ended_at_utc,
        nodes=sorted_nodes,
        edges=sorted_edges,
        snapshot_hash=h,
    )


def attributes_to_json(attrs: dict) -> str:
    """Serialise span attributes dict to compact sorted JSON string."""
    return json.dumps(attrs, sort_keys=True, separators=(",", ":"), default=str)
