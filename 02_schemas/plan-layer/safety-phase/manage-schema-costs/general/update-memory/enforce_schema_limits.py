"""
Schema definitions for schema limits enforcement and management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Union
from enum import Enum


class LimitType(Enum):
    """Schema limit enforcement types."""
    MEMORY = "memory"
    COMPUTATION = "computation"
    NETWORK = "network"
    STORAGE = "storage"


class EnforcementAction(Enum):
    """Limit enforcement actions."""
    THROTTLE = "throttle"
    BLOCK = "block"
    QUEUE = "queue"
    ESCALATE = "escalate"


@dataclass
class SchemaLimit:
    """Schema for individual schema limit."""
    limit_id: str
    limit_type: LimitType
    threshold_value: Union[int, float]
    current_usage: Union[int, float]
    enforcement_action: EnforcementAction


@dataclass
class LimitEnforcement:
    """Schema for limit enforcement context."""
    enforcement_id: str
    target_schema_id: str
    applied_limits: List[SchemaLimit]
    enforcement_timestamp: str
    context: Dict[str, Any]


@dataclass
class LimitEnforcementResult:
    """Schema for limit enforcement results."""
    result_id: str
    enforcement: LimitEnforcement
    violations_detected: List[str]
    actions_taken: List[EnforcementAction]
    enforcement_successful: bool