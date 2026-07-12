"""Enhancement 6: Deterministic graph snapshotting.

Produces a canonical, replayable snapshot from a ScanResult that is:
- Fully deterministic (same repo state → same hash)
- Ordered (canonical node and edge ordering)
- Self-describing (schema_version, scanner_version, counts)
- Serializable to dict / JSON
"""

from __future__ import annotations

import gzip
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
        graph_hash: SHA-256 over canonical nodes and lossless edge occurrences.
        graph_hash_version: Versioned hashing contract for compatibility.
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
        canonical_edge_order: compatibility list of unique (from, relation, to) tuples.
        canonical_edge_occurrences: sorted, lossless occurrence tuples used for hashing.
        edge_counts_by_relation: per-relation breakdown.
        commit_sha: originating commit SHA (may be empty).
    """

    graph_hash: str = ""
    graph_hash_version: str = "edge-occurrence-v2"
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
    canonical_edge_occurrences: list[tuple] = field(default_factory=list)
    edge_counts_by_relation: dict[str, int] = field(default_factory=dict)
    commit_sha: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "graph_hash": self.graph_hash,
            "graph_hash_version": self.graph_hash_version,
            "scanner_hash": self.scanner_hash,
            "schema_version": self.schema_version,
            "scanner_version": self.scanner_version,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "violation_count": self.violation_count,
            "coverage_count": self.coverage_count,
            "call_count": self.call_count,
            "governance_count": self.governance_count,
            "canonical_node_order": self.canonical_node_order,
            "canonical_edge_order": self.canonical_edge_order,
            "canonical_edge_occurrences": self.canonical_edge_occurrences,
            "edge_counts_by_relation": self.edge_counts_by_relation,
            "commit_sha": self.commit_sha,
        }

    @classmethod
    def from_dict(cls, d: dict) -> CanonicalSnapshot:
        """Create from dictionary."""
        # Convert lists back to tuples for canonical_edge_order
        edge_order = d.get("canonical_edge_order", [])
        edge_order_tuples = [tuple(e) if isinstance(e, list) else e for e in edge_order]
        occurrences = d.get("canonical_edge_occurrences", [])
        occurrence_tuples = [tuple(e) if isinstance(e, list) else e for e in occurrences]

        return cls(
            graph_hash=d["graph_hash"],
            graph_hash_version=d.get("graph_hash_version", "triple-set-v1"),
            scanner_hash=d.get("scanner_hash", ""),
            schema_version=d.get("schema_version", ""),
            scanner_version=d.get("scanner_version", ""),
            node_count=d["node_count"],
            edge_count=d["edge_count"],
            violation_count=d.get("violation_count", 0),
            coverage_count=d.get("coverage_count", 0),
            call_count=d.get("call_count", 0),
            governance_count=d.get("governance_count", 0),
            canonical_node_order=d.get("canonical_node_order", []),
            canonical_edge_order=edge_order_tuples,
            canonical_edge_occurrences=occurrence_tuples,
            edge_counts_by_relation=d.get("edge_counts_by_relation", {}),
            commit_sha=d.get("commit_sha", ""),
        )

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, s: str) -> CanonicalSnapshot:
        return cls.from_dict(json.loads(s))


def save_snapshot(snapshot: CanonicalSnapshot, path: Path, compress: bool = True) -> None:
    """Persist a CanonicalSnapshot to disk as JSON (optionally gzipped).

    Args:
        snapshot: The snapshot to save
        path: Destination path (should end in .json or .json.gz)
        compress: Whether to use gzip compression (default: True for 5-10x size reduction)
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    json_data = snapshot.to_json()

    if compress:
        # Use .json.gz extension if not already specified
        gz_path = path if path.suffix == ".gz" else path.with_suffix(path.suffix + ".gz")
        with gzip.open(gz_path, "wt", encoding="utf-8") as f:
            f.write(json_data)
    else:
        path.write_text(json_data, encoding="utf-8")


def load_snapshot(path: Path) -> CanonicalSnapshot:
    """Load a CanonicalSnapshot from a JSON file on disk (handles .json.gz)."""
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as f:
            json_data = f.read()
    else:
        json_data = path.read_text(encoding="utf-8")
    return CanonicalSnapshot.from_json(json_data)


def load_latest_snapshot(artifacts_dir: Path) -> CanonicalSnapshot | None:
    """Load the most recent canonical snapshot from artifacts_dir, or None.

    Looks for files matching 'adg_graphsnap_*.json.gz' (compressed)
    or 'adg_graphsnap_*.json' (uncompressed), sorted by name
    (timestamp suffix).
    """
    # Try compressed files first (preferred)
    candidates = sorted(artifacts_dir.glob("adg_graphsnap_*.json.gz"))
    if not candidates:
        # Fall back to uncompressed
        candidates = sorted(artifacts_dir.glob("adg_graphsnap_*.json"))
    if not candidates:
        return None
    return load_snapshot(candidates[-1])


def build_snapshot(result: ScanResult) -> CanonicalSnapshot:
    """Build a deterministic, lossless CanonicalSnapshot from a ScanResult.

    The v2 graph hash includes every declared module and every edge occurrence,
    including edge kind, source location, symbol, semantic fields, confidence,
    spans, and dynamic-resolution evidence.  The compatibility triple list is
    retained for older GraphDiff consumers, but it is no longer the hash input.
    """
    from agentic_core.adg.extraction.static_scanner import (
        _SCANNER_VERSION,
        _SCHEMA_VERSION,
    )

    edge_triples: set[tuple[str, str, str]] = set()
    edge_occurrences: list[tuple] = []
    node_set: set[str] = set(result.modules)
    edge_counts: dict[str, int] = {}

    for e in result.edges:
        edge_triples.add((e.from_name, e.relation_type, e.to_name))
        node_set.add(e.from_name)
        node_set.add(e.to_name)
        edge_counts[e.relation_type] = edge_counts.get(e.relation_type, 0) + 1
        edge_occurrences.append(
            (
                e.from_name,
                e.relation_type,
                e.to_name,
                e.edge_kind,
                e.source_file,
                int(e.line_no),
                e.symbol,
                e.semantic_type,
                format(float(e.confidence), ".17g"),
                int(e.source_span_start),
                int(e.source_span_end),
                int(e.source_span_line),
                int(e.source_span_column),
                int(e.target_span_start),
                int(e.target_span_end),
                int(e.target_span_line),
                int(e.target_span_column),
                e.dynamic_resolution,
            )
        )

    canonical_edges = sorted(edge_triples)
    canonical_occurrences = sorted(edge_occurrences)
    canonical_nodes = sorted(node_set)

    hash_payload = json.dumps(
        {"nodes": canonical_nodes, "edge_occurrences": canonical_occurrences},
        sort_keys=True,
        separators=(",", ":"),
    )
    graph_hash = hashlib.sha256(hash_payload.encode()).hexdigest()

    return CanonicalSnapshot(
        graph_hash=graph_hash,
        graph_hash_version="edge-occurrence-v2",
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
        canonical_edge_occurrences=canonical_occurrences,
        edge_counts_by_relation=edge_counts,
    )
