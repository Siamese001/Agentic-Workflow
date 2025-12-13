"""Dataclass models for understand_request_load_planning."""

from typing import Any, Dict, List, Optional
# from .understand_request_load_planning_enums import *  # Star import removed

@dataclass
class ConfigLoadResult:
    """Result of config load planning."""
    success: bool
    load_plan: Optional[ConfigLoadPlan] = None
    parameter_count: int = 0
    section_count: int = 0
    validation_rule_count: int = 0
    load_time_estimate: int = 0
    memory_estimate: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
