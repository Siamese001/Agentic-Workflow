from __future__ import annotations

"\nMicro-Runtime & Execution Schemas\n=================================\nDefines the atomic stages (Subatomic Hops) and state transitions\nfor the Sovereign runtime.\n"
from enum import Enum
from typing import Any

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
    retryable_stages: list[MicroStage] = Field(
        default=[MicroStage.THINK, MicroStage.ACT, MicroStage.CRITIQUE]
    )


class MicroCheckpoint(BaseModel):
    """Checkpoint data for a micro-stage to support recovery."""

    hop_id: str
    stage: MicroStage
    timestamp: float
    state: HopState
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class StageTransition(BaseModel):
    """Record of a stage transition within a hop."""

    from_stage: MicroStage | None = None
    to_stage: MicroStage
    timestamp: float
    reason: str | None = None
