"""
Schema definitions for schema backoff strategy application and management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class BackoffType(Enum):
    """Backoff strategy types."""
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"
    ADAPTIVE = "adaptive"


class BackoffTrigger(Enum):
    """Backoff trigger conditions."""
    CONGESTION = "congestion"
    RATE_LIMIT = "rate_limit"
    SERVER_OVERLOAD = "server_overload"
    NETWORK_ISSUES = "network_issues"


@dataclass
class BackoffConfiguration:
    """Schema for backoff configuration."""
    backoff_type: BackoffType
    initial_delay_ms: int
    maximum_delay_ms: int
    multiplier: float = 2.0
    jitter: bool = True
    max_attempts: int = 5


@dataclass
class BackoffState:
    """Schema for backoff state tracking."""
    current_attempt: int
    current_delay_ms: int
    total_backoff_time_ms: int
    next_retry_time: Optional[str] = None


@dataclass
class BackoffResult:
    """Schema for backoff operation results."""
    backoff_id: str
    trigger_reason: BackoffTrigger
    total_attempts: int
    final_outcome: str
    backoff_history: List[int]
    total_delay_time_ms: int