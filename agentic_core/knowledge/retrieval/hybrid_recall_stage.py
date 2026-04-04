"""Hybrid Recall Stage.

Dense and sparse retrieval with merge/dedup candidate list.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


@dataclass
class RecallResult:
    """Result from recall stage."""
    doc_id: str
    score: float
    source: str  # "dense", "sparse"
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class HybridRecallStage:
    """Hybrid retrieval combining dense and sparse methods.

    The HybridRecallStage performs both vector similarity search
    and sparse term matching, then merges results with deduplication.
    """

    def __init__(
        self,
        vector_weight: float = 0.5,
        sparse_weight: float = 0.5,
        top_k: int = 20,
    ):
        """Initialize the hybrid recall stage.

        Args:
            vector_weight: Weight for dense retrieval (0-1)
            sparse_weight: Weight for sparse retrieval (0-1)
            top_k: Number of results to return
        """
        self.vector_weight = vector_weight
        self.sparse_weight = sparse_weight
        self.top_k = top_k

        # Mock backends (replace with actual implementations)
        self._vector_store = None
        self._sparse_index = None

        log.info(f"HybridRecallStage initialized (vector={vector_weight}, sparse={sparse_weight})")

    def recall(
        self,
        query_vector: list[float],
        query_terms: list[str],
        scope_filter: dict[str, Any] | None = None,
    ) -> list[RecallResult]:
        """Perform hybrid recall.

        Args:
            query_vector: Dense query vector
            query_terms: Sparse query terms
            scope_filter: Optional scope filter

        Returns:
            List of RecallResult with merged candidates
        """
        trace_id = f"recall_{hash(str(query_vector)) % 10000}"
        _emit_records_execution_trace(
            trace_id, LayerSegment.L1_REASONING, "HybridRecallStage.recall"
        )

        # Dense retrieval
        dense_results = self._dense_recall(query_vector, scope_filter)

        # Sparse retrieval
        sparse_results = self._sparse_recall(query_terms, scope_filter)

        # Merge and deduplicate
        merged = self._merge_results(dense_results, sparse_results)

        _emit_records_telemetry_event(
            "hybrid_recall",
            f"dense_{len(dense_results)}_sparse_{len(sparse_results)}"
        )

        log.debug(f"Hybrid recall: {len(dense_results)} dense + {len(sparse_results)} sparse = {len(merged)} merged")
        return merged[:self.top_k]

    def _dense_recall(
        self,
        query_vector: list[float],
        scope_filter: dict[str, Any] | None,
    ) -> list[RecallResult]:
        """Perform dense vector retrieval."""
        # Mock implementation - replace with actual vector store query
        results = []

        # Simulate vector similarity search
        for i in range(10):
            results.append(RecallResult(
                doc_id=f"doc_dense_{i}",
                score=0.9 - (i * 0.05),
                source="dense",
                content=f"Dense result {i}",
            ))

        return results

    def _sparse_recall(
        self,
        query_terms: list[str],
        scope_filter: dict[str, Any] | None,
    ) -> list[RecallResult]:
        """Perform sparse term retrieval."""
        # Mock implementation - replace with actual BM25/TF-IDF search
        results = []

        # Simulate sparse matching
        for i in range(10):
            results.append(RecallResult(
                doc_id=f"doc_sparse_{i}",
                score=0.85 - (i * 0.04),
                source="sparse",
                content=f"Sparse result {i}",
            ))

        return results

    def _merge_results(
        self,
        dense: list[RecallResult],
        sparse: list[RecallResult],
    ) -> list[RecallResult]:
        """Merge and deduplicate results from both sources."""
        # Create score lookup
        doc_scores: dict[str, tuple[float, float]] = {}  # doc_id -> (dense_score, sparse_score)
        doc_content: dict[str, str] = {}

        # Add dense scores
        for r in dense:
            doc_scores[r.doc_id] = (r.score, 0.0)
            doc_content[r.doc_id] = r.content

        # Add sparse scores
        for r in sparse:
            if r.doc_id in doc_scores:
                existing = doc_scores[r.doc_id]
                doc_scores[r.doc_id] = (existing[0], r.score)
            else:
                doc_scores[r.doc_id] = (0.0, r.score)
                doc_content[r.doc_id] = r.content

        # Calculate hybrid scores
        merged = []
        for doc_id, (dense_score, sparse_score) in doc_scores.items():
            hybrid_score = (
                dense_score * self.vector_weight +
                sparse_score * self.sparse_weight
            )

            # Determine source
            if dense_score > 0 and sparse_score > 0:
                source = "both"
            elif dense_score > 0:
                source = "dense"
            else:
                source = "sparse"

            merged.append(RecallResult(
                doc_id=doc_id,
                score=hybrid_score,
                source=source,
                content=doc_content.get(doc_id, ""),
                metadata={
                    "dense_score": dense_score,
                    "sparse_score": sparse_score,
                },
            ))

        # Sort by score descending
        merged.sort(key=lambda x: x.score, reverse=True)

        return merged


# Global instance
_global_recall: HybridRecallStage | None = None


def get_hybrid_recall_stage() -> HybridRecallStage:
    """Get or create the global hybrid recall stage."""
    global _global_recall
    if _global_recall is None:
        _global_recall = HybridRecallStage()
    return _global_recall
