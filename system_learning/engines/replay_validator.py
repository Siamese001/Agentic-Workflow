"""ReplayValidator for Plan B Phase 3.

Deterministic validator for seed pack integrity and EmbeddingArtifact stability.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class DeterminismViolationError(Exception):
    """Raised when determinism invariants are violated."""

    pass


class ReplayValidator:
    """Validates deterministic behavior of seed packs and embedding artifacts."""

    def validate_seed_pack(self, *, base_path: str, namespace: str, seed_index_version_hash: str) -> None:
        """Validate seed pack integrity and hash stability.

        Args:
            base_path: Base directory containing seed packs
            namespace: Namespace of the seed pack
            seed_index_version_hash: Expected seed index version hash

        Raises:
            DeterminismViolationError: If any validation fails
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ReplayValidator.validate_seed_pack")

        base = Path(base_path)
        pack_dir = base / "seed_packs" / namespace / seed_index_version_hash
        manifest_path = pack_dir / "seed_manifest.json"
        row_index_path = pack_dir / "row_index.jsonl"
        embeddings_path = pack_dir / "embeddings.f32"
        if not all(p.exists() for p in [manifest_path, row_index_path, embeddings_path]):
            if not pack_dir.exists():
                raise DeterminismViolationError(f"Seed pack directory does not exist: {pack_dir}")
            raise DeterminismViolationError(f"Missing required files in seed pack: {pack_dir}")
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
        with open(row_index_path, "rb") as f:
            row_index_bytes = f.read()
        row_index_hash = hashlib.sha256(row_index_bytes).hexdigest()
        with open(embeddings_path, "rb") as f:
            embeddings_bytes = f.read()
        embeddings_hash = hashlib.sha256(embeddings_bytes).hexdigest()
        if row_index_hash != manifest.get("row_index_hash"):
            raise DeterminismViolationError(
                f"Row index hash mismatch: computed {row_index_hash}, expected {manifest.get('row_index_hash')}"
            )
        if embeddings_hash != manifest.get("matrix_hash"):
            raise DeterminismViolationError(
                f"Embeddings hash mismatch: computed {embeddings_hash}, expected {manifest.get('matrix_hash')}"
            )
        if manifest.get("seed_index_version_hash") != seed_index_version_hash:
            raise DeterminismViolationError(
                f"Seed index version hash mismatch: manifest {manifest.get('seed_index_version_hash')}, expected {seed_index_version_hash}"
            )

    def validate_embedding_artifact(
        self,
        *,
        artifact: Any,
        expected_seed_index_version_hash: str,
        reference_artifact_hash: str | None = None,
    ) -> None:
        """Validate EmbeddingArtifact stability and consistency.

        Args:
            artifact: The EmbeddingArtifact to validate
            expected_seed_index_version_hash: Expected seed index version hash
            reference_artifact_hash: Optional reference hash for comparison

        Raises:
            DeterminismViolationError: If any validation fails
        """
        from system_learning.types.embedding_artifact import EmbeddingArtifact

        if not isinstance(artifact, EmbeddingArtifact):
            raise DeterminismViolationError(f"Expected EmbeddingArtifact, got {type(artifact)}")
        if artifact.seed_index_version_hash != expected_seed_index_version_hash:
            raise DeterminismViolationError(
                f"Seed index version hash mismatch: artifact {artifact.seed_index_version_hash}, expected {expected_seed_index_version_hash}"
            )
        if reference_artifact_hash is not None:
            computed_hash = artifact.artifact_hash()
            if computed_hash != reference_artifact_hash:
                raise DeterminismViolationError(
                    f"Artifact hash mismatch: computed {computed_hash}, expected {reference_artifact_hash}"
                )
        if not artifact.supporting_trace_ids:
            raise DeterminismViolationError("supporting_trace_ids cannot be empty")
        if len(artifact.supporting_trace_ids) != len(set(artifact.supporting_trace_ids)):
            raise DeterminismViolationError("supporting_trace_ids contains duplicates")
        if any(not trace_id for trace_id in artifact.supporting_trace_ids):
            raise DeterminismViolationError("supporting_trace_ids contains empty strings")
        if any(not content_hash for content_hash in artifact.supporting_content_hashes):
            raise DeterminismViolationError("supporting_content_hashes contains empty strings")
        if artifact.k != len(artifact.supporting_trace_ids):
            raise DeterminismViolationError(
                f"k ({artifact.k}) does not match number of trace IDs ({len(artifact.supporting_trace_ids)})"
            )
        if artifact.supporting_trace_ids != sorted(artifact.supporting_trace_ids):
            raise DeterminismViolationError("supporting_trace_ids not in canonical sorted order")
        if artifact.supporting_content_hashes != sorted(artifact.supporting_content_hashes):
            raise DeterminismViolationError("supporting_content_hashes not in canonical sorted order")


__all__ = ["ReplayValidator", "DeterminismViolationError"]
