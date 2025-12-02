"""
Schema definitions for schema impact evaluation and analysis.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class ImpactType(Enum):
    """Types of schema impacts."""
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    USER_EXPERIENCE = "user_experience"


class ImpactScope(Enum):
    """Impact evaluation scopes."""
    SINGLE_COMPONENT = "single_component"
    SYSTEM_WIDE = "system_wide"
    CROSS_LAYER = "cross_layer"
    EXTERNAL_DEPENDENCIES = "external_dependencies"


@dataclass
class ImpactMetric:
    """Schema for individual impact metric."""
    metric_id: str
    impact_type: ImpactType
    current_value: float
    projected_value: float
    change_percentage: float
    confidence_level: float


@dataclass
class ImpactEvaluation:
    """Schema for impact evaluation context."""
    evaluation_id: str
    target_schema_id: str
    impact_scope: ImpactScope
    metrics: List[ImpactMetric]
    evaluation_timestamp: str


@dataclass
class ImpactEvaluationResult:
    """Schema for impact evaluation results."""
    result_id: str
    evaluation: ImpactEvaluation
    overall_impact_score: float
    high_impact_areas: List[ImpactType]
    mitigation_strategies: List[str]
    approval_required: bool
