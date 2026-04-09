"""Tests for historical diff query pack."""

from __future__ import annotations

from pathlib import Path

import networkx as nx
import pytest

from tools.graphdb.queries.historical import HistoricalQueries
from tools.graphdb.snapshot import SnapshotManager, SnapshotMetadata
from tests.unit.tools.graphdb.conftest import _make_node, _make_edge


def _make_metadata(sha: str, timestamp: str, graph: nx.DiGraph) -> SnapshotMetadata:
    return SnapshotMetadata(
        commit_sha=sha,
        repo_state_hash=f"tree_{sha[:8]}",
        schema_version="1.0",
        scanner_digest="sd",
        artifact_digest="ad",
        run_id=f"run_{sha[:8]}",
        timestamp=timestamp,
        scanner_version="0.1.0",
        node_count=graph.number_of_nodes(),
        edge_count=graph.number_of_edges(),
    )


@pytest.fixture
def populated_manager(tmp_path: Path) -> SnapshotManager:
    """Manager with two saved snapshots: old and new."""
    mgr = SnapshotManager(tmp_path / "graphdb")

    old_graph = nx.DiGraph()
    _make_node(old_graph, "mod_a", "module", "mod_a", layer="L2")
    _make_node(old_graph, "mod_b", "module", "mod_b", layer="L3")
    _make_edge(old_graph, "mod_a", "mod_b", "calls")

    new_graph = nx.DiGraph()
    _make_node(new_graph, "mod_a", "module", "mod_a", layer="L2")
    _make_node(new_graph, "mod_b", "module", "mod_b", layer="L3")
    _make_node(new_graph, "mod_c", "module", "mod_c", layer="L4")
    _make_edge(new_graph, "mod_a", "mod_b", "calls")
    _make_edge(new_graph, "mod_a", "mod_c", "writes_to")

    mgr.save_snapshot(old_graph, _make_metadata("sha_old_0001", "2026-01-01T00:00:00Z", old_graph))
    mgr.save_snapshot(new_graph, _make_metadata("sha_new_0002", "2026-01-02T00:00:00Z", new_graph))

    return mgr


class TestHistoricalQueriesInit:
    def test_requires_snapshot_manager(self, snapshot_manager: SnapshotManager):
        hq = HistoricalQueries(snapshot_manager)
        assert hq.snapshot_manager is snapshot_manager


class TestNewForbiddenEdges:
    def test_returns_list(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        result = hq.new_forbidden_edges("sha_old_0001", "sha_new_0002")
        assert isinstance(result, list)

    def test_raises_on_missing_from_commit(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        with pytest.raises(FileNotFoundError):
            hq.new_forbidden_edges("sha_nonexistent", "sha_new_0002")

    def test_raises_on_missing_to_commit(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        with pytest.raises(FileNotFoundError):
            hq.new_forbidden_edges("sha_old_0001", "sha_nonexistent")

    def test_same_snapshot_no_new_edges(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        result = hq.new_forbidden_edges("sha_old_0001", "sha_old_0001")
        assert result == []


class TestNewDirectWrites:
    def test_returns_list(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        result = hq.new_direct_writes("sha_old_0001", "sha_new_0002")
        assert isinstance(result, list)

    def test_new_direct_writes_returns_new_type_entries(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        result = hq.new_direct_writes("sha_old_0001", "sha_new_0002")
        for entry in result:
            assert entry["type"] == "new_direct_write"

    def test_raises_on_missing_commit(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        with pytest.raises(FileNotFoundError):
            hq.new_direct_writes("sha_bad", "sha_new_0002")


class TestOrphanedInterfaces:
    def test_returns_list(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        result = hq.orphaned_interfaces("sha_old_0001", "sha_new_0002")
        assert isinstance(result, list)

    def test_raises_on_missing_commit(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        with pytest.raises(FileNotFoundError):
            hq.orphaned_interfaces("sha_nonexistent", "sha_new_0002")

    def test_same_snapshot_no_orphans(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        result = hq.orphaned_interfaces("sha_old_0001", "sha_old_0001")
        assert result == []


class TestL2PhaseCoverageRegression:
    def test_returns_dict(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        result = hq.new_l2_phase_coverage_regressions("sha_old_0001", "sha_new_0002")
        assert isinstance(result, dict)

    def test_required_keys_present(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        result = hq.new_l2_phase_coverage_regressions("sha_old_0001", "sha_new_0002")
        assert "from_commit" in result
        assert "to_commit" in result

    def test_raises_on_missing_commit(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        with pytest.raises(FileNotFoundError):
            hq.new_l2_phase_coverage_regressions("sha_bad", "sha_new_0002")


class TestToolProviderCallSurfaces:
    def test_returns_list(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        result = hq.new_tool_provider_call_surfaces("sha_old_0001", "sha_new_0002")
        assert isinstance(result, list)

    def test_same_snapshot_returns_empty(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        result = hq.new_tool_provider_call_surfaces("sha_old_0001", "sha_old_0001")
        assert result == []

    def test_raises_on_missing_commit(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        with pytest.raises(FileNotFoundError):
            hq.new_tool_provider_call_surfaces("sha_bad", "sha_new_0002")


class TestCrossLayerDependencies:
    def test_returns_list(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        result = hq.new_cross_layer_dependencies("sha_old_0001", "sha_new_0002")
        assert isinstance(result, list)

    def test_raises_on_missing_commit(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        with pytest.raises(FileNotFoundError):
            hq.new_cross_layer_dependencies("sha_bad", "sha_new_0002")

    def test_same_snapshot_no_new_deps(self, populated_manager: SnapshotManager):
        hq = HistoricalQueries(populated_manager)
        result = hq.new_cross_layer_dependencies("sha_old_0001", "sha_old_0001")
        assert result == []
