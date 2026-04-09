"""Shared fixtures for graphdb tests."""

from __future__ import annotations

import json
import sqlite3
import tempfile
from pathlib import Path

import networkx as nx
import pytest

from tools.graphdb.schema import NODE_TYPE_MAPPING, EDGE_TYPE_MAPPING
from tools.graphdb.snapshot import SnapshotManager, SnapshotMetadata


# ---------------------------------------------------------------------------
# Graph fixtures
# ---------------------------------------------------------------------------


def _make_node(graph: nx.DiGraph, node_id: str, adg_type: str, name: str, **props) -> None:
    """Helper to add a typed node."""
    graph_type = NODE_TYPE_MAPPING.get(adg_type, adg_type)
    graph.add_node(
        node_id,
        adg_id=node_id,
        adg_type=adg_type,
        graph_type=graph_type,
        name=name,
        properties=props,
    )


def _make_edge(graph: nx.DiGraph, u: str, v: str, adg_type: str, **props) -> None:
    """Helper to add a typed edge."""
    graph_type = EDGE_TYPE_MAPPING.get(adg_type, adg_type)
    graph.add_edge(u, v, adg_type=adg_type, graph_type=graph_type, properties=props)


@pytest.fixture
def minimal_graph() -> nx.DiGraph:
    """Minimal directed graph with one node of each core type."""
    g = nx.DiGraph()
    _make_node(g, "mod_l0", "module", "router_module", layer="L0")
    _make_node(g, "mod_l1", "module", "reasoning_module", layer="L1")
    _make_node(g, "mod_l2", "module", "execute_module", layer="L2")
    _make_node(g, "gw_uwg", "gateway", "UWGGateway", layer="L3")
    _make_node(g, "agent_a", "agent", "WorkerAgent", layer="L2")
    _make_node(g, "tool_t", "tool", "SearchTool", layer="L3")
    _make_node(g, "prov_p", "provider", "OpenAIProvider", layer="L6")
    _make_edge(g, "mod_l0", "mod_l1", "imports")
    _make_edge(g, "mod_l1", "mod_l2", "calls")
    _make_edge(g, "mod_l2", "gw_uwg", "writes_through")
    return g


@pytest.fixture
def gravity_violation_graph() -> nx.DiGraph:
    """Graph with a gravity import violation (lower layer imports higher layer)."""
    g = nx.DiGraph()
    _make_node(g, "mod_l0", "module", "l0_module", layer="L0")
    _make_node(g, "mod_l3", "module", "l3_module", layer="L3")
    _make_edge(g, "mod_l0", "mod_l3", "imports")
    return g


@pytest.fixture
def illegal_reach_graph() -> nx.DiGraph:
    """Graph with a forbidden layer transition."""
    g = nx.DiGraph()
    _make_node(g, "infra", "module", "infra_module", layer="L6")
    _make_node(g, "exec_", "module", "exec_module", layer="L2")
    _make_edge(g, "infra", "exec_", "imports")
    return g


@pytest.fixture
def clean_graph() -> nx.DiGraph:
    """Graph with no violations — L6 imports L5 (higher imports lower = ok)."""
    g = nx.DiGraph()
    _make_node(g, "mod_l5", "module", "safety_module", layer="L5")
    _make_node(g, "mod_l6", "module", "infra_module", layer="L6")
    _make_edge(g, "mod_l6", "mod_l5", "imports")
    return g


@pytest.fixture
def uwg_graph() -> nx.DiGraph:
    """Graph testing UWG write conformance."""
    g = nx.DiGraph()
    _make_node(g, "gw_uwg", "gateway", "UWGGateway")
    _make_node(g, "writer_ok", "module", "ok_writer")
    _make_node(g, "writer_bad", "module", "bad_writer")
    _make_node(g, "store", "datastore", "PrimaryStore")
    _make_edge(g, "writer_ok", "store", "writes_through")
    _make_edge(g, "writer_bad", "store", "writes_to")
    return g


@pytest.fixture
def snapshot_manager(tmp_path: Path) -> SnapshotManager:
    """SnapshotManager backed by a temp directory."""
    return SnapshotManager(tmp_path / "graphdb")


@pytest.fixture
def sample_metadata(minimal_graph: nx.DiGraph) -> SnapshotMetadata:
    """A deterministic SnapshotMetadata instance."""
    return SnapshotMetadata(
        commit_sha="abc123def456abc123def456abc123def456abc1",
        repo_state_hash="tree_hash_0001",
        schema_version="1.0",
        scanner_digest="scanner_digest_0001",
        artifact_digest="artifact_digest_0001",
        run_id="graphdb_20260101_000000",
        timestamp="2026-01-01T00:00:00Z",
        scanner_version="0.1.0",
        node_count=minimal_graph.number_of_nodes(),
        edge_count=minimal_graph.number_of_edges(),
    )


@pytest.fixture
def minimal_sqlite(tmp_path: Path) -> Path:
    """Minimal ADG SQLite file with required schema for projection tests."""
    db_path = tmp_path / "test_adg.sqlite"
    with sqlite3.connect(db_path) as conn:
        conn.execute("CREATE TABLE entities (id TEXT PRIMARY KEY, type TEXT, name TEXT, properties TEXT)")
        conn.execute(
            "CREATE TABLE relations (id TEXT PRIMARY KEY, from_id TEXT, to_id TEXT, type TEXT, properties TEXT)"
        )
        conn.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT)")
        conn.execute(
            "INSERT INTO entities VALUES (?, ?, ?, ?)",
            ("mod_l0", "module", "router", json.dumps({"layer": "L0"})),
        )
        conn.execute(
            "INSERT INTO entities VALUES (?, ?, ?, ?)",
            ("mod_l1", "module", "reasoner", json.dumps({"layer": "L1"})),
        )
        conn.execute(
            "INSERT INTO relations VALUES (?, ?, ?, ?, ?)",
            ("rel_001", "mod_l0", "mod_l1", "imports", json.dumps({"line_number": 5})),
        )
        conn.commit()
    return db_path
