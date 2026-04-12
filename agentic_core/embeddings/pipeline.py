"""B7-B8 Pipeline - Metadata binding and vector index write.

10C-REQ-106: Metadata binding attach source provenance tags
10C-REQ-107: Vector index write commit to ChromaDB FAISS
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from pathlib import Path
import hashlib
import json
import time


@dataclass
class VectorRecord:
    """Vector record with metadata."""

    id: str
    embedding: list[float]
    sparse_vector: dict[int, float] | None
    metadata: dict[str, Any]
    source_uri: str
    chunk_index: int
    created_at: float


class EmbeddingPipeline:
    """B7-B8: Metadata binding and vector index write.

    10C-REQ-106/107: Full embedding pipeline with provenance.
    """

    def __init__(self, collection_name: str = "default") -> None:
        self._collection = collection_name
        self._records: list[VectorRecord] = []
        self._index_path: Path | None = None

    def bind_metadata(
        self,
        text: str,
        embedding: list[float],
        sparse: dict[int, float] | None,
        source_uri: str,
        chunk_index: int = 0,
        extra_meta: dict[str, Any] | None = None,
    ) -> VectorRecord:
        """B7: Bind metadata to embedding."""
        # Generate deterministic ID
        content = f"{source_uri}:{chunk_index}:{text[:100]}"
        record_id = hashlib.sha256(content.encode()).hexdigest()[:16]

        metadata = {
            "source_uri": source_uri,
            "chunk_index": chunk_index,
            "text_preview": text[:200],
            "char_count": len(text),
            "embedding_dim": len(embedding),
            "has_sparse": sparse is not None,
        }

        if extra_meta:
            metadata.update(extra_meta)

        return VectorRecord(
            id=record_id,
            embedding=embedding,
            sparse_vector=sparse,
            metadata=metadata,
            source_uri=source_uri,
            chunk_index=chunk_index,
            created_at=time.time(),
        )

    def stage_record(self, record: VectorRecord) -> None:
        """Stage record for batch write."""
        self._records.append(record)

    def write_index(
        self,
        index_path: str | None = None,
    ) -> dict[str, Any]:
        """B8: Write to vector index."""
        path = index_path or f"vector_store/{self._collection}"
        self._index_path = Path(path)

        # In production, this would write to ChromaDB/FAISS
        # For now, simulate with JSONL
        self._index_path.parent.mkdir(parents=True, exist_ok=True)

        records_data = []
        for r in self._records:
            records_data.append(
                {
                    "id": r.id,
                    "embedding": r.embedding[:10],  # Truncate for storage
                    "metadata": r.metadata,
                    "source_uri": r.source_uri,
                }
            )

        # Write to file
        index_file = self._index_path.with_suffix(".jsonl")
        with open(index_file, "w", encoding="utf-8") as f:
            for rec in records_data:
                f.write(json.dumps(rec) + "\n")

        return {
            "index_path": str(index_file),
            "records_written": len(self._records),
            "collection": self._collection,
        }

    def process_document(
        self,
        text: str,
        source_uri: str,
        encoder: Any,
    ) -> VectorRecord:
        """Full pipeline: encode + bind + stage."""
        # Encode
        result = encoder.encode(text, return_sparse=True)

        # Bind metadata
        record = self.bind_metadata(
            text=text,
            embedding=result.dense_vector,
            sparse=result.sparse_vector,
            source_uri=source_uri,
        )

        # Stage
        self.stage_record(record)

        return record

    def get_stats(self) -> dict[str, Any]:
        """Get pipeline statistics."""
        return {
            "staged_records": len(self._records),
            "collection": self._collection,
            "index_path": str(self._index_path) if self._index_path else None,
        }
