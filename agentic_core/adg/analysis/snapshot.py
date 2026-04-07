"""Enhancement 6: Deterministic graph snapshotting.

Produces a canonical, replayable snapshot from a ScanResult that is:
- Fully deterministic (same repo state → same hash)
- Ordered (canonical node and edge ordering)
- Self-describing (schema_version, scanner_version, counts)
- Serializable to dict / JSON
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.adg.extraction.static_scanner import ScanResult


@dataclass
class CanonicalSnapshot:
    """A deterministic, replayable ADG snapshot.

    Attributes:
        graph_hash: SHA-256 over canonical_edges (sorted, stable).
        scanner_hash: digest from ScanResult.digest.
        schema_version: ADG schema version string.
        scanner_version: static_scanner version string.
        node_count: number of distinct module nodes.
        edge_count: total edges in the graph.
        violation_count: number of `violates` edges.
        coverage_count: number of `covers` edges.
        call_count: number of `calls` edges.
        governance_count: number of `writes_through` + `routes_through` edges.
        canonical_node_order: sorted list of all module ADG names.
        canonical_edge_order: sorted list of (from, relation, to) tuples.
        edge_counts_by_relation: per-relation breakdown.
        commit_sha: originating commit SHA (may be empty).
    """

    graph_hash: str = ""
    scanner_hash: str = ""
    schema_version: str = ""
    scanner_version: str = ""
    node_count: int = 0
    edge_count: int = 0
    violation_count: int = 0
    coverage_count: int = 0
    call_count: int = 0
    governance_count: int = 0
    canonical_node_order: list[str] = field(default_factory=list)
    canonical_edge_order: list[tuple[str, str, str]] = field(default_factory=list)
    edge_counts_by_relation: dict[str, int] = field(default_factory=dict)
    commit_sha: str = ""

    def to_dict(self) -> dict:
        return {
            "graph_hash": self.graph_hash,
            "scanner_hash": self.scanner_hash,
            "schema_version": self.schema_version,
            "scanner_version": self.scanner_version,
            "commit_sha": self.commit_sha,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "violation_count": self.violation_count,
            "coverage_count": self.coverage_count,
            "call_count": self.call_count,
            "governance_count": self.governance_count,
            "canonical_node_order": self.canonical_node_order,
            "canonical_edge_order": [list(e) for e in self.canonical_edge_order],
            "edge_counts_by_relation": self.edge_counts_by_relation,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)

    @classmethod
    def from_dict(cls, d: dict) -> CanonicalSnapshot:
        snap = cls(
            graph_hash=d.get("graph_hash", ""),
            scanner_hash=d.get("scanner_hash", ""),
            schema_version=d.get("schema_version", ""),
            scanner_version=d.get("scanner_version", ""),
            commit_sha=d.get("commit_sha", ""),
            node_count=d.get("node_count", 0),
            edge_count=d.get("edge_count", 0),
            violation_count=d.get("violation_count", 0),
            coverage_count=d.get("coverage_count", 0),
            call_count=d.get("call_count", 0),
            governance_count=d.get("governance_count", 0),
            edge_counts_by_relation=d.get("edge_counts_by_relation", {}),
        )
        snap.canonical_node_order = d.get("canonical_node_order", [])
        snap.canonical_edge_order = [tuple(e) for e in d.get("canonical_edge_order", [])]
        return snap

    @classmethod
    def from_json(cls, s: str) -> CanonicalSnapshot:
        return cls.from_dict(json.loads(s))


def save_snapshot(snapshot: CanonicalSnapshot, path: Path) -> None:
    """Persist a CanonicalSnapshot to disk as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(snapshot.to_json(), encoding="utf-8")


def load_snapshot(path: Path) -> CanonicalSnapshot:
    """Load a CanonicalSnapshot from a JSON file on disk."""
    return CanonicalSnapshot.from_json(path.read_text(encoding="utf-8"))


def load_latest_snapshot(artifacts_dir: Path) -> CanonicalSnapshot | None:
    """Load the most recent canonical snapshot from artifacts_dir, or None.

    Looks for files matching 'adg_graphsnap_*.json' (preferred, avoids
    collision with the Tier-1 CI snapshot) or the legacy 'adg_snapshot_*.json'
    pattern, sorted by name (timestamp suffix).
    """
    candidates = sorted(artifacts_dir.glob("adg_graphsnap_*.json"))
    if not candidates:
        candidates = sorted(artifacts_dir.glob("adg_snapshot_*.json"))
    if not candidates:
        return None
    return load_snapshot(candidates[-1])


def build_snapshot(result: ScanResult) -> CanonicalSnapshot:
    """Build a deterministic CanonicalSnapshot from a ScanResult.

    The graph_hash is derived solely from the sorted canonical edge list,
    making it reproducible given identical source code regardless of scan
    order or Python version.
    """
    from agentic_core.adg.extraction.static_scanner import (
        _SCANNER_VERSION,
        _SCHEMA_VERSION,
    )

    canonical_edges: list[tuple[str, str, str]] = sorted(
        {(e.from_name, e.relation_type, e.to_name) for e in result.edges},
    )
    canonical_nodes: list[str] = sorted(
        {e.from_name for e in result.edges} | {e.to_name for e in result.edges},
    )

    edge_payload = json.dumps(canonical_edges, sort_keys=True, separators=(",", ":"))
    graph_hash = hashlib.sha256(edge_payload.encode()).hexdigest()

    edge_counts = result.edge_counts_by_relation()

    return CanonicalSnapshot(
        graph_hash=graph_hash,
        scanner_hash=result.digest,
        schema_version=_SCHEMA_VERSION,
        scanner_version=_SCANNER_VERSION,
        commit_sha=result.commit_sha,
        node_count=len(canonical_nodes),
        edge_count=len(result.edges),
        violation_count=edge_counts.get("violates", 0),
        coverage_count=edge_counts.get("covers", 0),
        call_count=edge_counts.get("calls", 0),
        governance_count=edge_counts.get("writes_through", 0) + edge_counts.get("routes_through", 0),
        canonical_node_order=canonical_nodes,
        canonical_edge_order=canonical_edges,
        edge_counts_by_relation=edge_counts,
    )
