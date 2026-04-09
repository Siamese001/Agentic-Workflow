"""BM25 Scorer - Probabilistic retrieval scoring.

10C-REQ-108: Weight terms with BM25 scoring.
"""

from __future__ import annotations

from typing import Any
import math


class BM25Scorer:
    """BM25 scoring for sparse retrieval.

    BM25 formula: score(D,Q) = sum(IDF(q) * f(q,D) * (k1+1) / (f(q,D) + k1 * (1-b+b*|D|/avgDL)))
    """

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        self._k1 = k1
        self._b = b

    def compute_idf(
        self,
        term: str,
        doc_freq: dict[str, int],
        total_docs: int,
    ) -> float:
        """Compute BM25 IDF."""
        df = doc_freq.get(term, 0)
        if df == 0:
            return 0.0

        # BM25 IDF variant
        idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1.0)
        return max(0.0, idf)

    def compute_tf_weight(
        self,
        term_freq: int,
        doc_length: int,
        avg_doc_length: float,
    ) -> float:
        """Compute BM25 TF weight component."""
        if term_freq == 0:
            return 0.0

        # Document length normalization
        norm_factor = 1 - self._b + self._b * (doc_length / max(1.0, avg_doc_length))

        # TF saturation
        tf_component = (term_freq * (self._k1 + 1)) / (term_freq + self._k1 * norm_factor)

        return tf_component

    def score_term(
        self,
        term: str,
        term_freq: int,
        doc_length: int,
        doc_freq: dict[str, int],
        total_docs: int,
        avg_doc_length: float,
    ) -> float:
        """Compute BM25 score for single term."""
        idf = self.compute_idf(term, doc_freq, total_docs)
        tf_weight = self.compute_tf_weight(term_freq, doc_length, avg_doc_length)
        return idf * tf_weight

    def score_document(
        self,
        query_terms: list[str],
        term_freqs: dict[str, int],
        doc_length: int,
        doc_freq: dict[str, int],
        total_docs: int,
        avg_doc_length: float,
    ) -> float:
        """Compute total BM25 score for document."""
        score = 0.0

        for term in query_terms:
            tf = term_freqs.get(term, 0)
            score += self.score_term(
                term, tf, doc_length,
                doc_freq, total_docs, avg_doc_length,
            )

        return score

    def get_params(self) -> dict[str, float]:
        """Get BM25 parameters."""
        return {
            "k1": self._k1,
            "b": self._b,
        }
