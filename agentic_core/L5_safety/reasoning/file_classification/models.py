"""Data models for file classification.

This module contains the core dataclasses used throughout the file classification
subpackage: ClassificationResult, Violation, and PlannedChange.
"""

from dataclasses import dataclass, field
from typing import Literal


@dataclass
class ClassificationResult:
    """Result of content-weighted file classification with confidence scoring."""

    file_type: str
    confidence: float  # 0.0 - 1.0
    signals: list[str]  # Evidence for classification
    warnings: list[str]  # Ambiguity warnings
    execution_mode: str = "DETERMINISTIC"  # REASONING or DETERMINISTIC (Phase 0)
    reasoning_signals: list[str] = field(default_factory=list)  # triggered signals
    # ADG behavioral signals sourced from the ADG SQLite index (optional, empty when ADG unavailable)
    adg_behavioral_signals: list[str] = field(default_factory=list)
    adg_behavioral_score: float = 0.5  # [0.0-1.0]: >0.7 agent-like, <0.4 script-like


@dataclass
class Violation:
    """A rule violation detected during file validation.

    Violations are returned by validation rules without triggering side effects.
    The caller decides whether and how to fix them.
    """

    type: str  # Violation type (e.g., "LAYER_MISALIGNMENT", "SUFFIX_CONFLICT")
    path: str  # File path where violation was detected
    message: str  # Human-readable description of the violation
    severity: Literal["ERROR", "WARNING", "INFO"]
    suggested_fix: str | None = None  # Optional suggested resolution


@dataclass
class PlannedChange:
    """A planned file system change (move, rename, or refactor).

    Changes are planned by validation/planning logic but not executed.
    The caller must explicitly approve execution.
    """

    source_path: str  # Current file path
    target_path: str  # Intended file path after change
    change_type: Literal["MOVE", "RENAME", "REFACTOR"]  # Type of change
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]  # Risk assessment
    reason: str  # Justification for the change
