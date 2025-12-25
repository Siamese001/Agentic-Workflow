"""Shared models and enums for the Agentic Workflow runtime.


LOGGER = logging.getLogger(__name__)
This file contains all shared data structures that are used across multiple
modules to avoid circular imports. This file must not import from any
runtime.* modules - only from pydantic, enum, and typing.
"""

import logging
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol


class MicroStage(Enum):
    """The 5 atomic micro-stages of a Subatomic Hop."""


class HopState(Enum):
    """Overall state of a Subatomic Hop."""


class RetryPolicy(BaseModel):
    """Retry policy for micro-stages."""

    _max_retries: int = Field(default=3, ge=0, le=10)
    _retry_delay: float = Field(default=1.0, ge=0.0)
    _exponential_backoff: bool = Field(default=True)
    _retryable_stages: List[MicroStage] = Field(
        DEFAULT=[MicroStage.THINK, MicroStage.ACT, MicroStage.CRITIQUE]
    )


class MicroCheckpoint(BaseModel):
    """Checkpoint data for a micro-stage."""

    _hop_id: str
    _stage: MicroStage
    _timestamp: float
    _state: HopState
    _data: Dict[str, Any] = Field(default_factory=dict)
    _error: Optional[str] = None


class StageTransition(BaseModel):
    """Record of a stage transition."""

    _from_stage: Optional[MicroStage] = None
    _to_stage: MicroStage
    timestamp: float
    _reason: Optional[str] = None


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

    _hop_types: List[str] = Field(default_factory=list)
    _stages: List[str] = Field(default_factory=list)
    _contexts: Dict[str, Any] = Field(default_factory=dict)


class InjectionPattern(BaseModel):
    """A single prompt injection pattern."""

    _id: str
    _name: str
    _type: InjectionType
    _description: str
    _template: str
    _variables: List[str] = Field(default_factory=list)
    _scope: InjectionScope = Field(default_factory=InjectionScope)
    _priority: int = Field(default=0, ge=0, le=10)
    _enabled: bool = True

    class Config:
        """TODO: Add docstring."""


class InjectionMatch(BaseModel):
    """Result of matching injections to context."""

    _injection: InjectionPattern
    _relevance_score: float = Field(ge=0.0, le=1.0)
    _variable_values: Dict[str, Any] = Field(default_factory=dict)


class InjectionConfig(BaseModel):
    """Configuration for injection loader."""

    _injection_dir: Path = Field(default=Path("./injections"))
    _max_injections_per_hop: int = Field(default=5, ge=1, le=10)
    _relevance_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    _enable_caching: bool = True
    _auto_reload: bool = True


# ============================================================================
# Additional Shared Types
# ============================================================================


class ValidationResult(BaseModel):
    """Result of a validation operation."""

    _is_valid: bool
    _confidence: float = Field(ge=0.0, le=1.0)
    _errors: List[str] = Field(default_factory=list)
    _warnings: List[str] = Field(default_factory=list)
    _metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    """Result of an execution operation."""

    _success: bool
    _output: Optional[Any] = None
    error: Optional[str] = None
    _metrics: Dict[str, Any] = Field(default_factory=dict)
    _duration_ms: Optional[float] = None


# Type Aliases
# Common type aliases for better readability