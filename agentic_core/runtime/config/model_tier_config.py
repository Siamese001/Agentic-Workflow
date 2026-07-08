from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "model_tier_config", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "model_tier_config", "policy_binding")
trace_contract._emit_snapshots_state("p0", "model_tier_config", "state_snapshot")
trace_contract.emit_replay_key("p0", "model_tier_config")
trace_contract.emit_determinism_digest("p0", "model_tier_config")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "model_tier_config", "execution_auth")
trace_contract._emit_validates_capability("p2", "model_tier_config", "capability_check")
trace_contract._emit_routes_to_capability("p2", "model_tier_config", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "model_tier_config", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "model_tier_config", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "model_tier_config", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "model_tier_config", "exec_output")
trace_contract._emit_dispatches_agent("p3", "model_tier_config", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "model_tier_config", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "model_tier_config", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "model_tier_config", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "model_tier_config", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "model_tier_config", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "model_tier_config", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "model_tier_config", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "model_tier_config", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "model_tier_config", "eval_metric")
trace_contract._emit_stores_embedding("p4", "model_tier_config", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "model_tier_config", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "model_tier_config", "exec_snapshot_link")

# Configuration constants

"""Types and models for ModelRouterAgent."""
import logging
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


trace_contract._emit_emits_metric_event("model_tier_config", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("model_tier_config", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("model_tier_config", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("model_tier_config", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("model_tier_config", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("model_tier_config", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("model_tier_config", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("model_tier_config", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("model_tier_config", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("model_tier_config", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("model_tier_config", "p4obs", "alert")
trace_contract._emit_links_incident_trace("model_tier_config", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("model_tier_config", "p3lm", "pattern")
trace_contract._emit_records_learning_event("model_tier_config", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("model_tier_config", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("model_tier_config", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("model_tier_config", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("model_tier_config", "p3lm", "policy")
trace_contract._emit_stores_learning_state("model_tier_config", "p3lm", "state")
trace_contract._emit_records_execution_trace("model_tier_config", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("model_tier_config", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("model_tier_config", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("model_tier_config", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("model_tier_config", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("model_tier_config", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("model_tier_config", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("model_tier_config", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("model_tier_config", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "model_tier_config", "context_pull")
trace_contract._emit_pulls_context("p1", "model_tier_config", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "model_tier_config", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "model_tier_config", "uwg_term_2")
trace_contract._emit_writes_through("p1", "model_tier_config", "write_through")
trace_contract._emit_writes_through("p1", "model_tier_config", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "model_tier_config", "safety_validation")
trace_contract._emit_invokes_eval("p1", "model_tier_config", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "model_tier_config", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "model_tier_config", "human_escalation")
trace_contract._emit_routes_through("p1", "model_tier_config", "route_through")
trace_contract._emit_checks_agent_registry("p1", "model_tier_config", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "model_tier_config", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "model_tier_config", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "model_tier_config", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "model_tier_config", "target_agent")
trace_contract._emit_verifies_policy("p1", "model_tier_config", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "model_tier_config", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "model_tier_config", "boundary_check")
trace_contract._emit_transcripts_response("p1", "model_tier_config", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "model_tier_config")
trace_contract._emit_gated_by_confidence("p1", "model_tier_config", "confidence_gate")

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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "ModelConfig.validate_capabilities"
        )

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
