# Ownership: schemas
# Layer: schemas
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
from typing import Dict, List, Optional, Any
from datetime import datetime

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
    "Provider",
    "APICallStatus",
    "RAGState",
    "ImmutableStagingBuffer",
]


class ValidationSeverity(Enum):
    """Severity levels for validation results."""

    INFO = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


class Provider(str, Enum):
    """Available LLM providers."""
    
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    COHERE = "cohere"
    GROQ = "groq"
    TOGETHER = "together"
    FIREWORKS = "fireworks"


class APICallStatus(Enum):
    """Status of API calls."""
    
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    TIMEOUT = auto()
    RATE_LIMITED = auto()


@dataclass
class ValidationResult:
    """Result of a validation rule execution."""

    rule_id: str
    passed: bool
    severity: ValidationSeverity
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ThematicAnalysis:
    """Analysis of thematic content in text."""
    
    themes: List[str] = field(default_factory=list)
    confidence_scores: List[float] = field(default_factory=list)
    dominant_theme: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGState:
    """State of RAG (Retrieval-Augmented Generation) process."""
    
    query: str = ""
    retrieved_documents: List[Dict[str, Any]] = field(default_factory=list)
    context: str = ""
    response: str = ""
    retrieval_score: float = 0.0
    generation_confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImmutableStagingBuffer:
    """Immutable buffer for staging data transformations."""
    
    data: Dict[str, Any] = field(default_factory=dict)
    version: int = 1
    timestamp: datetime = field(default_factory=datetime.utcnow)
    checksum: Optional[str] = None
    
    def with_data(self, new_data: Dict[str, Any]) -> ImmutableStagingBuffer:
        """Return a new buffer with updated data."""
        return ImmutableStagingBuffer(
            data={**self.data, **new_data},
            version=self.version + 1,
            timestamp=datetime.utcnow(),
            checksum=None
        )
    
    def clear(self) -> ImmutableStagingBuffer:
        """Return a new empty buffer."""
        return ImmutableStagingBuffer(
            version=self.version + 1,
            timestamp=datetime.utcnow()
        )
