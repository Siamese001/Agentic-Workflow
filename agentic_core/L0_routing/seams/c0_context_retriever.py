"""C0ContextRetriever — informational-only embeddings.

Guarantees: top_k=20, score >= 0.5, seed pack hash verification.
C0 context cannot affect routing decisions; only informational.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass


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
