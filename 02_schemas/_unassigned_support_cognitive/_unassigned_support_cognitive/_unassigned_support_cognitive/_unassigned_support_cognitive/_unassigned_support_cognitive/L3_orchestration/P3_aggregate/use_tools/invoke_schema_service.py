"""
Schema definitions for schema service invocation and execution.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class ServiceType(Enum):
    """Schema service types."""
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    ANALYSIS = "analysis"
    ORCHESTRATION = "orchestration"


class InvocationMode(Enum):
    """Service invocation modes."""
    SYNCHRONOUS = "synchronous"
    ASYNCHRONOUS = "asynchronous"
    STREAMING = "streaming"
    BATCH = "batch"


@dataclass
class ServiceInvocation:
    """Schema for individual service invocation."""
    invocation_id: str
    service_type: ServiceType
    service_name: str
    parameters: Dict[str, Any]
    invocation_mode: InvocationMode
    timeout_ms: int = 30000


@dataclass
class ServiceInvocationContext:
    """Schema for service invocation context."""
    context_id: str
    target_schema_id: str
    invocations: List[ServiceInvocation]
    invocation_environment: Dict[str, Any]
    invocation_timestamp: str


@dataclass
class ServiceInvocationResult:
    """Schema for service invocation results."""
    result_id: str
    context: ServiceInvocationContext
    invocation_successful: bool
    service_responses: List[Dict[str, Any]]
    invocation_time_ms: int