"""
HealingMemoryEmbedder - Convert violation signatures to embeddings.

[PHASE 1] Core Infrastructure Implementation

Provides:
- Violation signature embedding generation
- Healing pattern embedding for semantic retrieval
- Batch embedding support for efficiency
- Fallback to hash-based signatures when embedding unavailable
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "memory_embedder", "L1")
_emit_routes_through("p1", "memory_embedder", "L1")
_emit_escalates_to_human("p1", "memory_embedder", "L1")
_emit_reads_policy_state("p1", "memory_embedder", "L1")


def _get_embedding_sovereign_agent():
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_embedding_sovereign_agent", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_embedding_sovereign_agent", "p0_governance")
    from agentic_core.interfaces.execution_agents import EmbeddingSovereignAgent

    return EmbeddingSovereignAgent


from agentic_core.L1_cognition.types.memory_types import (
    EMBEDDING_DIMENSION,
    MAX_TEXT_LENGTH,
    ViolationSignature,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

Logger = logging.getLogger(__name__)
_embedder_singleton: Any = None


@dataclass
class HealingMemoryEmbedder:
    """
    Convert violation signatures to embeddings for semantic retrieval.

    [PHASE 1] Core Infrastructure Implementation

    Features:
    - Violation signature embedding generation
    - Healing pattern embedding for semantic retrieval
    - Batch embedding support for efficiency
    - Fallback to hash-based signatures when embedding unavailable
    """

    embedding_dimension: int = EMBEDDING_DIMENSION
    max_text_length: int = MAX_TEXT_LENGTH
    _embedding_agent: Any = field(default=None, init=False)
    _initialized: bool = field(default=False, init=False)
    stats: dict[str, int] = field(
        default_factory=lambda: {
            "embeddings_generated": 0,
            "fallback_hashes": 0,
            "batch_operations": 0,
            "errors": 0,
        }
    )

    def __new__(cls, *args, **kwargs):
        """Singleton constructor."""
        global _embedder_singleton
        if _embedder_singleton is None:
            _embedder_singleton = super().__new__(cls)
        return _embedder_singleton

    def __post_init__(self) -> None:
        """Initialize embedding agent."""
        if not self._initialized:
            self._initialize_embedding_agent()
            self._initialized = True

    @classmethod
    def reset_instance(cls) -> None:
        """[TESTING ONLY] Reset singleton state."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L1_REASONING, "HealingMemoryEmbedder.reset_instance"
        )

        global _embedder_singleton
        _embedder_singleton = None

    def _initialize_embedding_agent(self) -> None:
        """Initialize the embedding agent with fallback."""
        try:
            from pathlib import Path

            self._embedding_agent = _get_embedding_sovereign_agent()(Path.cwd())
            Logger.info("[HealingMemoryEmbedder] Embedding agent initialized")
        # guardian: allow-silent-swallow
        except Exception as e:
            raise
            Logger.warning(f"[HealingMemoryEmbedder] Embedding agent unavailable: {e}")
            self._embedding_agent = None

    def embed_violation(self, violation: dict[str, Any]) -> list[float] | None:
        """
        Generate embedding for a violation.

        Args:
            violation: Violation dictionary

        Returns:
            Embedding vector or None if unavailable
        """
        signature = ViolationSignature.from_violation(violation)
        return self.embed_signature(signature)

    def embed_signature(self, signature: ViolationSignature) -> list[float] | None:
        """
        Generate embedding for a violation signature.

        Args:
            signature: ViolationSignature object

        Returns:
            Embedding vector or None if unavailable
        """
        text = signature.to_text()
        try:
            from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text

            embedding = bmg_embed_text(text[: self.max_text_length])
            if embedding:
                self.stats["embeddings_generated"] += 1
                return embedding
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.warning(f"[HealingMemoryEmbedder] Embedding failed: {e}")
            self.stats["errors"] += 1
        self.stats["fallback_hashes"] += 1
        return None

    def embed_healing_pattern(
        self, violation: dict[str, Any], healing_result: dict[str, Any]
    ) -> list[float] | None:
        """
        Generate embedding for a healing pattern (violation + result).

        Args:
            violation: Violation dictionary
            healing_result: Healing result dictionary

        Returns:
            Embedding vector or None if unavailable
        """
        signature = ViolationSignature.from_violation(violation)
        text = signature.to_text()
        result_summary = f" | healing_status: {healing_result.get('status', 'unknown')}"
        if healing_result.get("strategy"):
            result_summary += f" | strategy: {healing_result.get('strategy')}"
        full_text = (text + result_summary)[: self.max_text_length]
        try:
            from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text

            embedding = bmg_embed_text(full_text)
            if embedding:
                self.stats["embeddings_generated"] += 1
                return embedding
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.warning(f"[HealingMemoryEmbedder] Pattern embedding failed: {e}")
            self.stats["errors"] += 1
        self.stats["fallback_hashes"] += 1
        return None

    def embed_batch(self, violations: list[dict[str, Any]]) -> list[list[float] | None]:
        """
        Generate embeddings for multiple violations.

        Args:
            violations: List of violation dictionaries

        Returns:
            List of embedding vectors (None for failures)
        """
        self.stats["batch_operations"] += 1
        results: list[list[float] | None] = []
        for violation in violations:
            embedding = self.embed_violation(violation)
            results.append(embedding)
        return results

    def get_hash_signature(self, violation: dict[str, Any]) -> str:
        """
        Get hash-based signature for a violation (fallback when embedding unavailable).

        Args:
            violation: Violation dictionary

        Returns:
            Hash signature string
        """
        signature = ViolationSignature.from_violation(violation)
        return signature.to_hash()

    def compute_similarity(self, embedding1: list[float], embedding2: list[float]) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (0-1)
        """
        if not embedding1 or not embedding2:
            return 0.0
        if len(embedding1) != len(embedding2):
            Logger.warning("[HealingMemoryEmbedder] Embedding dimension mismatch")
            return 0.0
        dot_product = sum((a * b for a, b in zip(embedding1, embedding2, strict=False)))
        norm1 = sum(a * a for a in embedding1) ** 0.5
        norm2 = sum(b * b for b in embedding2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    def get_stats(self) -> dict[str, Any]:
        """Get current statistics."""
        return {**self.stats, "embedding_available": self._embedding_agent is not None}


_healing_memory_embedder: HealingMemoryEmbedder | None = None


def get_healing_memory_embedder() -> HealingMemoryEmbedder:
    """Get or create the HealingMemoryEmbedder singleton."""
    global _healing_memory_embedder
    if _healing_memory_embedder is None:
        _healing_memory_embedder = HealingMemoryEmbedder()
    return _healing_memory_embedder


def reset_healing_memory_embedder() -> None:
    """[TESTING ONLY] Reset the singleton."""
    global _healing_memory_embedder
    _healing_memory_embedder = None
    HealingMemoryEmbedder.reset_instance()
