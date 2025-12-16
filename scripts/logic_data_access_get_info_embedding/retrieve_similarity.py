"""Similarity Retriever - Retrieves and computes similarity between vectors.

This module provides similarity retrieval capabilities for vector operations,
including similarity computation, ranking, and batch processing.
Follows the functional component pattern with proper logging.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import List, Optional, Any, Dict, Tuple
from dataclasses import dataclass, field

import numpy as np

LOGGER = logging.getLogger(__name__)


class SimilarityMetric(Enum):
    """Similarity metrics for vector comparison."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"
    MANHATTAN = "manhattan"
    JACCARD = "jaccard"


@dataclass
class SimilarityRequest:
    """Request for similarity computation."""
    query_vector: List[float]
    candidate_vectors: List[List[float]]
    metric: SimilarityMetric = SimilarityMetric.COSINE
    top_k: int = 10
    threshold: float = 0.0
    return_distances: bool = False


@dataclass
class SimilarityResult:
    """Result of similarity computation."""
    scores: List[float]
    indices: List[int]
    distances: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchSimilarityRequest:
    """Request for batch similarity computation."""
    query_vectors: List[List[float]]
    candidate_vectors: List[List[float]]
    metric: SimilarityMetric = SimilarityMetric.COSINE
    top_k: int = 10
    threshold: float = 0.0


@dataclass
class SimilarityConfig:
    """Configuration for similarity operations."""
    default_metric: SimilarityMetric = SimilarityMetric.COSINE
    normalize_vectors: bool = True
    batch_size: int = 1000
    use_approximate_search: bool = False
    num_threads: int = 4


class SimilarityRetriever:
    """Main class for similarity retrieval operations."""

    def __init__(self, config: Optional[SimilarityConfig] = None):
        self.config = config or SimilarityConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._vector_cache = {}

    def _compute_similarities_by_metric(self,
                                        query_vector: np.ndarray,
                                        candidate_vectors: np.ndarray,
                                        metric: SimilarityMetric) -> np.ndarray:
        """Compute similarities based on the specified metric."""
        if metric == SimilarityMetric.COSINE:
            return np.dot(candidate_vectors, query_vector)
        elif metric == SimilarityMetric.DOT_PRODUCT:
            return np.dot(candidate_vectors, query_vector)
        elif metric == SimilarityMetric.EUCLIDEAN:
            distances = np.linalg.norm(
                candidate_vectors - query_vector, axis=1)
            return 1 / (1 + distances)
        elif metric == SimilarityMetric.MANHATTAN:
            distances = np.sum(
                np.abs(candidate_vectors - query_vector), axis=1)
            return 1 / (1 + distances)
        elif metric == SimilarityMetric.JACCARD:
            return np.array([self._jaccard_similarity(query_vector, v) for v in candidate_vectors])
        else:
            return np.zeros(len(candidate_vectors))

    def _compute_distances_if_requested(self, final_indices: np.ndarray, final_scores: List[float],
                                        query_vector: np.ndarray, candidate_vectors: np.ndarray,
                                        metric: SimilarityMetric) -> Optional[List[float]]:
        """Compute distances if requested by the user."""
        if metric == SimilarityMetric.EUCLIDEAN:
            return np.linalg.norm(candidate_vectors[final_indices] - query_vector, axis=1).tolist()
        elif metric == SimilarityMetric.MANHATTAN:
            return np.sum(np.abs(candidate_vectors[final_indices] - query_vector), axis=1).tolist()
        else:
            return [(1 - s) if s <= 1 else 0 for s in final_scores]

    def compute_similarity(self, request: SimilarityRequest) -> SimilarityResult:
        """Compute similarity between query and candidate vectors.

        Args:
            request: Similarity computation request

        Returns:
            SimilarityResult: Similarity scores and rankings
        """
        self.logger.info(
            f"Computing similarity with metric: {request.metric.value}")

        try:
            # Convert to numpy arrays
            query_vector = np.array(request.query_vector)
            candidate_vectors = np.array(request.candidate_vectors)

            # Normalize vectors if configured
            if self.config.normalize_vectors:
                query_vector = self._normalize_vector(query_vector)
                candidate_vectors = np.array(
                    [self._normalize_vector(v) for v in candidate_vectors])

            # Compute similarities
            similarities = self._compute_similarities_by_metric(query_vector,
                                                                candidate_vectors,
                                                                request.metric)

            # Apply threshold
            threshold_mask = similarities >= request.threshold
            filtered_indices = np.where(threshold_mask)[0]
            filtered_similarities = similarities[threshold_mask]

            # Sort by similarity (descending)
            sorted_indices = np.argsort(filtered_similarities)[::-1]
            top_indices = sorted_indices[:request.top_k]
            final_indices = filtered_indices[top_indices]
            final_scores = filtered_similarities[top_indices].tolist()

            # Compute distances if requested
            distances = None
            if request.return_distances:
                distances = self._compute_distances_if_requested(
                    final_indices, final_scores, query_vector, candidate_vectors, request.metric
                )

            result = SimilarityResult(
                scores=final_scores,
                indices=final_indices.tolist(),
                distances=distances,
                metadata={
                    "computed_at": datetime.utcnow().isoformat(),
                    "metric": request.metric.value,
                    "total_candidates": len(request.candidate_vectors),
                    "threshold_applied": request.threshold,
                    "retriever": "SimilarityRetriever"
                }
            )

            self.logger.info(
                f"""Similarity computed: {len(final_scores)} results above threshold {request.threshold}"""
            )

            return result

        except Exception as e:
