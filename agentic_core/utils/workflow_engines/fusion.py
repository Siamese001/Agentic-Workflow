"""
Candidate Fusion

Reciprocal Rank Fusion (RRF) implementation for merging lexical and vector
retrieval results into a single ranked candidate list.
"""

from __future__ import annotations

from .interfaces import Document, ICandidateFusion


class ReciprocalRankFusion(ICandidateFusion):
    """Merges retrieval results using Reciprocal Rank Fusion (RRF).

    RRF score = sum(1 / (k + rank_i)) across all ranked lists.
    k=60 is the standard constant (Cormack et al., 2009).
    """

    def __init__(self, k: int = 60):
        if k <= 0:
            raise ValueError(f"k must be positive, got {k}")
        self.k = k

    def merge(self, lexical_results: list[Document], vector_results: list[Document]) -> list[Document]:
        """Merge lexical and vector results via RRF.

        Args:
            lexical_results: Ranked documents from lexical retrieval
            vector_results: Ranked documents from vector retrieval

        Returns:
            Merged list sorted by descending RRF score
        """
        rrf_scores: dict[str, float] = {}
        doc_map: dict[str, Document] = {}
        for rank, doc in enumerate(lexical_results, start=1):
            rrf_scores[doc.doc_id] = rrf_scores.get(doc.doc_id, 0.0) + 1.0 / (self.k + rank)
            doc_map[doc.doc_id] = doc
        for rank, doc in enumerate(vector_results, start=1):
            rrf_scores[doc.doc_id] = rrf_scores.get(doc.doc_id, 0.0) + 1.0 / (self.k + rank)
            if doc.doc_id not in doc_map:
                doc_map[doc.doc_id] = doc
        merged = []
        for doc_id, rrf_score in sorted(rrf_scores.items(), key=lambda x: -x[1]):
            src = doc_map[doc_id]
            merged.append(
                Document(
                    doc_id=src.doc_id,
                    content=src.content,
                    score=rrf_score,
                    metadata={**src.metadata, "rrf_score": rrf_score},
                )
            )
        return merged


class ScoreFusion(ICandidateFusion):
    """Merges retrieval results by normalizing and averaging scores."""

    def merge(self, lexical_results: list[Document], vector_results: list[Document]) -> list[Document]:
        """Merge by normalized score averaging.

        Args:
            lexical_results: Ranked documents from lexical retrieval
            vector_results: Ranked documents from vector retrieval

        Returns:
            Merged list sorted by descending average score
        """

        def _normalize(docs: list[Document]) -> dict[str, float]:
            if not docs:
                return {}
            scores = [d.score for d in docs]
            min_s, max_s = (min(scores), max(scores))
            if max_s == min_s:
                return {d.doc_id: 1.0 for d in docs}
            return {d.doc_id: (d.score - min_s) / (max_s - min_s) for d in docs}

        lex_norm = _normalize(lexical_results)
        vec_norm = _normalize(vector_results)
        doc_map: dict[str, Document] = {d.doc_id: d for d in lexical_results}
        doc_map.update({d.doc_id: d for d in vector_results})
        all_ids = set(lex_norm) | set(vec_norm)
        fused_scores: dict[str, float] = {}
        for doc_id in all_ids:
            s_lex = lex_norm.get(doc_id, 0.0)
            s_vec = vec_norm.get(doc_id, 0.0)
            count = (1 if doc_id in lex_norm else 0) + (1 if doc_id in vec_norm else 0)
            fused_scores[doc_id] = (s_lex + s_vec) / count
        merged = []
        for doc_id, score in sorted(fused_scores.items(), key=lambda x: -x[1]):
            src = doc_map[doc_id]
            merged.append(
                Document(
                    doc_id=src.doc_id,
                    content=src.content,
                    score=score,
                    metadata={**src.metadata, "fused_score": score},
                )
            )
        return merged


__all__ = ["ReciprocalRankFusion", "ScoreFusion"]
