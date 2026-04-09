"""Tests for blast-radius query pack."""

from __future__ import annotations

import networkx as nx
import pytest

from tools.graphdb.queries.blast_radius import BlastRadiusQueries
from tests.unit.tools.graphdb.conftest import _make_node, _make_edge


@pytest.fixture
def chain_graph() -> nx.DiGraph:
    """Linear dependency chain: A → B → C → D."""
    g = nx.DiGraph()
    for node_id in ["A", "B", "C", "D"]:
        _make_node(g, node_id, "module", node_id.lower(), layer="L2")
    _make_edge(g, "A", "B", "imports")
    _make_edge(g, "B", "C", "imports")
    _make_edge(g, "C", "D", "imports")
    return g


@pytest.fixture
def gateway_graph() -> nx.DiGraph:
    """Source → Gateway → Target (and Source → Bypass → Target)."""
    g = nx.DiGraph()
    _make_node(g, "src", "module", "source_mod", layer="L2")
    _make_node(g, "gw", "gateway", "ApprovedGateway")
    _make_node(g, "bypass", "module", "bypass_mod", layer="L2")
    _make_node(g, "tgt", "datastore", "target_store")
    _make_edge(g, "src", "tgt", "writes_through")
    _make_edge(g, "src", "bypass", "calls")
    _make_edge(g, "bypass", "tgt", "writes_to")
    return g


class TestTransitiveDependents:
    def test_raises_on_missing_node(self, chain_graph: nx.DiGraph):
        bq = BlastRadiusQueries(chain_graph)
        with pytest.raises(ValueError, match="not found in graph"):
            bq.transitive_dependents("NONEXISTENT")

    def test_finds_all_upstream_dependents(self, chain_graph: nx.DiGraph):
        bq = BlastRadiusQueries(chain_graph)
        result = bq.transitive_dependents("D")
        assert result["total_dependents"] == 3
        assert "A" in result["dependents"]
        assert "B" in result["dependents"]
        assert "C" in result["dependents"]

    def test_leaf_node_has_no_dependents(self, chain_graph: nx.DiGraph):
        bq = BlastRadiusQueries(chain_graph)
        result = bq.transitive_dependents("A")
        assert result["total_dependents"] == 0

    def test_returns_required_keys(self, chain_graph: nx.DiGraph):
        result = BlastRadiusQueries(chain_graph).transitive_dependents("C")
        assert "source_node" in result
        assert "total_dependents" in result
        assert "dependents" in result
        assert "layers_affected" in result

    def test_depth_limits_traversal(self, chain_graph: nx.DiGraph):
        bq = BlastRadiusQueries(chain_graph)
        result = bq.transitive_dependents("D", max_depth=2)
        assert result["total_dependents"] <= 3

    def test_dependent_has_depth_and_path(self, chain_graph: nx.DiGraph):
        bq = BlastRadiusQueries(chain_graph)
        result = bq.transitive_dependents("D")
        for dep_info in result["dependents"].values():
            assert "depth" in dep_info
            assert "path" in dep_info
            assert "node_type" in dep_info


class TestShortestIllegalPath:
    def test_raises_on_missing_node(self, chain_graph: nx.DiGraph):
        bq = BlastRadiusQueries(chain_graph)
        with pytest.raises(ValueError, match="not found in graph"):
            bq.shortest_illegal_path("A", "NONEXISTENT")

    def test_returns_required_keys(self, chain_graph: nx.DiGraph):
        result = BlastRadiusQueries(chain_graph).shortest_illegal_path("A", "D")
        assert "source" in result
        assert "sink" in result
        assert "paths_found" in result
        assert "illegal_paths" in result
        assert "shortest_legal_path" in result

    def test_detects_gravity_violation_path(self):
        g = nx.DiGraph()
        _make_node(g, "l0", "module", "l0_mod", layer="L0")
        _make_node(g, "l3", "module", "l3_mod", layer="L3")
        _make_edge(g, "l0", "l3", "imports")
        result = BlastRadiusQueries(g).shortest_illegal_path("l0", "l3")
        assert result["has_illegal_path"] is True

    def test_no_path_returns_empty(self):
        g = nx.DiGraph()
        _make_node(g, "x", "module", "x_mod", layer="L2")
        _make_node(g, "y", "module", "y_mod", layer="L2")
        result = BlastRadiusQueries(g).shortest_illegal_path("x", "y")
        assert result["paths_found"] == 0


