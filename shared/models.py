# Ownership: shared
# Layer: shared
# Agent: all
# -*- coding: utf-8 -*-
"""
Shared data models - validation and analysis types.

EXTRACTED FROM: apps_rg/L3_orchestration/orchestrate_resume_generation.py
CANON COMPLIANCE: Sub-atomic split for line limit enforcement
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional

# Re-exports for backwards compatibility
from shared.reasoning_config import ReasoningConfig
from shared.workflow_types import CircuitState, GateDecision, HopCheckpoint, HopStatus

__all__ = [
    "ReasoningConfig",
    "ValidationSeverity",
    "ValidationResult",
    "ThematicAnalysis",
    "CircuitState",
    "HopStatus",
    "GateDecision",
    "HopCheckpoint",
]


class ValidationSeverity(Enum):
    """Severity levels for validation results."""

    INFO = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass
class ValidationResult:
    """Result of a validation rule execution."""

    rule_id: str
    passed: bool
    severity: ValidationSeverity
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThematicAnalysis:
    """Thematic analysis results from content inspection."""

    primary_theme: Dict[str, Any] = field(default_factory=dict)
    secondary_themes: List[Dict[str, Any]] = field(default_factory=list)
    role_classification: Dict[str, Any] = field(default_factory=dict)
    positioning_directives: Dict[str, Any] = field(default_factory=dict)
    authenticity_patterns: Dict[str, Any] = field(default_factory=dict)
    competitive_intelligence: Any = None
    problem_solution_narratives: Optional[Dict[str, Any]] = None
    signal_quality_score: float = 0.0
    retrieval_method: str = "UNKNOWN"
    retrieval_sources: List[Any] = field(default_factory=list)
    weighting_formula: Optional[Dict[str, Any]] = None
