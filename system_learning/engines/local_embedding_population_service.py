"""LocalEmbeddingPopulationService - Plan A deterministic batch pipeline.

Extracts embeddings from JSONL sources, normalizes, and writes to FAISS indexes.
Enforces deterministic ordering, canonicalization, and L2 normalization.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from system_learning.engines.local_faiss_store import LocalFAISSStore
from system_learning.types.index_build_metadata_types import IndexBuildMetadata
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class EmbeddingProvider(Protocol):
    """Protocol for embedding providers used by LocalEmbeddingPopulationService."""

    def embed_batch(self, texts: list[str], dimension: int) -> list[list[float]]:
        """Embed a batch of texts into vectors of specified dimension."""
        ...


def extract_embedding_text(record: dict) -> str:
    """Extract text for embedding from a record.

    Phase 2: Accepts only "text" field. Raises ValueError if missing.

    Args:
        record: JSON record from source file.

    Returns:
        Text content for embedding.

    Raises:
        ValueError: If "text" field is missing or not a string.
    """
    if "text" not in record:
        raise ValueError("Record missing required 'text' field")
    text = record["text"]
    if not isinstance(text, str):
        raise ValueError(f"Record 'text' field must be string, got {type(text)}")
    return text


def normalize_l2(vector: list[float]) -> list[float]:
    """Normalize vector to unit L2 norm.

    Args:
        vector: Input vector.

    Returns:
        L2-normalized vector.
    """
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0:
        return vector
    return [x / norm for x in vector]


@dataclass(frozen=True, slots=True)
class _RecordKey:
    """Key for deterministic record ordering."""

    file_path: str
    record_index: int


class LocalEmbeddingPopulationService:
    """Deterministic batch embedding population service.

    INVARIANT: Enforces deterministic ordering, canonicalization, and L2 normalization.
    INVARIANT: Single-writer discipline for index writes.
    """

    def __init__(
        self,
        faiss_store: LocalFAISSStore,
        embedder: EmbeddingProvider,
        canonicalization_version: str,
        embedding_model_version: str,
        embedding_model_checksum: str,
        build_seed: int = 42,
    ) -> None:
        """Initialize service with dependencies.

        Args:
            faiss_store: FAISS store for index operations.
            embedder: Embedding provider for text-to-vector conversion.
            canonicalization_version: Version of canonicalization format.
            embedding_model_version: Version of embedding model.
            embedding_model_checksum: SHA-256 checksum of embedding model.
            build_seed: Random seed for deterministic builds (default: 42).
        """
        self.faiss_store = faiss_store
        self.embedder = embedder
        self.canonicalization_version = canonicalization_version
        self.embedding_model_version = embedding_model_version
        self.embedding_model_checksum = embedding_model_checksum
        self.build_seed = build_seed

    def populate_from_jsonl(
        self,
        *,
        index_id: str,
        source_files: list[Path],
        dimension: int,
        built_at_utc: int,
        batch_size: int = 5000,
        max_workers: int = 8,
    ) -> IndexBuildMetadata:
        """Populate index from JSONL source files.

        Args:
            index_id: Identifier for the index.
            source_files: List of JSONL source files.
            dimension: Embedding dimension.
            built_at_utc: Build timestamp (injected, not wall clock).
            batch_size: Batch size for embedding calls.
            max_workers: Maximum parallel workers for embedding.

        Returns:
            IndexBuildMetadata for the built index.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LocalEmbeddingPopulationService.populate_from_jsonl")

        sorted_files = sorted(source_files, key=lambda p: str(p))
        all_records = []
        for file_path in sorted_files:
            with open(file_path, encoding="utf-8") as f:
                for record_index, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    all_records.append((_RecordKey(str(file_path), record_index), record))
        all_records.sort(key=lambda x: (x[0].file_path, x[0].record_index))
        self.faiss_store.begin_build(index_id, dimension, self.build_seed)
        vectors = []
        metadatas = []
        for i, (_, record) in enumerate(all_records):
            canonical_record = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
            text = extract_embedding_text(record)
            vectors.append(text)
            metadatas.append(
                {
                    "content_hash": record.get("content_hash", ""),
                    "trace_id": record.get("trace_id", ""),
                    "canonical_record": canonical_record,
                }
            )
            if len(vectors) >= batch_size or i == len(all_records) - 1:
                batch_vectors = self.embedder.embed_batch(vectors, dimension)
                normalized_vectors = [normalize_l2(v) for v in batch_vectors]
                self.faiss_store.add_vectors(index_id, normalized_vectors, metadatas)
                vectors = []
                metadatas = []
        return self.faiss_store.finalize_build(
            index_id,
            built_at_utc=built_at_utc,
            canonicalization_version=self.canonicalization_version,
            embedding_model_version=self.embedding_model_version,
            embedding_model_checksum=self.embedding_model_checksum,
        )


__all__ = ["LocalEmbeddingPopulationService", "EmbeddingProvider", "extract_embedding_text", "normalize_l2"]
