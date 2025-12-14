"""Dataclass models for orchestrate_observability_planning."""

from typing import Any, Dict, List, Optional
import logging

# from .orchestrate_observability_planning_enums import *  # Star import removed

@dataclass
class ObservabilityPlanningResult:
    """Result of observability planning orchestration."""
    success: bool
    metric_definitions: List[MetricDefinition] = field(default_factory=list)
    log_configuration: Optional[LogConfiguration] = None
    trace_configuration: Optional[TraceConfiguration] = None
    alert_rules: List[AlertRule] = field(default_factory=list)
    resource_estimates: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
