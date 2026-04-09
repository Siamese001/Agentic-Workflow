"""Tests for graphdb projection — deterministic rebuild and correctness."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import networkx as nx
import pytest

from tools.graphdb.projection import GraphProjector


class TestGraphProjectorInit:
    def test_raises_on_missing_file(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            GraphProjector(tmp_path / "nonexistent.sqlite")

    def test_raises_on_missing_tables(self, tmp_path: Path):
        db = tmp_path / "empty.sqlite"
        with sqlite3.connect(db) as conn:
            conn.execute("CREATE TABLE foo (id TEXT)")
        with pytest.raises(ValueError, match="missing required tables"):
            GraphProjector(db)

    def test_raises_on_missing_entity_columns(self, tmp_path: Path):
        db = tmp_path / "partial.sqlite"
        with sqlite3.connect(db) as conn:
            conn.execute("CREATE TABLE entities (id TEXT)")
            conn.execute(
                "CREATE TABLE relations (id TEXT, from_id TEXT, to_id TEXT, type TEXT, properties TEXT)"
            )
            conn.execute("CREATE TABLE metadata (key TEXT)")
        with pytest.raises(ValueError, match="entities table missing columns"):
            GraphProjector(db)

    def test_raises_on_missing_relation_columns(self, tmp_path: Path):
        db = tmp_path / "partial2.sqlite"
        with sqlite3.connect(db) as conn:
            conn.execute("CREATE TABLE entities (id TEXT, type TEXT, name TEXT, properties TEXT)")
            conn.execute("CREATE TABLE relations (id TEXT)")
            conn.execute("CREATE TABLE metadata (key TEXT)")
        with pytest.raises(ValueError, match="relations table missing columns"):
            GraphProjector(db)

    def test_accepts_valid_sqlite(self, minimal_sqlite: Path):
        projector = GraphProjector(minimal_sqlite)
        assert projector.sqlite_path == minimal_sqlite


class TestProjectGraph:
    def test_returns_networkx_graph(self, minimal_sqlite: Path):
        graph = GraphProjector(minimal_sqlite).project_graph()
        assert isinstance(graph, nx.Graph)

    def test_nodes_loaded_from_entities(self, minimal_sqlite: Path):
        graph = GraphProjector(minimal_sqlite).project_graph()
        assert graph.number_of_nodes() == 2
        assert "mod_l0" in graph
        assert "mod_l1" in graph

    def test_edges_loaded_from_relations(self, minimal_sqlite: Path):
        graph = GraphProjector(minimal_sqlite).project_graph()
        assert graph.number_of_edges() == 1

    def test_node_has_required_attributes(self, minimal_sqlite: Path):
        graph = GraphProjector(minimal_sqlite).project_graph()
        attrs = graph.nodes["mod_l0"]
        assert attrs["adg_id"] == "mod_l0"
        assert attrs["adg_type"] == "module"
        assert attrs["graph_type"] == "Module"
        assert attrs["name"] == "router"

    def test_edge_has_required_attributes(self, minimal_sqlite: Path):
        graph = GraphProjector(minimal_sqlite).project_graph()
        edge_attrs = graph.edges["mod_l0", "mod_l1"]
        assert edge_attrs["adg_type"] == "imports"
        assert edge_attrs["graph_type"] == "IMPORTS"

    def test_properties_preserved_on_node(self, minimal_sqlite: Path):
        graph = GraphProjector(minimal_sqlite).project_graph()
        assert graph.nodes["mod_l0"]["properties"]["layer"] == "L0"

    def test_properties_preserved_on_edge(self, minimal_sqlite: Path):
        graph = GraphProjector(minimal_sqlite).project_graph()
        edge_props = graph.edges["mod_l0", "mod_l1"]["properties"]
        assert edge_props["line_number"] == 5

    def test_unknown_entity_type_skipped(self, tmp_path: Path):
        db = tmp_path / "unknown_type.sqlite"
        with sqlite3.connect(db) as conn:
            conn.execute("CREATE TABLE entities (id TEXT, type TEXT, name TEXT, properties TEXT)")
            conn.execute(
                "CREATE TABLE relations (id TEXT, from_id TEXT, to_id TEXT, type TEXT, properties TEXT)"
            )
            conn.execute("CREATE TABLE metadata (key TEXT, value TEXT)")
            conn.execute("INSERT INTO entities VALUES (?, ?, ?, ?)", ("n1", "module", "mod", json.dumps({})))
            conn.execute(
                "INSERT INTO entities VALUES (?, ?, ?, ?)",
                ("n2", "totally_unknown_type_xyz", "unk", json.dumps({})),
            )
        graph = GraphProjector(db).project_graph()
        assert "n1" in graph
        assert "n2" not in graph

    def test_edge_skipped_if_node_missing(self, tmp_path: Path):
        db = tmp_path / "missing_node.sqlite"
        with sqlite3.connect(db) as conn:
            conn.execute("CREATE TABLE entities (id TEXT, type TEXT, name TEXT, properties TEXT)")
            conn.execute(
                "CREATE TABLE relations (id TEXT, from_id TEXT, to_id TEXT, type TEXT, properties TEXT)"
            )
            conn.execute("CREATE TABLE metadata (key TEXT, value TEXT)")
            conn.execute("INSERT INTO entities VALUES (?, ?, ?, ?)", ("n1", "module", "mod", json.dumps({})))
            conn.execute(
                "INSERT INTO relations VALUES (?, ?, ?, ?, ?)",
                ("r1", "n1", "missing_node", "imports", json.dumps({})),
            )
        graph = GraphProjector(db).project_graph()
        assert graph.number_of_edges() == 0


class TestDeterministicRebuild:
    def test_same_input_same_output(self, minimal_sqlite: Path):
        """Same canonical artifact must produce identical graphs on repeated projection."""
        g1 = GraphProjector(minimal_sqlite).project_graph()
        g2 = GraphProjector(minimal_sqlite).project_graph()
        assert set(g1.nodes()) == set(g2.nodes())
        assert set(g1.edges()) == set(g2.edges())

    def test_node_attributes_stable_across_runs(self, minimal_sqlite: Path):
        g1 = GraphProjector(minimal_sqlite).project_graph()
        g2 = GraphProjector(minimal_sqlite).project_graph()
        for node in g1.nodes():
            assert g1.nodes[node] == g2.nodes[node]

    def test_edge_attributes_stable_across_runs(self, minimal_sqlite: Path):
        g1 = GraphProjector(minimal_sqlite).project_graph()
        g2 = GraphProjector(minimal_sqlite).project_graph()
        for u, v in g1.edges():
            assert g1.edges[u, v] == g2.edges[u, v]


class TestGraphStatistics:
    def test_returns_dict_with_expected_keys(self, minimal_sqlite: Path):
        stats = GraphProjector(minimal_sqlite).get_graph_statistics()
        expected_keys = {
            "total_nodes",
            "total_edges",
            "node_type_counts",
            "edge_type_counts",
            "density",
            "average_clustering",
            "num_connected_components",
            "largest_component_size",
            "is_directed",
        }
        assert expected_keys.issubset(set(stats.keys()))

    def test_node_count_matches(self, minimal_sqlite: Path):
        stats = GraphProjector(minimal_sqlite).get_graph_statistics()
        assert stats["total_nodes"] == 2

    def test_edge_count_matches(self, minimal_sqlite: Path):
        stats = GraphProjector(minimal_sqlite).get_graph_statistics()
        assert stats["total_edges"] == 1

    def test_node_type_counts_non_empty(self, minimal_sqlite: Path):
        stats = GraphProjector(minimal_sqlite).get_graph_statistics()
        assert len(stats["node_type_counts"]) > 0


class TestValidateProjection:
    def test_empty_graph_returns_warning(self, minimal_sqlite: Path):
        projector = GraphProjector(minimal_sqlite)
        empty = nx.DiGraph()
        warnings = projector.validate_projection(empty)
        assert any("no nodes" in w for w in warnings)

    def test_valid_graph_may_return_empty_warnings(self, minimal_sqlite: Path):
        projector = GraphProjector(minimal_sqlite)
        graph = projector.project_graph()
        warnings = projector.validate_projection(graph)
        assert isinstance(warnings, list)
