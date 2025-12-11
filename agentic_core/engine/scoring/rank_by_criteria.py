"""Rank by Criteria - Utility for ranking items based on multiple criteria.

This module provides utilities for ranking items using multiple criteria with
different weighting strategies and ranking methods.
Follows the functional component pattern with proper logging.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
import logging
from datetime import datetime
from enum import Enum
import math

logger = logging.getLogger(__name__)


class RankingMethod(Enum):
    """Methods for multi-criteria ranking."""
    WEIGHTED_SUM = "weighted_sum"
    WEIGHTED_PRODUCT = "weighted_product"
    TOPSIS = "topsis"
    ELECTRE = "electre"
    PARETO = "pareto"


class AggregationType(Enum):
    """Types of score aggregation."""
    SUM = "sum"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"


@dataclass
class Criterion:
    """Definition of a ranking criterion."""
    name: str
    weight: float
    direction: str = "max"  # "max" for benefit, "min" for cost
    normalize: bool = True
    scale: Optional[Tuple[float, float]] = None


@dataclass
class RankingItem:
    """Item to be ranked with its criteria values."""
    id: str
    name: str
    values: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RankingConfig:
    """Configuration for ranking operations."""
    method: RankingMethod = RankingMethod.WEIGHTED_SUM
    normalize_criteria: bool = True
    handle_missing: str = "zero"  # zero, mean, median, skip
    tie_breaker: str = "id"  # id, name, random


@dataclass
class RankingResult:
    """Result of ranking operation."""
    item_id: str
    rank: int
    score: float
    criteria_scores: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RankingReport:
    """Complete ranking results with analysis."""
    criteria: List[Criterion]
    results: List[RankingResult]
    total_items: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class CriteriaRanker:
    """Main class for ranking by multiple criteria."""

    def __init__(self, criteria: List[Criterion], config: Optional[RankingConfig] = None):
        self.criteria = criteria
        self.config = config or RankingConfig()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Validate weights sum to 1 for weighted methods
        if self.config.method in [RankingMethod.WEIGHTED_SUM, RankingMethod.WEIGHTED_PRODUCT]:
            total_weight = sum(c.weight for c in criteria)
            if abs(total_weight - 1.0) > 0.001:
                self.logger.warning(f"Criterion weights sum to {total_weight}, normalizing to 1.0")
                for c in criteria:
                    c.weight = c.weight / total_weight

    def rank_items(self, items: List[RankingItem]) -> RankingReport:
        """Rank items based on criteria.
        
        Args:
            items: List of items to rank
            
        Returns:
            RankingReport: Complete ranking results
        """
        self.logger.info(f"Ranking {len(items)} items using {len(self.criteria)} criteria")
        
        try:
            # Validate input
            if not items:
                return RankingReport(
                    criteria=self.criteria,
                    results=[],
                    total_items=0,
                    metadata={"error": "No items provided"}
                )
            
            # Prepare criteria values matrix
            values_matrix = self._prepare_values_matrix(items)
            
            # Normalize values if configured
            if self.config.normalize_criteria:
                values_matrix = self._normalize_values(values_matrix)
            
            # Calculate ranking scores
            if self.config.method == RankingMethod.WEIGHTED_SUM:
                scores, criteria_scores = self._weighted_sum_ranking(values_matrix)
            elif self.config.method == RankingMethod.WEIGHTED_PRODUCT:
                scores, criteria_scores = self._weighted_product_ranking(values_matrix)
            elif self.config.method == RankingMethod.TOPSIS:
                scores, criteria_scores = self._topsis_ranking(values_matrix)
            elif self.config.method == RankingMethod.ELECTRE:
                scores, criteria_scores = self._electre_ranking(values_matrix)
            else:  # PARETO
                scores, criteria_scores = self._pareto_ranking(values_matrix)
            
            # Create ranking results
            results = []
            sorted_indices = sorted(range(len(scores)), key=lambda x: scores[x], reverse=True)
            
            for rank, idx in enumerate(sorted_indices, 1):
                item = items[idx]
                result = RankingResult(
                    item_id=item.id,
                    rank=rank,
                    score=scores[idx],
                    criteria_scores=criteria_scores[idx],
                    metadata=item.metadata
                )
                results.append(result)
            
            # Handle ties
            results = self._handle_ties(results)
            
            report = RankingReport(
                criteria=self.criteria,
                results=results,
                total_items=len(items),
                metadata={
                    "ranked_at": datetime.utcnow().isoformat(),
                    "method": self.config.method.value,
                    "items_ranked": len(results)
                }
            )
            
            self.logger.info(f"Ranking completed successfully")
            return report
            
        except Exception as e:
            self.logger.error(f"Ranking failed: {str(e)}")
            return RankingReport(
                criteria=self.criteria,
                results=[],
                total_items=len(items),
                metadata={"error": str(e)}
            )

    def get_top_k(self, items: List[RankingItem], k: int) -> List[RankingResult]:
        """Get top k ranked items.
        
        Args:
            items: List of items to rank
            k: Number of top items to return
            
        Returns:
            List[RankingResult]: Top k items
        """
        report = self.rank_items(items)
        return report.results[:k]

    def get_criterion_importance(self) -> Dict[str, float]:
        """Get importance weights for all criteria.
        
        Returns:
            Dict[str, float]: Criterion importance weights
        """
        return {c.name: c.weight for c in self.criteria}

    def analyze_sensitivity(self, items: List[RankingItem], 
                           criterion_name: str, 
                           weight_range: Tuple[float, float] = (0.0, 1.0),
                           steps: int = 10) -> Dict[str, List[float]]:
        """Analyze ranking sensitivity to criterion weight changes.
        
        Args:
            items: Items to analyze
            criterion_name: Criterion to vary
            weight_range: Range of weight values to test
            steps: Number of steps in the range
            
        Returns:
            Dict: Sensitivity analysis results
        """
        # Find criterion
        criterion = None
        for c in self.criteria:
            if c.name == criterion_name:
                criterion = c
                break
        
        if not criterion:
            raise ValueError(f"Criterion {criterion_name} not found")
        
        # Store original weight
        original_weight = criterion.weight
        
        # Test different weight values
        sensitivity_results = {}
        weight_step = (weight_range[1] - weight_range[0]) / (steps - 1)
        
        for i in range(steps):
            new_weight = weight_range[0] + i * weight_step
            
            # Update criterion weight and normalize others
            criterion.weight = new_weight
            total_other_weight = sum(c.weight for c in self.criteria if c != criterion)
            
            if total_other_weight > 0:
                remaining_weight = 1.0 - new_weight
                for c in self.criteria:
                    if c != criterion:
                        c.weight = c.weight * remaining_weight / total_other_weight
            
            # Rank items
            report = self.rank_items(items)
            sensitivity_results[f"weight_{new_weight:.2f}"] = [r.rank for r in report.results]
        
        # Restore original weight
        criterion.weight = original_weight
        
        return sensitivity_results

    def _prepare_values_matrix(self, items: List[RankingItem]) -> List[List[float]]:
        """Prepare matrix of criteria values for all items."""
        matrix = []
        
        for item in items:
            row = []
            for criterion in self.criteria:
                value = item.values.get(criterion.name, 0.0)
                
                # Handle missing values
                if criterion.name not in item.values:
                    if self.config.handle_missing == "mean":
                        # Calculate mean for this criterion
                        values = [i.values.get(criterion.name, 0.0) for i in items]
                        values = [v for v in values if v != 0.0]
                        value = sum(values) / len(values) if values else 0.0
                    elif self.config.handle_missing == "median":
                        # Calculate median for this criterion
                        values = [i.values.get(criterion.name, 0.0) for i in items]
                        values = sorted(v for v in values if v != 0.0)
                        if values:
                            mid = len(values) // 2
                            value = values[mid] if len(values) % 2 else (values[mid-1] + values[mid]) / 2
                        else:
                            value = 0.0
                    elif self.config.handle_missing == "skip":
                        value = float('nan')
                    else:  # zero
                        value = 0.0
                
                row.append(value)
            
            matrix.append(row)
        
        return matrix

    def _normalize_values(self, values_matrix: List[List[float]]) -> List[List[float]]:
        """Normalize criterion values."""
        if not values_matrix:
            return values_matrix
        
        n_items = len(values_matrix)
        n_criteria = len(self.criteria)
        
        normalized_matrix = []
        
        for j in range(n_criteria):
            criterion = self.criteria[j]
            column = [values_matrix[i][j] for i in range(n_items)]
            
            # Remove NaN values for normalization
            valid_values = [v for v in column if not math.isnan(v)]
            
            if not valid_values:
                normalized_column = [0.0] * n_items
            else:
                min_val = min(valid_values)
                max_val = max(valid_values)
                range_val = max_val - min_val
                
                if range_val == 0:
                    normalized_column = [1.0 if not math.isnan(v) else 0.0 for v in column]
                else:
                    normalized_column = []
                    for v in column:
                        if math.isnan(v):
                            normalized_column.append(0.0)
                        else:
                            if criterion.direction == "max":
                                normalized_val = (v - min_val) / range_val
                            else:  # min
                                normalized_val = (max_val - v) / range_val
                            normalized_column.append(normalized_val)
            
            # Add to matrix
            if not normalized_matrix:
                normalized_matrix = [[] for _ in range(n_items)]
            
            for i in range(n_items):
                normalized_matrix[i].append(normalized_column[i])
        
        return normalized_matrix

    def _weighted_sum_ranking(self, values_matrix: List[List[float]]) -> Tuple[List[float], List[Dict[str, float]]]:
        """Calculate weighted sum ranking scores."""
        scores = []
        criteria_scores = []
        
        for row in values_matrix:
            score = 0.0
            criterion_scores = {}
            
            for i, (value, criterion) in enumerate(zip(row, self.criteria)):
                weighted_value = value * criterion.weight
                score += weighted_value
                criterion_scores[criterion.name] = weighted_value
            
            scores.append(score)
            criteria_scores.append(criterion_scores)
        
        return scores, criteria_scores

    def _weighted_product_ranking(self, values_matrix: List[List[float]]) -> Tuple[List[float], List[Dict[str, float]]]:
        """Calculate weighted product ranking scores."""
        scores = []
        criteria_scores = []
        
        for row in values_matrix:
            score = 1.0
            criterion_scores = {}
            
            for i, (value, criterion) in enumerate(zip(row, self.criteria)):
                # Avoid zero values in product
                adjusted_value = max(value, 0.001)
                weighted_value = adjusted_value ** criterion.weight
                score *= weighted_value
                criterion_scores[criterion.name] = weighted_value
            
            scores.append(score)
            criteria_scores.append(criterion_scores)
        
        return scores, criteria_scores

    def _topsis_ranking(self, values_matrix: List[List[float]]) -> Tuple[List[float], List[Dict[str, float]]]:
        """Calculate TOPSIS ranking scores."""
        if not values_matrix:
            return [], []
        
        n_items = len(values_matrix)
        n_criteria = len(self.criteria)
        
        # Calculate weighted normalized matrix
        weighted_matrix = []
        for row in values_matrix:
            weighted_row = [value * criterion.weight for value, criterion in zip(row, self.criteria)]
            weighted_matrix.append(weighted_row)
        
        # Find ideal and negative ideal solutions
        ideal_best = []
        ideal_worst = []
        
        for j in range(n_criteria):
            column = [weighted_matrix[i][j] for i in range(n_items)]
            ideal_best.append(max(column))
            ideal_worst.append(min(column))
        
        # Calculate TOPSIS scores
        scores = []
        criteria_scores = []
        
        for i in range(n_items):
            # Distance to ideal best
            dist_best = math.sqrt(sum((weighted_matrix[i][j] - ideal_best[j]) ** 2 for j in range(n_criteria)))
            
            # Distance to ideal worst
            dist_worst = math.sqrt(sum((weighted_matrix[i][j] - ideal_worst[j]) ** 2 for j in range(n_criteria)))
            
            # TOPSIS score
            score = dist_worst / (dist_best + dist_worst) if (dist_best + dist_worst) > 0 else 0.0
            
            scores.append(score)
            criteria_scores.append({c.name: weighted_matrix[i][j] for j, c in enumerate(self.criteria)})
        
        return scores, criteria_scores

    def _electre_ranking(self, values_matrix: List[List[float]]) -> Tuple[List[float], List[Dict[str, float]]]:
        """Calculate ELECTRE ranking scores."""
        n_items = len(values_matrix)
        n_criteria = len(self.criteria)
        
        # Calculate concordance and discordance matrices
        concordance = [[0.0] * n_items for _ in range(n_items)]
        discordance = [[0.0] * n_items for _ in range(n_items)]
        
        for i in range(n_items):
            for j in range(n_items):
                if i != j:
                    concordance_sum = 0.0
                    max_discordance = 0.0
                    
                    for k in range(n_criteria):
                        if values_matrix[i][k] >= values_matrix[j][k]:
                            concordance_sum += self.criteria[k].weight
                        else:
                            discordance_val = (values_matrix[j][k] - values_matrix[i][k])
                            max_discordance = max(max_discordance, discordance_val)
                    
                    concordance[i][j] = concordance_sum
                    discordance[i][j] = max_discordance
        
        # Calculate net outranking scores
        scores = []
        criteria_scores = []
        
        for i in range(n_items):
            net_score = 0.0
            criterion_scores = {c.name: values_matrix[i][j] for j, c in enumerate(self.criteria)}
            
            for j in range(n_items):
                if i != j:
                    if concordance[i][j] > concordance[j][i]:
                        net_score += 1
                    elif concordance[i][j] < concordance[j][i]:
                        net_score -= 1
            
            scores.append(net_score)
            criteria_scores.append(criterion_scores)
        
        return scores, criteria_scores

    def _pareto_ranking(self, values_matrix: List[List[float]]) -> Tuple[List[float], List[Dict[str, float]]]:
        """Calculate Pareto ranking scores."""
        n_items = len(values_matrix)
        
        # Find Pareto fronts
        scores = [0] * n_items
        criteria_scores = []
        
        for i in range(n_items):
            criterion_scores = {c.name: values_matrix[i][j] for j, c in enumerate(self.criteria)}
            criteria_scores.append(criterion_scores)
            
            # Count how many items dominate this item
            dominated_count = 0
            for j in range(n_items):
                if i != j:
                    dominates = True
                    for k in range(len(self.criteria)):
                        if values_matrix[i][k] < values_matrix[j][k]:
                            dominates = False
                            break
                    if dominates:
                        dominated_count += 1
            
            # Lower dominated count is better (Pareto rank)
            scores[i] = -dominated_count
        
        return scores, criteria_scores

    def _handle_ties(self, results: List[RankingResult]) -> List[RankingResult]:
        """Handle ties in ranking results."""
        # Group by score
        score_groups = {}
        for result in results:
            if result.score not in score_groups:
                score_groups[result.score] = []
            score_groups[result.score].append(result)
        
        # Sort within each tie group
        final_results = []
        current_rank = 1
        
        for score in sorted(score_groups.keys(), reverse=True):
            tied_results = score_groups[score]
            
            if self.config.tie_breaker == "id":
                tied_results.sort(key=lambda x: x.item_id)
            elif self.config.tie_breaker == "name":
                tied_results.sort(key=lambda x: x.metadata.get("name", ""))
            elif self.config.tie_breaker == "random":
                import random
                random.shuffle(tied_results)
            
            # Assign ranks
            for result in tied_results:
                result.rank = current_rank
                final_results.append(result)
            
            current_rank += len(tied_results)
        
        return final_results


# Factory function for easy instantiation
def create_criteria_ranker(
    criteria: List[Dict[str, Any]],
    method: str = "weighted_sum",
    normalize_criteria: bool = True,
    **kwargs
) -> CriteriaRanker:
    """Create a configured criteria ranker."""
    criterion_objects = []
    for c in criteria:
        criterion_objects.append(Criterion(
            name=c["name"],
            weight=c["weight"],
            direction=c.get("direction", "max"),
            normalize=c.get("normalize", True)
        ))
    
    config = RankingConfig(
        method=RankingMethod(method),
        normalize_criteria=normalize_criteria,
        **kwargs
    )
    return CriteriaRanker(criterion_objects, config)


# Convenience function for direct usage
def rank_by_criteria(
    items: List[Dict[str, Any]],
    criteria: List[Dict[str, Any]],
    method: str = "weighted_sum",
    top_k: int = None
) -> Dict[str, Any]:
    """Rank items by multiple criteria.
    
    Args:
        items: List of items to rank
        criteria: List of ranking criteria
        method: Ranking method to use
        top_k: Number of top results to return
        
    Returns:
        Dict: Ranking results
    """
    ranker = create_criteria_ranker(criteria, method=method)
    
    # Convert items
    item_objects = []
    for item in items:
        item_obj = RankingItem(
            id=item["id"],
            name=item.get("name", ""),
            values=item.get("values", {}),
            metadata=item.get("metadata", {})
        )
        item_objects.append(item_obj)
    
    # Rank items
    report = ranker.rank_items(item_objects)
    
    # Limit results if top_k specified
    results = report.results[:top_k] if top_k else report.results
    
    return {
        "criteria": [{"name": c.name, "weight": c.weight} for c in report.criteria],
        "results": [
            {
                "item_id": r.item_id,
                "rank": r.rank,
                "score": r.score,
                "criteria_scores": r.criteria_scores
            }
            for r in results
        ],
        "total_items": report.total_items,
        "metadata": report.metadata
    }
