"""
Schema definitions for schema filter construction and application.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Any, List, Union
from enum import Enum


class FilterOperator(Enum):
    """Schema filter operators."""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IN = "in"
    NOT_IN = "not_in"


class FilterLogic(Enum):
    """Filter combination logic."""
    AND = "and"
    OR = "or"
    NOT = "not"


@dataclass
class SchemaFilter:
    """Schema for individual schema filter."""
    field_path: str
    operator: FilterOperator
    value: Union[str, int, float, bool, List[Any]]
    case_sensitive: bool = True


@dataclass
class FilterGroup:
    """Schema for grouped filters with logic."""
    filters: List[SchemaFilter]
    logic: FilterLogic
    nested_groups: Optional[List['FilterGroup']] = None


@dataclass
class FilterConfiguration:
    """Schema for filter configuration."""
    filter_group: FilterGroup
    max_results: Optional[int] = None
    sort_by: Optional[str] = None
    sort_order: str = "ascending"