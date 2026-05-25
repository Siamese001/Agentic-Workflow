"""Embedding storage layout constants for Plan A SSD organization.

Provides pure Path-join layout builder without filesystem side effects.
No OS-specific mounting logic; only path construction utilities.

NOTE (bge-m3-gap-closure-c8f3a2 W2.3):
  ``healing_contexts`` is a SYSTEM_LEARNING surface — NOT part of
  apps_qna retrieval. It stores runtime healing context embeddings used
  by the adaptive-learning pipeline (system_learning/adapters/) for
  cross-session exemplar recall. The seed pack at
  ``C:/AgenticEmbeddings/seed_packs/healing_contexts/<hash>/`` is NOT
  the same index as apps_qna_interview_cards. They share the storage
  root (C:/AgenticEmbeddings) and the BGE-M3 embedder but are fully
  independent indexes with separate manifests, purposes, and consumers.

  ADR-055 ``PROVENANCE_ENFORCED_COLLECTIONS`` does NOT cover the
  healing_contexts namespace (it is not a ChromaDB collection; it is a
  seed-pack flat file). ADR-055 enforcement is scoped to ChromaDB
  writes in SovereignChromaClient.add_documents.

  FALSE-POSITIVE NOTE: During bge-m3 gap analysis this file was
  initially flagged as a potential GlobalCacheStrategy concern because
  HEALING_CONTEXTS_SEED_INDEX_VERSION_HASH is a hardcoded digest.
  This is intentional — the hash is a content-addressable anchor for
  the seed pack, not a model version or embedding dim. It is safe.
"""

from __future__ import annotations

import os
from pathlib import Path

# Default embedding store root when AGENTIC_EMBEDDING_STORE_ROOT is unset.
# Preserves the historical Windows layout used by the healing_contexts seed pack.
_DEFAULT_EMBEDDING_STORE_ROOT = Path("C:/AgenticEmbeddings")

# Canonical seed_index_version_hash for the healing_contexts namespace. This
# is the deterministic directory name under seed_packs/healing_contexts/ and
# matches the `seed_index_version_hash` field inside seed_manifest.json.
HEALING_CONTEXTS_SEED_INDEX_VERSION_HASH = "5d94b5b12ec92312d0240be9984ff92b9478f74ed6f1335511a202c5351520d9"


def default_embedding_store_root() -> Path:
    """Resolve the base embedding storage root.

    Resolution order:
      1. ``AGENTIC_EMBEDDING_STORE_ROOT`` environment variable, if set.
      2. ``C:/AgenticEmbeddings`` (historical default).
    """
    env = os.environ.get("AGENTIC_EMBEDDING_STORE_ROOT")
    if env:
        return Path(env)
    return _DEFAULT_EMBEDDING_STORE_ROOT


def default_healing_contexts_seed_pack(
    seed_index_version_hash: str = HEALING_CONTEXTS_SEED_INDEX_VERSION_HASH,
) -> Path:
    """Return the absolute path to the default healing_contexts seed pack."""
    return default_embedding_store_root() / "seed_packs" / "healing_contexts" / seed_index_version_hash


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

    def current_faiss_file(self, index_id: str) -> Path:
        """Path to current .faiss file for given index_id."""
        return self.indexes_dir / index_id / "current.faiss"

    def current_metadata_file(self, index_id: str) -> Path:
        """Path to current .meta.json file for given index_id."""
        return self.indexes_dir / index_id / "current.meta.json"

    def archive_dir(self, index_id: str) -> Path:
        """Archive directory for pruned index versions."""
        return self.indexes_dir / index_id / "archive"

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

    @property
    def raw_staging_dir(self) -> Path:
        """Temporary directory for raw staging data."""
        return self.base_path / "raw_staging"


__all__ = [
    "EmbeddingStorageLayout",
    "HEALING_CONTEXTS_SEED_INDEX_VERSION_HASH",
    "default_embedding_store_root",
    "default_healing_contexts_seed_pack",
]
