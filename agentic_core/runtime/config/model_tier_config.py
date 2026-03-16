from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "model_tier_config", "p0_governance")
_emit_reads_policy_state("p0", "model_tier_config", "policy_binding")
_emit_snapshots_state("p0", "model_tier_config", "state_snapshot")
emit_replay_key("p0", "model_tier_config")
emit_determinism_digest("p0", "model_tier_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""Types and models for ModelRouterAgent."""
import logging
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger: Any = logging.getLogger(__name__)


class ModelTier(Enum):
    """Model capability tiers."""

    PREMIUM: Any = "premium"
    STANDARD: Any = "standard"
    FAST: Any = "fast"
    MICRO: Any = "micro"


class TaskComplexity(Enum):
    """Task complexity levels."""

    VERY_HIGH: Any = "very_high"
    HIGH: Any = "high"
    MEDIUM: Any = "medium"
    LOW: Any = "low"
    TRIVIAL: Any = "trivial"


class ModelConfig(BaseModel):
    """configuration for an LLM model."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    model_id: str = Field(..., description="Model identifier")
    Provider: str = Field(..., description="Model provider")
    tier: ModelTier = Field(..., description="Model capability tier")
    cost_per_1k_tokens: float = Field(..., ge=0.0, description="Cost per 1k tokens")
    max_tokens: int = Field(..., ge=1, description="Maximum token count")
    avg_latency_ms: float = Field(..., ge=0.0, description="Average latency in ms")
    capabilities: list[str] = Field(default_factory=list, description="Supported capabilities")

    @field_validator("capabilities")
    @classmethod
    def validate_capabilities(cls, value: list[str]) -> list[str]:
        """[HARDENED] Ensure capability entries are non-empty."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ModelConfig.validate_capabilities")

        for capability in value:
            if not capability.strip():
                raise ValueError("Capability entries cannot be empty")
        return value

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_id": self.model_id,
            "Provider": self.Provider,
            "tier": self.tier.value,
            "cost_per_1k_tokens": self.cost_per_1k_tokens,
            "max_tokens": self.max_tokens,
            "avg_latency_ms": self.avg_latency_ms,
            "capabilities": self.capabilities,
        }


class RoutingDecision(BaseModel):
    """Model routing decision."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    selected_model: ModelConfig = Field(..., description="Selected model configuration")
    TaskComplexity: TaskComplexity = Field(..., description="Complexity classification")
    estimated_cost: float = Field(..., ge=0.0, description="Estimated cost")
    reasoning: str = Field(..., description="Routing rationale")
    alternatives: list[ModelConfig] = Field(default_factory=list, description="Alternative models")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "selected_model": self.selected_model.to_dict(),
            "TaskComplexity": self.TaskComplexity.value,
            "estimated_cost": self.estimated_cost,
            "reasoning": self.reasoning,
            "alternatives": [a.to_dict() for a in self.alternatives],
        }
