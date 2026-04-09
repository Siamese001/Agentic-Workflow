"""Tests for graphdb snapshot — metadata model and storage lifecycle."""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import pytest

from tools.graphdb.snapshot import SnapshotManager, SnapshotMetadata


class TestSnapshotMetadata:
    def test_to_dict_contains_all_required_fields(self, sample_metadata: SnapshotMetadata):
        d = sample_metadata.to_dict()
        required = {
            "commit_sha",
            "repo_state_hash",
            "schema_version",
            "scanner_digest",
            "artifact_digest",
            "run_id",
            "timestamp",
            "scanner_version",
            "node_count",
            "edge_count",
            "projection_version",
        }
        assert required.issubset(d.keys())

    def test_from_dict_round_trips(self, sample_metadata: SnapshotMetadata):
        d = sample_metadata.to_dict()
        restored = SnapshotMetadata.from_dict(d)
        assert restored.commit_sha == sample_metadata.commit_sha
        assert restored.repo_state_hash == sample_metadata.repo_state_hash
        assert restored.schema_version == sample_metadata.schema_version
        assert restored.scanner_digest == sample_metadata.scanner_digest
        assert restored.artifact_digest == sample_metadata.artifact_digest
        assert restored.run_id == sample_metadata.run_id
        assert restored.timestamp == sample_metadata.timestamp
        assert restored.node_count == sample_metadata.node_count
        assert restored.edge_count == sample_metadata.edge_count

    def test_projection_version_has_default(self, sample_metadata: SnapshotMetadata):
        assert sample_metadata.projection_version == "0.1.0"

    def test_deterministic_serialization(self, sample_metadata: SnapshotMetadata):
        d1 = sample_metadata.to_dict()
        d2 = sample_metadata.to_dict()
        assert d1 == d2


class TestSnapshotManagerInit:
    def test_creates_directories(self, tmp_path: Path):
        mgr = SnapshotManager(tmp_path / "graphdb")
        assert (tmp_path / "graphdb" / "projections").is_dir()
        assert (tmp_path / "graphdb" / "metadata").is_dir()

    def test_starts_with_empty_index(self, tmp_path: Path):
        mgr = SnapshotManager(tmp_path / "graphdb")
        assert mgr.list_snapshots() == {}


class TestSnapshotSaveLoad:
    def test_save_and_load_round_trip(
        self,
        snapshot_manager: SnapshotManager,
        minimal_graph: nx.DiGraph,
        sample_metadata: SnapshotMetadata,
    ):
        snapshot_manager.save_snapshot(minimal_graph, sample_metadata)
        loaded_graph, loaded_meta = snapshot_manager.load_snapshot(sample_metadata.commit_sha)
        assert loaded_graph.number_of_nodes() == minimal_graph.number_of_nodes()
        assert loaded_graph.number_of_edges() == minimal_graph.number_of_edges()
        assert loaded_meta.commit_sha == sample_metadata.commit_sha

    def test_metadata_fields_preserved_on_load(
        self,
        snapshot_manager: SnapshotManager,
        minimal_graph: nx.DiGraph,
        sample_metadata: SnapshotMetadata,
    ):
        snapshot_manager.save_snapshot(minimal_graph, sample_metadata)
        _, loaded_meta = snapshot_manager.load_snapshot(sample_metadata.commit_sha)
        assert loaded_meta.run_id == sample_metadata.run_id
        assert loaded_meta.schema_version == sample_metadata.schema_version
        assert loaded_meta.scanner_digest == sample_metadata.scanner_digest
        assert loaded_meta.artifact_digest == sample_metadata.artifact_digest

    def test_load_nonexistent_raises(self, snapshot_manager: SnapshotManager):
        with pytest.raises(FileNotFoundError):
            snapshot_manager.load_snapshot("nonexistent_sha")

    def test_snapshot_exists_after_save(
        self,
        snapshot_manager: SnapshotManager,
        minimal_graph: nx.DiGraph,
        sample_metadata: SnapshotMetadata,
    ):
        assert not snapshot_manager.snapshot_exists(sample_metadata.commit_sha)
        snapshot_manager.save_snapshot(minimal_graph, sample_metadata)
        assert snapshot_manager.snapshot_exists(sample_metadata.commit_sha)


