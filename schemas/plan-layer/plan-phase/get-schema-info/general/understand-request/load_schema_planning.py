"""
Schema definitions for loading and parsing schema planning information.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class PlanningPriority(Enum):
    """Priority levels for schema planning operations."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SchemaPlanningRequest:
    """Schema for planning request parameters."""
    schema_id: str
    priority: PlanningPriority
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, str]] = None


@dataclass
class SchemaPlanningResponse:
    """Schema for planning response structure."""
    request_id: str
    status: str
    planning_data: Dict[str, Any]
    execution_plan: Optional[List[str]] = None
    errors: Optional[List[str]] = None


@dataclass
class PlanningParameters:
    """Schema for planning configuration parameters."""
    timeout_seconds: int
    max_retries: int
    resource_limits: Dict[str, int]
    validation_rules: List[str]