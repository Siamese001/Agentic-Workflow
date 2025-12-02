"""
Schema definitions for schema response processing and handling.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ResponseType(Enum):
    """Types of schema responses."""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    TIMEOUT = "timeout"


class ProcessingAction(Enum):
    """Response processing actions."""
    STORE = "store"
    FORWARD = "forward"
    TRANSFORM = "transform"
    AGGREGATE = "aggregate"


@dataclass
class ResponseMetadata:
    """Schema for response metadata."""
    response_id: str
    source_service: str
    timestamp: str
    processing_time_ms: int
    size_bytes: int


@dataclass
class ProcessingConfiguration:
    """Schema for response processing configuration."""
    default_action: ProcessingAction
    error_handling: str = "retry"
    max_retries: int = 3
    timeout_ms: int = 10000


@dataclass
class ProcessedResponse:
    """Schema for processed response data."""
    original_response: Dict[str, Any]
    processed_data: Optional[Dict[str, Any]] = None
    processing_actions: List[ProcessingAction]
    metadata: ResponseMetadata
    processing_timestamp: str