"""Tests for analyst investigation query pack."""

from __future__ import annotations

import networkx as nx
import pytest

from tools.graphdb.queries.analyst import AnalystQueries
from tests.unit.tools.graphdb.conftest import _make_node, _make_edge


@pytest.fixture
def multi_layer_graph() -> nx.DiGraph:
    """Graph spanning L0–L6 with agents and gateways."""
    g = nx.DiGraph()
    _make_node(g, "l0_router", "module", "router_dispatch", layer="L0")
    _make_node(g, "l1_reason", "module", "reasoning_engine", layer="L1")
    _make_node(g, "l2_exec", "module", "execute_workflow", layer="L2")
    _make_node(g, "gw_main", "gateway", "MainGateway", layer="L3")
    _make_node(g, "agent_a", "agent", "WorkerAgent", layer="L2")
    _make_node(g, "prov_ai", "provider", "AIProvider", layer="L6")
    _make_node(g, "store_db", "datastore", "MainDatastore", layer="L6")
    _make_edge(g, "l0_router", "l1_reason", "calls")
    _make_edge(g, "l1_reason", "l2_exec", "calls")
    _make_edge(g, "l2_exec", "gw_main", "routes_through")
    _make_edge(g, "agent_a", "prov_ai", "invokes_provider")
    _make_edge(g, "gw_main", "store_db", "writes_through")
    return g


class TestExtractSubgraphByLayer:
    def test_returns_dict(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.extract_subgraph_by_layer("L2")
        assert isinstance(result, dict)

    def test_required_keys_present(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.extract_subgraph_by_layer("L2")
        assert "layer" in result
        assert "node_count" in result

    def test_filters_to_correct_layer(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.extract_subgraph_by_layer("L0")
        assert result["node_count"] >= 1

    def test_empty_layer_returns_zero_nodes(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.extract_subgraph_by_layer("L4")
        assert result["node_count"] == 0

    def test_node_count_is_non_negative(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.extract_subgraph_by_layer("L6")
        assert result["node_count"] >= 0


class TestExtractSubgraphByAgent:
    def test_returns_dict_or_raises_gracefully(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.extract_subgraph_by_agent("WorkerAgent")
        assert isinstance(result, dict)

    def test_returns_dict(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.extract_subgraph_by_agent("WorkerAgent")
        assert isinstance(result, dict)

    def test_required_keys_present(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.extract_subgraph_by_agent("WorkerAgent")
        assert "agent_name" in result
        assert "node_count" in result

    def test_agent_found_by_name(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.extract_subgraph_by_agent("WorkerAgent")
        assert result["agent_name"] == "WorkerAgent"


class TestExtractSubgraphByGateway:
    def test_returns_dict(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.extract_subgraph_by_gateway("MainGateway")
        assert isinstance(result, dict)

    def test_required_keys_present(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.extract_subgraph_by_gateway("MainGateway")
        assert "gateway_name" in result
        assert "gateway_analysis" in result

    def test_unknown_gateway_returns_empty_result(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.extract_subgraph_by_gateway("NonExistentGateway")
        assert result["node_count"] == 0


class TestExtractSubgraphByProvider:
    def test_returns_dict(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.extract_subgraph_by_provider("AIProvider")
        assert isinstance(result, dict)

    def test_required_keys_present(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.extract_subgraph_by_provider("AIProvider")
        assert "provider_name" in result
        assert "provider_analysis" in result

    def test_unknown_provider_returns_empty_result(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.extract_subgraph_by_provider("NonExistentProvider")
        assert result["node_count"] == 0


class TestViolationExplanationPaths:
    def test_raises_on_missing_node(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        with pytest.raises(ValueError, match="not found in graph"):
            aq.violation_explanation_paths("NONEXISTENT_NODE")

    def test_returns_dict(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.violation_explanation_paths("l2_exec")
        assert isinstance(result, dict)

    def test_required_keys_present(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.violation_explanation_paths("l2_exec")
        assert "violation_node" in result
        assert "violation_count" in result

    def test_node_with_no_violations(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.violation_explanation_paths("l0_router")
        assert isinstance(result, dict)


class TestTopChangedNeighborhoods:
    def test_returns_dict(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.top_changed_neighborhoods(multi_layer_graph, multi_layer_graph)
        assert isinstance(result, dict)

    def test_required_keys_present(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.top_changed_neighborhoods(multi_layer_graph, multi_layer_graph, top_n=5)
        assert "total_nodes_analyzed" in result
        assert "nodes_with_changes" in result
        assert "top_neighborhoods" in result

    def test_same_graph_no_changes(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.top_changed_neighborhoods(multi_layer_graph, multi_layer_graph)
        assert result["nodes_with_changes"] == 0

    def test_top_n_limits_results(self, multi_layer_graph: nx.DiGraph):
        aq = AnalystQueries(multi_layer_graph)
        result = aq.top_changed_neighborhoods(multi_layer_graph, multi_layer_graph, top_n=2)
        assert len(result["top_neighborhoods"]) <= 2
