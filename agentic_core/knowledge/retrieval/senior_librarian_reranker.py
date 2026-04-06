"""Senior Librarian Reranker.

Advanced reranking with scoring, coverage evaluation, and evidence-based ranking.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


@dataclass
class RerankResult:
    """Result after reranking."""
    doc_id: str
    original_score: float
    rerank_score: float
    relevance_score: float
    coverage_score: float
    authority_score: float
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class SeniorLibrarianReranker:
    """Advanced reranking for retrieved documents.

    The SeniorLibrarianReranker performs sophisticated reranking based on
    relevance, coverage, authority, and evidence quality.
    """

    def __init__(
        self,
        relevance_weight: float = 0.4,
        coverage_weight: float = 0.3,
        authority_weight: float = 0.3,
        prune_threshold: float = 0.5,
    ):
        """Initialize the reranker.

        Args:
            relevance_weight: Weight for relevance scoring
            coverage_weight: Weight for coverage evaluation
            authority_weight: Weight for authority assessment
            prune_threshold: Score threshold for pruning low-signal nodes
        """
        self.relevance_weight = relevance_weight
        self.coverage_weight = coverage_weight
        self.authority_weight = authority_weight
        self.prune_threshold = prune_threshold

        log.info("SeniorLibrarianReranker initialized")

    def rerank(
        self,
        query: str,
        candidates: list[Any],
        top_k: int = 10,
    ) -> list[RerankResult]:
        """Rerank retrieved candidates.

        Args:
            query: Original query
            candidates: List of recall results
            top_k: Number of top results to return

        Returns:
            List of RerankResult with improved ranking
        """
        trace_id = f"rerank_{hash(query) % 10000}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "SeniorLibrarianReranker.rerank"
        )

        reranked = []

        for candidate in candidates:
            # Calculate component scores
            relevance = self._score_relevance(query, candidate)
            coverage = self._score_coverage(query, candidate)
            authority = self._score_authority(candidate)

            # Combined score
            final_score = (
                relevance * self.relevance_weight +
                coverage * self.coverage_weight +
                authority * self.authority_weight
            )

            reranked.append(RerankResult(
                doc_id=getattr(candidate, 'doc_id', 'unknown'),
                original_score=getattr(candidate, 'score', 0.0),
                rerank_score=final_score,
                relevance_score=relevance,
                coverage_score=coverage,
                authority_score=authority,
                content=getattr(candidate, 'content', ''),
                metadata=getattr(candidate, 'metadata', {}),
            ))

        # Sort by rerank score
        reranked.sort(key=lambda x: x.rerank_score, reverse=True)

        # Prune low-signal results
        pruned = [r for r in reranked if r.rerank_score >= self.prune_threshold]

        _emit_records_telemetry_event(
            "rerank",
            f"candidates_{len(candidates)}_pruned_{len(pruned)}"
        )

        log.debug(f"Reranked {len(candidates)} -> {len(pruned)} (threshold={self.prune_threshold})")
        return pruned[:top_k]

    def _score_relevance(self, query: str, candidate: Any) -> float:
        """Score relevance of candidate to query."""
        content = getattr(candidate, 'content', '').lower()
        query_terms = query.lower().split()

        if not content or not query_terms:
            return 0.5

        # Simple term overlap scoring
        matches = sum(1 for term in query_terms if term in content)
        return min(matches / len(query_terms), 1.0) * 0.8 + 0.2

    def _score_coverage(self, query: str, candidate: Any) -> float:
        """Score how well candidate covers query aspects."""
        content = getattr(candidate, 'content', '')

        if not content:
            return 0.5

        # Length-based coverage (longer docs cover more)
        length_score = min(len(content) / 1000, 1.0)

        return length_score * 0.6 + 0.4

    def _score_authority(self, candidate: Any) -> float:
        """Score authority/trustworthiness of candidate."""
        metadata = getattr(candidate, 'metadata', {})

        # Source quality indicators
        score = 0.5

        if metadata.get('is_official'):
            score += 0.3
        if metadata.get('is_reviewed'):
            score += 0.1
        if metadata.get('version'):
            score += 0.1

        return min(score, 1.0)


# Global instance
_global_reranker: SeniorLibrarianReranker | None = None


def get_senior_librarian_reranker() -> SeniorLibrarianReranker:
    """Get or create the global reranker."""
    global _global_reranker
    if _global_reranker is None:
        _global_reranker = SeniorLibrarianReranker()
    return _global_reranker
