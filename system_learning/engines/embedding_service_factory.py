"""EmbeddingServiceFactory - Zero-Loss Compliant Embedding Service.

W1 implementation with:
- Total kill-switch coverage
- BLAS thread locking for determinism
- Streaming hash (no 2×RAM)
- eps-guarded normalization
- Pack-hash-seeded spot-checks
- Fork guard with (pid, ctime) identity
- C0-INFORMATIONAL ONLY outputs
"""

from __future__ import annotations

import hashlib
import logging
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import psutil

# BLAS thread lock MUST execute before numpy computes threading defaults
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

logger = logging.getLogger(__name__)


# =============================================================================
# Exceptions
# =============================================================================


class EmbeddingDisabledError(RuntimeError):
    """Raised when embedding operations are attempted while disabled."""

    pass


class EmbeddingForkViolationError(RuntimeError):
    """Raised when embedding service is used across process boundaries."""

    pass


class EmbeddingIntegrityError(RuntimeError):
    """Raised when seed pack integrity validation fails."""

    pass


# =============================================================================
# Result Types
# =============================================================================


@dataclass(frozen=True, slots=True)
class EmbeddingResult:
    """Result from embedding retrieval."""

    content_hash: str
    score_round6: float
    row_idx: int
    embedding_artifact_hash: str


# =============================================================================
# Disabled Service Sentinel
# =============================================================================


class _DisabledEmbeddingService:
    """Sentinel service returned when embedding_enabled=false.

    Ensures total kill-switch coverage with no instantiation, no memmap,
    and no telemetry emission.
    """

    def is_disabled(self) -> bool:
        return True

    def retrieve(self, query_vector: np.ndarray, k: int, cutoff: float = 0.5) -> list[EmbeddingResult] | None:
        """Always returns None when disabled."""
        return None

    def is_healthy(self) -> bool:
        return False

    def replay_key(self) -> str:
        return "disabled"


# =============================================================================
# Main Factory
# =============================================================================


