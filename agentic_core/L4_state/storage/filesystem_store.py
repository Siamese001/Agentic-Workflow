"""
Filesystem-based Storage Backend

Local-only, append-only storage implementation for agentic artifacts.
Provides deterministic versioning and path traversal protection.
"""

from __future__ import annotations

import json
from pathlib import Path

from .persistent_store import (
    StoredArtifact,
    StoredArtifactRef,
    _canonicalize_payload,
    _sanitize_id,
)


class FileSystemStore:
    """Local filesystem storage backend with append-only semantics."""

    def __init__(self, root_dir: Path | str, max_artifact_size: int = 5 * 1024 * 1024):
        """Initialize filesystem store.

        Args:
            root_dir: Root directory for storage
            max_artifact_size: Maximum artifact size in bytes (default: 5MB)
        """
        self.root_dir = Path(root_dir)
        self.max_artifact_size = max_artifact_size
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def _get_artifact_dir(self, kind: str, logical_id: str) -> Path:
        """Get directory for a specific artifact type and ID."""
        kind_clean = _sanitize_id(kind)
        id_clean = _sanitize_id(logical_id)
        return self.root_dir / "docs" / "store" / kind_clean / id_clean

    def _get_next_version(self, artifact_dir: Path) -> int:
        """Get next version number for artifact directory."""
        if not artifact_dir.exists():
            artifact_dir.mkdir(parents=True, exist_ok=True)
            return 1

        # Find existing versions
        versions = []
        for item in artifact_dir.iterdir():
            if item.is_file() and item.name.startswith("v") and item.suffix == ".json":
                try:
                    version_num = int(item.name[1:-5])  # Remove "v" prefix and ".json"
                    versions.append(version_num)
                except ValueError:
                    continue

        if not versions:
            return 1

        return max(versions) + 1

    def _get_artifact_path(self, artifact_dir: Path, version: int) -> Path:
        """Get file path for specific version."""
        return artifact_dir / f"v{version:04d}.json"

    def _validate_artifact(self, artifact: StoredArtifact) -> None:
        """Validate artifact before storage."""
        # Check size
        payload_json = _canonicalize_payload(artifact.payload)
        payload_size = len(payload_json.encode("utf-8"))
        if payload_size > self.max_artifact_size:
            raise ValueError(f"Artifact size {payload_size} exceeds maximum {self.max_artifact_size}")

        # Validate kind and logical_id (already sanitized in create_artifact)
        if not artifact.kind:
            raise ValueError("Artifact kind cannot be empty")
        if not artifact.logical_id:
            raise ValueError("Artifact logical_id cannot be empty")

    def put(self, artifact: StoredArtifact) -> StoredArtifactRef:
        """Store an artifact and return its reference.

        Args:
            artifact: Artifact to store

        Returns:
            Reference to stored artifact

        Raises:
            ValueError: If artifact validation fails
            OSError: If filesystem operation fails
        """
        self._validate_artifact(artifact)

        # Get artifact directory and next version
        artifact_dir = self._get_artifact_dir(artifact.kind, artifact.logical_id)
        version = self._get_next_version(artifact_dir)
        artifact_path = self._get_artifact_path(artifact_dir, version)

        # Prepare storage format
        storage_data = {
            "kind": artifact.kind,
            "logical_id": artifact.logical_id,
            "version": version,
            "created_utc": artifact.created_utc,
            "content_type": artifact.content_type,
            "payload": artifact.payload,
            "hashes": artifact.hashes,
            "metadata": artifact.metadata,
        }

        # Write atomically
        temp_path = artifact_path.with_suffix(".tmp")
        try:
            temp_path.write_text(json.dumps(storage_data, sort_keys=True, indent=2), encoding="utf-8")
            # Atomic rename
            temp_path.rename(artifact_path)
        except Exception:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise

        # Get file size for reference
        file_size = artifact_path.stat().st_size

        return StoredArtifactRef(
            kind=artifact.kind,
            logical_id=artifact.logical_id,
            version=version,
            path=str(artifact_path.relative_to(self.root_dir)),
            size_bytes=file_size,
        )

    def get(self, ref: StoredArtifactRef) -> StoredArtifact:
        """Retrieve an artifact by reference.

        Args:
            ref: Artifact reference

        Returns:
            Retrieved artifact

        Raises:
            FileNotFoundError: If artifact doesn't exist
            ValueError: If artifact data is invalid
        """
        artifact_path = self.root_dir / ref.path

        if not artifact_path.exists():
            raise FileNotFoundError(f"Artifact not found: {ref.path}")

        try:
            data = json.loads(artifact_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid artifact JSON: {e}")

        # Validate version matches
        if data.get("version") != ref.version:
            raise ValueError(f"Version mismatch: expected {ref.version}, got {data.get('version')}")

        return StoredArtifact(
            kind=data["kind"],
            logical_id=data["logical_id"],
            created_utc=data["created_utc"],
            content_type=data["content_type"],
            payload=data["payload"],
            hashes=data.get("hashes", {}),
            metadata=data.get("metadata", {}),
        )

    def list(self, kind: str | None = None, limit: int | None = None) -> list[StoredArtifactRef]:
        """List stored artifacts, optionally filtered by kind and limited.

        Args:
            kind: Filter by artifact kind (if None, list all)
            limit: Maximum number of results to return (if None, return all)

        Returns:
            List of artifact references, deterministically sorted and limited
        """
        refs = []
        store_base = self.root_dir / "docs" / "store"

        if not store_base.exists():
            return []

        # Walk through stored artifacts
        for kind_dir in store_base.iterdir():
            if not kind_dir.is_dir():
                continue

            current_kind = kind_dir.name
            if kind is not None and current_kind != kind:
                continue

            for id_dir in kind_dir.iterdir():
                if not id_dir.is_dir():
                    continue

                current_logical_id = id_dir.name

                for file_path in id_dir.iterdir():
                    if (
                        not file_path.is_file()
                        or not file_path.name.startswith("v")
                        or not file_path.suffix == ".json"
                    ):
                        continue

                    try:
                        version = int(file_path.name[1:-5])  # Remove "v" prefix and ".json"
                        file_size = file_path.stat().st_size
                        refs.append(
                            StoredArtifactRef(
                                kind=current_kind,
                                logical_id=current_logical_id,
                                version=version,
                                path=str(file_path.relative_to(self.root_dir)),
                                size_bytes=file_size,
                            )
                        )
                    except ValueError:
                        continue

        # Deterministic sorting
        refs.sort(key=lambda r: (r.kind, r.logical_id, r.version))

        # Apply limit if specified
        if limit is not None and limit > 0:
            refs = refs[:limit]

        return refs


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    "FileSystemStore",
]
