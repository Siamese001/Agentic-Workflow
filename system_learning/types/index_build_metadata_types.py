"""IndexBuildMetadata type for Plan A deterministic index builds.

This type is consumed by Plan B as part of the EmbeddingSearchProvider protocol.
All fields are frozen and ASCII-only for deterministic serialization.
"""

from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IndexBuildMetadata:
    """Stable contract consumed by Plan B.

    INVARIANT: If embedding_model_version or embedding_model_checksum changes,
    the index is invalid and must be fully rebuilt before reads are permitted.
    """

    index_id: str  # e.g., "healing_contexts_v1"
    faiss_version: str  # e.g., "1.7.4"
    build_seed: int  # Always 42
    canonicalization_version: str  # e.g., "canon-v1"
    embedding_model_version: str  # e.g., "text-embedding-004-v1"  ← REQUIRED
    embedding_model_checksum: str  # SHA-256 of embedder identifier/weights hash  ← REQUIRED
    built_at_utc: int  # Injected, no wall clock
    index_version_hash: str  # SHA-256 of serialized index bytes
    vector_count: int
    dimension: int

    def to_canonical_json_bytes(self) -> bytes:
        """Return deterministic ASCII-only JSON bytes.

        Uses canonical JSON: keys sorted ASC, no whitespace, ASCII encoding.
        Result is suitable for hashing and replay determinism.
        """
        data = {
            "index_id": self.index_id,
            "faiss_version": self.faiss_version,
            "build_seed": self.build_seed,
            "canonicalization_version": self.canonicalization_version,
            "embedding_model_version": self.embedding_model_version,
            "embedding_model_checksum": self.embedding_model_checksum,
            "built_at_utc": self.built_at_utc,
            "index_version_hash": self.index_version_hash,
            "vector_count": self.vector_count,
            "dimension": self.dimension,
        }
        return json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")


__all__ = ["IndexBuildMetadata"]
