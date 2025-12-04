"""
Schema definitions for schema fallback implementation and management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class FallbackType(Enum):
    """Schema fallback types."""
    ALTERNATIVE_SERVICE = "alternative_service"
    CACHED_RESULT = "cached_result"
    DEFAULT_RESPONSE = "default_response"
    SIMPLIFIED_OPERATION = "simplified_operation"


class FallbackTrigger(Enum):
    """Fallback trigger conditions."""
    FAILURE_THRESHOLD = "failure_threshold"
    TIMEOUT = "timeout"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    MANUAL_OVERRIDE = "manual_override"


@dataclass
class SchemaFallback:
    """Schema for individual schema fallback."""
    fallback_id: str
    fallback_type: FallbackType
    trigger_condition: FallbackTrigger
    fallback_configuration: Dict[str, Any]
    priority: int = 0


@dataclass
class FallbackImplementation:
    """Schema for fallback implementation context."""
    implementation_id: str
    target_schema_id: str
    active_fallbacks: List[SchemaFallback]
    implementation_timestamp: str
    implementation_environment: Dict[str, Any]


@dataclass
class FallbackImplementationResult:
    """Schema for fallback implementation results."""
    result_id: str
    implementation: FallbackImplementation
    implementation_successful: bool
    fallback_responses: List[Dict[str, Any]]
    implementation_time_ms: int