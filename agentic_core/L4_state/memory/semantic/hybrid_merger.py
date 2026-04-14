"""Hybrid Merger - Combine sparse and dense results.

10C-REQ-109: Query-time hybrid merge combine sparse BM25 with dense vectors merge strategy
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from tqdm import tqdm


@dataclass
class SearchResult:
    """Single search result."""

    doc_id: str
    score: float
    source: str  # 'sparse' or 'dense'
    metadata: dict[str, Any]


class HybridMerger:
    """Hybrid merger for sparse + dense retrieval.

    10C-REQ-109: Combine BM25 sparse with dense vector similarity.
    """

    def __init__(
        self,
        sparse_weight: float = 0.3,
        dense_weight: float = 0.7,
    ) -> None:
        self._sparse_weight = sparse_weight
        self._dense_weight = dense_weight

    def merge(
        self,
        sparse_results: list[tuple[str, float]],
        dense_results: list[tuple[str, float]],
        top_k: int = 10,
    ) -> list[SearchResult]:
        """Merge sparse and dense results."""
        # Normalize scores to [0, 1]
        all_sparse_scores = [s for _, s in sparse_results] if sparse_results else [0]
        all_dense_scores = [s for _, s in dense_results] if dense_results else [0]

        sparse_max = max(all_sparse_scores) if max(all_sparse_scores) > 0 else 1
        dense_max = max(all_dense_scores) if max(all_dense_scores) > 0 else 1

        # Build combined scores
        combined: dict[str, tuple[float, float, float]] = {}  # doc_id -> (sparse, dense, combined)

        # Add sparse results
        for doc_id, score in sparse_results:
            norm_score = score / sparse_max
            combined[doc_id] = (norm_score, 0.0, norm_score * self._sparse_weight)

        # Add/merge dense results
        for doc_id, score in dense_results:
            norm_score = score / dense_max
            if doc_id in combined:
                existing_sparse, _, _ = combined[doc_id]
                combined_score = existing_sparse * self._sparse_weight + norm_score * self._dense_weight
                combined[doc_id] = (existing_sparse, norm_score, combined_score)
            else:
                combined[doc_id] = (0.0, norm_score, norm_score * self._dense_weight)

        # Sort by combined score
        sorted_results = sorted(
            combined.items(),
            key=lambda x: x[1][2],  # combined score
            reverse=True,
        )

        # Build SearchResult objects
        results: list[SearchResult] = []
        for doc_id, (sparse_s, dense_s, combined_s) in tqdm(
            sorted_results[:top_k], desc="Processing", unit="item"
        ):
            # Determine primary source
            if sparse_s > 0 and dense_s > 0:
                source = "hybrid"
            elif sparse_s > 0:
                source = "sparse"
            else:
                source = "dense"

            results.append(
                SearchResult(
                    doc_id=doc_id,
                    score=combined_s,
                    source=source,
                    metadata={
                        "sparse_score": sparse_s,
                        "dense_score": dense_s,
                        "sparse_weight": self._sparse_weight,
                        "dense_weight": self._dense_weight,
                    },
                )
            )

        return results

    def rerank(
        self,
        results: list[SearchResult],
        boost_recent: bool = True,
        timestamp_meta: str = "created_at",
    ) -> list[SearchResult]:
        """Rerank results with additional signals."""
        # Simple reranking - could add diversity, recency, etc.
        if not boost_recent:
            return results

        # Boost by recency if timestamp available
        boosted: list[tuple[SearchResult, float]] = []
        for r in results:
            score = r.score
            if timestamp_meta in r.metadata:
                # Simple recency boost (would need actual timestamps in production)
                score *= 1.05
            boosted.append((r, score))

        # Re-sort
        boosted.sort(key=lambda x: x[1], reverse=True)

        # Update scores
        for i, (r, new_score) in enumerate(boosted):
            r.score = new_score

        return [r for r, _ in boosted]

    def get_params(self) -> dict[str, float]:
        """Get merger parameters."""
        return {
            "sparse_weight": self._sparse_weight,
            "dense_weight": self._dense_weight,
        }
