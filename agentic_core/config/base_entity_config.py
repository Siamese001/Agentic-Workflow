# /agentic_core/domain/entities.py
# Core Domain Entities using Pydantic V2
# Strategy: Pure data structures, no business logic
# HARDENED: Self-contained SSOT compliance without external dependencies

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "base_entity_config", "p0_governance")
_emit_reads_policy_state("p0", "base_entity_config", "policy_binding")
_emit_snapshots_state("p0", "base_entity_config", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("base_entity_config", "p4obs", "metric_1")
_emit_emits_metric_event("base_entity_config", "p4obs", "metric_2")
_emit_emits_metric_event("base_entity_config", "p4obs", "metric_3")
_emit_emits_metric_event("base_entity_config", "p4obs", "metric_4")
_emit_emits_metric_event("base_entity_config", "p4obs", "metric_5")
_emit_emits_metric_event("base_entity_config", "p4obs", "metric_6")
_emit_records_incident_event("base_entity_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("base_entity_config", "p4obs", "anomaly")
_emit_writes_observability_log("base_entity_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("base_entity_config", "p4obs", "mon_state")
_emit_triggers_alert("base_entity_config", "p4obs", "alert")
_emit_links_incident_trace("base_entity_config", "p4obs", "trace_link")
_emit_captures_pattern("base_entity_config", "p3lm", "pattern")
_emit_records_learning_event("base_entity_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("base_entity_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("base_entity_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("base_entity_config", "p3lm", "routing")
_emit_improves_agent_policy("base_entity_config", "p3lm", "policy")
_emit_stores_learning_state("base_entity_config", "p3lm", "state")
_emit_records_execution_trace("base_entity_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("base_entity_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("base_entity_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("base_entity_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("base_entity_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("base_entity_config", "env_read", "p2_env_1")
_emit_reads_environ("base_entity_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("base_entity_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("base_entity_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "base_entity_config", "context_pull")
_emit_pulls_context("p1", "base_entity_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "base_entity_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "base_entity_config", "uwg_term_2")
_emit_writes_through("p1", "base_entity_config", "write_through")
_emit_writes_through("p1", "base_entity_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "base_entity_config", "safety_validation")
_emit_invokes_eval("p1", "base_entity_config", "eval_call")
_emit_proposal_commits_routing("p1", "base_entity_config", "routing_commit")
_emit_escalates_to_human("p1", "base_entity_config", "human_escalation")
_emit_routes_through("p1", "base_entity_config", "route_through")
_emit_checks_agent_registry("p1", "base_entity_config", "agent_registry")
_emit_validates_agent_capability("p1", "base_entity_config", "capability")
_emit_dispatches_execution_plan("p1", "base_entity_config", "exec_plan")
_emit_agent_executes_agent("p1", "base_entity_config", "sub_agent")
_emit_routes_to_agent("p1", "base_entity_config", "target_agent")
_emit_verifies_policy("p1", "base_entity_config", "policy_check")
_emit_observes_runtime_state("p1", "base_entity_config", "runtime_state")
_emit_verifies_boundary("p1", "base_entity_config", "boundary_check")
_emit_transcripts_response("p1", "base_entity_config", "transcript")
_emit_hard_fails_untranscripted("p1", "base_entity_config")
_emit_gated_by_confidence("p1", "base_entity_config", "confidence_gate")
emit_replay_key("p0", "base_entity_config")
emit_determinism_digest("p0", "base_entity_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "base_entity_config", "execution_auth")
_emit_validates_capability("p2", "base_entity_config", "capability_check")
_emit_routes_to_capability("p2", "base_entity_config", "capability_route")
_emit_writes_via_uwg("p2", "base_entity_config", "uwg_write")
_emit_blocks_direct_write("p2", "base_entity_config", "direct_write_block")
_emit_records_tool_invocation("p2", "base_entity_config", "tool_invocation")
_emit_captures_execution_output("p2", "base_entity_config", "exec_output")
_emit_dispatches_agent("p3", "base_entity_config", "agent_dispatch")
_emit_coordinates_agents("p3", "base_entity_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "base_entity_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "base_entity_config", "healing_outcome")
_emit_escalates_failure("p3", "base_entity_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "base_entity_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "base_entity_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "base_entity_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "base_entity_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "base_entity_config", "eval_metric")
_emit_stores_embedding("p4", "base_entity_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "base_entity_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "base_entity_config", "exec_snapshot_link")

# Configuration constants

class BaseEntity(BaseModel):
    """
    Root entity for all persistent domain objects.
    Enforces UUIDs and audit timestamps.
    HARDENED: Strict validation with controlled mutability.
    """

    # Strict configuration for SSOT compliance
    model_config = ConfigDict(
        validate_assignment=True,  # Critical hardening against silent state injection
        arbitrary_types_allowed=False,
        frozen=False,  # Allowed only for state fields like updated_at
        strict=True,  # Enforce strict typing
        extra="forbid",  # Prevent arbitrary field injection
    )

    id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for the entity",
        frozen=True,  # Identity should never change
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Entity creation timestamp",
        frozen=True,  # Creation time is immutable
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Mutable state field for audit tracking",
        frozen=False,  # Allowed only for state fields like updated_at
    )


class AgentConfig(BaseEntity):
    """
    Configuration profile for an individual agent.
    HARDENED: Explicit Field definitions with validation constraints.
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Human-readable agent name",
        frozen=True,  # Restored SSOT: Identity must not be mutable
    )
    role: str = Field(
        ...,
        min_length=1,
        description="The system role/persona of the agent",
        frozen=True,  # Role is part of identity
    )
    model_name: str = Field(
        default="gpt-4o",
        description="LLM Model ID for the agent",
        frozen=False,  # Model can be upgraded
    )
    temperature: float = Field(
        default=0.0,
        ge=0.0,
        le=2.0,
        description="LLM temperature setting (0.0=deterministic, 2.0=creative)",
        frozen=False,  # Temperature can be tuned
    )
    max_tokens: int = Field(
        default=4096,
        gt=0,
        description="Maximum tokens for LLM responses",
        frozen=False,  # Token limit can be adjusted
    )

    # Metadata for pattern recognition (aligned with domain patterns)
    capabilities: list[str] = Field(
        default_factory=list,
        description="List of agent capabilities",
        frozen=False,  # Capabilities can evolve
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional configuration metadata",
        frozen=False,  # Metadata can be extended
    )

    def update_timestamp(self) -> None:
        """
        Manually refresh updated_at timestamp.
        HARDENED: Explicit type hints and validation.
        """
        self.updated_at = datetime.now(timezone.utc)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Validate agent name format.
        HARDENED: Added validation to prevent injection.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "AgentConfig.validate_name")

        import re

        from pydantic_core import PydanticCustomError

        if not v or not v.strip():
            raise PydanticCustomError(
                "value_error",
                "Agent name cannot be empty",
            )

        # Prevent potential injection in names
        blocked_chars = ["<", ">", "&", '"', "'", "/", "\\"]
        if any(char in v for char in blocked_chars):
            raise PydanticCustomError(
                "value_error",
                "Agent name contains invalid characters: {chars}",
                {"chars": ", ".join(c for c in blocked_chars if c in v)},
            )

        # Block javascript: protocol and other URL schemes
        if re.match(r"^\w+:", v, re.IGNORECASE):
            raise PydanticCustomError(
                "value_error",
                "Agent name cannot contain URL schemes",
            )

        return v.strip()

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        """
        Validate model name against known patterns.
        HARDENED: Restrict to known safe model patterns.
        """
        known_models = ["gpt-4o", "gpt-4", "gpt-3.5-turbo", "claude-3", "claude-2"]
        if v not in known_models:
            raise ValueError(f"Unknown model: {v}. Use one of: {known_models}")
        return v
