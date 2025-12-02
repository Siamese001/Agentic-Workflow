"""
Schema definitions for orchestration-level schema filter construction.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Any, List, Union
from enum import Enum


class FilterScope(Enum):
    """Orchestration filter scopes."""
    WORKFLOW = "workflow"
    SERVICE = "service"
    TASK = "task"
    RESOURCE = "resource"


class FilterOperator(Enum):
    """Orchestration filter operators."""
    EQUALS = "equals"
    CONTAINS = "contains"
    MATCHES = "matches"
    IN_RANGE = "in_range"
    HAS_ATTRIBUTE = "has_attribute"


@dataclass
class OrchestrationFilter:
    """Schema for orchestration filter definition."""
    filter_id: str
    scope: FilterScope
    operator: FilterOperator
    attribute_path: str
    value: Union[str, int, float, bool, List[Any]]
    case_sensitive: bool = True


@dataclass
class FilterComposition:
    """Schema for filter composition logic."""
    composition_id: str
    filters: List[OrchestrationFilter]
    logical_operator: str
    nested_compositions: Optional[List['FilterComposition']] = None


@dataclass
class FilterConstructionResult:
    """Schema for filter construction results."""
    construction_id: str
    composition: FilterComposition
    estimated_performance_cost: float
    optimization_suggestions: List[str]
    construction_timestamp: str
