"""
Shared Analysis Mixin - Phase 2 Optimization
Provides common analysis workflow patterns for agents.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Any


@dataclass
class AnalysisResult:
    """Result of an analysis operation."""

    summary: str
    metrics: dict[str, Any]
    insights: list[str]
    recommendations: list[str]
    confidence: float


class AnalysisMixin:
    """
    Shared mixin for common analysis patterns.

    Provides standardized analysis methods that eliminate
    duplicate analysis boilerplate across agents.
    """

    def analyze_metrics(self, data: list[dict[str, Any]], metric_keys: list[str]) -> dict[str, Any]:
        """
        Analyze metrics from data collection.

        Args:
            data: List of data dictionaries
            metric_keys: Keys to analyze in each data item

        Returns:
            Dictionary with statistical analysis of metrics
        """
        results = {}

        for key in metric_keys:
            values = [item.get(key) for item in data if key in item and item[key] is not None]

            if not values:
                results[key] = {"error": "No data available"}
                continue

            # Handle numeric values
            if all(isinstance(v, int | float) for v in values):
                results[key] = {
                    "count": len(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "min": min(values),
                    "max": max(values),
                    "stdev": statistics.stdev(values) if len(values) > 1 else 0,
                }
            else:
                # Handle categorical values
                from collections import Counter

                counter = Counter(values)
                results[key] = {
                    "count": len(values),
                    "unique": len(counter),
                    "most_common": counter.most_common(5),
                }

        return results

    def calculate_trends(
        self,
        time_series: list[tuple[Any, float]],
        window_size: int = 5,
    ) -> dict[str, Any]:
        """
        Calculate trends from time series data.

        Args:
            time_series: List of (timestamp, value) tuples
            window_size: Size of moving average window

        Returns:
            Dictionary with trend analysis
        """
        if len(time_series) < 2:
            return {"trend": "insufficient_data", "direction": "unknown"}

        values = [v for _, v in time_series]

        # Calculate moving average
        moving_avg = []
        for i in range(len(values) - window_size + 1):
            window = values[i : i + window_size]
            moving_avg.append(sum(window) / window_size)

        # Determine trend direction
        if len(moving_avg) >= 2:
            if moving_avg[-1] > moving_avg[0]:
                direction = "increasing"
            elif moving_avg[-1] < moving_avg[0]:
                direction = "decreasing"
            else:
                direction = "stable"
        else:
            direction = "unknown"

        # Calculate rate of change
        if len(values) >= 2:
            rate_of_change = (values[-1] - values[0]) / len(values)
        else:
            rate_of_change = 0

        return {
            "trend": "calculated",
            "direction": direction,
            "rate_of_change": rate_of_change,
            "moving_average": moving_avg,
            "current_value": values[-1] if values else None,
        }

    def compare_datasets(
        self,
        dataset_a: list[Any],
        dataset_b: list[Any],
        comparison_key: str | None = None,
    ) -> dict[str, Any]:
        """
        Compare two datasets and identify differences.

        Args:
            dataset_a: First dataset
            dataset_b: Second dataset
            comparison_key: Key to use for comparison if datasets are dicts

        Returns:
            Dictionary with comparison results
        """
        results = {
            "size_a": len(dataset_a),
            "size_b": len(dataset_b),
            "size_difference": len(dataset_a) - len(dataset_b),
        }

        if comparison_key:
            # Compare by key
            keys_a = {item.get(comparison_key) for item in dataset_a if comparison_key in item}
            keys_b = {item.get(comparison_key) for item in dataset_b if comparison_key in item}

            results["unique_to_a"] = list(keys_a - keys_b)
            results["unique_to_b"] = list(keys_b - keys_a)
            results["common"] = list(keys_a & keys_b)
        else:
            # Direct comparison
            is_hashable_a = all(isinstance(x, str | int | float) for x in dataset_a)
            is_hashable_b = all(isinstance(x, str | int | float) for x in dataset_b)
            set_a = set(dataset_a) if is_hashable_a else None
            set_b = set(dataset_b) if is_hashable_b else None

            if set_a and set_b:
                results["unique_to_a"] = list(set_a - set_b)
                results["unique_to_b"] = list(set_b - set_a)
                results["common"] = list(set_a & set_b)

        return results

    def generate_insights(
        self,
        analysis_data: dict[str, Any],
        thresholds: dict[str, float] | None = None,
    ) -> list[str]:
        """
        Generate insights from analysis data.

        Args:
            analysis_data: Dictionary with analysis results
            thresholds: Optional thresholds for generating insights

        Returns:
            List of insight strings
        """
        insights = []
        thresholds = thresholds or {}

        for key, value in analysis_data.items():
            if isinstance(value, dict):
                # Check for threshold violations
                if "mean" in value:
                    mean_val = value["mean"]
                    threshold = thresholds.get(f"{key}_mean")
                    if threshold and mean_val > threshold:
                        insights.append(
                            f"{key} mean ({mean_val:.2f}) exceeds threshold ({threshold})",
                        )

                if "stdev" in value:
                    stdev_val = value["stdev"]
                    threshold = thresholds.get(f"{key}_stdev")
                    if threshold and stdev_val > threshold:
                        insights.append(f"{key} shows high variability (stdev: {stdev_val:.2f})")

        return insights

    def calculate_score(
        self,
        metrics: dict[str, float],
        weights: dict[str, float] | None = None,
    ) -> float:
        """
        Calculate weighted score from metrics.

        Args:
            metrics: Dictionary of metric names to values
            weights: Optional dictionary of metric names to weights

        Returns:
            Calculated weighted score (0.0 to 1.0)
        """
        if not metrics:
            return 0.0

        weights = weights or {key: 1.0 for key in metrics.keys()}
        total_weight = sum(weights.values())

        if total_weight == 0:
            return 0.0

        weighted_sum = sum(metrics.get(key, 0) * weights.get(key, 0) for key in metrics.keys())

        return weighted_sum / total_weight

    def identify_outliers(self, values: list[float], threshold: float = 2.0) -> dict[str, Any]:
        """
        Identify outliers in a dataset using standard deviation.

        Args:
            values: List of numeric values
            threshold: Number of standard deviations for outlier detection

        Returns:
            Dictionary with outlier analysis
        """
        if len(values) < 2:
            return {"outliers": [], "outlier_count": 0}

        mean = statistics.mean(values)
        stdev = statistics.stdev(values)

        outliers = []
        for i, value in enumerate(values):
            z_score = abs((value - mean) / stdev) if stdev > 0 else 0
            if z_score > threshold:
                outliers.append({"index": i, "value": value, "z_score": z_score})

        return {
            "outliers": outliers,
            "outlier_count": len(outliers),
            "mean": mean,
            "stdev": stdev,
            "threshold": threshold,
        }