class TestBypassPaths:
    def test_raises_on_missing_gateway(self, minimal_graph: nx.DiGraph):
        bq = BlastRadiusQueries(minimal_graph)
        with pytest.raises(ValueError, match="not found in graph"):
            bq.bypass_paths("NONEXISTENT_GW")

    def test_raises_if_node_not_gateway_type(self, chain_graph: nx.DiGraph):
        bq = BlastRadiusQueries(chain_graph)
        with pytest.raises(ValueError, match="not a gateway"):
            bq.bypass_paths("A")

    def test_returns_list(self, gateway_graph: nx.DiGraph):
        result = BlastRadiusQueries(gateway_graph).bypass_paths("gw")
        assert isinstance(result, list)


class TestImpactAnalysis:
    @pytest.fixture
    def undirected_chain(self) -> nx.Graph:
        """Undirected chain for impact_analysis (uses connected_components)."""
        from tests.unit.tools.graphdb.conftest import _make_node, _make_edge

        g = nx.Graph()
        for node_id in ["A", "B", "C", "D"]:
            g.add_node(
                node_id,
                adg_id=node_id,
                adg_type="module",
                graph_type="Module",
                name=node_id.lower(),
                properties={"layer": "L2"},
            )
        g.add_edge("A", "B", adg_type="imports", graph_type="IMPORTS", properties={})
        g.add_edge("B", "C", adg_type="imports", graph_type="IMPORTS", properties={})
        g.add_edge("C", "D", adg_type="imports", graph_type="IMPORTS", properties={})
        return g

    def test_raises_on_missing_node(self, undirected_chain: nx.Graph):
        bq = BlastRadiusQueries(undirected_chain)
        with pytest.raises(ValueError, match="not found in graph"):
            bq.impact_analysis("NONEXISTENT")

    def test_returns_required_keys(self, undirected_chain: nx.Graph):
        result = BlastRadiusQueries(undirected_chain).impact_analysis("B")
        required = {
            "removed_node",
            "node_type",
            "impact_score",
            "impact_level",
            "impact_factors",
            "original_degree",
            "broken_dependencies",
            "isolated_nodes",
            "connectivity_change",
        }
        assert required.issubset(result.keys())

    def test_impact_level_valid_values(self, undirected_chain: nx.Graph):
        result = BlastRadiusQueries(undirected_chain).impact_analysis("B")
        assert result["impact_level"] in {"low", "medium", "high", "critical"}

    def test_hub_node_has_higher_impact_than_leaf(self, undirected_chain: nx.Graph):
        bq = BlastRadiusQueries(undirected_chain)
        hub_result = bq.impact_analysis("B")
        leaf_result = bq.impact_analysis("D")
        assert hub_result["impact_score"] >= leaf_result["impact_score"]

    def test_broken_dependencies_is_list(self, undirected_chain: nx.Graph):
        result = BlastRadiusQueries(undirected_chain).impact_analysis("B")
        assert isinstance(result["broken_dependencies"], list)


class TestHighFanInOutHubs:
    def test_returns_dict(self, minimal_graph: nx.DiGraph):
        result = BlastRadiusQueries(minimal_graph).high_fan_in_out_hubs()
        assert isinstance(result, dict)

    def test_required_keys_present(self, minimal_graph: nx.DiGraph):
        result = BlastRadiusQueries(minimal_graph).high_fan_in_out_hubs()
        assert "min_connections_threshold" in result
        assert "total_hubs" in result
        assert "hubs" in result

    def test_empty_graph_has_no_hubs(self):
        g = nx.DiGraph()
        result = BlastRadiusQueries(g).high_fan_in_out_hubs(min_connections=1)
        assert result["total_hubs"]["fan_in"] == 0
        assert result["total_hubs"]["fan_out"] == 0
        assert result["total_hubs"]["bidirectional"] == 0


class TestAffectedNeighborhoods:
    def test_returns_dict(self, chain_graph: nx.DiGraph):
        result = BlastRadiusQueries(chain_graph).affected_neighborhoods([("A", "B")])
        assert isinstance(result, dict)

    def test_required_keys_present(self, chain_graph: nx.DiGraph):
        result = BlastRadiusQueries(chain_graph).affected_neighborhoods([("A", "B")])
        assert "edge_additions_analyzed" in result
        assert "affected_areas" in result
        assert "total_violations" in result

    def test_skips_edges_with_missing_nodes(self, chain_graph: nx.DiGraph):
        result = BlastRadiusQueries(chain_graph).affected_neighborhoods([("A", "MISSING")])
        assert result["edge_additions_analyzed"] == 1
        assert result["affected_areas"] == []

    def test_empty_edge_list(self, chain_graph: nx.DiGraph):
        result = BlastRadiusQueries(chain_graph).affected_neighborhoods([])
        assert result["edge_additions_analyzed"] == 0
        assert result["affected_areas"] == []
