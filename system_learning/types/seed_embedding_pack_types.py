"""Seed Embedding Pack types for Plan B Phase 0.

Immutable, deterministic types for governed embedding bootstrap.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass(frozen=True, slots=True)
class SeedEmbeddingPackManifest:
    """Immutable manifest for a Seed Embedding Pack.

    All hash fields are computed AFTER canonical serialization of non-hash material.
    built_at_utc is metadata-only and excluded from hash computation.
    """

    # Identity / compatibility
    namespace: str
    bootstrap_mode: Literal["minimal_seed", "curated_seed"]
    embedding_model_version: str
    embedding_model_checksum: str  # 64-hex SHA-256
    canonicalization_version: str
    dimensions: int
    vector_count: int

    # Integrity (computed after canonical serialization)
    row_index_hash: str
    matrix_hash: str
    seed_index_version_hash: str

    # Metadata (excluded from hash material)
    built_at_utc: int

    def to_canonical_json_bytes(self) -> bytes:
        """Serialize manifest to canonical JSON bytes.

        Returns:
            ASCII-only canonical JSON bytes.
        """
        # Build manifest without hash fields and built_at_utc for canonical bytes
        canonical_data = {
            "namespace": self.namespace,
            "bootstrap_mode": self.bootstrap_mode,
            "embedding_model_version": self.embedding_model_version,
            "embedding_model_checksum": self.embedding_model_checksum,
            "canonicalization_version": self.canonicalization_version,
            "dimensions": self.dimensions,
            "vector_count": self.vector_count,
        }
        return json.dumps(
            canonical_data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")

    def to_full_json_bytes(self) -> bytes:
        """Serialize full manifest including hash fields and metadata.

        Returns:
            ASCII-only JSON bytes with all fields.
        """
        data = {
            "namespace": self.namespace,
            "bootstrap_mode": self.bootstrap_mode,
            "embedding_model_version": self.embedding_model_version,
            "embedding_model_checksum": self.embedding_model_checksum,
            "canonicalization_version": self.canonicalization_version,
            "dimensions": self.dimensions,
            "vector_count": self.vector_count,
            "row_index_hash": self.row_index_hash,
            "matrix_hash": self.matrix_hash,
            "seed_index_version_hash": self.seed_index_version_hash,
            "built_at_utc": self.built_at_utc,
        }
        return json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")


@dataclass(frozen=True, slots=True)
class SeedEmbeddingPackConfig:
    """Configuration for building a Seed Embedding Pack."""

    namespace: str
    bootstrap_mode: Literal["minimal_seed", "curated_seed"]
    minimal_seed_count: int | None = None  # Required for minimal_seed mode
    curated_allowlist: list[tuple[str, str]] | None = None  # List of (trace_id, content_hash) for curated_seed mode
    embedding_model_version: str = "v1"
    embedding_model_checksum: str = "0" * 64  # Placeholder for deterministic tests
    canonicalization_version: str = "v1"


__all__ = [
    "SeedEmbeddingPackManifest",
    "SeedEmbeddingPackConfig",
]
