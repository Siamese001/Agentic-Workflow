"""Normalize Vectors - Utility for normalizing vector embeddings.

This module provides various methods for normalizing vectors, including
L1, L2, and unit vector normalization with proper handling of edge cases.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
from datetime import datetime
from enum import Enum
import math

logger = logging.getLogger(__name__)


class NormalizationMethod(Enum):
    """Methods for vector normalization."""
    L1 = "l1"
    L2 = "l2"
    MAX = "max"
    UNIT = "unit"
    MIN_MAX = "min_max"
    Z_SCORE = "z_score"


@dataclass
class NormalizationConfig:
    """Configuration for normalization operations."""
    method: NormalizationMethod = NormalizationMethod.L2
    handle_zeros: str = "keep"  # keep, skip, warn
    epsilon: float = 1e-8
    target_range: Tuple[float, float] = (0.0, 1.0)


@dataclass
class NormalizationResult:
    """Result of vector normalization."""
    normalized_vectors: List[List[float]]
    original_vectors: List[List[float]]
    method: NormalizationMethod
    statistics: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class VectorNormalizer:
    """Main class for normalizing vectors."""

    def __init__(self, config: Optional[NormalizationConfig] = None):
        self.config = config or NormalizationConfig()
        self.logger = logging.getLogger(self.__class__.__name__)

    def normalize_vectors(self, vectors: List[List[float]], 
                         method: Optional[NormalizationMethod] = None) -> NormalizationResult:
        """Normalize a list of vectors.
        
        Args:
            vectors: List of vectors to normalize
            method: Normalization method (uses config default if not provided)
            
        Returns:
            NormalizationResult: Normalized vectors with metadata
        """
        method = method or self.config.method
        
        self.logger.info(f"Normalizing {len(vectors)} vectors using method: {method.value}")
        
        try:
            # Validate input
            if not vectors:
                return NormalizationResult(
                    normalized_vectors=[],
                    original_vectors=[],
                    method=method,
                    metadata={"error": "No vectors provided"}
                )
            
            # Check for zero vectors
            zero_count = sum(1 for v in vectors if self._is_zero_vector(v))
            if zero_count > 0 and self.config.handle_zeros == "warn":
                self.logger.warning(f"Found {zero_count} zero vectors")
            
            # Normalize based on method
            if method == NormalizationMethod.L1:
                normalized = self._normalize_l1(vectors)
            elif method == NormalizationMethod.L2:
                normalized = self._normalize_l2(vectors)
            elif method == NormalizationMethod.MAX:
                normalized = self._normalize_max(vectors)
            elif method == NormalizationMethod.UNIT:
                normalized = self._normalize_unit(vectors)
            elif method == NormalizationMethod.MIN_MAX:
                normalized = self._normalize_min_max(vectors)
            elif method == NormalizationMethod.Z_SCORE:
                normalized = self._normalize_z_score(vectors)
            else:
                raise ValueError(f"Unknown normalization method: {method}")
            
            # Calculate statistics
            statistics = self._calculate_statistics(normalized)
            
            result = NormalizationResult(
                normalized_vectors=normalized,
                original_vectors=vectors,
                method=method,
                statistics=statistics,
                metadata={
                    "normalized_at": datetime.utcnow().isoformat(),
                    "vector_count": len(vectors),
                    "dimension": len(vectors[0]) if vectors else 0,
                    "zero_vectors_handled": zero_count
                }
            )
            
            self.logger.info(f"Normalization completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Normalization failed: {str(e)}")
            return NormalizationResult(
                normalized_vectors=[],
                original_vectors=vectors,
                method=method,
                metadata={"error": str(e)}
            )

    def normalize_single_vector(self, vector: List[float], 
                               method: Optional[NormalizationMethod] = None) -> List[float]:
        """Normalize a single vector.
        
        Args:
            vector: Vector to normalize
            method: Normalization method
            
        Returns:
            List[float]: Normalized vector
        """
        result = self.normalize_vectors([vector], method)
        return result.normalized_vectors[0] if result.normalized_vectors else []

    def batch_normalize(self, vector_batches: List[List[List[float]]], 
                       method: Optional[NormalizationMethod] = None) -> List[NormalizationResult]:
        """Normalize multiple batches of vectors.
        
        Args:
            vector_batches: List of vector batches
            method: Normalization method
            
        Returns:
            List[NormalizationResult]: Results for each batch
        """
        results = []
        
        for i, batch in enumerate(vector_batches):
            self.logger.debug(f"Normalizing batch {i+1}/{len(vector_batches)}")
            result = self.normalize_vectors(batch, method)
            results.append(result)
        
        return results

    def denormalize_vectors(self, normalized_vectors: List[List[float]], 
                           original_statistics: Dict[str, float],
                           method: Optional[NormalizationMethod] = None) -> List[List[float]]:
        """Denormalize vectors back to original scale.
        
        Args:
            normalized_vectors: Normalized vectors
            original_statistics: Statistics from original normalization
            method: Normalization method used
            
        Returns:
            List[List[float]]: Denormalized vectors
        """
        method = method or self.config.method
        
        self.logger.info(f"Denormalizing {len(normalized_vectors)} vectors")
        
        try:
            if method == NormalizationMethod.MIN_MAX:
                return self._denormalize_min_max(normalized_vectors, original_statistics)
            elif method == NormalizationMethod.Z_SCORE:
                return self._denormalize_z_score(normalized_vectors, original_statistics)
            else:
                # For L1, L2, MAX, UNIT normalization, denormalization is not straightforward
                self.logger.warning(f"Denormalization not supported for method: {method.value}")
                return normalized_vectors
                
        except Exception as e:
            self.logger.error(f"Denormalization failed: {str(e)}")
            return normalized_vectors

    def _normalize_l1(self, vectors: List[List[float]]) -> List[List[float]]:
        """L1 normalization (Manhattan norm)."""
        normalized = []
        
        for vector in vectors:
            if self._is_zero_vector(vector):
                if self.config.handle_zeros != "skip":
                    normalized.append(vector.copy())
                continue
            
            l1_norm = sum(abs(x) for x in vector)
            if l1_norm > self.config.epsilon:
                normalized.append([x / l1_norm for x in vector])
            else:
                normalized.append(vector.copy())
        
        return normalized

    def _normalize_l2(self, vectors: List[List[float]]) -> List[List[float]]:
        """L2 normalization (Euclidean norm)."""
        normalized = []
        
        for vector in vectors:
            if self._is_zero_vector(vector):
                if self.config.handle_zeros != "skip":
                    normalized.append(vector.copy())
                continue
            
            l2_norm = math.sqrt(sum(x * x for x in vector))
            if l2_norm > self.config.epsilon:
                normalized.append([x / l2_norm for x in vector])
            else:
                normalized.append(vector.copy())
        
        return normalized

    def _normalize_max(self, vectors: List[List[float]]) -> List[List[float]]:
        """Max normalization (divide by max absolute value)."""
        normalized = []
        
        for vector in vectors:
            if self._is_zero_vector(vector):
                if self.config.handle_zeros != "skip":
                    normalized.append(vector.copy())
                continue
            
            max_val = max(abs(x) for x in vector)
            if max_val > self.config.epsilon:
                normalized.append([x / max_val for x in vector])
            else:
                normalized.append(vector.copy())
        
        return normalized

    def _normalize_unit(self, vectors: List[List[float]]) -> List[List[float]]:
        """Unit vector normalization (same as L2)."""
        return self._normalize_l2(vectors)

    def _normalize_min_max(self, vectors: List[List[float]]) -> List[List[float]]:
        """Min-max normalization to [0, 1] range."""
        if not vectors:
            return []
        
        # Find global min and max for each dimension
        dimensions = len(vectors[0])
        mins = [float('inf')] * dimensions
        maxs = [float('-inf')] * dimensions
        
        for vector in vectors:
            for i, val in enumerate(vector):
                mins[i] = min(mins[i], val)
                maxs[i] = max(maxs[i], val)
        
        # Normalize each vector
        normalized = []
        for vector in vectors:
            normalized_vector = []
            for i, val in enumerate(vector):
                range_val = maxs[i] - mins[i]
                if range_val > self.config.epsilon:
                    normalized_val = (val - mins[i]) / range_val
                else:
                    normalized_val = 0.0
                normalized_vector.append(normalized_val)
            normalized.append(normalized_vector)
        
        return normalized

    def _normalize_z_score(self, vectors: List[List[float]]) -> List[List[float]]:
        """Z-score normalization (standardization)."""
        if not vectors:
            return []
        
        # Calculate mean and std for each dimension
        dimensions = len(vectors[0])
        sums = [0.0] * dimensions
        sums_sq = [0.0] * dimensions
        
        for vector in vectors:
            for i, val in enumerate(vector):
                sums[i] += val
                sums_sq[i] += val * val
        
        n = len(vectors)
        means = [s / n for s in sums]
        stds = [math.sqrt((sq / n) - (mean * mean)) for sq, mean in zip(sums_sq, means)]
        
        # Normalize each vector
        normalized = []
        for vector in vectors:
            normalized_vector = []
            for i, val in enumerate(vector):
                if stds[i] > self.config.epsilon:
                    normalized_val = (val - means[i]) / stds[i]
                else:
                    normalized_val = 0.0
                normalized_vector.append(normalized_val)
            normalized.append(normalized_vector)
        
        return normalized

    def _denormalize_min_max(self, normalized_vectors: List[List[float]], 
                             statistics: Dict[str, float]) -> List[List[float]]:
        """Denormalize from min-max scaling."""
        # This would need the original min/max values
        # For now, return as-is
        return normalized_vectors

    def _denormalize_z_score(self, normalized_vectors: List[List[float]], 
                            statistics: Dict[str, float]) -> List[List[float]]:
        """Denormalize from z-score."""
        # This would need the original mean and std values
        # For now, return as-is
        return normalized_vectors

    def _is_zero_vector(self, vector: List[float]) -> bool:
        """Check if vector is all zeros."""
        return all(abs(x) < self.config.epsilon for x in vector)

    def _calculate_statistics(self, vectors: List[List[float]]) -> Dict[str, float]:
        """Calculate normalization statistics."""
        if not vectors:
            return {}
        
        stats = {}
        
        # Calculate average norm
        norms = []
        for vector in vectors:
            norm = math.sqrt(sum(x * x for x in vector))
            norms.append(norm)
        
        stats["avg_norm"] = sum(norms) / len(norms)
        stats["min_norm"] = min(norms)
        stats["max_norm"] = max(norms)
        
        # Calculate sparsity (percentage of near-zero values)
        total_elements = len(vectors) * len(vectors[0])
        zero_elements = sum(
            1 for vector in vectors 
            for x in vector 
            if abs(x) < self.config.epsilon
        )
        stats["sparsity"] = zero_elements / total_elements
        
        return stats


# Factory function for easy instantiation
def create_vector_normalizer(
    method: str = "l2",
    handle_zeros: str = "keep",
    epsilon: float = 1e-8,
    **kwargs
) -> VectorNormalizer:
    """Create a configured vector normalizer."""
    config = NormalizationConfig(
        method=NormalizationMethod(method),
        handle_zeros=handle_zeros,
        epsilon=epsilon,
        **kwargs
    )
    return VectorNormalizer(config)


# Convenience function for direct usage
def normalize_vectors(
    vectors: List[List[float]],
    method: str = "l2",
    handle_zeros: str = "keep",
    epsilon: float = 1e-8
) -> List[List[float]]:
    """Normalize vectors.
    
    Args:
        vectors: List of vectors to normalize
        method: Normalization method
        handle_zeros: How to handle zero vectors
        epsilon: Small value to avoid division by zero
        
    Returns:
        List[List[float]]: Normalized vectors
    """
    normalizer = create_vector_normalizer(
        method=method,
        handle_zeros=handle_zeros,
        epsilon=epsilon
    )
    
    result = normalizer.normalize_vectors(vectors)
    return result.normalized_vectors
