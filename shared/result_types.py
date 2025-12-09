# Ownership: shared
# -*- coding: utf-8 -*-
"""Common result types for workflow operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScoreResult:
    """Result of a scoring operation."""

    score: float = 0.0
    confidence: float = 0.0
    details: Dict[str, object] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Result of an execution operation."""

    success: bool = False
    output: object = None
    error: Optional[str] = None
    details: Dict[str, object] = field(default_factory=dict)


@dataclass
class FormatResult:
    """Result of a formatting operation."""

    formatted: str = ""
    success: bool = True
    details: Dict[str, object] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    """Result of a retrieval operation."""

    data: object = None
    found: bool = False
    source: str = ""
    details: Dict[str, object] = field(default_factory=dict)


@dataclass
class DiagnosticReport:
    """Result of a diagnostic operation."""

    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    passed: bool = True
    details: Dict[str, object] = field(default_factory=dict)


@dataclass
class OperationResult:
    """general result of an operation."""

    success: bool = False
    result: object = None
    error: Optional[str] = None


@dataclass
class RefinementResult:
    """Result of a refinement operation."""

    refined: object = None
    changes: List[str] = field(default_factory=list)
    success: bool = True


@dataclass
class RetryResult:
    """Result of a retry operation."""

    success: bool = False
    attempts: int = 0
    final_result: object = None
    error: Optional[str] = None
