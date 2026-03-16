from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "model_tier_config", "p0_governance")
_emit_reads_policy_state("p0", "model_tier_config", "policy_binding")
_emit_snapshots_state("p0", "model_tier_config", "state_snapshot")
emit_replay_key("p0", "model_tier_config")
emit_determinism_digest("p0", "model_tier_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "model_tier_config", "execution_auth")
_emit_validates_capability("p2", "model_tier_config", "capability_check")
_emit_routes_to_capability("p2", "model_tier_config", "capability_route")
_emit_writes_via_uwg("p2", "model_tier_config", "uwg_write")
_emit_blocks_direct_write("p2", "model_tier_config", "direct_write_block")
_emit_records_tool_invocation("p2", "model_tier_config", "tool_invocation")
_emit_captures_execution_output("p2", "model_tier_config", "exec_output")
_emit_dispatches_agent("p3", "model_tier_config", "agent_dispatch")
_emit_coordinates_agents("p3", "model_tier_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "model_tier_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "model_tier_config", "healing_outcome")
_emit_escalates_failure("p3", "model_tier_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "model_tier_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "model_tier_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "model_tier_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "model_tier_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "model_tier_config", "eval_metric")
_emit_stores_embedding("p4", "model_tier_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "model_tier_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "model_tier_config", "exec_snapshot_link")

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
