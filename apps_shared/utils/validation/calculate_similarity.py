"""Calculate Similarity - Utility for calculating similarity between vectors.

This module provides various similarity metrics for comparing vectors, including
cosine similarity, Euclidean distance, and correlation measures.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
from datetime import datetime
from enum import Enum
import math

logger = logging.getLogger(__name__)


class SimilarityMetric(Enum):
    """Similarity metrics for vector comparison."""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    MANHATTAN = "manhattan"
    DOT_PRODUCT = "dot_product"
    PEARSON = "pearson"
    JACCARD = "jaccard"
    HAMMING = "hamming"


@dataclass
class SimilarityConfig:
    """Configuration for similarity calculations."""
    metric: SimilarityMetric = SimilarityMetric.COSINE
    normalize_inputs: bool = True
    epsilon: float = 1e-8
    return_distance: bool = False


@dataclass
class SimilarityResult:
    """Result of similarity calculation."""
    similarity: float
    distance: Optional[float] = None
    metric: SimilarityMetric = SimilarityMetric.COSINE
    metadata: Dict[str, Any] = field(default_factory=dict)


class SimilarityCalculator:
    """Main class for calculating vector similarities."""

    def __init__(self, config: Optional[SimilarityConfig] = None):
        self.config = config or SimilarityConfig()
        self.logger = logging.getLogger(self.__class__.__name__)

    def calculate_similarity(self, vector1: List[float], vector2: List[float],
                           metric: Optional[SimilarityMetric] = None) -> SimilarityResult:
        """Calculate similarity between two vectors.
        
        Args:
            vector1: First vector
            vector2: Second vector
            metric: Similarity metric to use
            
        Returns:
            SimilarityResult: Similarity score and optional distance
        """
        metric = metric or self.config.metric
        
        self.logger.debug(f"Calculating similarity using metric: {metric.value}")
        
        try:
            # Validate inputs
            if len(vector1) != len(vector2):
                raise ValueError("Vectors must have the same dimension")
            
            if not vector1 or not vector2:
                return SimilarityResult(
                    similarity=0.0,
                    metric=metric,
                    metadata={"error": "Empty vectors provided"}
                )
            
            # Normalize if configured
            if self.config.normalize_inputs:
                vector1 = self._normalize_vector(vector1)
                vector2 = self._normalize_vector(vector2)
            
            # Calculate similarity based on metric
            if metric == SimilarityMetric.COSINE:
                similarity = self._cosine_similarity(vector1, vector2)
                distance = 1 - similarity if self.config.return_distance else None
            
            elif metric == SimilarityMetric.EUCLIDEAN:
                distance = self._euclidean_distance(vector1, vector2)
                similarity = 1 / (1 + distance) if not self.config.return_distance else None
            
            elif metric == SimilarityMetric.MANHATTAN:
                distance = self._manhattan_distance(vector1, vector2)
                similarity = 1 / (1 + distance) if not self.config.return_distance else None
            
            elif metric == SimilarityMetric.DOT_PRODUCT:
                similarity = self._dot_product(vector1, vector2)
                distance = None
            
            elif metric == SimilarityMetric.PEARSON:
                similarity = self._pearson_correlation(vector1, vector2)
                distance = 1 - abs(similarity) if self.config.return_distance else None
            
            elif metric == SimilarityMetric.JACCARD:
                similarity = self._jaccard_similarity(vector1, vector2)
                distance = 1 - similarity if self.config.return_distance else None
            
            elif metric == SimilarityMetric.HAMMING:
                distance = self._hamming_distance(vector1, vector2)
                similarity = 1 - distance if not self.config.return_distance else None
            
            else:
                raise ValueError(f"Unknown similarity metric: {metric}")
            
            result = SimilarityResult(
                similarity=similarity if similarity is not None else 0.0,
                distance=distance,
                metric=metric,
                metadata={
                    "calculated_at": datetime.utcnow().isoformat(),
                    "vector_dimension": len(vector1),
                    "normalized": self.config.normalize_inputs
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Similarity calculation failed: {str(e)}")
            return SimilarityResult(
                similarity=0.0,
                metric=metric,
                metadata={"error": str(e)}
            )

    def calculate_pairwise_similarities(self, vectors: List[List[float]],
                                      metric: Optional[SimilarityMetric] = None) -> List[List[float]]:
        """Calculate pairwise similarity matrix.
        
        Args:
            vectors: List of vectors
            metric: Similarity metric to use
            
        Returns:
            List[List[float]]: Similarity matrix
        """
        n = len(vectors)
        similarity_matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(i, n):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                else:
                    result = self.calculate_similarity(vectors[i], vectors[j], metric)
                    similarity = result.similarity
                    similarity_matrix[i][j] = similarity
                    similarity_matrix[j][i] = similarity
        
        return similarity_matrix

    def find_most_similar(self, query_vector: List[float], 
                         candidate_vectors: List[List[float]],
                         top_k: int = 5,
                         metric: Optional[SimilarityMetric] = None) -> List[Tuple[int, float]]:
        """Find most similar vectors to query.
        
        Args:
            query_vector: Query vector
            candidate_vectors: List of candidate vectors
            top_k: Number of top results to return
            metric: Similarity metric to use
            
        Returns:
            List[Tuple[int, float]]: (index, similarity) pairs
        """
        similarities = []
        
        for i, candidate in enumerate(candidate_vectors):
            result = self.calculate_similarity(query_vector, candidate, metric)
            similarities.append((i, result.similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]

    def calculate_similarity_batch(self, vector_pairs: List[Tuple[List[float], List[float]]],
                                 metric: Optional[SimilarityMetric] = None) -> List[SimilarityResult]:
        """Calculate similarities for multiple vector pairs.
        
        Args:
            vector_pairs: List of vector pairs
            metric: Similarity metric to use
            
        Returns:
            List[SimilarityResult]: Results for each pair
        """
        results = []
        
        for vector1, vector2 in vector_pairs:
            result = self.calculate_similarity(vector1, vector2, metric)
            results.append(result)
        
        return results

    def _normalize_vector(self, vector: List[float]) -> List[float]:
        """Normalize vector to unit length."""
        norm = math.sqrt(sum(x * x for x in vector))
        if norm < self.config.epsilon:
            return vector.copy()
        return [x / norm for x in vector]

    def _cosine_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """Calculate cosine similarity."""
        dot_product = sum(x * y for x, y in zip(vector1, vector2))
        norm1 = math.sqrt(sum(x * x for x in vector1))
        norm2 = math.sqrt(sum(x * x for x in vector2))
        
        if norm1 < self.config.epsilon or norm2 < self.config.epsilon:
            return 0.0
        
        return dot_product / (norm1 * norm2)

    def _euclidean_distance(self, vector1: List[float], vector2: List[float]) -> float:
        """Calculate Euclidean distance."""
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(vector1, vector2)))

    def _manhattan_distance(self, vector1: List[float], vector2: List[float]) -> float:
        """Calculate Manhattan distance."""
        return sum(abs(x - y) for x, y in zip(vector1, vector2))

    def _dot_product(self, vector1: List[float], vector2: List[float]) -> float:
        """Calculate dot product."""
        return sum(x * y for x, y in zip(vector1, vector2))

    def _pearson_correlation(self, vector1: List[float], vector2: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        n = len(vector1)
        
        # Calculate means
        mean1 = sum(vector1) / n
        mean2 = sum(vector2) / n
        
        # Calculate covariance and variances
        covariance = sum((x - mean1) * (y - mean2) for x, y in zip(vector1, vector2))
        var1 = sum((x - mean1) ** 2 for x in vector1)
        var2 = sum((y - mean2) ** 2 for y in vector2)
        
        if var1 < self.config.epsilon or var2 < self.config.epsilon:
            return 0.0
        
        return covariance / math.sqrt(var1 * var2)

    def _jaccard_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """Calculate Jaccard similarity (for binary vectors)."""
        # Convert to binary (non-zero = 1)
        binary1 = [1 if x != 0 else 0 for x in vector1]
        binary2 = [1 if x != 0 else 0 for x in vector2]
        
        intersection = sum(1 for x, y in zip(binary1, binary2) if x == 1 and y == 1)
        union = sum(1 for x, y in zip(binary1, binary2) if x == 1 or y == 1)
        
        if union == 0:
            return 1.0
        
        return intersection / union

    def _hamming_distance(self, vector1: List[float], vector2: List[float]) -> float:
        """Calculate Hamming distance (for binary vectors)."""
        # Convert to binary
        binary1 = [1 if x > 0 else 0 for x in vector1]
        binary2 = [1 if x > 0 else 0 for x in vector2]
        
        differences = sum(1 for x, y in zip(binary1, binary2) if x != y)
        
        return differences / len(binary1)


# Factory function for easy instantiation
def create_similarity_calculator(
    metric: str = "cosine",
    normalize_inputs: bool = True,
    epsilon: float = 1e-8,
    **kwargs
) -> SimilarityCalculator:
    """Create a configured similarity calculator."""
    config = SimilarityConfig(
        metric=SimilarityMetric(metric),
        normalize_inputs=normalize_inputs,
        epsilon=epsilon,
        **kwargs
    )
    return SimilarityCalculator(config)


# Convenience function for direct usage
def calculate_similarity(
    vector1: List[float],
    vector2: List[float],
    metric: str = "cosine",
    normalize_inputs: bool = True,
    return_distance: bool = False
) -> Dict[str, Any]:
    """Calculate similarity between two vectors.
    
    Args:
        vector1: First vector
        vector2: Second vector
        metric: Similarity metric to use
        normalize_inputs: Whether to normalize inputs
        return_distance: Whether to return distance
        
    Returns:
        Dict: Similarity result
    """
    calculator = create_similarity_calculator(
        metric=metric,
        normalize_inputs=normalize_inputs,
        return_distance=return_distance
    )
    
    result = calculator.calculate_similarity(vector1, vector2)
    
    return {
        "similarity": result.similarity,
        "distance": result.distance,
        "metric": result.metric.value,
        "metadata": result.metadata
    }
