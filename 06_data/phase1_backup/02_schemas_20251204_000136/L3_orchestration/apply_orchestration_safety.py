"""
Schema definitions for orchestration safety application and enforcement.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class SafetyLevel(Enum):
    """Orchestration safety levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SafetyCategory(Enum):
    """Orchestration safety categories."""
    WORKFLOW_SAFETY = "workflow_safety"
    RESOURCE_SAFETY = "resource_safety"
    COORDINATION_SAFETY = "coordination_safety"
    COMMUNICATION_SAFETY = "communication_safety"


@dataclass
class OrchestrationSafetyRule:
    """Schema for individual orchestration safety rule."""
    rule_id: str
    category: SafetyCategory
    safety_level: SafetyLevel
    rule_expression: str
    auto_correctable: bool = False


@dataclass
class SafetyApplication:
    """Schema for safety application context."""
    application_id: str
    target_orchestration_id: str
    applied_rules: List[OrchestrationSafetyRule]
    application_timestamp: str
    context: Dict[str, Any]


@dataclass
class SafetyApplicationResult:
    """Schema for safety application results."""
    result_id: str
    application: SafetyApplication
    safety_passed: bool
    violations: List[Dict[str, Any]]
    auto_corrections: List[Dict[str, Any]]