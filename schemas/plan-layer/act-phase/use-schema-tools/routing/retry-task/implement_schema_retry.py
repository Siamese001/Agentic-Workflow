"""
Schema definitions for schema retry implementation and management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class RetryStrategy(Enum):
    """Retry implementation strategies."""
    FIXED_INTERVAL = "fixed_interval"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    CUSTOM = "custom"


class RetryTrigger(Enum):
    """Retry trigger conditions."""
    NETWORK_ERROR = "network_error"
    TIMEOUT = "timeout"
    SERVER_ERROR = "server_error"
    RATE_LIMIT = "rate_limit"


@dataclass
class RetryConfiguration:
    """Schema for retry configuration."""
    strategy: RetryStrategy
    max_attempts: int
    base_delay_ms: int
    max_delay_ms: int
    retry_on_triggers: List[RetryTrigger]


@dataclass
class RetryAttempt:
    """Schema for individual retry attempt."""
    attempt_number: int
    trigger_reason: RetryTrigger
    delay_ms: int
    attempt_timestamp: str
    result: Optional[Dict[str, Any]] = None


@dataclass
class RetryResult:
    """Schema for retry operation results."""
    retry_id: str
    original_request_id: str
    total_attempts: int
    successful_attempt: Optional[int] = None
    attempts: List[RetryAttempt]
    final_status: str