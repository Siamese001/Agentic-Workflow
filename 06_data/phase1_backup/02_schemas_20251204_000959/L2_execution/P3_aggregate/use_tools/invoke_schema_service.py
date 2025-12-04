"""
Schema definitions for schema service invocation and communication.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class ServiceType(Enum):
    """Types of schema services."""
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    GENERATION = "generation"
    ANALYSIS = "analysis"


class InvocationMethod(Enum):
    """Service invocation methods."""
    REST_API = "rest_api"
    GRPC = "grpc"
    MESSAGE_QUEUE = "message_queue"
    DIRECT_CALL = "direct_call"


@dataclass
class ServiceEndpoint:
    """Schema for service endpoint definition."""
    service_type: ServiceType
    url: str
    method: InvocationMethod
    authentication: Optional[Dict[str, str]] = None
    timeout_ms: int = 5000


@dataclass
class ServiceRequest:
    """Schema for service request payload."""
    request_id: str
    service_type: ServiceType
    payload: Dict[str, Any]
    headers: Optional[Dict[str, str]] = None
    priority: str = "normal"


@dataclass
class ServiceResponse:
    response_id: str
    request_id: str
    status_code: int
    response_time_ms: int
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    """Schema for service response data."""