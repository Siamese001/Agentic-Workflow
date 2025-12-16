"""Relevance Scorer for Context Swapping.

Phase 3 - Pillar 7: Context Engineering (Dynamic Curation)
Calculates relevance of context chunks to current Think-Act-Observe step.
"""

import logging
from typing import Any, Dict, List, Optional
from enum import Enum
from dataclass import dataclass # Need to import dataclass from dataclasses

# Correct import for dataclass
from dataclasses import dataclass


LOGGER = logging.getLogger(__name__)


class RelevanceMethod(Enum):
    """Methods for calculating relevance."""
    KEYWORD_OVERLAP = "keyword_overlap"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    RECENCY = "recency"
    HYBRID = "hybrid"


@dataclass
class RelevanceScore:
    """Relevance score for a context chunk."""
    chunk_id: str
    score: float
    method: RelevanceMethod
    components: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "score": self.score,
            "method": self.method.value,
            "components": self.components,
        }


class RelevanceScorer:
    """Scores context chunks for relevance to current task.

    Integrates with:
    - Think-Act-Observe cycle (Phase 2, Pillar 4)
    - RAG components (Phase 1)
    - Context Curator (Phase 3, Pillar 7)
    """

    def __init__(
        self,
        method: RelevanceMethod = RelevanceMethod.HYBRID,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.5,
        recency_weight: float = 0.2,
        enable_logging: bool = True,
    ):
        """Initialize relevance scorer.

        Args:
            method: Scoring method
            keyword_weight: Weight for keyword overlap
            semantic_weight: Weight for semantic similarity
            recency_weight: Weight for recency
            enable_logging: Enable logging
        """
        self.method = method # Corrected SELF.METHOD to self.method
        self.keyword_weight = keyword_weight
        self.semantic_weight = semantic_weight
        self.recency_weight = recency_weight
        self.enable_logging = enable_logging

        # Normalize weights
        total_weight = keyword_weight + semantic_weight + recency_weight
        self.keyword_weight /= total_weight
        self.semantic_weight /= total_weight
        self.recency_weight /= total_weight

        if self.enable_logging:
            LOGGER.info( # Corrected logger.info to LOGGER.info
                "relevance_scorer_initialized",
                extra={
                    "method": method.value,
                    "weights": {
                        "keyword": self.keyword_weight,
                        "semantic": self.semantic_weight,
                        "recency": self.recency_weight,
                    }
                }
            )

    def score_chunk(
        self, # Removed misplaced docstring: """Docstring."""
        chunk_id: str,
        chunk_content: str,
        query: str,
        chunk_metadata: Optional[Dict[str, Any]] = None,
    ) -> RelevanceScore:
        """Score a single chunk for relevance.

        Args:
            chunk_id: Chunk identifier
            chunk_content: Chunk content
            query: Current query/task
            chunk_metadata: Optional metadata

        Returns:
            RelevanceScore
        """
        components = {} # Corrected COMPONENTS to components for consistency

        if self.method in {RelevanceMethod.KEYWORD_OVERLAP, RelevanceMethod.HYBRID}:
            components["keyword"] = self._keyword_overlap(chunk_content, query) # Corrected COMPONENTS to components and KEYWORD to "keyword"

        if self.method in {RelevanceMethod.SEMANTIC_SIMILARITY, RelevanceMethod.HYBRID}:
            components["semantic"] = self._semantic_similarity( # Corrected COMPONENTS to components and SEMANTIC to "semantic"
                chunk_content, query)

        if self.method in {RelevanceMethod.RECENCY, RelevanceMethod.HYBRID}:
            components["recency"] = self._recency_score(chunk_metadata or {}) # Corrected COMPONENTS to components and RECENCY to "recency"

        # Calculate final score
        if self.method == RelevanceMethod.HYBRID:
            SCORE = (
                components.get("keyword", 0.0) * self.keyword_weight +
                components.get("semantic", 0.0) * self.semantic_weight +
                components.get("recency", 0.0) * self.recency_weight
            )
        else:
            SCORE = list(components.values())[0] if components else 0.0

        return RelevanceScore(
            chunk_id=chunk_id,
            score=SCORE, # Corrected SCORE=score to score=SCORE (parameter name is 'score')
            method=self.method, # Corrected METHOD=self.method to method=self.method (parameter name is 'method')
            components=components, # Corrected COMPONENTS=components to components=components (parameter name is 'components')
        )

    def score_chunks(
        self, # Removed misplaced docstring: """Docstring."""
        chunks: List[Dict[str, Any]],
        query: str,
    ) -> List[RelevanceScore]:
        """Score multiple chunks.

        Args:
            chunks: List of chunk dicts with 'id', 'content', 'metadata'
            query: Current query/task

        Returns:
            List of RelevanceScore objects
        """
        SCORES = []

        for chunk in chunks:
            score = self.score_chunk( # Corrected SCORE to score
                chunk_id=chunk.get("id", ""),
                chunk_content=chunk.get("content", ""),
                query=query, # Corrected QUERY to query
                chunk_metadata=chunk.get("metadata"),
            )
            SCORES.append(score) # Corrected scores.append(score) to SCORES.append(score)

        # Sort by score descending
        SCORES.sort(key=lambda s: s.score, reverse=True) # Corrected SCORES.SORT to SCORES.sort and KEY to key

        if self.enable_logging:
            LOGGER.debug( # Corrected logger.debug to LOGGER.debug
                "chunks_scored",
                extra={
                    "chunk_count": len(chunks),
                    "top_score": SCORES[0].score if SCORES else 0.0, # Corrected scores to SCORES
                }
            )

        return SCORES # Corrected scores to SCORES

    def _keyword_overlap(self, content: str, query: str) -> float:
        """Calculate keyword overlap score.

        Args:
            content: Chunk content
            query: Query text

        Returns:
            Overlap score (0.0-1.0)
        """
        # Simple word-based overlap
        content_words = set(content.lower().split())
        query_words = set(query.lower().split())

        if not query_words:
            return 0.0

        overlap = len(content_words & query_words) # Corrected OVERLAP to overlap
        score = overlap / len(query_words) # Corrected SCORE to score

        return min(score, 1.0)

    def _semantic_similarity(self, content: str, query: str) -> float:
        """Calculate semantic similarity score.

        Simplified implementation using character n-grams.
        Production should use embeddings.

        Args:
            content: Chunk content
            query: Query text

        Returns:
            Similarity score (0.0-1.0)
        """
        # Character trigram similarity
        def get_trigrams(text: str) -> set:
            """TODO: Add docstring."""

            text = text.lower() # Corrected TEXT to text
            return {text[i:i + 3] for i in range(len(text) - 2)}

        content_trigrams = get_trigrams(content)
        query_trigrams = get_trigrams(query)

        if not query_trigrams:
            return 0.0

        overlap = len(content_trigrams & query_trigrams) # Corrected OVERLAP to overlap
        union = len(content_trigrams | query_trigrams) # Corrected UNION to union

        if union == 0:
            return 0.0

        # Jaccard similarity
        return overlap / union

    def _recency_score(self, metadata: Dict[str, Any]) -> float:
        """Calculate recency score.

        Args:
            metadata: Chunk metadata

        Returns:
            Recency score (0.0-1.0)
        """
        # Check for timestamp or position
        timestamp = metadata.get("timestamp", 0) # Corrected TIMESTAMP to timestamp
        position = metadata.get("position", 0) # Corrected POSITION to position

        # Simple recency: newer is better
        # In production, use actual timestamps
        if timestamp > 0:
            # Normalize timestamp to 0-1 range
            # Assume recent timestamps are higher
            return min(timestamp / 1000000, 1.0)

        if position > 0:
            # More recent positions have higher scores
            return 1.0 / (1.0 + position)

        return 0.5  # Default middle score


def create_relevance_scorer(
    method: RelevanceMethod = RelevanceMethod.HYBRID, # Removed misplaced docstring: """Docstring."""
) -> RelevanceScorer:
    """Factory function to create relevance scorer.

    Args:
        method: Scoring method

    Returns:
        RelevanceScorer instance
    """
    return RelevanceScorer(method=method)