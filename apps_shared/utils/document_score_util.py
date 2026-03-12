"""RAG scoring utilities for document relevance and ranking.

Provides scoring algorithms for retrieved documents in RAG systems.
"""
import math
import re
from dataclasses import dataclass
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

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
        self.final_score = 0.4 * self.relevance_score + 0.3 * self.semantic_score + 0.2 * self.keyword_score + 0.1 * self.freshness_score

class RAGScorer:
    """Scores and ranks documents for RAG retrieval."""

    def __init__(self, config: dict[str, Any] | None=None):
        """Initialize RAG scorer.

        Args:
            config: Optional configuration for scoring weights
        """
        self.config = config or {}
        self.weights = self.config.get('weights', {'relevance': 0.4, 'semantic': 0.3, 'keyword': 0.2, 'freshness': 0.1})

    def score_documents(self, documents: list[dict[str, Any]], query: str, query_embedding: list[float] | None=None, document_embeddings: list[list[float]] | None=None) -> list[DocumentScore]:
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
            relevance = self._calculate_relevance(doc['content'], query)
            semantic = self._calculate_semantic_score(doc, query, query_embedding, document_embeddings[i] if document_embeddings else None)
            keyword = self._calculate_keyword_score(doc['content'], query)
            freshness = self._calculate_freshness_score(doc)
            doc_score = DocumentScore(document_id=doc['id'], content=doc['content'], relevance_score=relevance, semantic_score=semantic, keyword_score=keyword, freshness_score=freshness, final_score=0.0)
            scores.append(doc_score)
        scores.sort(key=lambda x: x.final_score, reverse=True)
        return scores

    def _calculate_relevance(self, content: str, query: str) -> float:
        """Calculate basic relevance score based on term overlap."""
        content_words = set(re.findall('\\b\\w+\\b', content.lower()))
        query_words = set(re.findall('\\b\\w+\\b', query.lower()))
        if not query_words:
            return 0.0
        overlap = len(content_words & query_words)
        return min(overlap / len(query_words), 1.0)

    def _calculate_semantic_score(self, doc: dict[str, Any], query: str, query_embedding: list[float] | None, doc_embedding: list[float] | None) -> float:
        """Calculate semantic similarity score."""
        if not query_embedding or not doc_embedding:
            return self._calculate_relevance(doc['content'], query)
        dot_product = sum((q * d for q, d in zip(query_embedding, doc_embedding, strict=False)))
        query_norm = math.sqrt(sum((q * q for q in query_embedding)))
        doc_norm = math.sqrt(sum((d * d for d in doc_embedding)))
        if query_norm == 0 or doc_norm == 0:
            return 0.0
        return dot_product / (query_norm * doc_norm)

    def _calculate_keyword_score(self, content: str, query: str) -> float:
        """Calculate keyword matching score."""
        score = 0.0
        query_terms = re.findall('\\b\\w+\\b', query.lower())
        for term in query_terms:
            if term in content.lower():
                score += 1.0
            elif any((term in word for word in content.lower().split())):
                score += 0.5
        return min(score / len(query_terms), 1.0) if query_terms else 0.0

    def _calculate_freshness_score(self, doc: dict[str, Any]) -> float:
        """Calculate freshness score based on document metadata."""
        if 'timestamp' not in doc and 'date' not in doc:
            return 0.5
        return 0.5

def create_rag_scorer(config: dict[str, Any] | None=None) -> RAGScorer:
    """Create a RAG scorer instance.

    Args:
        config: Optional configuration

    Returns:
        RAGScorer instance
    """
    return RAGScorer(config)
