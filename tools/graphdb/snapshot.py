"""GraphDB Snapshot Management - Handles graph projection snapshots and metadata.

This module provides functionality for creating, storing, and managing
graph projection snapshots with full metadata for historical diffing.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import networkx as nx
from networkx.readwrite import json_graph

logger = logging.getLogger(__name__)


@dataclass
class SnapshotMetadata:
    """Metadata for a graph projection snapshot."""

    commit_sha: str
    repo_state_hash: str
    schema_version: str
    scanner_digest: str
    artifact_digest: str
    run_id: str
    timestamp: str
    scanner_version: str
    node_count: int
    edge_count: int
    projection_version: str = "0.1.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "commit_sha": self.commit_sha,
            "repo_state_hash": self.repo_state_hash,
            "schema_version": self.schema_version,
            "scanner_digest": self.scanner_digest,
            "artifact_digest": self.artifact_digest,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "scanner_version": self.scanner_version,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "projection_version": self.projection_version,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SnapshotMetadata:
        """Create from dictionary."""
        return cls(**data)


class SnapshotManager:
    """Manages graph projection snapshots with metadata and storage."""

    def __init__(self, storage_dir: Path):
        """Initialize snapshot manager.

        Args:
            storage_dir: Base directory for storing snapshots
        """
        self.storage_dir = Path(storage_dir)
        self.projections_dir = self.storage_dir / "projections"
        self.metadata_dir = self.storage_dir / "metadata"
        self.index_file = self.storage_dir / "index.json"

        # Create directories
        self.projections_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

        # Load existing index
        self._load_index()

    def _load_index(self) -> None:
        """Load snapshot index from disk."""
        if self.index_file.exists():
            try:
                self.index = json.loads(self.index_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Failed to load snapshot index: %s", e)
                self.index = {}
        else:
            self.index = {}

    def _save_index(self) -> None:
        """Save snapshot index to disk."""
        try:
            self.index_file.write_text(json.dumps(self.index, indent=2), encoding="utf-8")
        except OSError as e:
            raise RuntimeError(f"Failed to save snapshot index: {e}")

    def _get_snapshot_paths(self, commit_sha: str) -> tuple[Path, Path]:
        """Get file paths for a snapshot."""
        snapshot_dir = self.projections_dir / commit_sha
        graph_file = snapshot_dir / "graph.json"
        metadata_file = self.metadata_dir / f"{commit_sha}.json"
        return graph_file, metadata_file

    def _get_legacy_pickle_path(self, commit_sha: str) -> Path:
        """Get the legacy pickle path for backward-compatibility checks and cleanup."""
        snapshot_dir = self.projections_dir / commit_sha
        return snapshot_dir / "graph.pkl"

    def _calculate_artifact_digest(self, sqlite_path: Path) -> str:
        """Calculate SHA256 digest of the source SQLite file."""
        hasher = hashlib.sha256()
        try:
            with open(sqlite_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
        except OSError as e:
            raise RuntimeError(f"Failed to calculate artifact digest: {e}")
        return hasher.hexdigest()

    def save_snapshot(
        self,
        graph: nx.Graph,
        metadata: SnapshotMetadata,
    ) -> Path:
        """Save a graph snapshot with metadata.

        Args:
            graph: NetworkX graph to save
            metadata: Snapshot metadata

        Returns:
            Path to the saved graph file
        """
        commit_sha = metadata.commit_sha
        graph_file, metadata_file = self._get_snapshot_paths(commit_sha)

        # Create snapshot directory
        graph_file.parent.mkdir(parents=True, exist_ok=True)

        # Save graph as JSON node-link data to avoid unsafe pickle deserialization.
        try:
            graph_payload = json_graph.node_link_data(graph)
            graph_file.write_text(json.dumps(graph_payload, indent=2), encoding="utf-8")
        except (OSError, TypeError, ValueError) as e:
            raise RuntimeError(f"Failed to save graph: {e}")

        # Save metadata
        try:
            metadata_file.write_text(json.dumps(metadata.to_dict(), indent=2), encoding="utf-8")
        except OSError as e:
            raise RuntimeError(f"Failed to save metadata: {e}")

        # Update index
        self.index[commit_sha] = {
            "timestamp": metadata.timestamp,
            "run_id": metadata.run_id,
            "node_count": metadata.node_count,
            "edge_count": metadata.edge_count,
            "graph_file": str(graph_file.relative_to(self.storage_dir)),
            "metadata_file": str(metadata_file.relative_to(self.storage_dir)),
        }
        self._save_index()

        return graph_file

    def load_snapshot(self, commit_sha: str) -> tuple[nx.Graph, SnapshotMetadata]:
        """Load a graph snapshot and metadata.

        Args:
            commit_sha: Commit SHA of the snapshot to load

        Returns:
            Tuple of (graph, metadata)
        """
        graph_file, metadata_file = self._get_snapshot_paths(commit_sha)

        legacy_graph_file = self._get_legacy_pickle_path(commit_sha)

        if not metadata_file.exists():
            raise FileNotFoundError(f"Snapshot metadata not found for commit {commit_sha}")

        if not graph_file.exists():
            if legacy_graph_file.exists():
                raise RuntimeError(
                    "Legacy pickle snapshots are no longer loaded automatically. "
                    f"Regenerate or migrate snapshot for commit {commit_sha}."
                )
            raise FileNotFoundError(f"Snapshot graph not found for commit {commit_sha}")

        # Load graph
        try:
            graph_payload = json.loads(graph_file.read_text(encoding="utf-8"))
            graph = json_graph.node_link_graph(graph_payload)
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as e:
            raise RuntimeError(f"Failed to load graph: {e}")

        # Load metadata
        try:
            metadata_dict = json.loads(metadata_file.read_text(encoding="utf-8"))
            metadata = SnapshotMetadata.from_dict(metadata_dict)
        except (OSError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load metadata: {e}")

        return graph, metadata

    def list_snapshots(self) -> Dict[str, Dict[str, Any]]:
        """List all available snapshots.

        Returns:
            Dictionary mapping commit SHA to snapshot info
        """
        return self.index.copy()

    def snapshot_exists(self, commit_sha: str) -> bool:
        """Check if a snapshot exists for the given commit."""
        return commit_sha in self.index

    def delete_snapshot(self, commit_sha: str) -> None:
        """Delete a snapshot.

        Args:
            commit_sha: Commit SHA of the snapshot to delete
        """
        if commit_sha not in self.index:
            raise FileNotFoundError(f"Snapshot not found for commit {commit_sha}")

        graph_file, metadata_file = self._get_snapshot_paths(commit_sha)

        # Delete files
        if graph_file.exists():
            try:
                graph_file.unlink()
            except OSError as e:
                logger.warning("Failed to delete graph file: %s", e)

        if metadata_file.exists():
            try:
                metadata_file.unlink()
            except OSError as e:
                logger.warning("Failed to delete metadata file: %s", e)

        legacy_graph_file = self._get_legacy_pickle_path(commit_sha)
        if legacy_graph_file.exists():
            try:
                legacy_graph_file.unlink()
            except OSError as e:
                logger.warning("Failed to delete legacy pickle graph file: %s", e)

        # Clean up empty directory
        try:
            graph_file.parent.rmdir()
        except OSError:
            # Directory not empty, that's fine
            pass

        # Update index
        del self.index[commit_sha]
        self._save_index()

    def cleanup_old_snapshots(self, keep_count: int = 30) -> list[str]:
        """Clean up old snapshots, keeping only the most recent ones.

        Args:
            keep_count: Number of recent snapshots to keep

        Returns:
            List of deleted commit SHAs
        """
        if len(self.index) <= keep_count:
            return []

        # Sort by timestamp (newest first)
        sorted_snapshots = sorted(
            self.index.items(),
            key=lambda x: x[1]["timestamp"],
            reverse=True,
        )

        # Delete old snapshots
        to_delete = [commit_sha for commit_sha, _ in sorted_snapshots[keep_count:]]
        deleted = []

        for commit_sha in to_delete:
            try:
                self.delete_snapshot(commit_sha)
                deleted.append(commit_sha)
            except FileNotFoundError:
                # Already deleted, skip
                continue
            except (OSError, RuntimeError) as e:
                logger.warning("Failed to delete snapshot %s: %s", commit_sha, e)

        return deleted

    def get_latest_snapshot(self) -> Optional[tuple[str, Dict[str, Any]]]:
        """Get the most recent snapshot.

        Returns:
            Tuple of (commit_sha, snapshot_info) or None if no snapshots
        """
        if not self.index:
            return None

        # Sort by timestamp (newest first)
        sorted_snapshots = sorted(
            self.index.items(),
            key=lambda x: x[1]["timestamp"],
            reverse=True,
        )

        return sorted_snapshots[0]

    def create_metadata(
        self,
        commit_sha: str,
        repo_state_hash: str,
        schema_version: str,
        scanner_digest: str,
        sqlite_path: Path,
        run_id: str,
        timestamp: str,
        scanner_version: str,
        graph: nx.Graph,
    ) -> SnapshotMetadata:
        """Create snapshot metadata from graph and source information.

        Args:
            commit_sha: Git commit SHA
            repo_state_hash: Git tree hash
            schema_version: ADG schema version
            scanner_digest: Digest of scanner code
            sqlite_path: Path to source SQLite file
            run_id: Unique run identifier
            timestamp: ISO8601 timestamp
            scanner_version: Scanner version string
            graph: NetworkX graph

        Returns:
            SnapshotMetadata instance
        """
        artifact_digest = self._calculate_artifact_digest(sqlite_path)

        return SnapshotMetadata(
            commit_sha=commit_sha,
            repo_state_hash=repo_state_hash,
            schema_version=schema_version,
            scanner_digest=scanner_digest,
            artifact_digest=artifact_digest,
            run_id=run_id,
            timestamp=timestamp,
            scanner_version=scanner_version,
            node_count=graph.number_of_nodes(),
            edge_count=graph.number_of_edges(),
        )
