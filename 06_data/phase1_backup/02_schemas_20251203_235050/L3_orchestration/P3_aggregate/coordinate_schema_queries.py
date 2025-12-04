"""
Schema definitions for schema query coordination and management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class QueryType(Enum):
    """Schema query types."""
    RETRIEVAL = "retrieval"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    ANALYSIS = "analysis"


class CoordinationStrategy(Enum):
    """Query coordination strategies."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PRIORITY_BASED = "priority_based"
    ADAPTIVE = "adaptive"


@dataclass
class SchemaQuery:
    """Schema for individual schema query."""
    query_id: str
    query_type: QueryType
    query_parameters: Dict[str, Any]
    target_schema_id: str
    priority: int = 0


@dataclass
class QueryCoordination:
    """Schema for query coordination context."""
    coordination_id: str
    queries: List[SchemaQuery]
    coordination_strategy: CoordinationStrategy
    coordination_timestamp: str
    resource_allocation: Dict[str, int]


@dataclass
class QueryCoordinationResult:
    """Schema for query coordination results."""
    result_id: str
    coordination: QueryCoordination
    coordination_successful: bool
    executed_queries: List[str]
    coordination_time_ms: int