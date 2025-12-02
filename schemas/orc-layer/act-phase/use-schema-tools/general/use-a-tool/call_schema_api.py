"""
Schema definitions for schema API calling and invocation.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ApiType(Enum):
    """Schema API types."""
    REST = "rest"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    WEBSOCKET = "websocket"


class CallMode(Enum):
    """API call modes."""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    STREAMING = "streaming"
    BATCH = "batch"


@dataclass
class ApiCall:
    """Schema for individual API call."""
    call_id: str
    api_type: ApiType
    endpoint: str
    method: str
    parameters: Dict[str, Any]
    call_mode: CallMode
    timeout_ms: int = 30000


@dataclass
class ApiCallContext:
    """Schema for API call context."""
    context_id: str
    target_schema_id: str
    api_calls: List[ApiCall]
    call_environment: Dict[str, Any]
    call_timestamp: str


@dataclass
class ApiCallResult:
    """Schema for API call results."""
    result_id: str
    context: ApiCallContext
    call_successful: bool
    responses: List[Dict[str, Any]]
    call_time_ms: int