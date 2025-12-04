"""
Schema definitions for schema context management and orchestration.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class ContextType(Enum):
    """Schema context types."""
    EXECUTION = "execution"
    SECURITY = "security"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"


class ManagementStrategy(Enum):
    """Context management strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    HYBRID = "hybrid"
    EVENT_DRIVEN = "event_driven"


@dataclass
class SchemaContext:
    """Schema for individual schema context."""
    context_id: str
    context_type: ContextType
    context_data: Dict[str, Any]
    target_schema_id: str
    expiration_timestamp: str


@dataclass
class ContextManagement:
    """Schema for context management configuration."""
    management_id: str
    contexts: List[SchemaContext]
    management_strategy: ManagementStrategy
    management_timestamp: str
    retention_policy: Dict[str, Any]


@dataclass
class ContextManagementResult:
    """Schema for context management results."""
    result_id: str
    management: ContextManagement
    management_successful: bool
    managed_contexts: List[str]
    management_time_ms: int