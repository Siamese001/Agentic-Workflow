"""Embedding exception types — raised at collection write boundaries.

ADR-055: Hard embedding model enforcement.
Plan: .windsurf/plans/bge-m3-gap-closure-c8f3a2.md W3.1
"""

from __future__ import annotations


class EmbeddingProvenanceMismatchError(ValueError):
    """Raised when an embedding write would corrupt collection provenance.

    Fired by ``SovereignChromaClient.add_documents`` when the
    ``embedding_model`` / ``embedding_dim`` supplied with the incoming
    embeddings disagrees with the stamped metadata on the target collection.

    This is a **hard-fail** for the collections listed in
    ``PROVENANCE_ENFORCED_COLLECTIONS`` — a mismatch on those collections is
    always a programming error, never a recoverable condition.

    Attributes:
        collection_name: The target ChromaDB collection.
        expected_model: The ``embedding_model`` already stamped on the collection.
        expected_dim: The ``embedding_dim`` already stamped on the collection.
        actual_model: The ``embedding_model`` asserted by the caller.
        actual_dim: The ``embedding_dim`` asserted by the caller.
    """

    def __init__(
        self,
        *,
        collection_name: str,
        expected_model: str,
        expected_dim: int,
        actual_model: str,
        actual_dim: int,
    ) -> None:
        self.collection_name = collection_name
        self.expected_model = expected_model
        self.expected_dim = expected_dim
        self.actual_model = actual_model
        self.actual_dim = actual_dim
        super().__init__(
            f"Embedding provenance mismatch on collection '{collection_name}': "
            f"collection stamped with model={expected_model!r} dim={expected_dim}, "
            f"but caller supplied model={actual_model!r} dim={actual_dim}. "
            "Re-embed or use the correct embedder. "
            "(ADR-055 hard-fail — see bge-m3-gap-closure-c8f3a2 W3.1)"
        )


# Collections for which a dim/model mismatch raises EmbeddingProvenanceMismatchError
# (hard-fail) rather than only logging a warning.
# Extend this set as more app-owned collections become stable.
# ADR-056: sparse and ColBERT sidecar collections added 2026-05-05.
PROVENANCE_ENFORCED_COLLECTIONS: frozenset[str] = frozenset(
    {
        # Dense (original)
        "apps_qna_interview_cards",
        # ADR-056 — BGE-M3 sparse head sidecar collections
        "apps_qna_interview_cards_sparse",
        # ADR-056 — BGE-M3 ColBERT head sidecar collections
        "apps_qna_interview_cards_colbert",
    }
)


__all__ = [
    "EmbeddingProvenanceMismatchError",
    "PROVENANCE_ENFORCED_COLLECTIONS",
]
