"""
Schema definitions for schema ranking refinement and optimization.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class RefinementStrategy(Enum):
    """Ranking refinement strategies."""
    ITERATIVE_IMPROVEMENT = "iterative_improvement"
    GENETIC_ALGORITHM = "genetic_algorithm"
    SIMULATED_ANNEALING = "simulated_annealing"
    GRADIENT_DESCENT = "gradient_descent"


class OptimizationObjective(Enum):
    """Optimization objectives for ranking."""
    MAXIMIZE_RELEVANCE = "maximize_relevance"
    MINIMIZE_BIAS = "minimize_bias"
    BALANCE_DIVERSITY = "balance_diversity"
    OPTIMIZE_PERFORMANCE = "optimize_performance"


@dataclass
class RefinementConfiguration:
    """Schema for ranking refinement configuration."""
    strategy: RefinementStrategy
    objective: OptimizationObjective
    max_iterations: int = 100
    convergence_threshold: float = 0.001
    early_stopping: bool = True


@dataclass
class RefinementIteration:
    """Schema for individual refinement iteration."""
    iteration_number: int
    current_ranking: List[str]
    objective_score: float
    improvement_delta: float
    iteration_metadata: Dict[str, Any]


@dataclass
class RefinedRanking:
    """Schema for refined ranking results."""
    refinement_id: str
    final_ranking: List[str]
    iterations: List[RefinementIteration]
    final_objective_score: float
    convergence_achieved: bool