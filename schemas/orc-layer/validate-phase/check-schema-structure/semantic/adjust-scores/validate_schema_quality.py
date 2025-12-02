"""
Schema definitions for orchestration-level schema quality validation.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, Any, List
from enum import Enum


class QualityDimension(Enum):
    """Orchestration quality dimensions."""
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    SCALABILITY = "scalability"
    MAINTAINABILITY = "maintainability"


class ValidationMethod(Enum):
    """Quality validation methods."""
    AUTOMATED = "automated"
    MANUAL = "manual"
    HYBRID = "hybrid"
    PEER_REVIEW = "peer_review"


@dataclass
class QualityValidationRule:
    """Schema for quality validation rule."""
    rule_id: str
    dimension: QualityDimension
    validation_method: ValidationMethod
    criteria: Dict[str, Any]
    threshold: float


@dataclass
class QualityValidationConfig:
    """Schema for quality validation configuration."""
    dimensions: List[QualityDimension]
    validation_method: ValidationMethod
    parallel_validation: bool = True
    generate_reports: bool = True


@dataclass
class QualityValidationResult:
    """Schema for quality validation results."""
    validation_id: str
    configuration: QualityValidationConfig
    quality_scores: Dict[QualityDimension, float]
    validation_passed: bool
    recommendations: List[str]
    validation_timestamp: str
