"""
Schema definitions for schema operation retry and recovery.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class RetryStrategy(Enum):
    """Schema retry strategies."""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_INTERVAL = "fixed_interval"
    ADAPTIVE = "adaptive"


class RetryCondition(Enum):
    """Retry trigger conditions."""
    TRANSIENT_ERROR = "transient_error"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    SERVICE_UNAVAILABLE = "service_unavailable"


@dataclass
class RetryConfiguration:
    """Schema for retry configuration."""
    config_id: str
    retry_strategy: RetryStrategy
    max_attempts: int
    base_delay_ms: int
    max_delay_ms: int
    retry_conditions: List[RetryCondition]


@dataclass
class SchemaRetry:
    """Schema for individual schema retry."""
    retry_id: str
    target_operation_id: str
    configuration: RetryConfiguration
    attempt_count: int
    retry_timestamp: str


@dataclass
class RetryResult:
    """Schema for retry results."""
    result_id: str
    retry: SchemaRetry
    retry_successful: bool
    total_attempts: int
    final_outcome: Dict[str, Any]