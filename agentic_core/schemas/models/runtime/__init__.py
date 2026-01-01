"""
Runtime Contracts - SSOT for hop states, micro stages, and execution models.
Modularized from core_contracts.py for DDD bounded context isolation.
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class micro_stage(Enum):
    """The 5 atomic micro-stages of a Subatomic Hop."""
    INIT = "init"
    THINK = "think"
    ACT = "act"
    CRITIQUE = "critique"
    COMMIT = "commit"

# Backward compat alias
MicroStage = micro_stage


class hop_state(Enum):
    """Overall state of a Subatomic Hop."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Backward compat alias
HopState = hop_state


class retry_policy(BaseModel):
    """Retry policy for micro-stages."""
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay: float = Field(default=1.0, ge=0.0)
    exponential_backoff: bool = Field(default=True)
    retryable_stages: List[micro_stage] = Field(
        default=[micro_stage.THINK, micro_stage.ACT, micro_stage.CRITIQUE]
    )

# Backward compat alias
RetryPolicy = retry_policy


class micro_checkpoint(BaseModel):
    """Checkpoint data for a micro-stage."""
    hop_id: str
    stage: micro_stage
    timestamp: float
    state: hop_state
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

# Backward compat alias
MicroCheckpoint = micro_checkpoint


class stage_transition(BaseModel):
    """Record of a stage transition."""
    from_stage: Optional[micro_stage] = None
    to_stage: micro_stage
    timestamp: float
    reason: Optional[str] = None

# Backward compat alias
StageTransition = stage_transition


class injection_type(Enum):
    """Types of prompt injections."""
    SYSTEM = "system"
    USER = "user"
    CONTEXT = "context"
    REASONING = "reasoning"
    TOOLING = "tooling"
    SAFETY = "safety"
    OUTPUT = "output"

# Backward compat alias
InjectionType = injection_type


class injection_scope(BaseModel):
    """Scope where injection should be applied."""
    hop_types: List[str] = Field(default_factory=list)
    stages: List[str] = Field(default_factory=list)
    contexts: Dict[str, Any] = Field(default_factory=dict)

# Backward compat alias
InjectionScope = injection_scope


class injection_pattern(BaseModel):
    """A single prompt injection pattern."""
    id: str
    name: str
    type: injection_type
    description: str
    template: str
    variables: List[str] = Field(default_factory=list)
    scope: injection_scope = Field(default_factory=injection_scope)
    priority: int = Field(default=0, ge=0, le=10)
    enabled: bool = True

# Backward compat alias
InjectionPattern = injection_pattern


# Public exports
__all__ = [
    # Snake case (canonical)
    "micro_stage",
    "hop_state",
    "retry_policy",
    "micro_checkpoint",
    "stage_transition",
    "injection_type",
    "injection_scope",
    "injection_pattern",
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