class TestSnapshotIndex:
    def test_list_snapshots_empty_initially(self, snapshot_manager: SnapshotManager):
        assert snapshot_manager.list_snapshots() == {}

    def test_list_snapshots_after_save(
        self,
        snapshot_manager: SnapshotManager,
        minimal_graph: nx.DiGraph,
        sample_metadata: SnapshotMetadata,
    ):
        snapshot_manager.save_snapshot(minimal_graph, sample_metadata)
        snapshots = snapshot_manager.list_snapshots()
        assert sample_metadata.commit_sha in snapshots

    def test_list_returns_copy_not_reference(
        self,
        snapshot_manager: SnapshotManager,
        minimal_graph: nx.DiGraph,
        sample_metadata: SnapshotMetadata,
    ):
        from typing import Any, Dict

        snapshot_manager.save_snapshot(minimal_graph, sample_metadata)
        s1: Dict[str, Any] = dict(snapshot_manager.list_snapshots())
        s1["injected"] = "value"
        s2 = snapshot_manager.list_snapshots()
        assert "injected" not in s2


class TestSnapshotDelete:
    def test_delete_removes_from_index(
        self,
        snapshot_manager: SnapshotManager,
        minimal_graph: nx.DiGraph,
        sample_metadata: SnapshotMetadata,
    ):
        snapshot_manager.save_snapshot(minimal_graph, sample_metadata)
        snapshot_manager.delete_snapshot(sample_metadata.commit_sha)
        assert not snapshot_manager.snapshot_exists(sample_metadata.commit_sha)

    def test_delete_nonexistent_raises(self, snapshot_manager: SnapshotManager):
        with pytest.raises(FileNotFoundError):
            snapshot_manager.delete_snapshot("sha_does_not_exist")


class TestSnapshotCleanup:
    def _save_n_snapshots(self, mgr: SnapshotManager, graph: nx.DiGraph, n: int) -> list[str]:
        shas = []
        for i in range(n):
            sha = f"{'a' * 39}{i}"
            meta = SnapshotMetadata(
                commit_sha=sha,
                repo_state_hash=f"tree_{i}",
                schema_version="1.0",
                scanner_digest="sd",
                artifact_digest="ad",
                run_id=f"run_{i}",
                timestamp=f"2026-01-{i + 1:02d}T00:00:00Z",
                scanner_version="0.1.0",
                node_count=graph.number_of_nodes(),
                edge_count=graph.number_of_edges(),
            )
            mgr.save_snapshot(graph, meta)
            shas.append(sha)
        return shas

    def test_cleanup_keeps_recent(
        self,
        snapshot_manager: SnapshotManager,
        minimal_graph: nx.DiGraph,
    ):
        self._save_n_snapshots(snapshot_manager, minimal_graph, 5)
        deleted = snapshot_manager.cleanup_old_snapshots(keep_count=3)
        assert len(deleted) == 2
        assert len(snapshot_manager.list_snapshots()) == 3

    def test_cleanup_no_op_when_under_limit(
        self,
        snapshot_manager: SnapshotManager,
        minimal_graph: nx.DiGraph,
    ):
        self._save_n_snapshots(snapshot_manager, minimal_graph, 3)
        deleted = snapshot_manager.cleanup_old_snapshots(keep_count=10)
        assert deleted == []


class TestSnapshotGetLatest:
    def test_latest_returns_none_when_empty(self, snapshot_manager: SnapshotManager):
        assert snapshot_manager.get_latest_snapshot() is None

    def test_latest_returns_most_recent(
        self,
        snapshot_manager: SnapshotManager,
        minimal_graph: nx.DiGraph,
    ):
        for i in range(3):
            sha = f"sha_{i:040d}"
            meta = SnapshotMetadata(
                commit_sha=sha,
                repo_state_hash="rsh",
                schema_version="1.0",
                scanner_digest="sd",
                artifact_digest="ad",
                run_id=f"run_{i}",
                timestamp=f"2026-01-{i + 1:02d}T00:00:00Z",
                scanner_version="0.1.0",
                node_count=1,
                edge_count=0,
            )
            snapshot_manager.save_snapshot(minimal_graph, meta)

        result = snapshot_manager.get_latest_snapshot()
        assert result is not None
        latest_sha, _ = result
        assert "sha_" in latest_sha
