"""Dataclass models for load_planning."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .load_planning_enums import *

@dataclass
class ConfigLoadResult:
    """Result of config load planning."""
    success: bool
    load_plan: Optional[ConfigLoadPlan] = None
    estimated_config_size: int = 0
    validation_count: int = 0
    transformation_count: int = 0
    load_time_estimate: int = 0
    security_requirements: Dict[str, bool] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

