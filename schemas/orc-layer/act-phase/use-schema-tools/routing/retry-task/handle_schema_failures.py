"""
Schema definitions for schema failure handling and recovery.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class FailureType(Enum):
    """Schema failure types."""
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    VALIDATION_ERROR = "validation_error"
    SYSTEM_ERROR = "system_error"


class HandlingStrategy(Enum):
    """Failure handling strategies."""
    RETRY = "retry"
    FALLBACK = "fallback"
    ESCALATE = "escalate"
    IGNORE = "ignore"


@dataclass
class SchemaFailure:
    """Schema for individual schema failure."""
    failure_id: str
    failure_type: FailureType
    failure_message: str
    failure_timestamp: str
    context: Dict[str, Any]


@dataclass
class FailureHandling:
    """Schema for failure handling context."""
    handling_id: str
    target_schema_id: str
    failures: List[SchemaFailure]
    handling_strategy: HandlingStrategy
    handling_timestamp: str


@dataclass
class FailureHandlingResult:
    """Schema for failure handling results."""
    result_id: str
    handling: FailureHandling
    handling_successful: bool
    recovered_failures: List[str]
    handling_actions: List[str]