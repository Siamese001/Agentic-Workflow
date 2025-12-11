"""Aggregate Weighted Results - Utility for aggregating results with weights.

This module provides utilities for aggregating multiple results using various
weighting strategies and aggregation methods.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
import logging
from datetime import datetime
from enum import Enum
import math

logger = logging.getLogger(__name__)


class AggregationMethod(Enum):
    """Methods for aggregating weighted results."""
    WEIGHTED_AVERAGE = "weighted_average"
    WEIGHTED_SUM = "weighted_sum"
    WEIGHTED_MEDIAN = "weighted_median"
    WEIGHTED_MAX = "weighted_max"
    WEIGHTED_MIN = "weighted_min"
    CONSENSUS = "consensus"


class WeightStrategy(Enum):
    """Strategies for determining weights."""
    UNIFORM = "uniform"
    SCORE_BASED = "score_based"
    RANK_BASED = "rank_based"
    CUSTOM = "custom"
    CONFIDENCE_BASED = "confidence_based"


@dataclass
class WeightedResult:
    """Result with associated weight."""
    id: str
    value: Union[float, int, str, Dict[str, Any], List[Any]]
    weight: float
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AggregationConfig:
    """Configuration for aggregation operations."""
    method: AggregationMethod = AggregationMethod.WEIGHTED_AVERAGE
    weight_strategy: WeightStrategy = WeightStrategy.UNIFORM
    normalize_weights: bool = True
    handle_missing: str = "ignore"  # ignore, zero, average
    consensus_threshold: float = 0.7


@dataclass
class AggregationResult:
    """Result of aggregation operation."""
    aggregated_value: Union[float, int, str, Dict[str, Any], List[Any]]
    contributing_results: List[WeightedResult]
    weights_used: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)


class WeightedResultsAggregator:
    """Main class for aggregating weighted results."""

    def __init__(self, config: Optional[AggregationConfig] = None):
        self.config = config or AggregationConfig()
        self.logger = logging.getLogger(self.__class__.__name__)

    def aggregate(self, results: List[WeightedResult], 
                  custom_weights: Optional[List[float]] = None) -> AggregationResult:
        """Aggregate weighted results.
        
        Args:
            results: List of weighted results to aggregate
            custom_weights: Optional custom weights to use
            
        Returns:
            AggregationResult: Aggregated value with metadata
        """
        self.logger.info(f"Aggregating {len(results)} results using method: {self.config.method.value}")
        
        try:
            # Validate input
            if not results:
                return AggregationResult(
                    aggregated_value=None,
                    contributing_results=[],
                    weights_used=[],
                    metadata={"error": "No results provided"}
                )
            
            # Determine weights
            weights = self._determine_weights(results, custom_weights)
            
            # Normalize weights if configured
            if self.config.normalize_weights:
                weights = self._normalize_weights(weights)
            
            # Apply aggregation method
            aggregated_value = self._apply_aggregation(results, weights)
            
            result = AggregationResult(
                aggregated_value=aggregated_value,
                contributing_results=results,
                weights_used=weights,
                metadata={
                    "aggregated_at": datetime.utcnow().isoformat(),
                    "method": self.config.method.value,
                    "weight_strategy": self.config.weight_strategy.value,
                    "total_weight": sum(weights)
                }
            )
            
            self.logger.info(f"Aggregation completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Aggregation failed: {str(e)}")
            return AggregationResult(
                aggregated_value=None,
                contributing_results=results,
                weights_used=weights if 'weights' in locals() else [],
                metadata={"error": str(e)}
            )

    def aggregate_scores(self, scores: List[float], 
                         weights: Optional[List[float]] = None,
                         method: str = "weighted_average") -> float:
        """Simple aggregation for numeric scores.
        
        Args:
            scores: List of scores to aggregate
            weights: Optional weights for each score
            method: Aggregation method
            
        Returns:
            float: Aggregated score
        """
        # Convert to WeightedResult objects
        results = [
            WeightedResult(id=str(i), value=score, weight=1.0)
            for i, score in enumerate(scores)
        ]
        
        # Update config
        config = AggregationConfig(method=AggregationMethod(method))
        aggregator = WeightedResultsAggregator(config)
        
        # Aggregate
        result = aggregator.aggregate(results, weights)
        
        return float(result.aggregated_value) if result.aggregated_value is not None else 0.0

    def aggregate_rankings(self, rankings: List[List[str]], 
                          weights: Optional[List[float]] = None) -> List[str]:
        """Aggregate multiple rankings using weighted Borda count.
        
        Args:
            rankings: List of rankings (each is a list of items)
            weights: Optional weights for each ranking
            
        Returns:
            List[str]: Aggregated ranking
        """
        if not rankings:
            return []
        
        # Get all unique items
        all_items = set()
        for ranking in rankings:
            all_items.update(ranking)
        
        # Calculate Borda scores
        borda_scores = {item: 0.0 for item in all_items}
        
        # Determine weights
        if weights is None:
            weights = [1.0] * len(rankings)
        elif self.config.normalize_weights:
            weights = self._normalize_weights(weights)
        
        # Calculate weighted Borda scores
        for ranking, weight in zip(rankings, weights):
            for i, item in enumerate(ranking):
                # Borda score: (n - rank) * weight
                borda_scores[item] += (len(ranking) - i - 1) * weight
        
        # Sort by Borda score
        sorted_items = sorted(borda_scores.items(), key=lambda x: x[1], reverse=True)
        
        return [item for item, score in sorted_items]

    def aggregate_predictions(self, predictions: List[Dict[str, float]], 
                             weights: Optional[List[float]] = None) -> Dict[str, float]:
        """Aggregate probability predictions.
        
        Args:
            predictions: List of prediction dictionaries
            weights: Optional weights for each prediction
            
        Returns:
            Dict[str, float]: Aggregated predictions
        """
        if not predictions:
            return {}
        
        # Get all unique keys
        all_keys = set()
        for pred in predictions:
            all_keys.update(pred.keys())
        
        # Determine weights
        if weights is None:
            weights = [1.0] * len(predictions)
        elif self.config.normalize_weights:
            weights = self._normalize_weights(weights)
        
        # Aggregate predictions
        aggregated = {}
        for key in all_keys:
            weighted_sum = 0.0
            total_weight = 0.0
            
            for pred, weight in zip(predictions, weights):
                if key in pred:
                    weighted_sum += pred[key] * weight
                    total_weight += weight
            
            if total_weight > 0:
                aggregated[key] = weighted_sum / total_weight
        
        return aggregated

    def _determine_weights(self, results: List[WeightedResult], 
                          custom_weights: Optional[List[float]]) -> List[float]:
        """Determine weights for results."""
        if custom_weights is not None:
            return custom_weights
        
        if self.config.weight_strategy == WeightStrategy.UNIFORM:
            return [1.0] * len(results)
        
        elif self.config.weight_strategy == WeightStrategy.SCORE_BASED:
            # Use confidence or numeric values as weights
            weights = []
            for result in results:
                if result.confidence is not None:
                    weights.append(result.confidence)
                elif isinstance(result.value, (int, float)):
                    weights.append(abs(result.value))
                else:
                    weights.append(1.0)
            return weights
        
        elif self.config.weight_strategy == WeightStrategy.RANK_BASED:
            # Higher rank gets higher weight
            n = len(results)
            return [(n - i) / n for i in range(n)]
        
        elif self.config.weight_strategy == WeightStrategy.CUSTOM:
            # Use predefined weights from metadata
            return [result.weight for result in results]
        
        else:  # CONFIDENCE_BASED
            return [result.confidence or 1.0 for result in results]

    def _normalize_weights(self, weights: List[float]) -> List[float]:
        """Normalize weights to sum to 1."""
        total = sum(weights)
        if total == 0:
            return [1.0 / len(weights)] * len(weights)
        return [w / total for w in weights]

    def _apply_aggregation(self, results: List[WeightedResult], 
                          weights: List[float]) -> Union[float, int, str, Dict[str, Any], List[Any]]:
        """Apply the aggregation method."""
        if self.config.method == AggregationMethod.WEIGHTED_AVERAGE:
            return self._weighted_average(results, weights)
        
        elif self.config.method == AggregationMethod.WEIGHTED_SUM:
            return self._weighted_sum(results, weights)
        
        elif self.config.method == AggregationMethod.WEIGHTED_MEDIAN:
            return self._weighted_median(results, weights)
        
        elif self.config.method == AggregationMethod.WEIGHTED_MAX:
            return self._weighted_max(results, weights)
        
        elif self.config.method == AggregationMethod.WEIGHTED_MIN:
            return self._weighted_min(results, weights)
        
        else:  # CONSENSUS
            return self._consensus_aggregation(results, weights)

    def _weighted_average(self, results: List[WeightedResult], 
                          weights: List[float]) -> float:
        """Calculate weighted average."""
        if not results or not weights:
            return 0.0
        
        # Only works with numeric values
        numeric_results = []
        numeric_weights = []
        
        for result, weight in zip(results, weights):
            if isinstance(result.value, (int, float)):
                numeric_results.append(float(result.value))
                numeric_weights.append(weight)
        
        if not numeric_results:
            return 0.0
        
        weighted_sum = sum(v * w for v, w in zip(numeric_results, numeric_weights))
        total_weight = sum(numeric_weights)
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _weighted_sum(self, results: List[WeightedResult], 
                     weights: List[float]) -> float:
        """Calculate weighted sum."""
        if not results or not weights:
            return 0.0
        
        # Only works with numeric values
        numeric_results = []
        numeric_weights = []
        
        for result, weight in zip(results, weights):
            if isinstance(result.value, (int, float)):
                numeric_results.append(float(result.value))
                numeric_weights.append(weight)
        
        if not numeric_results:
            return 0.0
        
        return sum(v * w for v, w in zip(numeric_results, numeric_weights))

    def _weighted_median(self, results: List[WeightedResult], 
                         weights: List[float]) -> float:
        """Calculate weighted median."""
        if not results or not weights:
            return 0.0
        
        # Only works with numeric values
        numeric_pairs = []
        
        for result, weight in zip(results, weights):
            if isinstance(result.value, (int, float)):
                numeric_pairs.append((float(result.value), weight))
        
        if not numeric_pairs:
            return 0.0
        
        # Sort by value
        numeric_pairs.sort(key=lambda x: x[0])
        
        # Find median
        total_weight = sum(w for _, w in numeric_pairs)
        half_weight = total_weight / 2
        
        cumulative_weight = 0
        for value, weight in numeric_pairs:
            cumulative_weight += weight
            if cumulative_weight >= half_weight:
                return value
        
        return numeric_pairs[-1][0]

    def _weighted_max(self, results: List[WeightedResult], 
                     weights: List[float]) -> Union[float, int, str, Dict[str, Any], List[Any]]:
        """Find value with maximum weight."""
        if not results or not weights:
            return None
        
        max_pair = max(zip(results, weights), key=lambda x: x[1])
        return max_pair[0].value

    def _weighted_min(self, results: List[WeightedResult], 
                     weights: List[float]) -> Union[float, int, str, Dict[str, Any], List[Any]]:
        """Find value with minimum weight."""
        if not results or not weights:
            return None
        
        min_pair = min(zip(results, weights), key=lambda x: x[1])
        return min_pair[0].value

    def _consensus_aggregation(self, results: List[WeightedResult], 
                              weights: List[float]) -> Union[float, int, str, Dict[str, Any], List[Any]]:
        """Aggregate based on consensus threshold."""
        if not results or not weights:
            return None
        
        # Count occurrences with weights
        value_weights = {}
        
        for result, weight in zip(results, weights):
            value = result.value
            if value not in value_weights:
                value_weights[value] = 0.0
            value_weights[value] += weight
        
        # Find value with highest weight
        max_weight = max(value_weights.values())
        total_weight = sum(weights)
        
        # Check if consensus threshold is met
        if max_weight / total_weight >= self.config.consensus_threshold:
            return max(value_weights.items(), key=lambda x: x[1])[0]
        
        # No consensus, return weighted average for numeric values
        numeric_values = [(v, w) for v, w in value_weights.items() if isinstance(v, (int, float))]
        if numeric_values:
            weighted_sum = sum(v * w for v, w in numeric_values)
            total_numeric_weight = sum(w for _, w in numeric_values)
            return weighted_sum / total_numeric_weight if total_numeric_weight > 0 else 0.0
        
        # Return most common value
        return max(value_weights.items(), key=lambda x: x[1])[0]


# Factory function for easy instantiation
def create_weighted_results_aggregator(
    method: str = "weighted_average",
    weight_strategy: str = "uniform",
    normalize_weights: bool = True,
    **kwargs
) -> WeightedResultsAggregator:
    """Create a configured weighted results aggregator."""
    config = AggregationConfig(
        method=AggregationMethod(method),
        weight_strategy=WeightStrategy(weight_strategy),
        normalize_weights=normalize_weights,
        **kwargs
    )
    return WeightedResultsAggregator(config)


# Convenience function for direct usage
def aggregate_weighted_results(
    results: List[Dict[str, Any]],
    weights: Optional[List[float]] = None,
    method: str = "weighted_average",
    weight_strategy: str = "uniform"
) -> Dict[str, Any]:
    """Aggregate weighted results.
    
    Args:
        results: List of results with values and weights
        weights: Optional weights to use
        method: Aggregation method
        weight_strategy: Strategy for determining weights
        
    Returns:
        Dict: Aggregation result
    """
    # Create aggregator
    aggregator = create_weighted_results_aggregator(
        method=method,
        weight_strategy=weight_strategy
    )
    
    # Convert to WeightedResult objects
    weighted_results = []
    for i, result in enumerate(results):
        weighted_result = WeightedResult(
            id=result.get("id", str(i)),
            value=result.get("value"),
            weight=result.get("weight", 1.0),
            confidence=result.get("confidence")
        )
        weighted_results.append(weighted_result)
    
    # Aggregate
    result = aggregator.aggregate(weighted_results, weights)
    
    # Convert to dict
    return {
        "aggregated_value": result.aggregated_value,
        "contributing_results": [
            {
                "id": r.id,
                "value": r.value,
                "weight": r.weight,
                "confidence": r.confidence
            }
            for r in result.contributing_results
        ],
        "weights_used": result.weights_used,
        "metadata": result.metadata
    }