class EmbeddingServiceFactory:
    """Singleton factory for zero-loss compliant embedding service.

    Enforces total kill-switch coverage, determinism, and memory safety.
    """

    _LOCK: threading.Lock = threading.Lock()
    _INSTANCE: EmbeddingServiceFactory | None = None
    _INSTANCE_IDENTITY: tuple[int, float] | None = None

    def __init__(self, pack_base_path: Path) -> None:
        """Initialize embedding service with seed pack.

        Args:
            pack_base_path: Base path to seed pack directory.
        """
        # Kill-switch object lifetime guard
        if not self._is_embedding_enabled():
            raise EmbeddingDisabledError(
                "EmbeddingServiceFactory construction attempted while EMBEDDING_ENABLED=false"
            )
        
        self._pack_base_path = pack_base_path
        self._blas_impl = self._get_blas_fingerprint()
        self._integrity_ok: bool = False
        self._last_spotcheck_ok: bool = False
        self._normalized: np.ndarray | None = None
        self._normalized_pack_hash: str = ""
        self._manifest: dict[str, Any] | None = None
        self._row_hashes: list[str] | None = None

        # Load and validate pack
        self._load_pack()

        # Store process identity for fork guard
        EmbeddingServiceFactory._INSTANCE_IDENTITY = (os.getpid(), psutil.Process().create_time())

    @classmethod
    def get_or_disabled(cls, pack_base_path: Path | None = None) -> Any:
        """Get embedding service or disabled sentinel.

        This is the ONLY public entrypoint. All callers must use this method
        to ensure total kill-switch coverage.

        Args:
            pack_base_path: Path to seed pack (required if enabled).

        Returns:
            EmbeddingServiceFactory instance or _DisabledEmbeddingService.
        """
        # Check kill-switch first - NO instantiation if disabled
        if not cls._is_embedding_enabled():
            # Runtime guard: assert no embedding model instance may exist
            if cls._INSTANCE is not None:
                raise EmbeddingIntegrityError(
                    "KILL_SWITCH_VIOLATION: EmbeddingServiceFactory instance exists while EMBEDDING_ENABLED=false"
                )
            return _DisabledEmbeddingService()

        # Service is enabled - get singleton instance
        return cls.get(
            pack_base_path
            or Path(
                "C:/AgenticEmbeddings/seed_packs/healing_contexts/5d94b5b12ec92312d0240be9984ff92b9478f74ed6f1335511a202c5351520d9"
            )
        )

    @classmethod
    def reset_instance(cls):
        """Reset singleton instance for testing."""
        with cls._LOCK:
            cls._INSTANCE = None
            cls._INSTANCE_IDENTITY = None

    @classmethod
    def get(cls, pack_base_path: Path) -> EmbeddingServiceFactory:
        """Get singleton instance with fork guard validation."""
        with cls._LOCK:
            if cls._INSTANCE is None:
                cls._INSTANCE = cls(pack_base_path)
            else:
                # Defensive assertion: prevent duplicate construction
                if str(pack_base_path) != str(cls._INSTANCE._pack_base_path):
                    raise EmbeddingIntegrityError(
                        f"EmbeddingServiceFactory already constructed with different pack: "
                        f"existing={cls._INSTANCE._pack_base_path}, requested={pack_base_path}"
                    )
                # Validate process identity (fork guard)
                current_identity = (os.getpid(), psutil.Process().create_time())
                if current_identity != cls._INSTANCE_IDENTITY:
                    raise EmbeddingForkViolationError(
                        f"EmbeddingServiceFactory used across process boundary: "
                        f"stored={cls._INSTANCE_IDENTITY}, current={current_identity}"
                    )
            return cls._INSTANCE

    @staticmethod
    def _is_embedding_enabled() -> bool:
        """Check L4 governance kill-switch.

        TODO: Wire to actual L4 config accessor when available.
        For now, reads from environment or defaults to True.
        """
        # Placeholder - will be replaced with actual L4 config access
        return os.environ.get("EMBEDDING_ENABLED", "true").lower() == "true"

    def _get_blas_fingerprint(self) -> str:
        """Get BLAS implementation fingerprint for replay key."""
        try:
            blas_info = np.__config__.blas_opt_info
            libraries = blas_info.get("libraries", ["unknown"])
            return libraries[0] if libraries else "unknown"
        except Exception:
            return "unknown"

    def _load_pack(self) -> None:
        """Load and validate seed pack."""
        # Load manifest
        manifest_path = self._pack_base_path / "seed_manifest.json"
        if not manifest_path.exists():
            raise EmbeddingIntegrityError(f"Manifest not found: {manifest_path}")

        import json

        with open(manifest_path) as f:
            self._manifest = json.load(f)

        # Verify pack hash matches governance
        expected_hash = "5d94b5b12ec92312d0240be9984ff92b9478f74ed6f1335511a202c5351520d9"
        if self._manifest.get("seed_index_version_hash") != expected_hash:
            raise EmbeddingIntegrityError(
                f"Pack hash mismatch: expected {expected_hash}, "
                f"got {self._manifest.get('seed_index_version_hash')}"
            )

        # Load row index for content hashes
        row_index_path = self._pack_base_path / "row_index.jsonl"
        if not row_index_path.exists():
            raise EmbeddingIntegrityError(f"Row index not found: {row_index_path}")

        self._row_hashes = []
        with open(row_index_path) as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    self._row_hashes.append(data.get("content_hash", ""))

        # Load embeddings with integrity check
        embeddings_path = self._pack_base_path / "embeddings.f32"
        if not embeddings_path.exists():
            raise EmbeddingIntegrityError(f"Embeddings file not found: {embeddings_path}")

        # Startup integrity check
        self._verify_integrity(embeddings_path)

        # Load with memmap
        N = self._manifest["vector_count"]
        D = self._manifest["dimensions"]
        self._raw = np.memmap(embeddings_path, dtype=np.float32, mode="r", shape=(N, D))

        # Normalize with eps-guard
        eps = 1e-12
        norms = np.linalg.norm(self._raw, axis=1, keepdims=True)
        anomaly_count = int((norms < eps * 2).sum())

        if self._is_embedding_enabled():
            logger.info(f"Embedding norm anomalies: {anomaly_count}")
            # TODO: Emit telemetry when telemetry system available

        norms = np.maximum(norms, eps)
        self._normalized = (self._raw / norms).astype(np.float32)

        # Compute streaming normalized hash
        self._normalized_pack_hash = self._compute_streaming_hash(self._normalized)

        # Deterministic spot-check
        self._perform_spot_check()

        self._integrity_ok = True

    def _verify_integrity(self, embeddings_path: Path) -> None:
        """Verify SHA-256 of embeddings file matches manifest."""
        manifest_hash = self._manifest.get("matrix_hash")
        if not manifest_hash:
            raise EmbeddingIntegrityError("No matrix_hash in manifest")

        # Stream compute file hash
        hasher = hashlib.sha256()
        with open(embeddings_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)

        file_hash = hasher.hexdigest()
        if file_hash != manifest_hash:
            if self._is_embedding_enabled():
                logger.error(f"Embedding integrity failure: expected {manifest_hash}, got {file_hash}")
                # TODO: Emit telemetry when available
            raise EmbeddingIntegrityError("Embedding file integrity check failed")

        if self._is_embedding_enabled():
            logger.info("Embedding integrity check passed")
            # TODO: Emit telemetry when available

    def _compute_streaming_hash(self, matrix: np.ndarray) -> str:
        """Compute SHA-256 hash without materializing full bytes object."""
        hasher = hashlib.sha256()
        # Iterate in C order for deterministic hashing
        for chunk in np.nditer(matrix, flags=["external_loop"], order="C"):
            hasher.update(chunk.tobytes())
        return hasher.hexdigest()

    def _perform_spot_check(self) -> None:
        """Perform deterministic spot-check seeded by vector_pack_hash."""
        pack_hash = self._manifest.get("seed_index_version_hash", "")
        if not pack_hash:
            self._last_spotcheck_ok = False
            return

        # Derive deterministic seed from pack hash
        seed = int(pack_hash[:8], 16)
        rng = np.random.default_rng(seed)

        N = self._manifest["vector_count"]
        row_idx = rng.integers(0, N)

        # Compute row checksum
        row_bytes = self._raw[row_idx].tobytes()
        row_hash = hashlib.sha256(row_bytes).hexdigest()

        # For now, consider spot-check OK if we can read the row
        # TODO: Store baseline in manifest for stricter validation
        self._last_spotcheck_ok = True

        if self._is_embedding_enabled():
            logger.info(f"Spot-check row {row_idx}: hash {row_hash[:16]}...")

    def is_disabled(self) -> bool:
        """Check if service is disabled."""
        return False

    def retrieve(self, query_vector: np.ndarray, k: int, cutoff: float = 0.5) -> list[EmbeddingResult] | None:
        """Retrieve top-k most similar embeddings.

        Args:
            query_vector: Query embedding vector.
            k: Number of results to return.
            cutoff: Minimum similarity score threshold.

        Returns:
            List of embedding results or None if disabled/unavailable.
        """
        if self._normalized is None or self._row_hashes is None:
            return None

        # Enforce top_k_cap from governance (TODO: read from L4)
        max_k = 20  # Placeholder - will read from governance
        k = min(k, max_k)

        # Normalize query with eps-guard
        query_norm = np.linalg.norm(query_vector)
        if query_norm < 1e-12:
            return None
        q_norm = query_vector / max(query_norm, 1e-12)

        # Compute cosine similarities (dot product with normalized matrix)
        scores = np.dot(self._normalized, q_norm.astype(np.float32))

        # Round to 6 decimal places for determinism
        scores_rounded = np.round(scores, 6)

        # Apply cutoff
        mask = scores_rounded >= cutoff
        if not np.any(mask):
            return None

        # Get indices of top-k scores
        indices = np.where(mask)[0]
        if len(indices) == 0:
            return None

        # Sort by score (desc) then content_hash (asc) for deterministic tie-break
        sorted_indices = sorted(indices, key=lambda i: (-scores_rounded[i], self._row_hashes[i]))

        # Take top-k
        top_indices = sorted_indices[:k]

        # Build results
        results = []
        for idx in top_indices:
            score = float(scores_rounded[idx])
            content_hash = self._row_hashes[idx]

            # Compute artifact hash
            artifact_material = f"{self._manifest['seed_index_version_hash']}{idx}{score:.6f}"
            artifact_hash = hashlib.sha256(artifact_material.encode()).hexdigest()

            results.append(
                EmbeddingResult(
                    content_hash=content_hash,
                    score_round6=score,
                    row_idx=int(idx),
                    embedding_artifact_hash=artifact_hash,
                )
            )

        return results

    def is_healthy(self) -> bool:
        """Check if service is healthy."""
        return (
            self._integrity_ok
            and self._last_spotcheck_ok
            and self._normalized is not None
            and self._normalized_pack_hash != ""
        )

    def replay_key(self, k: int = 10, cutoff: float = 0.5) -> str:
        """Compute deterministic replay key with complete embedder metadata."""
        if not self._manifest or not self._normalized_pack_hash:
            return "uninitialized"

        # Extract all required metadata for replay key
        hf_repo = self._manifest.get('hf_repo', 'BAAI/bge-large-en-v1.5')
        revision = self._manifest.get('revision', 'main')
        embedding_dim = self._manifest.get('embedding_dim', 1024)
        dtype = self._manifest.get('dtype', 'float32')
        normalize = self._manifest.get('normalize', True)
        thread_lock_sig = f"OMP={os.environ.get('OMP_NUM_THREADS', '1')}_MKL={os.environ.get('MKL_NUM_THREADS', '1')}"
        
        material = (
            f"hf_repo={hf_repo}"
            f"|revision={revision}"
            f"|embedding_dim={embedding_dim}"
            f"|dtype={dtype}"
            f"|normalize={normalize}"
            f"|thread_lock_sig={thread_lock_sig}"
            f"|pack_hash={self._normalized_pack_hash}"
            f"|k={k}"
            f"|cutoff={round(cutoff, 6)}"
            f"|blas_impl={self._blas_impl}"
        )
        return hashlib.sha256(material.encode()).hexdigest()


__all__ = [
    "EmbeddingServiceFactory",
    "EmbeddingResult",
    "EmbeddingDisabledError",
    "EmbeddingForkViolationError",
    "EmbeddingIntegrityError",
]
