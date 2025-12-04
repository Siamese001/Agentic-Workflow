"""
Schema definitions for schema filter enforcement and application.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class FilterType(Enum):
    """Schema filter types."""
    CONTENT_FILTER = "content_filter"
    ACCESS_FILTER = "access_filter"
    PRIVACY_FILTER = "privacy_filter"
    SECURITY_FILTER = "security_filter"


class FilterAction(Enum):
    """Filter enforcement actions."""
    ALLOW = "allow"
    BLOCK = "block"
    MODIFY = "modify"
    LOG = "log"
    ESCALATE = "escalate"


@dataclass
class SchemaFilter:
    """Schema for individual schema filter."""
    filter_id: str
    filter_type: FilterType
    conditions: List[Dict[str, Any]]
    action: FilterAction
    priority: int = 0


@dataclass
class FilterEnforcement:
    """Schema for filter enforcement context."""
    enforcement_id: str
    target_schema_id: str
    applied_filters: List[SchemaFilter]
    enforcement_timestamp: str
    trigger_context: Dict[str, Any]


@dataclass
class FilterEnforcementResult:
    """Schema for filter enforcement results."""
    result_id: str
    enforcement: FilterEnforcement
    filters_triggered: List[str]
    final_action: FilterAction
    modifications_made: Optional[Dict[str, Any]] = None