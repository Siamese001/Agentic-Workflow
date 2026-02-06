"""Hybrid Scorer for RAG systems.

Combines multiple scoring strategies for optimal document ranking.
"""

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any


@dataclass
class ScoringWeights:
    """Weights for different scoring components."""

    bm25_weight: float = 0.4
    semantic_weight: float = 0.3
    tfidf_weight: float = 0.2
    freshness_weight: float = 0.1


@dataclass
class ScoringResult:
    """Result of scoring operation."""

    document_id: str
    bm25_score: float
    semantic_score: float
    tfidf_score: float
    freshness_score: float
    final_score: float
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BM25Scorer:
    """BM25 scoring algorithm implementation."""

    def __init__(self, k1: float = 1.2, b: float = 0.75):
        """Initialize BM25 scorer.

        Args:
            k1: Controls term frequency saturation
            b: Controls document length normalization
        """
        self.k1 = k1
        self.b = b
        self.doc_freqs: dict[str, int] = {}
        self.doc_lengths: list[int] = []
        self.avg_doc_length = 0.0

    def build_index(self, documents: list[str]) -> None:
        """Build BM25 index from documents.

        Args:
            documents: List of document texts
        """
        # Calculate document frequencies
        all_terms = []
        for doc in documents:
            terms = self._tokenize(doc)
            all_terms.append(terms)
            self.doc_lengths.append(len(terms))

            # Count unique terms in this document
            for term in set(terms):
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        # Calculate average document length
        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0

        # Store tokenized documents for scoring
        self.documents = all_terms

    def score(self, query: str, doc_idx: int) -> float:
        """Score document against query using BM25.

        Args:
            query: Query string
            doc_idx: Index of document to score

        Returns:
            BM25 score
        """
        if doc_idx >= len(self.documents):
            return 0.0

        query_terms = self._tokenize(query)
        doc_terms = self.documents[doc_idx]
        doc_length = self.doc_lengths[doc_idx]

        if not query_terms or doc_length == 0:
            return 0.0

        score = 0.0
        doc_term_counts = Counter(doc_terms)

        for term in query_terms:
            if term in doc_term_counts:
                # BM25 formula components
                tf = doc_term_counts[term]
                df = self.doc_freqs.get(term, 0)
                idf = math.log((len(self.documents) - df + 0.5) / (df + 0.5))

                # BM25 score for this term
                term_score = (
                    idf
                    * (tf * (self.k1 + 1))
                    / (tf + self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length))
                )
                score += term_score

        return score

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into terms."""
        return re.findall(r"\b\w+\b", text.lower())


class HybridScorer:
    """Hybrid scorer combining multiple scoring strategies."""

    def __init__(self, weights: ScoringWeights | None = None):
        """Initialize hybrid scorer.

        Args:
            weights: scoring weights for different components
        """
        self.weights = weights or ScoringWeights()
        self.bm25_scorer = BM25Scorer()
        self.documents: list[dict[str, Any]] = []

    def index_documents(self, documents: list[dict[str, Any]]) -> None:
        """Index documents for scoring.

        Args:
            documents: List of document dictionaries with 'id' and 'content'
        """
        self.documents = documents
        doc_texts = [doc["content"] for doc in documents]
        self.bm25_scorer.build_index(doc_texts)

    def score_documents(self, query: str, top_k: int | None = None) -> list[ScoringResult]:
        """Score all documents against query.

        Args:
            query: Query string
            top_k: Optional limit on number of results

        Returns:
            List of scoring results
        """
        results = []

        for i, doc in enumerate(self.documents):
            # Calculate individual scores
            bm25_score = self.bm25_scorer.score(query, i)
            semantic_score = self._calculate_semantic_score(doc["content"], query)
            tfidf_score = self._calculate_tfidf_score(doc["content"], query)
            freshness_score = self._calculate_freshness_score(doc)

            # Calculate weighted final score
            final_score = (
                self.weights.bm25_weight * bm25_score
                + self.weights.semantic_weight * semantic_score
                + self.weights.tfidf_weight * tfidf_score
                + self.weights.freshness_weight * freshness_score
            )

            result = ScoringResult(
                document_id=doc["id"],
                bm25_score=bm25_score,
                semantic_score=semantic_score,
                tfidf_score=tfidf_score,
                freshness_score=freshness_score,
                final_score=final_score,
                metadata={"content_length": len(doc["content"])},
            )

            results.append(result)

        # Sort by final score
        results.sort(key=lambda x: x.final_score, reverse=True)

        if top_k:
            results = results[:top_k]

        return results

    def _calculate_semantic_score(self, content: str, query: str) -> float:
        """Calculate semantic similarity score (mock implementation)."""
        # Simple overlap-based semantic score
        content_words = set(re.findall(r"\b\w+\b", content.lower()))
        query_words = set(re.findall(r"\b\w+\b", query.lower()))

        if not query_words:
            return 0.0

        overlap = len(content_words & query_words)
        return overlap / len(query_words)

    def _calculate_tfidf_score(self, content: str, query: str) -> float:
        """Calculate TF-IDF score."""
        query_terms = re.findall(r"\b\w+\b", query.lower())
        content_terms = re.findall(r"\b\w+\b", content.lower())

        if not query_terms or not content_terms:
            return 0.0

        # Calculate TF
        content_counter = Counter(content_terms)
        total_terms = len(content_terms)

        # Simple TF-IDF calculation
        score = 0.0
        for term in query_terms:
            tf = content_counter.get(term, 0) / total_terms
            # IDF would require corpus stats, using simple heuristic
            idf = 1.0 if term in content_counter else 0.0
            score += tf * idf

        return min(score, 1.0)

    def _calculate_freshness_score(self, doc: dict[str, Any]) -> float:
        """Calculate freshness score."""
        # Default to neutral score
        return 0.5

    def calculate_hybrid_score(
        self,
        vector_score: float,
        keyword_score: float,
        weights: dict[str, float] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> float:
        """Calculate hybrid score from vector and keyword scores.

        Args:
            vector_score: Semantic similarity score
            keyword_score: Keyword/BM25 score
            weights: Optional weights dictionary
            metadata: Optional document metadata for recency boost

        Returns:
            Combined hybrid score
        """
        if weights is None:
            weights = {"semantic_weight": 0.5, "bm25_weight": 0.5, "recency_weight": 0.0}

        semantic_weight = weights.get("semantic_weight", 0.5)
        bm25_weight = weights.get("bm25_weight", 0.5)
        recency_weight = weights.get("recency_weight", 0.0)

        # Normalize weights to sum to 1 (excluding recency)
        total_weight = semantic_weight + bm25_weight
        if total_weight > 0:
            semantic_weight = semantic_weight / total_weight
            bm25_weight = bm25_weight / total_weight

        score = (vector_score * semantic_weight) + (keyword_score * bm25_weight)

        # Add recency boost if applicable
        if recency_weight > 0 and metadata:
            recency_boost = self._calculate_recency_boost(metadata)
            score = score * (1 - recency_weight) + recency_boost * recency_weight

        return score

    def _normalize_score(
        self,
        score: float,
        min_score: float = 0.0,
        max_score: float = 1.0,
    ) -> float:
        """Normalize score to [0, 1] range.

        Args:
            score: Raw score
            min_score: Minimum possible score
            max_score: Maximum possible score

        Returns:
            Normalized score
        """
        # If max_score is None or unbounded, clamp to [0, 1]
        if max_score is None or max_score == float("inf"):
            return min(max(score, 1.0), 0.0)

        if max_score - min_score == 0:
            return 0.0

        normalized = (score - min_score) / (max_score - min_score)
        # Clamp to [0, 1] range
        return min(max(normalized, 0.0), 1.0)

    def _calculate_recency_boost(self, document: dict[str, Any]) -> float:
        """Calculate recency boost for document.

        Args:
            document: Document dictionary

        Returns:
            Recency boost factor
        """
        # Check for date in document
        if "date" in document:
            return self._calculate_date_recency(document["date"])

        # Check for timestamp
        if "timestamp" in document:
            return 0.9

        # Check for recent keywords
        content = str(document.get("content", "")).lower()
        recent_keywords = ["latest", "new", "recent", "current", "updated"]
        if any(keyword in content for keyword in recent_keywords):
            return 0.7

        return 0.5
