"""FAISS Vector Store - Spec-Compliant Vector Database Backend

Implements Pipeline B/C vector storage using FAISS for concept-clustered
vector search as specified in Agentic Retrieval Models v9.

Supports:
- IVF (Inverted File) indices for large-scale search
- HNSW (Hierarchical Navigable Small World) for approximate search
- Exact L2/IP search for small datasets
- Metadata storage alongside vectors
- Incremental index updates
"""

from __future__ import annotations

import hashlib
import logging
import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_stores_embedding,
)

Logger = logging.getLogger(__name__)


@dataclass
class VectorDocument:
    """Document stored in FAISS with metadata."""
    id: str
    vector: np.ndarray
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    fact_vec_hash: str = ""  # SHA-256 of the 🟠 fact_vec for verification


class FaissVectorStore:
    """FAISS-based vector store for semantic search.

    Implements the 🟠 fact_vec storage as specified in the v9 spec.

    Features:
    - IVF indices for scalable search
    - HNSW for high-performance approximate search
    - Metadata persistence alongside vectors
    - Incremental updates
    """

    def __init__(
        self,
        dimension: int = 1024,  # BGE-M3 default dimension
        index_type: str = "IVF",  # IVF, HNSW, Flat
        nlist: int = 100,  # IVF clusters
        metric: str = "cosine",  # cosine, l2, ip
        persist_path: str | None = None,
        normalize: bool = False,
    ):
        """Initialize FAISS vector store.

        Args:
            dimension: Vector dimension (1024 for BGE-M3)
            index_type: Index type (IVF, HNSW, Flat)
            nlist: Number of IVF clusters
            metric: Distance metric (cosine, l2, ip)
            persist_path: Path for persistence
            normalize: Whether to normalize vectors
        """
        self.dimension = dimension
        self.index_type = index_type
        self.nlist = nlist
        self.metric = metric
        self.persist_path = persist_path
        self.normalize = normalize

        self._index: Any | None = None
        self._documents: dict[str, VectorDocument] = {}
        self._id_to_idx: dict[str, int] = {}
        self._next_idx = 0

        self._search_count = 0
        self._avg_search_time_ms = 0.0

        self._initialize_index()

    def _initialize_index(self) -> None:
        """Initialize FAISS index based on configuration."""
        try:
            import faiss
        except ImportError as e:
            raise ImportError(
                "faiss is required for FAISS vector store. "
                "Install with: pip install faiss-cpu (or faiss-gpu)"
            ) from e

        # Map metric
        metric_map = {
            "l2": faiss.METRIC_L2,
            "ip": faiss.METRIC_INNER_PRODUCT,
            "cosine": faiss.METRIC_INNER_PRODUCT,  # Normalized vectors for cosine
        }
        faiss_metric = metric_map.get(self.metric, faiss.METRIC_INNER_PRODUCT)

        # Create index
        if self.index_type == "Flat":
            if self.metric == "cosine":
                self._index = faiss.IndexFlatIP(self.dimension)
            else:
                self._index = faiss.IndexFlatL2(self.dimension)

        elif self.index_type == "IVF":
            quantizer = faiss.IndexFlatL2(self.dimension)
            self._index = faiss.IndexIVFFlat(quantizer, self.dimension, self.nlist, faiss_metric)
            self._needs_training = True

        elif self.index_type == "HNSW":
            self._index = faiss.IndexHNSWFlat(self.dimension, 32)  # 32 neighbors
            self._index.hnsw.efConstruction = 40
            self._index.metric_type = faiss_metric
            self._needs_training = False

        else:
            raise ValueError(f"Unknown index type: {self.index_type}")

        Logger.info(f"Initialized FAISS {self.index_type} index (dim={self.dimension})")

    def add_documents(self, documents: list[VectorDocument]) -> list[str]:
        """Add documents to the vector store.

        Args:
            documents: List of VectorDocument objects

        Returns:
            List of added document IDs
        """
        _trace_id = f"faiss_add_{hashlib.sha256(str(id(documents)).encode()).hexdigest()[:16]}"
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "FaissVectorStore.add")

        if not documents:
            return []

        # Prepare vectors
        vectors = np.array([doc.vector for doc in documents], dtype=np.float32)

        # Normalize for cosine similarity
        if self.metric == "cosine":
            import faiss
            faiss.normalize_L2(vectors)

        # Add to FAISS index
        start_idx = self._next_idx

        # Train IVF if needed
        if hasattr(self, '_needs_training') and self._needs_training:
            if not self._index.is_trained:
                Logger.info("Training IVF index...")
                self._index.train(vectors)

        self._index.add(vectors)

        # Store document metadata
        added_ids = []
        for i, doc in enumerate(documents):
            idx = start_idx + i
            self._documents[doc.id] = doc
            self._id_to_idx[doc.id] = idx
            added_ids.append(doc.id)

            # _emit_stores_embedding_fact_vec(_trace_id, doc.id, doc.fact_vec_hash or "")

        self._next_idx += len(documents)

        Logger.info(f"Added {len(documents)} documents to FAISS index (total: {self._next_idx})")

        return added_ids

    def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        filter_fn: callable | None = None,
    ) -> list[dict[str, Any]]:
        """Search for similar vectors.

        Args:
            query_vector: Query embedding vector
            k: Number of results to return
            filter_fn: Optional filter function (doc -> bool)

        Returns:
            List of search results with scores and metadata
        """
        import time
        start_time = time.time()

        _trace_id = f"faiss_search_{self._search_count}"
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "FaissVectorStore.search")

        if self._index is None or self._next_idx == 0:
            return []

        # Prepare query
        query = np.array([query_vector], dtype=np.float32)

        if self.metric == "cosine":
            import faiss
            faiss.normalize_L2(query)

        # Search
        # Use larger k for filtering
        search_k = k * 3 if filter_fn else k
        distances, indices = self._index.search(query, search_k)

        # Build results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue

            # Find document by index
            doc_id = None
            for doc_id_candidate, doc_idx in self._id_to_idx.items():
                if doc_idx == idx:
                    doc_id = doc_id_candidate
                    break

            if doc_id is None or doc_id not in self._documents:
                continue

            doc = self._documents[doc_id]

            # Apply filter
            if filter_fn and not filter_fn(doc):
                continue

            # Convert distance to score
            # For IP/cosine: higher is better (1.0 = identical)
            # For L2: lower is better (0.0 = identical)
            if self.metric in ("cosine", "ip"):
                score = float(dist)
            else:
                score = 1.0 / (1.0 + float(dist))  # Convert L2 to similarity

            results.append({
                "id": doc_id,
                "chunk_id": doc_id,
                "score": score,
                "distance": float(dist),
                "content": doc.content,
                "metadata": doc.metadata,
                "fact_vec_hash": doc.fact_vec_hash,
            })

            if len(results) >= k:
                break

        # Update stats
        elapsed_ms = (time.time() - start_time) * 1000
        self._avg_search_time_ms = (
            self._avg_search_time_ms * self._search_count + elapsed_ms
        ) / (self._search_count + 1)
        self._search_count += 1

        return results

    def delete(self, doc_id: str) -> bool:
        """Delete a document from the store.

        Args:
            doc_id: Document ID to delete

        Returns:
            True if deleted
        """
        if doc_id not in self._documents:
            return False

        # Note: FAISS doesn't support true deletion, we mark as deleted
        del self._documents[doc_id]
        if doc_id in self._id_to_idx:
            del self._id_to_idx[doc_id]

        return True

    def delete_document(self, doc_id: str) -> bool:
        """Alias for delete method."""
        return self.delete(doc_id)

    def get_document(self, doc_id: str) -> VectorDocument | None:
        """Get a document by ID.

        Args:
            doc_id: Document ID

        Returns:
            VectorDocument if found
        """
        return self._documents.get(doc_id)

    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """Normalize vector to unit length.

        Args:
            vector: Input vector

        Returns:
            Normalized vector
        """
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def persist(self, path: str | None = None) -> bool:
        """Persist index and metadata to disk.

        Args:
            path: Path to persist to (defaults to persist_path)

        Returns:
            True if successful
        """
        persist_path = path or self.persist_path
        if persist_path is None:
            return False

        try:
            import faiss

            path_obj = Path(persist_path)
            path_obj.mkdir(parents=True, exist_ok=True)

            # Save FAISS index
            index_path = path_obj / "index.faiss"
            faiss.write_index(self._index, str(index_path))

            # Save metadata
            metadata = {
                "documents": {
                    doc_id: {
                        "id": doc.id,
                        "content": doc.content,
                        "metadata": doc.metadata,
                        "fact_vec_hash": doc.fact_vec_hash,
                        "vector_shape": doc.vector.shape,
                    }
                    for doc_id, doc in self._documents.items()
                },
                "id_to_idx": self._id_to_idx,
                "next_idx": self._next_idx,
                "dimension": self.dimension,
                "index_type": self.index_type,
                "metric": self.metric,
            }

            metadata_path = path_obj / "metadata.pkl"
            with open(metadata_path, "wb") as f:
                pickle.dump(metadata, f)

            Logger.info(f"Persisted FAISS index to {persist_path}")
            return True

        except Exception as e:
            Logger.error(f"Failed to persist FAISS index: {e}")
            return False

    def load(self, path: str | None = None) -> bool:
        """Load index and metadata from disk.

        Args:
            path: Path to load from (defaults to persist_path)

        Returns:
            True if successful
        """
        load_path = path or self.persist_path
        if load_path is None:
            return False

        try:
            import faiss

            path_obj = Path(load_path)

            # Load FAISS index
            index_path = path_obj / "index.faiss"
            if not index_path.exists():
                return False

            self._index = faiss.read_index(str(index_path))

            # Load metadata
            metadata_path = path_obj / "metadata.pkl"
            if metadata_path.exists():
                with open(metadata_path, "rb") as f:
                    metadata = pickle.load(f)

                # Reconstruct documents (vectors not stored, will be loaded from index)
                self._id_to_idx = metadata.get("id_to_idx", {})
                self._next_idx = metadata.get("next_idx", 0)

                # We can't reconstruct vectors from metadata alone
                # Mark for lazy loading or require re-indexing
                Logger.warning("Metadata loaded but vectors not available for lazy loading")

            Logger.info(f"Loaded FAISS index from {load_path}")
            return True

        except Exception as e:
            Logger.error(f"Failed to load FAISS index: {e}")
            return False

    def get_stats(self) -> dict[str, Any]:
        """Get store statistics."""
        return {
            "document_count": len(self._documents),
            "index_type": self.index_type,
            "dimension": self.dimension,
            "metric": self.metric,
            "search_count": self._search_count,
            "avg_search_time_ms": self._avg_search_time_ms,
        }