self.logger.error(f"Similarity computation failed: {str(e)}")
            return SimilarityResult(
                scores=[],
                indices=[],
                metadata={"error": str(e)}
            )

    def batch_similarity(self, request: BatchSimilarityRequest) -> List[SimilarityResult]:
        """Compute similarity for multiple query vectors.

        Args:
            request: Batch similarity request

        Returns:
            List[SimilarityResult]: Results for each query vector
        """
        self.logger.info(
            f"Computing batch similarity for {len(request.query_vectors)} queries")

        results = []

        try:
            # Process in batches to manage memory
            for i in range(0, len(request.query_vectors), self.config.batch_size):
                batch_queries = request.query_vectors[i : i + self.config.batch_size]

                for query_vector in batch_queries:
                    similarity_request = SimilarityRequest(
                        query_vector=query_vector,
                        candidate_vectors=request.candidate_vectors,
                        metric=request.metric,
                        top_k=request.top_k,
                        threshold=request.threshold
                    )

                    result = self.compute_similarity(similarity_request)
                    results.append(result)

            self.logger.info(
                f"Batch similarity completed for {len(results)} queries")

        except Exception as e:
self.logger.error(f"Batch similarity failed: {str(e)}")
            # Return empty results for failed batch
            results = [SimilarityResult(scores=[], indices=[], metadata={"error": str(e)})
                       for _ in request.query_vectors]

        return results

    def find_similar_vectors(self, query_vector: List[float], vector_dict: Dict[str, List[float]],
                             metric: Optional[SimilarityMetric] = None, top_k: int = 10) -> List[Tuple[str, float]]:
        """Find most similar vectors from a dictionary.

        Args:
            query_vector: Query vector to compare against
            vector_dict: Dictionary of vector_id -> vector
            metric: Similarity metric to use
            top_k: Number of results to return

        Returns:
            List of (vector_id, similarity_score) tuples
        """
        if not vector_dict:
            return []

        # Extract vectors and maintain mapping to IDs
        vector_ids = list(vector_dict.keys())
        vectors = list(vector_dict.values())

        # Compute similarity
        request = SimilarityRequest(
            query_vector=query_vector,
            candidate_vectors=vectors,
            metric=metric or self.config.default_metric,
            top_k=top_k
        )

        result = self.compute_similarity(request)

        # Map indices back to IDs
        similar_vectors = [(vector_ids[idx],
                            score) for idx,
                           score in zip(result.indices,
                                        result.scores)]

        return similar_vectors

    def _compute_pairwise_metric(self,
                                 vector1: np.ndarray,
                                 vector2: np.ndarray,
                                 metric: SimilarityMetric) -> float:
        """Compute similarity between two vectors for pairwise comparison."""
        if metric == SimilarityMetric.COSINE:
            return np.dot(vector1, vector2)
        elif metric == SimilarityMetric.DOT_PRODUCT:
            return np.dot(vector1, vector2)
        elif metric == SimilarityMetric.EUCLIDEAN:
            dist = np.linalg.norm(vector1 - vector2)
            return 1 / (1 + dist)
        elif metric == SimilarityMetric.MANHATTAN:
            dist = np.sum(np.abs(vector1 - vector2))
            return 1 / (1 + dist)
        else:
            return 0.0

    def compute_pairwise_similarity(self, vectors: List[List[float]],
                                    metric: Optional[SimilarityMetric] = None) -> np.ndarray:
        """Compute pairwise similarity matrix.

        Args:
            vectors: List of vectors to compare
            metric: Similarity metric to use

        Returns:
            np.ndarray: Similarity matrix
        """
        if not vectors:
            return np.array([])

        metric = metric or self.config.default_metric
        vectors_array = np.array(vectors)

        # Normalize if configured
        if self.config.normalize_vectors:
            vectors_array = np.array(
                [self._normalize_vector(v) for v in vectors_array])

        # Compute similarity matrix
        n = len(vectors)
        similarity_matrix = np.zeros((n, n))

        for i in range(n):
            for j in range(i, n):
                if i == j:
                    similarity_matrix[i, j] = 1.0
                else:
                    sim = self._compute_pairwise_metric(
                        vectors_array[i], vectors_array[j], metric)
                    similarity_matrix[i, j] = sim
                    similarity_matrix[j, i] = sim

        return similarity_matrix

    def _normalize_vector(self, vector: np.ndarray) -> np.ndarray:
        """Normalize vector to unit length."""
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def _jaccard_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> float:
        """Compute Jaccard similarity for binary vectors."""
        # Convert to binary (non-zero = 1)
        binary1 = (vector1 != 0).astype(int)
        binary2 = (vector2 != 0).astype(int)

        intersection = np.sum(binary1 & binary2)
        union = np.sum(binary1 | binary2)

        return intersection / union if union > 0 else 0.0

    def cache_vector(self, vector_id: str, vector: List[float]) -> None:
        """Cache a vector for faster retrieval.

        Args:
            vector_id: Unique identifier for the vector
            vector: Vector to cache
        """
        self._vector_cache[vector_id] = np.array(vector)

    def get_cached_vector(self, vector_id: str) -> Optional[List[float]]:
        """Get a cached vector.

        Args:
            vector_id: ID of cached vector

        Returns:
            Vector if found, None otherwise
        """
        if vector_id in self._vector_cache:
            return self._vector_cache[vector_id].tolist()
        return None

    def clear_cache(self) -> None:
        """Clear the vector cache."""
        self._vector_cache.clear()
        self.logger.info("Vector cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dict: Cache statistics
        """
        return {
            "cached_vectors": len(self._vector_cache),
            "cache_memory_mb": sum(v.nbytes for v in self._vector_cache.values()) / (1024 * 1024),
            "batch_size": self.config.batch_size,
            "normalize_vectors": self.config.normalize_vectors
        }

# Factory function for easy instantiation


def create_similarity_retriever(
    default_metric: str = "cosine",
    normalize_vectors: bool = True,
    batch_size: int = 1000,
        **kwargs: Dict[str, object]) -> SimilarityRetriever:
    """Create a configured similarity retriever."""
    config = SimilarityConfig(
        default_metric=SimilarityMetric(default_metric),
        normalize_vectors=normalize_vectors,
        batch_size=batch_size,
        **kwargs
    )
    return SimilarityRetriever(config)

# Convenience function for direct usage


def retrieve_similarity(
    query_vector: List[float],
    candidate_vectors: List[List[float]],
    metric: str = "cosine",
    top_k: int = 10,
    threshold: float = 0.0,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Retrieve similarity scores.

    Args:
        query_vector: Query vector
        candidate_vectors: List of candidate vectors
        metric: Similarity metric to use
        top_k: Number of top results to return
        threshold: Minimum similarity threshold
        config: Optional retriever configuration

    Returns:
        Dict: Similarity results
    """
    # Create retriever and compute similarity
    retriever_config = SimilarityConfig(**config or {})
    retriever = SimilarityRetriever(retriever_config)

    request = SimilarityRequest(
        query_vector=query_vector,
        candidate_vectors=candidate_vectors,
        metric=SimilarityMetric(metric),
        top_k=top_k,
        threshold=threshold,
        return_distances=True
    )

    result = retriever.compute_similarity(request)

    # Convert result to dict for JSON serialization
    return {
        "scores": result.scores,
        "indices": result.indices,
        "distances": result.distances,
        "metadata": result.metadata
    }

