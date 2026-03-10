"""EmbeddingArtifact type for Plan B Phase 1.

Deterministic, replay-stable artifact representation with canonical bytes and hash.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Literal


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@dataclass(frozen=True)
class EmbeddingArtifact:
    """Deterministic embedding artifact with canonical bytes and hash.

    Informational-only type that captures embedding metadata in a deterministic
    and replay-stable format. Fully compliant with Governance Memory v5.
    """

    namespace: str
    seed_index_version_hash: str
    supporting_trace_ids: list[str]
    supporting_content_hashes: list[str]
    k: int
    similarity_metric: str
    embedding_model_version: str
    vector: list[float] = field(default_factory=list, repr=False)  # Exclude from default repr
    vector_hash: str = field(default="", init=False)
    influence_class: Literal["C0_INFORMATIONAL"] = field(default="C0_INFORMATIONAL", init=False)

    def __post_init__(self) -> None:
        """Enforce invariants after initialization."""
        # Ensure supporting_trace_ids is in deterministic order
        if not hasattr(self, "_trace_ids_sorted"):
            # Convert to tuple to enforce immutability and sort canonically
            sorted_trace_ids = tuple(sorted(self.supporting_trace_ids))
            if tuple(self.supporting_trace_ids) != sorted_trace_ids:
                object.__setattr__(self, "supporting_trace_ids", list(sorted_trace_ids))

        # Ensure supporting_content_hashes is in deterministic order
        if not hasattr(self, "_content_hashes_sorted"):
            sorted_content_hashes = tuple(sorted(self.supporting_content_hashes))
            if tuple(self.supporting_content_hashes) != sorted_content_hashes:
                object.__setattr__(self, "supporting_content_hashes", list(sorted_content_hashes))

        # Compute hash of the vector for deterministic inclusion in canonical form
        if self.vector:
            vector_bytes = json.dumps(self.vector, sort_keys=True, separators=(",", ":")).encode("utf-8")
            object.__setattr__(self, "vector_hash", hashlib.sha256(vector_bytes).hexdigest())

    def canonical_bytes(self) -> bytes:
        """Return canonical UTF-8 bytes representation.

        Requirements:
        - UTF-8 encoding
        - Minified JSON
        - Deterministic key order
        - Lists serialized in their stored order (already deterministic)
        - No whitespace variance

        Returns:
            Canonical bytes representation of the artifact.
        """
        # Create dictionary with deterministic key order
        data = {
            "namespace": self.namespace,
            "seed_index_version_hash": self.seed_index_version_hash,
            "supporting_trace_ids": self.supporting_trace_ids,
            "supporting_content_hashes": self.supporting_content_hashes,
            "k": self.k,
            "similarity_metric": self.similarity_metric,
            "embedding_model_version": self.embedding_model_version,
            "vector_hash": self.vector_hash,
        }

        # Serialize to minified JSON with deterministic key order
        json_str = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

        # Return UTF-8 bytes
        return json_str.encode("utf-8")

    def artifact_hash(self) -> str:
        """Compute SHA-256 hash of canonical bytes.

        Returns:
            SHA-256 hash of canonical_bytes as hex string.
        """
        canonical = self.canonical_bytes()
        return hashlib.sha256(canonical).hexdigest()

    def assert_non_authoritative(self) -> None:
        """Raise an error if the artifact is used in an authoritative context."""
        if self.influence_class != "C0_INFORMATIONAL":
            raise ValueError("EmbeddingArtifact cannot be used in an authoritative context.")


__all__ = ["EmbeddingArtifact"]
