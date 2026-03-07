"""
Phase A: Completeness-Aware Reranker.

Reranks candidates using a blended score of:
  relevance_score  (from retrieval — cosine/BM25)
  completeness_score (from IContextCompletenessScorer)

Does NOT promote fragments purely on similarity when completeness is low.

C0 RULE: Informational only — cannot alter routing, safety, or tiers.
"""

from __future__ import annotations

from dataclasses import dataclass

from agentic_core.evaluation.retrieval.completeness import (
    ContextCompletenessScore,
    IContextCompletenessScorer,
)
from agentic_core.evaluation.retrieval.interfaces import Document, IReranker


@dataclass(frozen=True)
class CompletenessRerankerConfig:
    """Configuration for the blended relevance + completeness reranker."""

    relevance_weight: float = 0.6
    completeness_weight: float = 0.4
    top_k: int = 10

    def __post_init__(self) -> None:
        total = self.relevance_weight + self.completeness_weight
        if abs(total - 1.0) > 1e-9:
            raise ValueError(f"relevance_weight + completeness_weight must sum to 1.0, got {total}")
        if self.top_k < 1:
            raise ValueError("top_k must be >= 1")


class CompletenessReranker(IReranker):
    """Reranks candidates by blending relevance with completeness scores.

    Prevents high-similarity but contextually incomplete fragments from
    dominating the final top-N context.

    C0 RULE: Output is informational top-N grounded context only.
    """

    def __init__(
        self,
        scorer: IContextCompletenessScorer,
        config: CompletenessRerankerConfig | None = None,
        query_id: str = "default",
    ) -> None:
        self._scorer = scorer
        self._cfg = config or CompletenessRerankerConfig()
        self._query_id = query_id

    def rerank(self, query: str, candidates: list[Document]) -> list[Document]:
        """Rerank candidates using blended relevance + completeness score.

        Args:
            query: Original query text used for completeness scoring.
            candidates: Documents to rerank (may be GroundedDocuments).

        Returns:
            Top-K reranked list, highest blended score first.
            Deterministic tie-break: doc_id ascending.
        """
        if not candidates:
            return []

        completeness_scores: list[ContextCompletenessScore] = self._scorer.score_batch(
            query_id=self._query_id,
            query=query,
            chunks=candidates,
        )

        scored: list[tuple[float, str, Document]] = []
        for doc, cs in zip(candidates, completeness_scores):
            blended = (
                self._cfg.relevance_weight * doc.score + self._cfg.completeness_weight * cs.completeness_score
            )
            scored.append((blended, doc.doc_id, doc))

        scored.sort(key=lambda t: (-t[0], t[1]))
        return [doc for _, _, doc in scored[: self._cfg.top_k]]


__all__ = [
    "CompletenessRerankerConfig",
    "CompletenessReranker",
]
