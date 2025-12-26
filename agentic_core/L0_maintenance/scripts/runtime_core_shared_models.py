"""Shared models and enums for the Agentic Workflow runtime.

Models migrated to SSOT: agentic_core/schemas/models/core_contracts.py

This file contains all shared data structures that are used across multiple
modules to avoid circular imports. This file must not import from any
runtime.* modules - only from pydantic, enum, and typing.
"""

import logging
from agentic_core.schemas.models.core_contracts import (
    MicroStage,
    HopState,
    RetryPolicy,
    MicroCheckpoint,
    StageTransition,
    InjectionType,
    InjectionScope,
    InjectionPattern,
    InjectionMatch,
    InjectionConfig,
    ValidationResult,
    ExecutionResult,
)

LOGGER = logging.getLogger(__name__)

# All models migrated to SSOT: agentic_core/schemas/models/core_contracts.py
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