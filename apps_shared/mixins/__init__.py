"""
Shared Mixins - Phase 2 Optimization
Common workflow patterns extracted from duplicate agent code.
"""

from __future__ import annotations

from apps_shared.mixins.validation_mixin import ValidationMixin, ValidationResult
from apps_shared.mixins.orchestration_mixin import (
    OrchestrationMixin,
    WorkflowStep,
    WorkflowStatus,
)
from apps_shared.mixins.analysis_mixin import AnalysisMixin, AnalysisResult

__all__ = [
    "ValidationMixin",
    "ValidationResult",
    "OrchestrationMixin",
    "WorkflowStep",
    "WorkflowStatus",
    "AnalysisMixin",
    "AnalysisResult",
]
