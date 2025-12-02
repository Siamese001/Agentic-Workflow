"""
Schema definitions for schema diagnostics capture and collection.
Contains only type definitions and data models - no execution logic.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Union
from enum import Enum


class DiagnosticCategory(Enum):
    """Diagnostic data categories."""
    PERFORMANCE = "performance"
    USAGE = "usage"
    ERRORS = "errors"
    VALIDATION = "validation"
    DEPENDENCIES = "dependencies"


class DiagnosticLevel(Enum):
    """Diagnostic data levels."""
    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"
    DEBUG = "debug"


@dataclass
class DiagnosticMetric:
    """Schema for individual diagnostic metric."""
    metric_name: str
    value: Union[int, float, str]
    unit: Optional[str] = None
    timestamp: str
    threshold: Optional[float] = None


@dataclass
class DiagnosticCapture:
    """Schema for diagnostic capture configuration."""
    capture_id: str
    categories: List[DiagnosticCategory]
    level: DiagnosticLevel
    time_range: Dict[str, str]
    schema_filter: Optional[Dict[str, Any]] = None


@dataclass
class DiagnosticReport:
    """Schema for diagnostic report results."""
    report_id: str
    capture_configuration: DiagnosticCapture
    metrics: List[DiagnosticMetric]
    anomalies: List[Dict[str, Any]]
    report_timestamp: str