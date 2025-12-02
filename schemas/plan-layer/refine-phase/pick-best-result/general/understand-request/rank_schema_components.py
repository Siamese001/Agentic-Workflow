"""
Schema definitions for schema component ranking and ordering.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class RankingCriterion(Enum):
    """Component ranking criteria."""
    RELEVANCE = "relevance"
    CONFIDENCE = "confidence"
    COMPLEXITY = "complexity"
    PERFORMANCE = "performance"
    COMPLETENESS = "completeness"


class RankingMethod(Enum):
    """Ranking computation methods."""
    WEIGHTED_SUM = "weighted_sum"
    PARETO_OPTIMAL = "pareto_optimal"
    MULTI_CRITERIA = "multi_criteria"
    HIERARCHICAL = "hierarchical"


@dataclass
class RankingConfiguration:
    """Schema for ranking configuration."""
    method: RankingMethod
    criteria: List[RankingCriterion]
    weights: Dict[RankingCriterion, float]
    max_results: int = 10
    tie_breaker: Optional[RankingCriterion] = None


@dataclass
class ComponentRank:
    """Schema for individual component rank."""
    component_id: str
    rank_position: int
    score: float
    criterion_scores: Dict[RankingCriterion, float]
    ranking_metadata: Dict[str, Any]


@dataclass
class RankingResult:
    """Schema for complete ranking results."""
    ranking_id: str
    ranked_components: List[ComponentRank]
    configuration: RankingConfiguration
    ranking_timestamp: str