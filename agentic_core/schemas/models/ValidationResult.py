from __future__ import annotations

"""Dataclass models for models."""
import datetime
import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

_logger = logging.getLogger(__name__)
# from agentic_core.models_enums import *  # Star import removed


class ValidationResult(BaseModel):
    """Result of a validation rule execution."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    rule_id: str = Field(..., description="Unique identifier for the validation rule")
    passed: bool = Field(..., description="Whether the validation passed")
    severity: str = Field(..., description="Severity level of the validation")
    message: str = Field(default="", description="Validation message")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional validation details")
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, description="Validation timestamp")
    
    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        """[HARDENED] Ensure severity is valid."""
        valid_severities = {"low", "medium", "high", "critical"}
        if v.lower() not in valid_severities:
            raise ValueError(f"Severity must be one of: {valid_severities}")
        return v.lower()


class ThematicAnalysis(BaseModel):
    """Analysis of thematic content in text."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    themes: list[str] = Field(default_factory=list, description="List of identified themes")
    confidence_scores: list[float] = Field(default_factory=list, description="Confidence scores for each theme")
    dominant_theme: str | None = Field(default=None, description="Most dominant theme")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional analysis metadata")
    
    @field_validator("confidence_scores")
    @classmethod
    def validate_confidence_scores(cls, v: list[float]) -> list[float]:
        """[HARDENED] Ensure all confidence scores are between 0 and 1."""
        for score in v:
            if not 0.0 <= score <= 1.0:
                raise ValueError("Confidence scores must be between 0.0 and 1.0")
        return v


class RagState(BaseModel):
    """State of RAG (Retrieval-Augmented Generation) process."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    query: str = Field(default="", description="The original query")
    retrieved_documents: list[dict[str, Any]] = Field(default_factory=list, description="Retrieved documents")
    context: str = Field(default="", description="Combined context for generation")
    response: str = Field(default="", description="Generated response")
    retrieval_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Retrieval relevance score")
    generation_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Generation confidence score")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional RAG metadata")


class ImmutableStagingBuffer(BaseModel):
    """Immutable buffer for staging data transformations."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    data: dict[str, Any] = Field(default_factory=dict, description="Buffer data")
    version: int = Field(default=1, ge=1, description="Buffer version")
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, description="Buffer timestamp")
    checksum: str | None = Field(default=None, description="Data checksum for integrity")


def with_data(original_buffer: ImmutableStagingBuffer, new_data: dict[str, Any]) -> ImmutableStagingBuffer:
    """Return a new buffer with updated data."""
    return ImmutableStagingBuffer(
        data={**original_buffer.data, **new_data},
        version=original_buffer.version + 1,
        timestamp=datetime.datetime.utcnow(),
        checksum=None,
    )


def clear(original_buffer: ImmutableStagingBuffer) -> ImmutableStagingBuffer:
    """Return a new empty buffer."""
    return ImmutableStagingBuffer(
        version=original_buffer.version + 1, 
        timestamp=datetime.datetime.utcnow()
    )
