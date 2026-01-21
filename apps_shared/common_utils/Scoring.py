"""RAG scoring utilities for document relevance and ranking.

Provides scoring algorithms for retrieved documents in RAG systems.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import math
import re


@dataclass
class DocumentScore:
    """Score for a retrieved document."""
    document_id: str
    content: str
    relevance_score: float
    semantic_score: float
    keyword_score: float
    freshness_score: float
    final_score: float

    def __post_init__(self):
        # Calculate final weighted score
        self.final_score = (
            0.4 * self.relevance_score +
            0.3 * self.semantic_score +
            0.2 * self.keyword_score +
            0.1 * self.freshness_score
        )


class RAGScorer:
    """Scores and ranks documents for RAG retrieval."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize RAG scorer.

        Args:
            config: Optional configuration for scoring weights
        """
        self.config = config or {}
        self.weights = self.config.get("weights", {
            "relevance": 0.4,
            "semantic": 0.3,
            "keyword": 0.2,
            "freshness": 0.1
        })

    def score_documents(
        self,
        documents: List[Dict[str, Any]],
        query: str,
        query_embedding: Optional[List[float]] = None,
        document_embeddings: Optional[List[List[float]]] = None
    ) -> List[DocumentScore]:
        """Score a list of documents against a query.

        Args:
            documents: List of document dictionaries with 'id' and 'content'
            query: Query string
            query_embedding: Optional query embedding for semantic scoring
            document_embeddings: Optional document embeddings

        Returns:
            List of DocumentScore objects
        """
        scores = []

        for i, doc in enumerate(documents):
            # Calculate different score components
            relevance = self._calculate_relevance(doc["content"], query)
            semantic = self._calculate_semantic_score(
                doc, query, query_embedding,
                document_embeddings[i] if document_embeddings else None
            )
            keyword = self._calculate_keyword_score(doc["content"], query)
            freshness = self._calculate_freshness_score(doc)

            # Create document score
            doc_score = DocumentScore(
                document_id=doc["id"],
                content=doc["content"],
                relevance_score=relevance,
                semantic_score=semantic,
                keyword_score=keyword,
                freshness_score=freshness,
                final_score=0.0  # Will be calculated in __post_init__
            )

            scores.append(doc_score)

        # Sort by final score
        scores.sort(key=lambda x: x.final_score, reverse=True)
        return scores

    def _calculate_relevance(self, content: str, query: str) -> float:
        """Calculate basic relevance score based on term overlap."""
        content_words = set(re.findall(r"\b\w+\b", content.lower()))
        query_words = set(re.findall(r"\b\w+\b", query.lower()))

        if not query_words:
            return 0.0

        overlap = len(content_words & query_words)
        return min(overlap / len(query_words), 1.0)

    def _calculate_semantic_score(
        self,
        doc: Dict[str, Any],
        query: str,
        query_embedding: Optional[List[float]],
        doc_embedding: Optional[List[float]]
    ) -> float:
        """Calculate semantic similarity score."""
        if not query_embedding or not doc_embedding:
            # Fallback to simple similarity
            return self._calculate_relevance(doc["content"], query)

        # Calculate cosine similarity
        dot_product = sum(q * d for q, d in zip(query_embedding, doc_embedding))
        query_norm = math.sqrt(sum(q * q for q in query_embedding))
        doc_norm = math.sqrt(sum(d * d for d in doc_embedding))

        if query_norm == 0 or doc_norm == 0:
            return 0.0

        return dot_product / (query_norm * doc_norm)

    def _calculate_keyword_score(self, content: str, query: str) -> float:
        """Calculate keyword matching score."""
        score = 0.0
        query_terms = re.findall(r"\b\w+\b", query.lower())

        for term in query_terms:
            # Check for exact matches
            if term in content.lower():
                score += 1.0
            # Check for partial matches
            elif any(term in word for word in content.lower().split()):
                score += 0.5

        return min(score / len(query_terms), 1.0) if query_terms else 0.0

    def _calculate_freshness_score(self, doc: Dict[str, Any]) -> float:
        """Calculate freshness score based on document metadata."""
        # Default to neutral score if no date info
        if "timestamp" not in doc and "date" not in doc:
            return 0.5

        # Simple implementation - could be enhanced with actual date logic
        return 0.5


def create_rag_scorer(config: Optional[Dict[str, Any]] = None) -> RAGScorer:
    """Create a RAG scorer instance.

    Args:
        config: Optional configuration

    Returns:
        RAGScorer instance
    """
    return RAGScorer(config)
