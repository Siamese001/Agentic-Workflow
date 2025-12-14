"""Shared models and enums for the Agentic Workflow runtime.

This file contains all shared data structures that are used across multiple
modules to avoid circular imports. This file must NOT import from any
runtime.* modules - only from pydantic, enum, and typing.
"""

import logging
from enum import Enum
from pathlib import Path


# ============================================================================
# SubatomicHop Models
# ============================================================================

class MicroStage(Enum):
    """The 5 atomic micro-stages of a Subatomic Hop."""

class HopState(Enum):
    """Overall state of a Subatomic Hop."""

class RetryPolicy(BaseModel):
    """Retry policy for micro-stages."""
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay: float = Field(default=1.0, ge=0.0)
    exponential_backoff: bool = Field(default=True)
    retryable_stages: List[MicroStage] = Field(
        default=[MicroStage.THINK, MicroStage.ACT, MicroStage.CRITIQUE]
    )

class MicroCheckpoint(BaseModel):
    """Checkpoint data for a micro-stage."""
    hop_id: str
    stage: MicroStage
    timestamp: float
    state: HopState
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

class StageTransition(BaseModel):
    """Record of a stage transition."""
    from_stage: Optional[MicroStage] = None
    to_stage: MicroStage
    timestamp: float
    reason: Optional[str] = None

# ============================================================================
# Prompt Injection Models
# ============================================================================

class InjectionType(Enum):
    """Types of prompt injections."""
    # Original built-in types

    # Instructional injection types - Framing Layer

    # Instructional injection types - Context Layer

    # Instructional injection types - Reasoning Layer

    # Instructional injection types - Tooling Layer

    # Instructional injection types - Safety Layer

    # Instructional injection types - Output Layer

class InjectionScope(BaseModel):
    """Scope where injection should be applied."""
    hop_types: List[str] = Field(default_factory=list)
    stages: List[str] = Field(default_factory=list)
    contexts: Dict[str, Any] = Field(default_factory=dict)

class InjectionPattern(BaseModel):
    """A single prompt injection pattern."""
    id: str
    name: str
    type: InjectionType
    description: str
    template: str
    variables: List[str] = Field(default_factory=list)
    scope: InjectionScope = Field(default_factory=InjectionScope)
    priority: int = Field(default=0, ge=0, le=10)
    enabled: bool = True

    class Config:
        """TODO: Add docstring."""


class InjectionMatch(BaseModel):
    """Result of matching injections to context."""
    injection: InjectionPattern
    relevance_score: float = Field(ge=0.0, le=1.0)
    variable_values: Dict[str, Any] = Field(default_factory=dict)

class InjectionConfig(BaseModel):
    """Configuration for injection loader."""
    injection_dir: Path = Field(default=Path("./injections"))
    max_injections_per_hop: int = Field(default=5, ge=1, le=10)
    relevance_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    enable_caching: bool = True
    auto_reload: bool = True

# ============================================================================
# Additional Shared Types
# ============================================================================

class ValidationResult(BaseModel):
    """Result of a validation operation."""
    is_valid: bool
    confidence: float = Field(ge=0.0, le=1.0)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ExecutionResult(BaseModel):
    """Result of an execution operation."""
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    duration_ms: Optional[float] = None

# Type Aliases
# Common type aliases for better readability
