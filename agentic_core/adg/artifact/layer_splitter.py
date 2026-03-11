"""ADG Layer Splitter — separate graph planes for targeted consumers.

Splits the monolithic ADGArtifact into four independent sub-graphs that
consumers can load selectively. This avoids loading 57 MB when you only
need test coverage edges.

Sub-graphs
----------
file_graph
    Node type: module only.
    Edge types: imports, belongs_to_layer, covers (module→module only).
    Consumer: CI import validation, layer boundary checks, ownership queries.

symbol_graph
    Node types: module + symbol.
    Edge types: calls, instantiates, implements, reads_from, writes_to,
                writes_through, invokes_provider, routes_through.
    Consumer: blast-radius, rename-safety, mutation-authority.

test_graph
    Node types: module (test + non-test).
    Edge types: covers, covers_module.
    Consumer: test-gap detection, blast-radius for test coverage.

governance_graph
    Node types: all (including prompt_slot, execution_trace, agent_action, etc.)
    Edge types: generates_prompt, consumes_prompt, assembles_into, injects_into,
                overrides_prompt, executed_with_prompt, triggered_telemetry,
                executes_action, invokes_tool, crosses_layer, bypasses_uwg,
                routes_through_uwg, layer_authority_violation, policy_hash_mismatch,
                lineage_of, violates, dynamic_exec.
    Consumer: P3+P6+P7 analysis modules — layer authority, mutation paths, policy hash.

Each sub-graph is a NormalizedGraph (compact node/edge format).

Usage::

    from agentic_core.adg.artifact.layer_splitter import split_artifact

    planes = split_artifact(artifact)
    planes.file_graph.write(out_dir / "adg_file_graph.json")
    planes.symbol_graph.write(out_dir / "adg_symbol_graph.json")
    planes.test_graph.write(out_dir / "adg_test_graph.json")
    planes.governance_graph.write(out_dir / "adg_governance_graph.json")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from agentic_core.adg.artifact.normalizer import NormalizedGraph

if TYPE_CHECKING:
    from agentic_core.adg.artifact.builder import ADGArtifact

# ---------------------------------------------------------------------------
# Edge-type sets per plane
# ---------------------------------------------------------------------------

_FILE_GRAPH_RELS: frozenset[str] = frozenset(
    {
        "imports",
        "belongs_to_layer",
        "covers",
        "in_cycle",
        "dead_imports",
    }
)

_SYMBOL_GRAPH_RELS: frozenset[str] = frozenset(
    {
        "calls",
        "instantiates",
        "implements",
        "reads_from",
        "writes_to",
        "writes_through",
        "invokes_provider",
        "routes_through",
        "type_annotation",
        "decorated_by",
    }
)

_TEST_GRAPH_RELS: frozenset[str] = frozenset(
    {
        "covers",
        "covers_module",
        "covers_symbol",
    }
)

_GOVERNANCE_GRAPH_RELS: frozenset[str] = frozenset(
    {
        # P6 prompt
        "generates_prompt",
        "consumes_prompt",
        "assembles_into",
        "injects_into",
        "overrides_prompt",
        "executed_with_prompt",
        "triggered_telemetry",
        "proposed_improvement",
        "updated_prompt",
        # P3 runtime/authority/mutation
        "executes_action",
        "invokes_tool",
        "crosses_layer",
        "bypasses_uwg",
        "routes_through_uwg",
        "layer_authority_violation",
        "policy_hash_mismatch",
        "lineage_of",
        # Existing violation/governance
        "violates",
        "dynamic_exec",
        "in_cycle",
    }
)

_TEST_PATH_MARKERS: tuple[str, ...] = ("tests/", "test_", "_test.py")


def _is_test_module(adg_name: str) -> bool:
    n = adg_name.lower()
    return any(m in n for m in _TEST_PATH_MARKERS)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class SplitArtifact:
    """Container for all four graph plane sub-artifacts."""

    file_graph: NormalizedGraph = field(default_factory=NormalizedGraph)
    symbol_graph: NormalizedGraph = field(default_factory=NormalizedGraph)
    test_graph: NormalizedGraph = field(default_factory=NormalizedGraph)
    governance_graph: NormalizedGraph = field(default_factory=NormalizedGraph)

    def write_all(self, out_dir: Path) -> dict[str, Path]:
        """Write all four planes to out_dir. Returns {plane: path}."""
        out_dir.mkdir(parents=True, exist_ok=True)
        paths = {}
        for plane, graph, fname in (
            ("file_graph", self.file_graph, "adg_file_graph.json"),
            ("symbol_graph", self.symbol_graph, "adg_symbol_graph.json"),
            ("test_graph", self.test_graph, "adg_test_graph.json"),
            ("governance_graph", self.governance_graph, "adg_governance_graph.json"),
        ):
            p = graph.write(out_dir / fname, indent=None)
            paths[plane] = p
        return paths

    def size_summary(self) -> dict[str, int]:
        return {
            plane: len(graph.to_json(indent=None).encode("utf-8"))
            for plane, graph in (
                ("file_graph", self.file_graph),
                ("symbol_graph", self.symbol_graph),
                ("test_graph", self.test_graph),
                ("governance_graph", self.governance_graph),
            )
        }


# ---------------------------------------------------------------------------
# Splitter
# ---------------------------------------------------------------------------


def _build_plane(
    artifact: ADGArtifact,
    rel_types: frozenset[str],
    *,
    node_type_filter: set[str] | None = None,
    plane_name: str = "",
) -> NormalizedGraph:
    """Build a NormalizedGraph containing only the specified relation types.

    Parameters
    ----------
    artifact:
        Source ADGArtifact.
    rel_types:
        Set of relation_type strings to include.
    node_type_filter:
        If given, only include entity nodes with these entity_type values.
        Nodes referenced by edges are always included regardless.
    plane_name:
        Label embedded in meta.plane.
    """
    # Step 1: filter edges
    selected_rels = [r for r in artifact.relations if r.relation_type in rel_types]

    # Step 2: collect referenced node names
    referenced: set[str] = set()
    for r in selected_rels:
        referenced.add(r.from_name)
        referenced.add(r.to_name)

    # Step 3: collect entity nodes
    entity_lookup: dict[str, object] = {e.adg_name: e for e in artifact.entities}

    # Build name → id mapping: entities first, then dangling references
    name_to_id: dict[str, int] = {}
    nodes: dict[str, dict] = {}

    def _register(name: str, ent=None) -> int:
        if name in name_to_id:
            return name_to_id[name]
        nid = len(name_to_id)
        name_to_id[name] = nid
        if ent is not None:
            nodes[str(nid)] = {
                "n": name,
                "t": ent.entity_type,
                "l": ent.layer,
                "k": ent.identity_kind,
                "c": ent.confidence,
                "p": ent.resolved_path,
            }
        else:
            # Dangling reference — minimal stub
            nodes[str(nid)] = {"n": name, "t": "symbol", "l": "", "k": "", "c": "", "p": ""}
        return nid

    # Register all entities that pass type filter
    for ent in sorted(artifact.entities, key=lambda e: e.adg_name):
        if node_type_filter and ent.entity_type not in node_type_filter:
            continue
        _register(ent.adg_name, ent)

    # Register dangling nodes from edges
    for name in sorted(referenced):
        if name not in name_to_id:
            ent = entity_lookup.get(name)
            _register(name, ent)

    # Step 4: compact edges
    edges: list[dict] = []
    for r in selected_rels:
        if r.from_name not in name_to_id or r.to_name not in name_to_id:
            continue
        e: dict = {
            "s": name_to_id[r.from_name],
            "d": name_to_id[r.to_name],
            "r": r.relation_type,
            "k": r.edge_kind,
            "f": r.source_file,
            "ln": r.line_no,
        }
        if r.symbol:
            e["sym"] = r.symbol
        edges.append(e)

    # Step 5: metrics
    by_rel: dict[str, int] = {}
    for e in edges:
        by_rel[e["r"]] = by_rel.get(e["r"], 0) + 1

    meta = {
        "plane": plane_name,
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "by_relation_type": dict(sorted(by_rel.items())),
    }

    ng = NormalizedGraph(
        commit_sha=artifact.commit_sha,
        scanner_digest=artifact.scanner_digest,
        nodes=nodes,
        edges=edges,
        meta=meta,
    )
    ng.compute_digest()
    return ng


def split_artifact(artifact: ADGArtifact) -> SplitArtifact:
    """Split an ADGArtifact into four focused graph planes.

    Returns a SplitArtifact with .file_graph, .symbol_graph, .test_graph,
    .governance_graph — each a compact NormalizedGraph.
    """
    file_graph = _build_plane(
        artifact,
        _FILE_GRAPH_RELS,
        node_type_filter={"module"},
        plane_name="file_graph",
    )
    symbol_graph = _build_plane(
        artifact,
        _SYMBOL_GRAPH_RELS,
        node_type_filter=None,  # include both module and symbol nodes
        plane_name="symbol_graph",
    )
    test_graph = _build_plane(
        artifact,
        _TEST_GRAPH_RELS,
        node_type_filter=None,
        plane_name="test_graph",
    )
    governance_graph = _build_plane(
        artifact,
        _GOVERNANCE_GRAPH_RELS,
        node_type_filter=None,
        plane_name="governance_graph",
    )
    return SplitArtifact(
        file_graph=file_graph,
        symbol_graph=symbol_graph,
        test_graph=test_graph,
        governance_graph=governance_graph,
    )


__all__ = [
    "SplitArtifact",
    "split_artifact",
    "_FILE_GRAPH_RELS",
    "_SYMBOL_GRAPH_RELS",
    "_TEST_GRAPH_RELS",
    "_GOVERNANCE_GRAPH_RELS",
]
