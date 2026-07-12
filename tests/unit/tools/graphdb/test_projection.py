"""Tests for lossless, directed GraphDB projection."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import networkx as nx
import pytest

from tools.graphdb.projection import GraphProjector


_NODE_INSERT = "INSERT INTO nodes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
_EDGE_INSERT = "INSERT INTO edges VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"


class TestGraphProjectorInit:
    def test_raises_on_missing_file(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            GraphProjector(tmp_path / "nonexistent.sqlite")

    def test_raises_on_missing_tables(self, tmp_path: Path):
        db = tmp_path / "empty.sqlite"
        with sqlite3.connect(db) as conn:
            conn.execute("CREATE TABLE foo (id TEXT)")
        with pytest.raises(ValueError, match="missing required canonical tables"):
            GraphProjector(db)

    def test_raises_on_missing_node_columns(self, tmp_path: Path):
        db = tmp_path / "partial.sqlite"
        with sqlite3.connect(db) as conn:
            conn.execute("CREATE TABLE nodes (id TEXT)")
            conn.execute(
                "CREATE TABLE edges ("
                "id TEXT, src_id TEXT, dst_id TEXT, relation_type TEXT, "
                "edge_kind TEXT, source_file TEXT, line_no INTEGER, "
                "symbol TEXT, semantic_type TEXT, confidence_score REAL)"
            )
            conn.execute("CREATE TABLE meta (key TEXT)")
        with pytest.raises(ValueError, match="nodes table missing columns"):
            GraphProjector(db)

    def test_raises_on_missing_edge_columns(self, tmp_path: Path):
        db = tmp_path / "partial2.sqlite"
        with sqlite3.connect(db) as conn:
            conn.execute(
                "CREATE TABLE nodes ("
                "id TEXT, entity_type TEXT, adg_name TEXT, layer TEXT, "
                "resolved_path TEXT, span_line INTEGER, enclosing_symbol TEXT, "
                "identity_kind TEXT, confidence REAL)"
            )
            conn.execute("CREATE TABLE edges (id TEXT)")
            conn.execute("CREATE TABLE meta (key TEXT)")
        with pytest.raises(ValueError, match="edges table missing columns"):
            GraphProjector(db)

    def test_accepts_valid_sqlite(self, minimal_sqlite: Path):
        assert GraphProjector(minimal_sqlite).sqlite_path == minimal_sqlite


class TestProjectGraph:
    def test_returns_directed_multigraph(self, minimal_sqlite: Path):
        graph = GraphProjector(minimal_sqlite).project_graph()
        assert isinstance(graph, nx.MultiDiGraph)
        assert graph.is_directed()
        assert graph.is_multigraph()

    def test_preserves_direction(self, minimal_sqlite: Path):
        graph = GraphProjector(minimal_sqlite).project_graph()
        assert graph.has_edge("mod_l0", "mod_l1")
        assert not graph.has_edge("mod_l1", "mod_l0")

    def test_loads_canonical_nodes_and_edges(self, minimal_sqlite: Path):
        graph = GraphProjector(minimal_sqlite).project_graph()
        assert set(graph.nodes) == {"mod_l0", "mod_l1"}
        assert graph.number_of_edges() == 1

    def test_node_has_required_attributes(self, minimal_sqlite: Path):
        attrs = GraphProjector(minimal_sqlite).project_graph().nodes["mod_l0"]
        assert attrs["adg_id"] == "mod_l0"
        assert attrs["adg_type"] == "module"
        assert attrs["graph_type"] == "Module"
        assert attrs["name"] == "router"
        assert attrs["mapping_status"] == "mapped"
        assert attrs["properties"]["layer"] == "L0"

    def test_edge_has_required_attributes(self, minimal_sqlite: Path):
        graph = GraphProjector(minimal_sqlite).project_graph()
        attrs = graph.edges["mod_l0", "mod_l1", "rel_001"]
        assert attrs["adg_type"] == "imports"
        assert attrs["graph_type"] == "IMPORTS"
        assert attrs["mapping_status"] == "mapped"
        assert attrs["properties"]["line_number"] == 5

    def test_unknown_entity_type_is_preserved(self, minimal_sqlite: Path):
        with sqlite3.connect(minimal_sqlite) as conn:
            conn.execute(
                _NODE_INSERT,
                (
                    "unknown", "totally_unknown_type_xyz", "unknown", None,
                    None, None, None, None, None,
                ),
            )
        graph = GraphProjector(minimal_sqlite).project_graph()
        assert graph.nodes["unknown"]["mapping_status"] == "unmapped"
        assert graph.nodes["unknown"]["graph_type"] == "UnmappedNode"

    def test_unknown_relation_type_is_preserved(self, minimal_sqlite: Path):
        with sqlite3.connect(minimal_sqlite) as conn:
            conn.execute(
                _EDGE_INSERT,
                (
                    "rel_unknown", "mod_l0", "mod_l1",
                    "totally_unknown_relation_xyz", "static", "router.py",
                    7, None, None, 1.0,
                ),
            )
        graph = GraphProjector(minimal_sqlite).project_graph()
        attrs = graph.edges["mod_l0", "mod_l1", "rel_unknown"]
        assert attrs["mapping_status"] == "unmapped"
        assert attrs["graph_type"] == "UNMAPPED_RELATION"

    def test_dangling_edge_fails_closed(self, minimal_sqlite: Path):
        with sqlite3.connect(minimal_sqlite) as conn:
            conn.execute(
                _EDGE_INSERT,
                (
                    "rel_bad", "mod_l0", "missing", "imports", "static",
                    "router.py", 9, None, None, 1.0,
                ),
            )
        with pytest.raises(RuntimeError, match="absent projected node"):
            GraphProjector(minimal_sqlite).project_graph()

    def test_parallel_edges_are_preserved(self, minimal_sqlite: Path):
        with sqlite3.connect(minimal_sqlite) as conn:
            conn.execute(
                _EDGE_INSERT,
                (
                    "rel_002", "mod_l0", "mod_l1", "imports", "runtime",
                    "router.py", 8, None, None, 0.8,
                ),
            )
        graph = GraphProjector(minimal_sqlite).project_graph()
        assert graph.number_of_edges("mod_l0", "mod_l1") == 2
        assert set(graph["mod_l0"]["mod_l1"]) == {"rel_001", "rel_002"}

    def test_relation_filter_preserves_edge_identity(self, minimal_sqlite: Path):
        graph = GraphProjector(minimal_sqlite).project_subgraph(
            relation_types=["imports"]
        )
        assert set(graph.edges(keys=True)) == {
            ("mod_l0", "mod_l1", "rel_001")
        }


class TestDeterministicRebuild:
    def test_same_input_same_output(self, minimal_sqlite: Path):
        g1 = GraphProjector(minimal_sqlite).project_graph()
        g2 = GraphProjector(minimal_sqlite).project_graph()
        assert set(g1.nodes()) == set(g2.nodes())
        assert set(g1.edges(keys=True)) == set(g2.edges(keys=True))
        for node in g1.nodes():
            assert g1.nodes[node] == g2.nodes[node]
        for src, dst, edge_key in g1.edges(keys=True):
            assert g1.edges[src, dst, edge_key] == g2.edges[
                src, dst, edge_key
            ]


class TestGraphStatistics:
    def test_statistics_report_directed_lossless_counts(
        self,
        minimal_sqlite: Path,
    ):
        stats = GraphProjector(minimal_sqlite).get_graph_statistics()
        assert stats["total_nodes"] == 2
        assert stats["total_edges"] == 1
        assert stats["is_directed"] is True
        assert stats["node_type_counts"]
        assert stats["edge_type_counts"]
        assert "average_clustering" in stats


class TestValidateProjection:
    def test_empty_graph_returns_warning(self, minimal_sqlite: Path):
        warnings = GraphProjector(minimal_sqlite).validate_projection(
            nx.MultiDiGraph()
        )
        assert any("no nodes" in warning for warning in warnings)

    def test_valid_projection_is_checked(self, minimal_sqlite: Path):
        projector = GraphProjector(minimal_sqlite)
        warnings = projector.validate_projection(projector.project_graph())
        assert isinstance(warnings, list)

    def test_missing_multiedge_attributes_include_key(
        self,
        minimal_sqlite: Path,
    ):
        projector = GraphProjector(minimal_sqlite)
        graph = nx.MultiDiGraph()
        graph.add_node(
            "a", adg_id="a", adg_type="module",
            graph_type="Module", name="a",
        )
        graph.add_node(
            "b", adg_id="b", adg_type="module",
            graph_type="Module", name="b",
        )
        graph.add_edge("a", "b", key="edge-1")
        warnings = projector.validate_projection(graph)
        assert any("key='edge-1'" in warning for warning in warnings)
