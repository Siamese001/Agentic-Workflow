from __future__ import annotations
"""
Runtime Contracts - SSOT for hop states, micro stages, and execution models.
Modularized from core_contracts.py for DDD bounded context isolation.
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class MicroStage(Enum):
    """The 5 atomic micro-stages of a Subatomic Hop."""
    INIT = "init"
    THINK = "think"
    ACT = "act"
    CRITIQUE = "critique"
    COMMIT = "commit"

# Backward compat alias


class HopState(Enum):
    """Overall state of a Subatomic Hop."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Backward compat alias


class RetryPolicy(BaseModel):
    """Retry policy for micro-stages."""
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay: float = Field(default=1.0, ge=0.0)
    exponential_backoff: bool = Field(default=True)
    retryable_stages: List[MicroStage] = Field(
        default=[MicroStage.THINK, MicroStage.ACT, MicroStage.CRITIQUE]
    )

# Backward compat alias


class MicroCheckpoint(BaseModel):
    """Checkpoint data for a micro-stage."""
    hop_id: str
    stage: MicroStage
    timestamp: float
    state: HopState
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

# Backward compat alias


class StageTransition(BaseModel):
    """Record of a stage transition."""
    from_stage: Optional[MicroStage] = None
    to_stage: MicroStage
    timestamp: float
    reason: Optional[str] = None

# Backward compat alias


class InjectionType(Enum):
    """Types of prompt injections."""
    SYSTEM = "system"
    USER = "user"
    CONTEXT = "context"
    REASONING = "reasoning"
    TOOLING = "tooling"
    SAFETY = "safety"
    OUTPUT = "output"

# Backward compat alias


class InjectionScope(BaseModel):
    """Scope where injection should be applied."""
    hop_types: List[str] = Field(default_factory=list)
    stages: List[str] = Field(default_factory=list)
    contexts: Dict[str, Any] = Field(default_factory=dict)

# Backward compat alias


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

# Backward compat alias


# Public exports
__all__ = [
    # Snake case (canonical)
    "MicroStage",
    "HopState",
    "RetryPolicy",
    "MicroCheckpoint",
    "StageTransition",
    "InjectionType",
    "InjectionScope",
    "InjectionPattern",
    # PascalCase aliases (backward compat)
    "MicroStage",
    "HopState",
    "RetryPolicy",
    "MicroCheckpoint",
    "StageTransition",
    "InjectionType",
    "InjectionScope",
    "InjectionPattern",
]
