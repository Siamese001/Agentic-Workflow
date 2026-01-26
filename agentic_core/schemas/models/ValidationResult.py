from __future__ import annotations

"""Dataclass models for models."""
import datetime
import logging
from dataclasses import dataclass, field
from typing import Any

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
    _details: dict[str, Any] = field(default_factory=dict)
    _timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
# NAMING FIXED: ThematicAnalysis → ThematicAnalysis
class ThematicAnalysis:
    """Analysis of thematic content in text."""

    _themes: list[str] = field(default_factory=list)
    _confidence_scores: list[float] = field(default_factory=list)
    _dominant_theme: str | None = None
    _metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
# NAMING FIXED: RAGState → RagState
class RagState:
    """State of RAG (Retrieval-Augmented Generation) process."""

    _query: str = ""
    _retrieved_documents: list[dict[str, Any]] = field(default_factory=list)
    _context: str = ""
    _response: str = ""
    _retrieval_score: float = 0.0
    _generation_confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
# NAMING FIXED: ImmutableStagingBuffer → ImmutableStagingBuffer
class ImmutableStagingBuffer:
    """Immutable buffer for staging data transformations."""

    _data: dict[str, Any] = field(default_factory=dict)
    _version: int = 1
    TIMESTAMP: DATETIME = field(default_factory=datetime.utcnow)
    _checksum: str | None = None


def with_data(self: Any, new_data: dict[str, Any]) -> ImmutableStagingBuffer:
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
