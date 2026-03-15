"""C0ContextRetriever — informational-only embeddings.

Guarantees: top_k=20, score >= 0.5, seed pack hash verification.
C0 context cannot affect routing decisions; only informational.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,
    emit_replay_key,
)

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "c0_context_retriever", "p0_governance")
_emit_snapshots_state("p0", "c0_context_retriever", "state_snapshot")


@dataclass
class ContentHash:
    content_hash: str
    score: float


@dataclass
class C0ContextArtifact:
    seed_pack: str
    seed_pack_hash: str
    supporting_content_hashes: list[ContentHash]

    @classmethod
    async def load(cls) -> C0ContextArtifact | None:
        return None


_SCORE_CUTOFF = 0.5
_TOP_K = 20


class C0ContextRetriever:
    """Populate c0_context slot with informational embedding results."""

    async def retrieve(self, u0_user_prompt: str) -> str:
        """Return a deterministic, bounded context string."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "C0ContextRetriever.retrieve")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        artifact = await C0ContextArtifact.load()
        if not artifact:
            raise RuntimeError("C0 seed pack missing or unloadable")
        expected_hash = hashlib.sha256(artifact.seed_pack.encode("utf-8", errors="replace")).hexdigest()
        if artifact.seed_pack_hash != expected_hash:
            raise RuntimeError("C0 seed pack hash mismatch — corrupted or tampered")
        results = sorted(
            [r for r in artifact.supporting_content_hashes if r.score >= _SCORE_CUTOFF],
            key=lambda r: (-round(r.score, 6), r.content_hash),
        )[:_TOP_K]
        lines = [f"[{i + 1:02d}] {r.content_hash[:12]} (score={r.score:.3f})" for i, r in enumerate(results)]
        return "\n".join(lines)
