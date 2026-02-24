"""Embedding storage layout constants for Plan A SSD organization.

Provides pure Path-join layout builder without filesystem side effects.
No OS-specific mounting logic; only path construction utilities.
"""

from __future__ import annotations

from pathlib import Path


class EmbeddingStorageLayout:
    """Pure path layout builder for embedding storage on SSD.

    Provides deterministic path construction without touching filesystem.
    All paths are relative to a configurable base_path.
    """

    def __init__(self, base_path: Path) -> None:
        """Initialize layout with base path.

        Args:
            base_path: Base directory for all embedding storage.
        """
        self.base_path = base_path

    # Index directories
    @property
    def indexes_dir(self) -> Path:
        """Base directory for FAISS indexes."""
        return self.base_path / "indexes"

    def healing_contexts_index_dir(self) -> Path:
        """Directory for healing contexts FAISS index."""
        return self.indexes_dir / "healing_contexts"

    def telemetry_events_index_dir(self) -> Path:
        """Directory for telemetry events FAISS index."""
        return self.indexes_dir / "telemetry_events"

    def dpo_pairs_index_dir(self) -> Path:
        """Directory for DPO pairs FAISS index."""
        return self.indexes_dir / "dpo_pairs"

    # Current index files
    def current_faiss_file(self, index_id: str) -> Path:
        """Path to current .faiss file for given index_id."""
        return self.indexes_dir / index_id / "current.faiss"

    def current_metadata_file(self, index_id: str) -> Path:
        """Path to current .meta.json file for given index_id."""
        return self.indexes_dir / index_id / "current.meta.json"

    def archive_dir(self, index_id: str) -> Path:
        """Archive directory for pruned index versions."""
        return self.indexes_dir / index_id / "archive"

    # Embedding cache directories
    @property
    def embedding_cache_dir(self) -> Path:
        """Base directory for embedding cache."""
        return self.base_path / "embedding_cache"

    def healing_contexts_cache_dir(self) -> Path:
        """Directory for healing contexts cache."""
        return self.embedding_cache_dir / "healing_contexts"

    def telemetry_events_cache_dir(self) -> Path:
        """Directory for telemetry events cache."""
        return self.embedding_cache_dir / "telemetry_events"

    def dpo_pairs_cache_dir(self) -> Path:
        """Directory for DPO pairs cache."""
        return self.embedding_cache_dir / "dpo_pairs"

    # Staging directory
    @property
    def raw_staging_dir(self) -> Path:
        """Temporary directory for raw staging data."""
        return self.base_path / "raw_staging"


__all__ = ["EmbeddingStorageLayout"]
