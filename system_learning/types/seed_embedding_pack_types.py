"""Seed Embedding Pack types for Plan B Phase 0.

Immutable, deterministic types for governed embedding bootstrap.
"""
from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Literal
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

@dataclass(frozen=True, slots=True)
class SeedEmbeddingPackManifest:
    """Immutable manifest for a Seed Embedding Pack.

    All hash fields are computed AFTER canonical serialization of non-hash material.
    built_at_utc is metadata-only and excluded from hash computation.
    """
    namespace: str
    bootstrap_mode: Literal['minimal_seed', 'curated_seed']
    embedding_model_version: str
    embedding_model_checksum: str
    canonicalization_version: str
    dimensions: int
    vector_count: int
    row_index_hash: str
    matrix_hash: str
    seed_index_version_hash: str
    built_at_utc: int

    def to_canonical_json_bytes(self) -> bytes:
        """Serialize manifest to canonical JSON bytes.

        Returns:
            ASCII-only canonical JSON bytes.
        """
        canonical_data = {'namespace': self.namespace, 'bootstrap_mode': self.bootstrap_mode, 'embedding_model_version': self.embedding_model_version, 'embedding_model_checksum': self.embedding_model_checksum, 'canonicalization_version': self.canonicalization_version, 'dimensions': self.dimensions, 'vector_count': self.vector_count}
        return json.dumps(canonical_data, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')

    def to_full_json_bytes(self) -> bytes:
        """Serialize full manifest including hash fields and metadata.

        Returns:
            ASCII-only JSON bytes with all fields.
        """
        data = {'namespace': self.namespace, 'bootstrap_mode': self.bootstrap_mode, 'embedding_model_version': self.embedding_model_version, 'embedding_model_checksum': self.embedding_model_checksum, 'canonicalization_version': self.canonicalization_version, 'dimensions': self.dimensions, 'vector_count': self.vector_count, 'row_index_hash': self.row_index_hash, 'matrix_hash': self.matrix_hash, 'seed_index_version_hash': self.seed_index_version_hash, 'built_at_utc': self.built_at_utc}
        return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')

@dataclass(frozen=True, slots=True)
class SeedEmbeddingPackConfig:
    """Configuration for building a Seed Embedding Pack."""
    namespace: str
    bootstrap_mode: Literal['minimal_seed', 'curated_seed']
    minimal_seed_count: int | None = None
    curated_allowlist: list[tuple[str, str]] | None = None
    embedding_model_version: str = 'v1'
    embedding_model_checksum: str = '0' * 64
    canonicalization_version: str = 'v1'
__all__ = ['SeedEmbeddingPackManifest', 'SeedEmbeddingPackConfig']
