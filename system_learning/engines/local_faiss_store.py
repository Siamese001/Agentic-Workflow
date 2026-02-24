"""LocalFAISSStore - Plan A deterministic FAISS index storage.

Read-only contract surfaces for Plan B consumption.
FAISS import is lazy to support unit_min_deps environments without optional dependencies.
"""

from __future__ import annotations

import hashlib
import json
import math
import struct
from pathlib import Path
from typing import Any

from system_learning.types.index_build_metadata_types import IndexBuildMetadata


class IndexNotBuiltError(RuntimeError):
    """Raised when attempting to access an index that has not been built."""

    pass


class IndexMetadataError(RuntimeError):
    """Raised when index metadata is missing or corrupted."""

    pass


class LocalFAISSStore:
    """Local FAISS index store with deterministic search.

    INVARIANT: FAISS is imported lazily inside methods only.
    INVARIANT: search() post-sorts results deterministically: (score_round6 DESC, content_hash ASC).
    INVARIANT: In-memory fallback enables unit_min_deps tests without faiss.
    """

    def __init__(self, base_path: Path) -> None:
        """Initialize store with base path for indexes.

        Args:
            base_path: Base directory for index storage.
        """
        self.base_path = base_path
        # In-memory fallback for unit_min_deps
        self._memory_indexes: Dict[str, Dict[str, Any]] = {}
        # Track rebuild requirement
        self._rebuild_required: Dict[str, bool] = {}

    def open(self, index_id: str) -> tuple[Any, str, IndexBuildMetadata]:
        """Open an index and return handle with metadata.

        Args:
            index_id: Identifier of the index to open.

        Returns:
            Tuple of (index_handle, index_version_hash, build_metadata).

        Raises:
            IndexNotBuiltError: If index has not been built or needs rebuild.
            IndexMetadataError: If metadata is missing or invalid.
        """
        # Check if rebuild is required
        if self._rebuild_required.get(index_id, False):
            raise IndexNotBuiltError(f"Index {index_id} requires rebuild after pruning")

        # Lazy import FAISS only when needed
        try:
            import importlib.util
            if importlib.util.find_spec("faiss") is None:
                raise ImportError("FAISS not available")
            # Real FAISS implementation would go here
        except ImportError:
            # Use in-memory fallback
            if index_id not in self._memory_indexes:
                raise IndexNotBuiltError(f"Index {index_id} not built (in-memory fallback)")
            memory_idx = self._memory_indexes[index_id]
            return (memory_idx["vectors"], memory_idx["version_hash"], memory_idx["metadata"])

        # Phase 1: NotImplementedError for real FAISS
        raise NotImplementedError("LocalFAISSStore.open() - Phase 1 skeleton")

    def search(
        self,
        index_id: str,
        query_vector: List[float],
        top_k: int,
        cutoff: float,
    ) -> List[Tuple[str, str, float]]:
        """Search index for similar vectors.

        Args:
            index_id: Identifier of the index to search.
            query_vector: Query embedding vector.
            top_k: Maximum number of results to return.
            cutoff: Minimum similarity score threshold.

        Returns:
            List of (content_hash, trace_id, score_round6) tuples.
            Results are post-sorted deterministically: (score_round6 DESC, content_hash ASC).

        Raises:
            IndexNotBuiltError: If index has not been built or needs rebuild.
        """
        # Check if rebuild is required
        if self._rebuild_required.get(index_id, False):
            raise IndexNotBuiltError(f"Index {index_id} requires rebuild after pruning")

        # Lazy import FAISS only when needed
        try:
            import importlib.util

            if importlib.util.find_spec("faiss") is None:
                raise ImportError("FAISS not available")
            # Real FAISS implementation would go here
        except ImportError:
            # Use in-memory fallback with cosine similarity
            if index_id not in self._memory_indexes:
                raise IndexNotBuiltError(f"Index {index_id} not built (in-memory fallback)")

            memory_idx = self._memory_indexes[index_id]
            vectors = memory_idx["vectors"]
            metadatas = memory_idx["metadatas"]

            # Normalize query vector
            query_norm = math.sqrt(sum(x * x for x in query_vector))
            if query_norm == 0:
                query_vec = query_vector
            else:
                query_vec = [x / query_norm for x in query_vector]

            # Compute cosine similarities
            results = []
            for i, vec in enumerate(vectors):
                # Dot product (vectors are normalized)
                score = sum(q * v for q, v in zip(query_vec, vec))
                if score >= cutoff:
                    metadata = metadatas[i]
                    content_hash = metadata.get("content_hash", "")
                    trace_id = metadata.get("trace_id", "")
                    score_round6 = round(score, 6)
                    results.append((content_hash, trace_id, score_round6))

            # Post-sort deterministically
            results.sort(key=lambda x: (-x[2], x[0]))  # score DESC, content_hash ASC
            return results[:top_k]

        # Phase 1: NotImplementedError for real FAISS
        raise NotImplementedError("LocalFAISSStore.search() - Phase 1 skeleton")

    def begin_build(self, index_id: str, dimension: int, seed: int) -> None:
        """Begin building a new index.

        Args:
            index_id: Identifier for the index.
            dimension: Embedding dimension.
            seed: Random seed for deterministic builds.
        """
        # Lazy import FAISS only when needed
        try:
            import importlib.util

            if importlib.util.find_spec("faiss") is None:
                raise ImportError("FAISS not available")
            # Real FAISS implementation would go here
        except ImportError:
            # Use in-memory fallback
            self._memory_indexes[index_id] = {
                "dimension": dimension,
                "seed": seed,
                "vectors": [],
                "metadatas": [],
            }
            return

        # Phase 2: NotImplementedError for real FAISS
        raise NotImplementedError("LocalFAISSStore.begin_build() - Phase 2 skeleton")

    def add_vectors(self, index_id: str, vectors: list[list[float]], metadatas: list[dict[str, Any]]) -> None:
        """Add vectors to the index being built.

        Args:
            index_id: Identifier for the index.
            vectors: List of embedding vectors.
            metadatas: List of metadata dictionaries.

        Raises:
            IndexNotBuiltError: If index build has not been started.
        """
        # Lazy import FAISS only when needed
        try:
            import importlib.util

            if importlib.util.find_spec("faiss") is None:
                raise ImportError("FAISS not available")
            # Real FAISS implementation would go here
        except ImportError:
            # Use in-memory fallback
            if index_id not in self._memory_indexes:
                raise IndexNotBuiltError(f"Index {index_id} build not started (in-memory fallback)")

            memory_idx = self._memory_indexes[index_id]
            memory_idx["vectors"].extend(vectors)
            memory_idx["metadatas"].extend(metadatas)
            return

        # Phase 2: NotImplementedError for real FAISS
        raise NotImplementedError("LocalFAISSStore.add_vectors() - Phase 2 skeleton")

    def finalize_build(
        self,
        index_id: str,
        *,
        built_at_utc: int,
        canonicalization_version: str,
        embedding_model_version: str,
        embedding_model_checksum: str,
    ) -> IndexBuildMetadata:
        """Finalize index build and return metadata.

        Args:
            index_id: Identifier for the index.
            built_at_utc: Build timestamp.
            canonicalization_version: Canonicalization format version.
            embedding_model_version: Embedding model version.
            embedding_model_checksum: Embedding model checksum.

        Returns:
            IndexBuildMetadata for the completed index.

        Raises:
            IndexNotBuiltError: If index build has not been started.
        """
        # Lazy import FAISS only when needed
        try:
            import importlib.util

            if importlib.util.find_spec("faiss") is None:
                raise ImportError("FAISS not available")
            # Real FAISS implementation would go here
        except ImportError:
            # Use in-memory fallback
            if index_id not in self._memory_indexes:
                raise IndexNotBuiltError(f"Index {index_id} build not started (in-memory fallback)")

            memory_idx = self._memory_indexes[index_id]
            vectors = memory_idx["vectors"]
            metadatas = memory_idx["metadatas"]

            # Compute deterministic index_version_hash
            hash_input = []
            for i, (vec, meta) in enumerate(zip(vectors, metadatas)):
                # Convert vector to little-endian float32 bytes
                vector_bytes = b"".join(struct.pack("<f", x) for x in vec)
                # Create canonical entry
                entry = {
                    "content_hash": meta.get("content_hash", ""),
                    "trace_id": meta.get("trace_id", ""),
                    "vector_bytes": vector_bytes.hex(),  # Store as hex for JSON serialization
                }
                entry_bytes = json.dumps(
                    entry,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=True,
                ).encode("ascii")
                hash_input.append(entry_bytes)

            # Compute SHA-256 over all entries
            hasher = hashlib.sha256()
            for entry_bytes in sorted(hash_input):  # Sort for determinism
                hasher.update(entry_bytes)
            index_version_hash = hasher.hexdigest()

            # Create metadata
            metadata = IndexBuildMetadata(
                index_id=index_id,
                faiss_version="memory-fallback-v1",
                build_seed=memory_idx["seed"],
                canonicalization_version=canonicalization_version,
                embedding_model_version=embedding_model_version,
                embedding_model_checksum=embedding_model_checksum,
                built_at_utc=built_at_utc,
                index_version_hash=index_version_hash,
                vector_count=len(vectors),
                dimension=memory_idx["dimension"],
            )

            # Store metadata in memory
            memory_idx["metadata"] = metadata
            memory_idx["version_hash"] = index_version_hash

            return metadata

        # Phase 2: NotImplementedError for real FAISS
        raise NotImplementedError("LocalFAISSStore.finalize_build() - Phase 2 skeleton")

    def prune(self, index_id: str, predicate: Callable[[Dict[str, Any]], bool]) -> int:
        """Prune vectors from index based on predicate.

        Args:
            index_id: Identifier for the index.
            predicate: Function that returns True for items to prune.

        Returns:
            Number of items removed.

        Raises:
            IndexNotBuiltError: If index has not been built.
        """
        # Lazy import FAISS only when needed
        try:
            import importlib.util
            if importlib.util.find_spec("faiss") is None:
                raise ImportError("FAISS not available")
            # Real FAISS implementation would go here
        except ImportError:
            # Use in-memory fallback
            if index_id not in self._memory_indexes:
                raise IndexNotBuiltError(f"Index {index_id} not built (in-memory fallback)")

            memory_idx = self._memory_indexes[index_id]
            vectors = memory_idx["vectors"]
            metadatas = memory_idx["metadatas"]

            # Find items to prune
            to_keep = []
            removed_count = 0

            for i, metadata in enumerate(metadatas):
                if predicate(metadata):
                    removed_count += 1
                else:
                    to_keep.append(i)

            # Rebuild arrays without pruned items
            if removed_count > 0:
                memory_idx["vectors"] = [vectors[i] for i in to_keep]
                memory_idx["metadatas"] = [metadatas[i] for i in to_keep]
                # Mark rebuild as required
                self._rebuild_required[index_id] = True

            return removed_count

        # Phase 4: NotImplementedError for real FAISS
        raise NotImplementedError("LocalFAISSStore.prune() - Phase 4 skeleton")

    def rebuild(
        self,
        index_id: str,
        *,
        built_at_utc: int,
        canonicalization_version: str,
        embedding_model_version: str,
        embedding_model_checksum: str,
    ) -> IndexBuildMetadata:
        """Rebuild index after pruning.

        Args:
            index_id: Identifier for the index.
            built_at_utc: Build timestamp.
            canonicalization_version: Canonicalization format version.
            embedding_model_version: Embedding model version.
            embedding_model_checksum: Embedding model checksum.

        Returns:
            IndexBuildMetadata for the rebuilt index.

        Raises:
            IndexNotBuiltError: If index has not been built.
        """
        # Lazy import FAISS only when needed
        try:
            import importlib.util
            if importlib.util.find_spec("faiss") is None:
                raise ImportError("FAISS not available")
            # Real FAISS implementation would go here
        except ImportError:
            # Use in-memory fallback
            if index_id not in self._memory_indexes:
                raise IndexNotBuiltError(f"Index {index_id} not built (in-memory fallback)")

            memory_idx = self._memory_indexes[index_id]
            vectors = memory_idx["vectors"]
            metadatas = memory_idx["metadatas"]

            # Compute deterministic index_version_hash for remaining items
            hash_input = []
            for i, (vec, meta) in enumerate(zip(vectors, metadatas)):
                # Convert vector to little-endian float32 bytes
                vector_bytes = b"".join(struct.pack("<f", x) for x in vec)
                # Create canonical entry
                entry = {
                    "content_hash": meta.get("content_hash", ""),
                    "trace_id": meta.get("trace_id", ""),
                    "vector_bytes": vector_bytes.hex(),  # Store as hex for JSON serialization
                }
                entry_bytes = json.dumps(
                    entry,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=True,
                ).encode("ascii")
                hash_input.append(entry_bytes)

            # Compute SHA-256 over all entries
            hasher = hashlib.sha256()
            for entry_bytes in sorted(hash_input):  # Sort for determinism
                hasher.update(entry_bytes)
            index_version_hash = hasher.hexdigest()

            # Create metadata
            metadata = IndexBuildMetadata(
                index_id=index_id,
                faiss_version="memory-fallback-v1",
                build_seed=memory_idx["seed"],
                canonicalization_version=canonicalization_version,
                embedding_model_version=embedding_model_version,
                embedding_model_checksum=embedding_model_checksum,
                built_at_utc=built_at_utc,
                index_version_hash=index_version_hash,
                vector_count=len(vectors),
                dimension=memory_idx["dimension"],
            )

            # Update stored metadata and clear rebuild flag
            memory_idx["metadata"] = metadata
            memory_idx["version_hash"] = index_version_hash
            self._rebuild_required[index_id] = False

            return metadata

        # Phase 4: NotImplementedError for real FAISS
        raise NotImplementedError("LocalFAISSStore.rebuild() - Phase 4 skeleton")


__all__ = ["LocalFAISSStore", "IndexNotBuiltError", "IndexMetadataError"]
