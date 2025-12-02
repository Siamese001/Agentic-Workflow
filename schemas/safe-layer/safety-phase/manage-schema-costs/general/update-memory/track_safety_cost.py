"""
Schema definitions for safety cost tracking and monitoring.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, List, Union
from enum import Enum


class CostType(Enum):
    """Safety cost tracking types."""
    COMPUTATIONAL = "computational"
    FINANCIAL = "financial"
    TEMPORAL = "temporal"
    RESOURCE = "resource"


class TrackingFrequency(Enum):
    """Cost tracking frequency."""
    REAL_TIME = "real_time"
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"


@dataclass
class CostMetric:
    """Schema for individual cost metric."""
    metric_id: str
    cost_type: CostType
    value: Union[int, float]
    unit: str
    timestamp: str
    schema_id: str


@dataclass
class CostTracking:
    """Schema for cost tracking configuration."""
    tracking_id: str
    target_schema_id: str
    tracking_frequency: TrackingFrequency
    cost_types_tracked: List[CostType]
    retention_days: int = 30


@dataclass
class CostTrackingResult:
    """Schema for cost tracking results."""
    result_id: str
    tracking: CostTracking
    metrics_collected: List[CostMetric]
    total_cost: Dict[CostType, Union[int, float]]
    tracking_period: Dict[str, str]