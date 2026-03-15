"""IndexBuildMetadata type for Plan A deterministic index builds.

This type is consumed by Plan B as part of the EmbeddingSearchProvider protocol.
All fields are frozen and ASCII-only for deterministic serialization.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass(frozen=True, slots=True)
class IndexBuildMetadata:
    """Stable contract consumed by Plan B.

    INVARIANT: If embedding_model_version or embedding_model_checksum changes,
    the index is invalid and must be fully rebuilt before reads are permitted.
    """

    index_id: str
    faiss_version: str
    build_seed: int
    canonicalization_version: str
    embedding_model_version: str
    embedding_model_checksum: str
    built_at_utc: int
    index_version_hash: str
    vector_count: int
    dimension: int

    def to_canonical_json_bytes(self) -> bytes:
        """Return deterministic ASCII-only JSON bytes.

        Uses canonical JSON: keys sorted ASC, no whitespace, ASCII encoding.
        Result is suitable for hashing and replay determinism.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "IndexBuildMetadata.to_canonical_json_bytes")

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
        return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


__all__ = ["IndexBuildMetadata"]
