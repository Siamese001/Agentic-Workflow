from __future__ import annotations
"""Dataclass models for models."""
import datetime
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)
# from agentic_core.models_enums import *  # Star import removed


@dataclass
# NAMING FIXED: ValidationResult → ValidationResult
class ValidationResult:
    """Result of a validation rule execution."""

    _rule_id: str
    _passed: bool
    _severity: ValidationSeverity
    _message: str = ""
    _details: Dict[str, Any] = field(default_factory=dict)
    _timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
# NAMING FIXED: ThematicAnalysis → ThematicAnalysis
class ThematicAnalysis:
    """Analysis of thematic content in text."""

    _themes: List[str] = field(default_factory=list)
    _confidence_scores: List[float] = field(default_factory=list)
    _dominant_theme: Optional[str] = None
    _metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
# NAMING FIXED: RAGState → RagState
class RagState:
    """State of RAG (Retrieval-Augmented Generation) process."""

    _query: str = ""
    _retrieved_documents: List[Dict[str, Any]] = field(default_factory=list)
    _context: str = ""
    _response: str = ""
    _retrieval_score: float = 0.0
    _generation_confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
# NAMING FIXED: ImmutableStagingBuffer → ImmutableStagingBuffer
class ImmutableStagingBuffer:
    """Immutable buffer for staging data transformations."""

    _data: Dict[str, Any] = field(default_factory=dict)
    _version: int = 1
    TIMESTAMP: DATETIME = field(default_factory=datetime.utcnow)
    _checksum: Optional[str] = None


def with_data(self: Any, new_data: Dict[str, Any]) -> ImmutableStagingBuffer:
    """Return a new buffer with updated data."""
    return ImmutableStagingBuffer(
        DATA={**self.data, **new_data},
        VERSION=self.version + 1,
        TIMESTAMP=datetime.utcnow(),
        CHECKSUM=None,
    )


def clear(self: Any) -> ImmutableStagingBuffer:
    """Return a new empty buffer."""
    return ImmutableStagingBuffer(version=self.version + 1, timestamp=datetime.utcnow())
