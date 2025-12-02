"""
Schema definitions for execution payload preparation and construction.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class PayloadType(Enum):
    """Execution payload types."""
    OPERATION = "operation"
    BATCH = "batch"
    STREAMING = "streaming"
    EVENT = "event"


class PreparationStrategy(Enum):
    """Payload preparation strategies."""
    IMMEDIATE = "immediate"
    LAZY = "lazy"
    CACHED = "cached"
    STREAMING = "streaming"


@dataclass
class PayloadSpecification:
    """Schema for payload specification."""
    spec_id: str
    payload_type: PayloadType
    content_size_bytes: int
    compression_required: bool = False
    encryption_required: bool = False


@dataclass
class ExecutionPayload:
    """Schema for execution payload."""
    payload_id: str
    specification: PayloadSpecification
    content: Dict[str, Any]
    preparation_strategy: PreparationStrategy
    preparation_timestamp: str


@dataclass
class PayloadPreparationResult:
    """Schema for payload preparation results."""
    result_id: str
    payload: ExecutionPayload
    preparation_successful: bool
    preparation_time_ms: int
    preparation_metadata: Dict[str, Any]