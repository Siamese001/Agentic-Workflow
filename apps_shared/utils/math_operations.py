"""
Math Operations Utilities - Phase 4 Optimization
Native Python implementations for common mathematical operations.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
import statistics
from dataclasses import dataclass


@dataclass
class ScoreResult:
    """Result of a scoring operation."""

    score: float
    normalized_score: float
    breakdown: Dict[str, float]
    metadata: Dict[str, Any]


class MathProcessor:
    """Native Python mathematical processing utilities."""

    @staticmethod
    def calculate_percentage(value: float, total: float, decimals: int = 2) -> float:
        """
        Calculate percentage.

        Args:
            value: Value to calculate percentage for
            total: Total value
            decimals: Number of decimal places

        Returns:
            Percentage value
        """
        if total == 0:
            return 0.0
        return round((value / total) * 100, decimals)

    @staticmethod
    def calculate_ratio(numerator: float, denominator: float, decimals: int = 2) -> float:
        """
        Calculate ratio.

        Args:
            numerator: Numerator value
            denominator: Denominator value
            decimals: Number of decimal places

        Returns:
            Ratio value
        """
        if denominator == 0:
            return 0.0
        return round(numerator / denominator, decimals)

    @staticmethod
    def normalize_score(
        score: float,
        min_val: float = 0.0,
        max_val: float = 100.0,
        target_min: float = 0.0,
        target_max: float = 1.0,
    ) -> float:
        """
        Normalize score to target range.

        Args:
            score: Score to normalize
            min_val: Minimum value in original range
            max_val: Maximum value in original range
            target_min: Minimum value in target range
            target_max: Maximum value in target range

        Returns:
            Normalized score
        """
        if max_val == min_val:
            return target_min

        normalized = (score - min_val) / (max_val - min_val)
        return target_min + (normalized * (target_max - target_min))

    @staticmethod
    def weighted_average(values: List[float], weights: Optional[List[float]] = None) -> float:
        """
        Calculate weighted average.

        Args:
            values: List of values
            weights: Optional list of weights (defaults to equal weights)

        Returns:
            Weighted average
        """
        if not values:
            return 0.0

        if weights is None:
            weights = [1.0] * len(values)

        if len(values) != len(weights):
            raise ValueError("Values and weights must have same length")

        total_weight = sum(weights)
        if total_weight == 0:
            return 0.0

        weighted_sum = sum(v * w for v, w in zip(values, weights))
        return weighted_sum / total_weight

    @staticmethod
    def calculate_statistics(values: List[float]) -> Dict[str, float]:
        """
        Calculate statistical measures.

        Args:
            values: List of numeric values

        Returns:
            Dictionary with statistical measures
        """
        if not values:
            return {
                "count": 0,
                "sum": 0.0,
                "mean": 0.0,
                "median": 0.0,
                "min": 0.0,
                "max": 0.0,
                "stdev": 0.0,
            }

        return {
            "count": len(values),
            "sum": sum(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "min": min(values),
            "max": max(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
        }

    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """
        Clamp value to range.

        Args:
            value: Value to clamp
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Returns:
            Clamped value
        """
        return max(min_val, min(value, max_val))

    @staticmethod
    def calculate_similarity(
        values1: List[float], values2: List[float], method: str = "cosine"
    ) -> float:
        """
        Calculate similarity between two value lists.

        Args:
            values1: First list of values
            values2: Second list of values
            method: Similarity method ('cosine', 'euclidean')

        Returns:
            Similarity score
        """
        if len(values1) != len(values2):
            raise ValueError("Value lists must have same length")

        if not values1:
            return 0.0

        if method == "cosine":
            dot_product = sum(a * b for a, b in zip(values1, values2))
            magnitude1 = sum(a * a for a in values1) ** 0.5
            magnitude2 = sum(b * b for b in values2) ** 0.5

            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0

            return dot_product / (magnitude1 * magnitude2)

        elif method == "euclidean":
            distance = sum((a - b) ** 2 for a, b in zip(values1, values2)) ** 0.5
            # Convert distance to similarity (0 = different, 1 = identical)
            max_distance = (len(values1) ** 0.5) * max(max(values1), max(values2))
            if max_distance == 0:
                return 1.0
            return 1.0 - (distance / max_distance)

        else:
            raise ValueError(f"Unknown similarity method: {method}")

    @staticmethod
    def calculate_growth_rate(old_value: float, new_value: float, decimals: int = 2) -> float:
        """
        Calculate growth rate.

        Args:
            old_value: Original value
            new_value: New value
            decimals: Number of decimal places

        Returns:
            Growth rate as percentage
        """
        if old_value == 0:
            return 0.0 if new_value == 0 else 100.0

        growth = ((new_value - old_value) / old_value) * 100
        return round(growth, decimals)

    @staticmethod
    def moving_average(values: List[float], window_size: int) -> List[float]:
        """
        Calculate moving average.

        Args:
            values: List of values
            window_size: Size of moving window

        Returns:
            List of moving averages
        """
        if window_size <= 0 or window_size > len(values):
            return []

        averages = []
        for i in range(len(values) - window_size + 1):
            window = values[i : i + window_size]
            averages.append(sum(window) / window_size)

        return averages

    @staticmethod
    def calculate_score_with_breakdown(
        components: Dict[str, float], weights: Optional[Dict[str, float]] = None
    ) -> ScoreResult:
        """
        Calculate weighted score with breakdown.

        Args:
            components: Dictionary of component scores
            weights: Optional dictionary of component weights

        Returns:
            ScoreResult with score and breakdown
        """
        if not components:
            return ScoreResult(
                score=0.0, normalized_score=0.0, breakdown={}, metadata={"total_weight": 0.0}
            )

        if weights is None:
            weights = {key: 1.0 for key in components.keys()}

        total_weight = sum(weights.get(key, 0.0) for key in components.keys())
        if total_weight == 0:
            return ScoreResult(
                score=0.0,
                normalized_score=0.0,
                breakdown=components,
                metadata={"total_weight": 0.0},
            )

        weighted_sum = sum(components[key] * weights.get(key, 0.0) for key in components.keys())
        score = weighted_sum / total_weight

        # Normalize to 0-1 range
        max_possible = max(components.values()) if components else 1.0
        normalized = score / max_possible if max_possible > 0 else 0.0

        return ScoreResult(
            score=score,
            normalized_score=normalized,
            breakdown=components,
            metadata={"total_weight": total_weight, "max_possible": max_possible},
        )
