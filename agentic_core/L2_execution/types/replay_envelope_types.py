"""
Canonical Replay Envelope for Universal Determinism

Provides a stable, canonical representation of all generation and embedding
flows to make semantic drift observable across runs.
"""

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


@dataclass(frozen=True)
class ReplayEnvelope:
    """Canonical replay envelope for deterministic generation tracking."""

    routing_hash: str
    manifest_hash: str
    model_id: str
    model_version: str
    temperature: float
    allowed_model_policy_version: str
    policy_version: str
    gateway_version: str
    embedder_provider: str
    embedder_model: str
    embedder_dim: int
    normalization_policy: str
    chunking_policy: str
    distance_metric: str
    retrieval_top_k: int
    retrieval_similarity_cutoff: float
    agent_registry_hash: str
    deterministic_engine_version: str
    code_commit_hash: str | None = None

    def to_canonical_json(self) -> str:
        """Generate canonical JSON representation with deterministic ordering."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ReplayEnvelope.to_canonical_json")
        import hashlib as _hashlib  # noqa: PLC0415
        _seg_hash = _hashlib.sha256(f"{_trace_id}:ReplayEnvelope.to_canonical_json".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {k: v for k, v in asdict(self).items() if v is not None}
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    def get_digest(self) -> str:
        """Get SHA256 digest of canonical JSON representation."""
        canonical_json = self.to_canonical_json()
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    @classmethod
    def from_generation_context(
        cls,
        routing_hash: str,
        manifest_hash: str,
        model_id: str,
        model_version: str,
        temperature: float,
        policy_version: str,
        gateway_version: str,
        embedder_provider: str,
        embedder_model: str,
        embedder_dim: int,
        agent_registry_hash: str,
        deterministic_engine_version: str,
        allowed_model_policy_version: str = "1.0",
        normalization_policy: str = "l2",
        chunking_policy: str = "semantic",
        distance_metric: str = "cosine",
        retrieval_top_k: int = 10,
        retrieval_similarity_cutoff: float = 0.7,
        code_commit_hash: str | None = None,
    ) -> "ReplayEnvelope":
        """Create ReplayEnvelope from generation context parameters."""
        return cls(
            routing_hash=routing_hash,
            manifest_hash=manifest_hash,
            model_id=model_id,
            model_version=model_version,
            temperature=temperature,
            allowed_model_policy_version=allowed_model_policy_version,
            policy_version=policy_version,
            gateway_version=gateway_version,
            embedder_provider=embedder_provider,
            embedder_model=embedder_model,
            embedder_dim=embedder_dim,
            normalization_policy=normalization_policy,
            chunking_policy=chunking_policy,
            distance_metric=distance_metric,
            retrieval_top_k=retrieval_top_k,
            retrieval_similarity_cutoff=retrieval_similarity_cutoff,
            agent_registry_hash=agent_registry_hash,
            deterministic_engine_version=deterministic_engine_version,
            code_commit_hash=code_commit_hash,
        )


def create_deterministic_cache_key(text: str, embedder_identity: dict[str, Any]) -> str:
    """Create deterministic cache key for embeddings."""
    canonical_embedder_json = json.dumps(embedder_identity, sort_keys=True, separators=(",", ":"))
    combined = f"{text}:{canonical_embedder_json}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()
