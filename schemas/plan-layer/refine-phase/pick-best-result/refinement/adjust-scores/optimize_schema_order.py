"""
Schema definitions for schema order optimization and sequencing.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum


class OptimizationAlgorithm(Enum):
    """Order optimization algorithms."""
    TRAVELING_SALESMAN = "traveling_salesman"
    GENETIC_ALGORITHM = "genetic_algorithm"
    ANT_COLONY = "ant_colony"
    SIMULATED_ANNEALING = "simulated_annealing"


class OrderObjective(Enum):
    """Order optimization objectives."""
    MINIMIZE_PROCESSING_TIME = "minimize_processing_time"
    MAXIMIZE_ACCURACY = "maximize_accuracy"
    BALANCE_WORKLOAD = "balance_workload"
    OPTIMIZE_MEMORY_USAGE = "optimize_memory_usage"


@dataclass
class OrderConstraints:
    """Schema for order optimization constraints."""
    mandatory_sequences: List[Tuple[str, str]]
    forbidden_sequences: List[Tuple[str, str]]
    time_limits: Dict[str, int]
    resource_constraints: Dict[str, int]


@dataclass
class OptimizedOrder:
    """Schema for optimized order results."""
    order_id: str
    schema_sequence: List[str]
    optimization_score: float
    constraints_satisfied: bool
    optimization_metadata: Dict[str, Any]


@dataclass
class OrderOptimizationResult:
    """Schema for complete order optimization results."""
    optimization_id: str
    best_order: OptimizedOrder
    alternative_orders: List[OptimizedOrder]
    optimization_statistics: Dict[str, float]