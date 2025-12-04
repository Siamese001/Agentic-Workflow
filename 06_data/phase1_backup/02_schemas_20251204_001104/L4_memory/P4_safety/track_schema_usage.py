"""
Schema definitions for schema usage tracking and monitoring.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, List, Union
from enum import Enum


class UsageType(Enum):
    """Schema usage tracking types."""
    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    STORAGE = "storage"
    API_CALLS = "api_calls"


class TrackingFrequency(Enum):
    """Usage tracking frequency."""
    REAL_TIME = "real_time"
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"


@dataclass
class UsageMetric:
    """Schema for individual usage metric."""
    metric_id: str
    usage_type: UsageType
    value: Union[int, float]
    unit: str
    timestamp: str
    schema_id: str


@dataclass
class UsageTracking:
    """Schema for usage tracking configuration."""
    tracking_id: str
    target_schema_id: str
    tracking_frequency: TrackingFrequency
    metrics_tracked: List[UsageType]
    retention_days: int = 30


@dataclass
class UsageTrackingResult:
    """Schema for usage tracking results."""
    result_id: str
    tracking: UsageTracking
    metrics_collected: List[UsageMetric]
    total_usage: Dict[UsageType, Union[int, float]]
    tracking_period: Dict[str, str]