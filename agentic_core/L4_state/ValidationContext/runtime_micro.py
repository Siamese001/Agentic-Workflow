from __future__ import annotations
"""
Micro-Runtime & Execution Schemas
=================================
Defines the atomic stages (Subatomic Hops) and state transitions
for the Sovereign runtime.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MicroStage(str, Enum):
    """The 5 atomic micro-stages of a Subatomic Hop."""
    INIT = "init"
    THINK = "think"
    ACT = "act"
    CRITIQUE = "critique"
    COMMIT = "commit"

class HopState(str, Enum):
    """Overall state of a Subatomic Hop."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"

class RetryPolicy(BaseModel):
    """Retry policy for micro-stages."""
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_delay: float = Field(default=1.0, ge=0.0)
    exponential_backoff: bool = Field(default=True)
    retryable_stages: List[MicroStage] = Field(
        default=[MicroStage.THINK, MicroStage.ACT, MicroStage.CRITIQUE]
    )

class MicroCheckpoint(BaseModel):
    """Checkpoint data for a micro-stage to support recovery."""
    hop_id: str
    stage: MicroStage
    timestamp: float
    state: HopState
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

class StageTransition(BaseModel):
    """Record of a stage transition within a hop."""
    from_stage: Optional[MicroStage] = None
    to_stage: MicroStage
    timestamp: float
    reason: Optional[str] = None
