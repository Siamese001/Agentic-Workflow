"""Sparse Index - Inverted index for lexical search.

10C-REQ-108: Build-time sparse index pipeline normalize extract tokenize weight inverted index build
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from collections import defaultdict
import re


@dataclass
class Posting:
    """Posting list entry."""
    doc_id: str
    term_freq: int
    positions: list[int]


class SparseIndex:
    """Sparse lexical index.

    10C-REQ-108: Normalize, tokenize, weight, build inverted index.
    """

    def __init__(self) -> None:
        self._index: dict[str, list[Posting]] = defaultdict(list)
        self._doc_freq: dict[str, int] = {}
        self._doc_count: int = 0
        self._avg_doc_length: float = 0.0
        self._total_doc_length: int = 0

    def _normalize(self, text: str) -> str:
        """Normalize text: lowercase, remove extra whitespace."""
        text = text.lower()
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into terms."""
        # Simple word tokenization
        return re.findall(r'\b[a-z0-9]+\b', text)

    def add_document(self, doc_id: str, text: str) -> None:
        """Add document to sparse index."""
        # Normalize
        normalized = self._normalize(text)

        # Tokenize
        tokens = self._tokenize(normalized)

        if not tokens:
            return

        # Track document stats
        self._doc_count += 1
        self._total_doc_length += len(tokens)
        self._avg_doc_length = self._total_doc_length / self._doc_count

        # Build postings
        term_positions: dict[str, list[int]] = defaultdict(list)
        for pos, token in enumerate(tokens):
            term_positions[token].append(pos)

        # Add to index
        for term, positions in term_positions.items():
            posting = Posting(
                doc_id=doc_id,
                term_freq=len(positions),
                positions=positions,
            )
            self._index[term].append(posting)

            # Update document frequency
            self._doc_freq[term] = self._doc_freq.get(term, 0) + 1

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        """Search sparse index."""
        # Normalize and tokenize query
        query_terms = self._tokenize(self._normalize(query))

        if not query_terms:
            return []

        # Score documents
        doc_scores: dict[str, float] = defaultdict(float)

        for term in query_terms:
            if term in self._index:
                postings = self._index[term]
                idf = self._compute_idf(term)

                for posting in postings:
                    # Simple TF weighting
                    tf_weight = 1 + posting.term_freq
                    doc_scores[posting.doc_id] += tf_weight * idf

        # Sort and return top-k
        sorted_results = sorted(
            doc_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return sorted_results[:top_k]

    def _compute_idf(self, term: str) -> float:
        """Compute inverse document frequency."""
        df = self._doc_freq.get(term, 0)
        if df == 0:
            return 0.0
        import math
        return math.log((self._doc_count + 1) / (df + 1)) + 1.0

    def get_stats(self) -> dict[str, Any]:
        """Get index statistics."""
        return {
            "terms": len(self._index),
            "documents": self._doc_count,
            "avg_doc_length": self._avg_doc_length,
            "total_postings": sum(len(p) for p in self._index.values()),
        }
