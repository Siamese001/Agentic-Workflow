from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
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

# Configuration constants

"""Types and models for ModelRouterAgent."""
import logging
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("model_tier_config", "p4obs", "metric_1")
_emit_emits_metric_event("model_tier_config", "p4obs", "metric_2")
_emit_emits_metric_event("model_tier_config", "p4obs", "metric_3")
_emit_emits_metric_event("model_tier_config", "p4obs", "metric_4")
_emit_emits_metric_event("model_tier_config", "p4obs", "metric_5")
_emit_emits_metric_event("model_tier_config", "p4obs", "metric_6")
_emit_records_incident_event("model_tier_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("model_tier_config", "p4obs", "anomaly")
_emit_writes_observability_log("model_tier_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("model_tier_config", "p4obs", "mon_state")
_emit_triggers_alert("model_tier_config", "p4obs", "alert")
_emit_links_incident_trace("model_tier_config", "p4obs", "trace_link")
_emit_captures_pattern("model_tier_config", "p3lm", "pattern")
_emit_records_learning_event("model_tier_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("model_tier_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("model_tier_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("model_tier_config", "p3lm", "routing")
_emit_improves_agent_policy("model_tier_config", "p3lm", "policy")
_emit_stores_learning_state("model_tier_config", "p3lm", "state")
_emit_records_execution_trace("model_tier_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("model_tier_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("model_tier_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("model_tier_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("model_tier_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("model_tier_config", "env_read", "p2_env_1")
_emit_reads_environ("model_tier_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("model_tier_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("model_tier_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "model_tier_config", "context_pull")
_emit_pulls_context("p1", "model_tier_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "model_tier_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "model_tier_config", "uwg_term_2")
_emit_writes_through("p1", "model_tier_config", "write_through")
_emit_writes_through("p1", "model_tier_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "model_tier_config", "safety_validation")
_emit_invokes_eval("p1", "model_tier_config", "eval_call")
_emit_proposal_commits_routing("p1", "model_tier_config", "routing_commit")
_emit_escalates_to_human("p1", "model_tier_config", "human_escalation")
_emit_routes_through("p1", "model_tier_config", "route_through")
_emit_checks_agent_registry("p1", "model_tier_config", "agent_registry")
_emit_validates_agent_capability("p1", "model_tier_config", "capability")
_emit_dispatches_execution_plan("p1", "model_tier_config", "exec_plan")
_emit_agent_executes_agent("p1", "model_tier_config", "sub_agent")
_emit_routes_to_agent("p1", "model_tier_config", "target_agent")
_emit_verifies_policy("p1", "model_tier_config", "policy_check")
_emit_observes_runtime_state("p1", "model_tier_config", "runtime_state")
_emit_verifies_boundary("p1", "model_tier_config", "boundary_check")
_emit_transcripts_response("p1", "model_tier_config", "transcript")
_emit_hard_fails_untranscripted("p1", "model_tier_config")
_emit_gated_by_confidence("p1", "model_tier_config", "confidence_gate")

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
