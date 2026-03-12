"""RetrievalProfile Authority (W4-A/B)

Deterministic, versioned profile for embedder and retrieval configuration.
Stored in L4, read by L1. No behavioral changes - only authority shift.

W4-A: RetrievalProfile Authority (L4 Only)
W4-B: Shadow Embedder wiring for drift detection (non-influential)
D2: embeddings_enabled is always True — BGE is a mandatory system dependency.
"""
from __future__ import annotations
import hashlib
import json
from dataclasses import asdict, dataclass
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

@dataclass(frozen=True, slots=True)
class RetrievalProfile:
    """Deterministic profile for embedder and retrieval configuration.

    W4-A: RetrievalProfile Authority (L4 Only)
    W4-B: Shadow Embedder wiring for drift detection (non-influential)

    This object governs embedder identity and retrieval knobs.
    It is versioned, deterministic, and stored in L4.
    Shadow embedder provides parallel embeddings for telemetry.
    """
    profile_id: str
    primary_embedder_id: str
    embedding_dim: int
    similarity_cutoff: float
    top_k: int
    influence_cap: float
    normalization_policy: str
    shadow_embedder_id: str | None = None
    hybrid_alpha: float | None = None
    embeddings_enabled: bool = True

    def to_canonical_json(self) -> str:
        """Serialize to canonical JSON with deterministic ordering.

        Returns:
            Canonical JSON string with sorted keys and fixed precision.
        """
        data = asdict(self)
        data = {k: v for k, v in data.items() if v is not None}
        for key, value in data.items():
            if isinstance(value, float):
                data[key] = round(value, 6)
        return json.dumps(data, separators=(',', ':'), sort_keys=True)

    @property
    def profile_digest(self) -> str:
        """Compute SHA-256 digest of the canonical JSON.

        Returns:
            64-character hex digest.
        """
        canonical_json = self.to_canonical_json()
        return hashlib.sha256(canonical_json.encode()).hexdigest()

    def emit_digest(self) -> None:
        """Print the profile digest for determinism verification."""
        print(f'W4-PROFILE-DIGEST: {self.profile_digest}')

    @classmethod
    def create_default(cls) -> RetrievalProfile:
        """Create the default RetrievalProfile matching current baseline.

        BGE embeddings are always enabled — mandatory system dependency.

        Returns:
            Default profile with current hardcoded values.
        """
        return cls(profile_id='retrieval-profile-v3', primary_embedder_id='BAAI/bge-m3', embedding_dim=1024, similarity_cutoff=0.75, top_k=10, influence_cap=0.25, normalization_policy='l2', shadow_embedder_id=None, hybrid_alpha=None, embeddings_enabled=True)
__all__ = ['RetrievalProfile']
