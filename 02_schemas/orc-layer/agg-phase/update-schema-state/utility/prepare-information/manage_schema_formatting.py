"""
Schema definitions for orchestration-level schema formatting management.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class FormattingStrategy(Enum):
    """Orchestration formatting strategies."""
    CENTRALIZED = "centralized"
    DISTRIBUTED = "distributed"
    TEMPLATE_BASED = "template_based"
    CUSTOM_RULES = "custom_rules"


class ManagementScope(Enum):
    """Formatting management scopes."""
    SINGLE_SCHEMA = "single_schema"
    SCHEMA_COLLECTION = "schema_collection"
    WORKFLOW_SPECIFIC = "workflow_specific"
    ENTERPRISE_WIDE = "enterprise_wide"


@dataclass
class FormattingManagementTask:
    """Schema for formatting management task."""
    task_id: str
    formatting_type: str
    target_schemas: List[str]
    formatting_strategy: FormattingStrategy
    management_scope: ManagementScope


@dataclass
class FormattingManagementPlan:
    """Schema for formatting management plan."""
    plan_id: str
    strategy: FormattingStrategy
    scope: ManagementScope
    tasks: List[FormattingManagementTask]
    estimated_completion_time_ms: int


@dataclass
class FormattingManagementResult:
    """Schema for formatting management results."""
    management_id: str
    plan: FormattingManagementPlan
    managed_formats: List[Dict[str, Any]]
    management_statistics: Dict[str, Any]
