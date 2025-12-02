"""
Schema definitions for schema quality validation and scoring.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Dict, List
from enum import Enum


class QualityDimension(Enum):
    """Schema quality dimensions."""
    COMPLETENESS = "completeness"
    CONSISTENCY = "consistency"
    CLARITY = "clarity"
    REUSABILITY = "reusability"
    MAINTAINABILITY = "maintainability"


class QualityMetric(Enum):
    """Quality measurement metrics."""
    COVERAGE = "coverage"
    COMPLEXITY = "complexity"
    DOCUMENTATION = "documentation"
    STANDARDIZATION = "standardization"
    TESTING = "testing"


@dataclass
class QualityThreshold:
    """Schema for quality threshold definition."""
    dimension: QualityDimension
    minimum_score: float
    target_score: float
    weight: float = 1.0


@dataclass
class QualityScore:
    """Schema for individual quality score."""
    dimension: QualityDimension
    score: float
    metrics: Dict[QualityMetric, float]
    issues_identified: List[str]
    recommendations: List[str]


@dataclass
class QualityValidationReport:
    """Schema for complete quality validation report."""
    schema_id: str
    overall_quality_score: float
    dimension_scores: List[QualityScore]
    quality_grade: str
    validation_timestamp: str