"""MetaLearningEmbeddingService for Plan B Phase 2.

Read-only embedding retrieval service that consumes Seed Embedding Packs
and produces deterministic EmbeddingArtifacts.
"""

from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Protocol

from system_learning.engines.embedding_service_factory import EmbeddingServiceFactory
from system_learning.engines.retrieval_profile import RetrievalProfile
from system_learning.types.embedding_artifact import EmbeddingArtifact


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class Embedder(Protocol):
    """Protocol for embedding generation.

    Production embedder will be injected; tests use deterministic stub.
    """

    def embed_batch(self, texts: list[str], dimensions: int) -> list[list[float]]:
        """Embed a batch of texts.

        Args:
            texts: List of texts to embed.
            dimensions: Embedding vector dimensions.

        Returns:
            List of embedding vectors as lists of floats.
        """
        ...


class IntegrityError(Exception):
    """Raised when seed pack integrity validation fails."""

    pass


class MetaLearningEmbeddingService:
    """Read-only embedding retrieval service for Seed Embedding Packs."""

    def __init__(self, base_path: str, embedder: Embedder | None = None):
        """Initialize the service.

        Args:
            base_path: Base directory containing seed packs.
            embedder: Embedder instance for query embedding. If None, a live OpenAI client is created.
        """
        self.base_path = Path(base_path)
        self._embedder_injected = embedder is not None
        if embedder:
            self.embedder = embedder
        else:
            raise RuntimeError(
                "MetaLearningEmbeddingService requires an explicit embedder injection. "
                "No live embedding client factory is available."
            )
        # Initialize factory (will return disabled sentinel if kill-switch is off)
        # When embedder is explicitly injected, factory is not used for kill-switch
        self._factory = EmbeddingServiceFactory.get_or_disabled()

    def retrieve(
        self,
        *,
        namespace: str,
        seed_index_version_hash: str,
        query_text: str,
        profile: RetrievalProfile | None = None,
        k: int | None = None,
    ) -> EmbeddingArtifact | None:
        """Retrieve top-k embeddings for a query.

        Args:
            namespace: Namespace of the seed pack.
            seed_index_version_hash: Version hash of the seed pack.
            query_text: Query text to embed.
            k: Number of results to retrieve.

        Returns:
            EmbeddingArtifact with results, or None if pack doesn't exist or disabled.

        Raises:
            IntegrityError: If pack integrity validation fails.
        """
        # Check if embedding service is disabled
        # When embedder is explicitly injected, bypass kill-switch (test/offline mode)
        if not self._embedder_injected and self._factory.is_disabled():
            return None

        # Resolve pack directory
        pack_dir = self.base_path / "seed_packs" / namespace / seed_index_version_hash

        # Missing pack - neutral behavior
        if not pack_dir.exists():
            return None

        # Load and validate pack
        manifest, row_data, embeddings_matrix = self._load_and_validate_pack(
            pack_dir, seed_index_version_hash
        )

        # FAISS Dimension Migration Guard
        if profile is not None and manifest["dimensions"] != profile.embedding_dim:
            raise IntegrityError(
                f"FAISS dimension mismatch: manifest={manifest['dimensions']}, "
                f"profile={profile.embedding_dim}. Rebuild seed pack for this profile."
            )

        # Embed query
        query_vecs = self.embedder.embed_batch([query_text], dimensions=manifest["dimensions"])
        query_vec = query_vecs[0]

        # Compute similarities and rank
        candidates = self._compute_similarities(query_vec, row_data, embeddings_matrix)

        # Sort deterministically and select top-k
        sorted_candidates = sorted(candidates, key=lambda x: (-x["score"], x["content_hash"], x["trace_id"]))

        effective_k = (
            k if k is not None else (profile.top_k if profile is not None else len(sorted_candidates))
        )
        top_k = sorted_candidates[:effective_k]

        # Build EmbeddingArtifact
        return EmbeddingArtifact(
            namespace=namespace,
            seed_index_version_hash=seed_index_version_hash,
            supporting_trace_ids=[c["trace_id"] for c in top_k],
            supporting_content_hashes=[c["content_hash"] for c in top_k],
            k=len(top_k),
            similarity_metric="cosine",
            embedding_model_version=manifest["embedding_model_version"],
        )

    def _load_and_validate_pack(
        self,
        pack_dir: Path,
        seed_index_version_hash: str,
    ) -> tuple[dict[str, Any], list[dict[str, Any]], list[list[float]]]:
        """Load and validate seed pack integrity.

        Args:
            pack_dir: Directory containing the seed pack.
            seed_index_version_hash: Expected version hash.

        Returns:
            Tuple of (manifest, row_data, embeddings_matrix).

        Raises:
            IntegrityError: If validation fails.
        """
        # Load files
        manifest_path = pack_dir / "seed_manifest.json"
        row_index_path = pack_dir / "row_index.jsonl"
        embeddings_path = pack_dir / "embeddings.f32"

        if not all(p.exists() for p in [manifest_path, row_index_path, embeddings_path]):
            raise IntegrityError(f"Missing required files in seed pack: {pack_dir}")

        # Read raw bytes for hash validation
        row_index_bytes = row_index_path.read_bytes()
        embeddings_bytes = embeddings_path.read_bytes()

        # Load manifest
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

        # Validate manifest hash
        if manifest.get("seed_index_version_hash") != seed_index_version_hash:
            raise IntegrityError(
                f"Seed index version hash mismatch: "
                f"manifest {manifest.get('seed_index_version_hash')}, "
                f"expected {seed_index_version_hash}"
            )

        # Validate file hashes
        row_index_hash = hashlib.sha256(row_index_bytes).hexdigest()
        if row_index_hash != manifest.get("row_index_hash"):
            raise IntegrityError(
                f"Row index hash mismatch: computed {row_index_hash}, "
                f"expected {manifest.get('row_index_hash')}"
            )

        embeddings_hash = hashlib.sha256(embeddings_bytes).hexdigest()
        if embeddings_hash != manifest.get("matrix_hash"):
            raise IntegrityError(
                f"Embeddings hash mismatch: computed {embeddings_hash}, "
                f"expected {manifest.get('matrix_hash')}"
            )

        # Parse row_index.jsonl
        row_data = []
        for line in row_index_bytes.decode("utf-8").strip().split("\n"):
            if line:
                row_data.append(json.loads(line))

        # Parse embeddings.f32
        dimensions = manifest["dimensions"]
        vector_count = manifest["vector_count"]

        if len(embeddings_bytes) != vector_count * dimensions * 4:
            raise IntegrityError(
                f"Embeddings file size mismatch: expected {vector_count * dimensions * 4} bytes, "
                f"got {len(embeddings_bytes)}"
            )

        # Parse little-endian float32 matrix
        embeddings_matrix = []
        for i in range(vector_count):
            offset = i * dimensions * 4
            vector = []
            for j in range(dimensions):
                byte_offset = offset + j * 4
                # Unpack little-endian float32
                value = struct.unpack("<f", embeddings_bytes[byte_offset : byte_offset + 4])[0]
                vector.append(value)
            embeddings_matrix.append(vector)

        return manifest, row_data, embeddings_matrix

    def _compute_similarities(
        self,
        query_vec: list[float],
        row_data: list[dict[str, Any]],
        embeddings_matrix: list[list[float]],
    ) -> list[dict[str, Any]]:
        """Compute cosine similarities between query and all embeddings.

        Args:
            query_vec: Query embedding vector.
            row_data: Parsed row index data.
            embeddings_matrix: Embedding vectors matrix.

        Returns:
            List of candidates with similarity scores.
        """
        if not embeddings_matrix:
            return []

        import numpy as np

        q = np.array(query_vec, dtype=np.float32)
        q_norm = np.linalg.norm(q)
        if q_norm == 0:
            return []
        q_unit = q / q_norm

        matrix = np.array(embeddings_matrix, dtype=np.float32)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        # Zero-norm guard: keep rows with non-zero norms
        valid_mask = (norms[:, 0] > 0)
        matrix_unit = np.where(norms > 0, matrix / np.maximum(norms, 1e-12), 0.0)
        scores = matrix_unit @ q_unit

        candidates = []
        for i, row in enumerate(row_data):
            if not valid_mask[i]:
                continue
            candidates.append(
                {
                    "score": float(scores[i]),
                    "trace_id": row["trace_id"],
                    "content_hash": row["content_hash"],
                    "row_id": row["row_id"],
                }
            )

        return candidates


__all__ = ["MetaLearningEmbeddingService", "IntegrityError"]
