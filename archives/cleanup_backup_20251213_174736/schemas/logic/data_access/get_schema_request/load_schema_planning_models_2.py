"""Dataclass models for load_schema_planning."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .load_schema_planning_enums import *

@dataclass
class SchemaLoadResult:
    """Result of schema load planning."""
    success: bool
    load_plan: Optional[SchemaLoadPlan] = None
    schema_count: int = 0
    dependency_count: int = 0
    validation_rule_count: int = 0
    transform_count: int = 0
    load_time_estimate: int = 0
    memory_estimate: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

