"""ADG Multi-Writer — produces all three artifact tiers in one pass.

Tier 1  adg_snapshot.json        CI-light, ~50 KB
    Metrics only: counts, digests, graph_plane_counts, violation summary,
    blind_spots, top-20 hotspots. No entities or edges.
    Used by: CI gate, drift detection, quick health checks.

Tier 2  adg_full.json            Canonical offline export, ~55 MB
    Full normalized format (NormalizedGraph v4.0.0) with all nodes and
    compact integer-indexed edges. Replaces the old verbose format.
    Used by: offline analysis, ADG CLI commands, all analysis modules.

Tier 3  adg_indexed.sqlite        Compact queryable store, ~8–12 MB
    SQLite database with three tables:
        nodes (id, adg_name, entity_type, layer, identity_kind, confidence, resolved_path)
        edges (id, src_id, dst_id, relation_type, edge_kind, source_file, line_no, symbol)
        meta  (key, value)
    Used by: state-lineage queries, layer-authority checks, mutation-path scans.

The four split-plane sub-graphs are written alongside:
    adg_file_graph.json
    adg_symbol_graph.json
    adg_test_graph.json
    adg_governance_graph.json

Usage::

    from agentic_core.adg.artifact.multi_writer import write_all_artifacts

    paths = write_all_artifacts(artifact, out_dir=Path("artifacts/adg"), ts="20260311T154637Z")
    print(paths)
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from agentic_core.adg.artifact.layer_splitter import split_artifact
from agentic_core.adg.artifact.normalizer import ArtifactNormalizer

if TYPE_CHECKING:
    from agentic_core.adg.artifact.builder import ADGArtifact


# ---------------------------------------------------------------------------
# Snapshot (Tier 1)
# ---------------------------------------------------------------------------


def _build_snapshot(artifact: ADGArtifact) -> dict:
    """Build a lightweight CI snapshot dict — no entities or edges."""
    sm = artifact.structural_metrics.to_dict()
    bs = artifact.blind_spots.to_dict()

    # Relation-type distribution
    by_rel = sm.get("by_relation_type", {})

    # Top-20 fan-in hotspots (module names only, no full edge data)
    hotspots_in = sorted(sm.get("high_fan_in_modules", []), key=lambda x: -x.get("fan_in", 0))[:20]
    hotspots_out = sorted(sm.get("high_fan_out_modules", []), key=lambda x: -x.get("fan_out", 0))[:20]

    return {
        "schema_version": "snapshot-1.0",
        "commit_sha": artifact.commit_sha,
        "scanner_digest": artifact.scanner_digest,
        "artifact_digest": artifact.artifact_digest,
        "counts": {
            "total_entities": sm.get("total_entities", 0),
            "total_relations": sm.get("total_relations", 0),
            "module_count": sm.get("module_count", 0),
            "symbol_count": sm.get("symbol_count", 0),
            "external_count": sm.get("external_count", 0),
            "unresolved_count": sm.get("unresolved_count", 0),
            "orphan_module_count": sm.get("orphan_module_count", 0),
            "layer_violation_count": sm.get("layer_violation_count", 0),
        },
        "graph_plane_counts": {
            k: v
            for k, v in by_rel.items()
            if k
            in (
                "imports",
                "calls",
                "implements",
                "writes_to",
                "writes_through",
                "covers",
                "violates",
                "invokes_provider",
                "routes_through",
                "generates_prompt",
                "bypasses_uwg",
            )
        },
        "by_layer": sm.get("by_layer", {}),
        "blind_spots": {
            "parse_failure_count": bs.get("parse_failure_count", 0),
            "dynamic_import_count": bs.get("dynamic_import_count", 0),
            "star_import_count": bs.get("star_import_count", 0),
        },
        "identity_health": artifact.identity_health,
        "top_fan_in_hotspots": hotspots_in,
        "top_fan_out_hotspots": hotspots_out,
    }


# ---------------------------------------------------------------------------
# SQLite index (Tier 3)
# ---------------------------------------------------------------------------

_DDL = """
CREATE TABLE IF NOT EXISTS nodes (
    id            INTEGER PRIMARY KEY,
    adg_name      TEXT NOT NULL,
    entity_type   TEXT NOT NULL,
    layer         TEXT NOT NULL,
    identity_kind TEXT NOT NULL,
    confidence    TEXT NOT NULL,
    resolved_path TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_nodes_type  ON nodes(entity_type);
CREATE INDEX IF NOT EXISTS idx_nodes_layer ON nodes(layer);
CREATE INDEX IF NOT EXISTS idx_nodes_name  ON nodes(adg_name);

CREATE TABLE IF NOT EXISTS edges (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    src_id        INTEGER NOT NULL REFERENCES nodes(id),
    dst_id        INTEGER NOT NULL REFERENCES nodes(id),
    relation_type TEXT NOT NULL,
    edge_kind     TEXT NOT NULL,
    source_file   TEXT NOT NULL,
    line_no       INTEGER NOT NULL,
    symbol        TEXT NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_edges_src  ON edges(src_id);
CREATE INDEX IF NOT EXISTS idx_edges_dst  ON edges(dst_id);
CREATE INDEX IF NOT EXISTS idx_edges_rel  ON edges(relation_type);

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def _write_sqlite(ng_full, db_path: Path) -> Path:
    """Write a NormalizedGraph to SQLite for fast querying."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(_DDL)

        # Insert nodes in bulk
        node_rows = []
        for nid_str, node in ng_full.nodes.items():
            node_rows.append((
                int(nid_str),
                node.get("n", ""),
                node.get("t", ""),
                node.get("l", ""),
                node.get("k", ""),
                node.get("c", ""),
                node.get("p", ""),
            ))
        conn.executemany(
            "INSERT OR REPLACE INTO nodes(id,adg_name,entity_type,layer,identity_kind,confidence,resolved_path) "
            "VALUES (?,?,?,?,?,?,?)",
            node_rows,
        )

        # Insert edges in bulk
        edge_rows = []
        for e in ng_full.edges:
            edge_rows.append((
                e["s"],
                e["d"],
                e["r"],
                e["k"],
                e["f"],
                e["ln"],
                e.get("sym", ""),
            ))
        conn.executemany(
            "INSERT INTO edges(src_id,dst_id,relation_type,edge_kind,source_file,line_no,symbol) "
            "VALUES (?,?,?,?,?,?,?)",
            edge_rows,
        )

        # Meta
        meta_rows = [
            ("schema_version", ng_full.schema_version),
            ("commit_sha", ng_full.commit_sha),
            ("scanner_digest", ng_full.scanner_digest),
            ("artifact_digest", ng_full.artifact_digest),
            ("total_nodes", str(len(ng_full.nodes))),
            ("total_edges", str(len(ng_full.edges))),
        ]
        conn.executemany("INSERT OR REPLACE INTO meta(key,value) VALUES (?,?)", meta_rows)

        conn.commit()
    finally:
        conn.close()

    return db_path


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


@dataclass
class ArtifactPaths:
    """Paths of all artifacts written by write_all_artifacts."""

    snapshot: Path
    full: Path
    sqlite: Path
    file_graph: Path
    symbol_graph: Path
    test_graph: Path
    governance_graph: Path

    def size_report(self) -> dict[str, str]:
        result = {}
        for name, path in (
            ("snapshot", self.snapshot),
            ("full", self.full),
            ("sqlite", self.sqlite),
            ("file_graph", self.file_graph),
            ("symbol_graph", self.symbol_graph),
            ("test_graph", self.test_graph),
            ("governance_graph", self.governance_graph),
        ):
            if path.exists():
                sz = path.stat().st_size
                result[name] = f"{sz / 1024:.0f} KB" if sz < 1_048_576 else f"{sz / 1_048_576:.1f} MB"
            else:
                result[name] = "missing"
        return result


def write_all_artifacts(
    artifact: ADGArtifact,
    out_dir: Path,
    *,
    ts: str = "",
    write_split_planes: bool = True,
    write_sqlite: bool = True,
) -> ArtifactPaths:
    """Write Tier 1 (snapshot), Tier 2 (full normalized), Tier 3 (sqlite)
    and four split-plane graphs to out_dir.

    Parameters
    ----------
    artifact:
        The fully-built ADGArtifact to serialize.
    out_dir:
        Target directory (will be created if missing).
    ts:
        Timestamp string for filenames, e.g. ``"20260311T154637Z"``.
        If empty, no timestamp suffix is added.
    write_split_planes:
        Whether to write the four plane sub-graphs.
    write_sqlite:
        Whether to write the SQLite index.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = f"_{ts}" if ts else ""

    # --- Tier 2: normalized full artifact ---
    normalizer = ArtifactNormalizer()
    ng_full = normalizer.normalize(artifact)
    full_path = out_dir / f"adg_full{suffix}.json"
    ng_full.write(full_path, indent=None)

    # --- Tier 1: lightweight snapshot ---
    snap_dict = _build_snapshot(artifact)
    snap_path = out_dir / f"adg_snapshot{suffix}.json"
    snap_path.write_text(json.dumps(snap_dict, sort_keys=True, indent=2), encoding="utf-8")

    # --- Tier 3: SQLite index ---
    sqlite_path = out_dir / f"adg_indexed{suffix}.sqlite"
    if write_sqlite:
        _write_sqlite(ng_full, sqlite_path)
    else:
        sqlite_path = out_dir / f"adg_indexed{suffix}.sqlite"  # path only, not written

    # --- Split planes ---
    file_graph_path = out_dir / f"adg_file_graph{suffix}.json"
    symbol_graph_path = out_dir / f"adg_symbol_graph{suffix}.json"
    test_graph_path = out_dir / f"adg_test_graph{suffix}.json"
    governance_graph_path = out_dir / f"adg_governance_graph{suffix}.json"

    if write_split_planes:
        planes = split_artifact(artifact)
        planes.file_graph.write(file_graph_path, indent=None)
        planes.symbol_graph.write(symbol_graph_path, indent=None)
        planes.test_graph.write(test_graph_path, indent=None)
        planes.governance_graph.write(governance_graph_path, indent=None)

    return ArtifactPaths(
        snapshot=snap_path,
        full=full_path,
        sqlite=sqlite_path,
        file_graph=file_graph_path,
        symbol_graph=symbol_graph_path,
        test_graph=test_graph_path,
        governance_graph=governance_graph_path,
    )


__all__ = [
    "ArtifactPaths",
    "write_all_artifacts",
]