class FaissEmbeddingStore:
    """High-level embedding store using FAISS backend.

    Provides a simpler interface for storing and retrieving embeddings
    with automatic batching and metadata management.
    """

    def __init__(
        self,
        store_path: str = "artifacts/faiss_store",
        dimension: int = 1024,
        index_type: str = "IVF",
    ):
        """Initialize embedding store.

        Args:
            store_path: Path for persistence
            dimension: Embedding dimension
            index_type: FAISS index type
        """
        self.store = FaissVectorStore(
            dimension=dimension,
            index_type=index_type,
            persist_path=store_path,
        )
        self.store_path = store_path

        # Try to load existing
        self.store.load()

    def store_embedding(
        self,
        chunk_id: str,
        embedding: list[float],
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Store a single embedding.

        Args:
            chunk_id: Unique chunk identifier
            embedding: Vector embedding
            content: Original content
            metadata: Optional metadata

        Returns:
            True if stored successfully
        """
        _trace_id = f"store_{chunk_id}"
        _emit_stores_embedding(_trace_id, chunk_id, len(embedding))

        # Compute fact_vec hash
        vec_bytes = np.array(embedding, dtype=np.float32).tobytes()
        fact_vec_hash = hashlib.sha256(vec_bytes).hexdigest()[:16]

        doc = VectorDocument(
            id=chunk_id,
            vector=np.array(embedding, dtype=np.float32),
            content=content,
            metadata=metadata or {},
            fact_vec_hash=fact_vec_hash,
        )

        self.store.add([doc])
        return True

    def search_similar(
        self,
        query_embedding: list[float],
        top_k: int = 10,
    ) -> list[dict[str, Any]]:
        """Search for similar embeddings.

        Args:
            query_embedding: Query vector
            top_k: Number of results

        Returns:
            List of similar documents with scores
        """
        query_vec = np.array(query_embedding, dtype=np.float32)
        return self.store.search(query_vec, k=top_k)

    def persist(self) -> bool:
        """Persist the store to disk."""
        return self.store.persist()

    def get_stats(self) -> dict[str, Any]:
        """Get store statistics."""
        return self.store.get_stats()


# Global instance
_global_faiss_store: FaissEmbeddingStore | None = None


def get_global_faiss_store() -> FaissEmbeddingStore:
    """Get or create global FAISS store."""
    global _global_faiss_store
    if _global_faiss_store is None:
        _global_faiss_store = FaissEmbeddingStore()
    return _global_faiss_store


def store_embedding(
    chunk_id: str,
    embedding: list[float],
    content: str,
    metadata: dict[str, Any] | None = None,
) -> bool:
    """Convenience function to store embedding."""
    return get_global_faiss_store().store_embedding(
        chunk_id, embedding, content, metadata
    )


def search_similar(
    query_embedding: list[float],
    top_k: int = 10,
) -> list[dict[str, Any]]:
    """Convenience function to search similar."""
    return get_global_faiss_store().search_similar(query_embedding, top_k)
