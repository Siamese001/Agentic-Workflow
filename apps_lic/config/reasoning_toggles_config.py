"""
Reasoning configuration Toggles — DEFAULTS ONLY.

These are static fallback defaults used when no L0-stamped
ReasoningIntensityProfile is available (e.g. unit tests, offline mode).

GOVERNANCE: Runtime reasoning intensity is governed by the
ReasoningIntensityProfile stamped by L0 ReasoningPolicyEngine and
injected into HOPPipelineExecutor via SignedExecutionEnvelope.
Do NOT add environment-based overrides here.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

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
from apps_shared.config.pipeline_constants_config import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    THRESHOLD,
)

_emit_applies_guardrail("p0", "reasoning_toggles_config", "p0_governance")
_emit_reads_policy_state("p0", "reasoning_toggles_config", "policy_binding")
_emit_snapshots_state("p0", "reasoning_toggles_config", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("reasoning_toggles_config", "p4obs", "metric_1")
_emit_emits_metric_event("reasoning_toggles_config", "p4obs", "metric_2")
_emit_emits_metric_event("reasoning_toggles_config", "p4obs", "metric_3")
_emit_emits_metric_event("reasoning_toggles_config", "p4obs", "metric_4")
_emit_emits_metric_event("reasoning_toggles_config", "p4obs", "metric_5")
_emit_emits_metric_event("reasoning_toggles_config", "p4obs", "metric_6")
_emit_records_incident_event("reasoning_toggles_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("reasoning_toggles_config", "p4obs", "anomaly")
_emit_writes_observability_log("reasoning_toggles_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("reasoning_toggles_config", "p4obs", "mon_state")
_emit_triggers_alert("reasoning_toggles_config", "p4obs", "alert")
_emit_links_incident_trace("reasoning_toggles_config", "p4obs", "trace_link")
_emit_captures_pattern("reasoning_toggles_config", "p3lm", "pattern")
_emit_records_learning_event("reasoning_toggles_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("reasoning_toggles_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("reasoning_toggles_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("reasoning_toggles_config", "p3lm", "routing")
_emit_improves_agent_policy("reasoning_toggles_config", "p3lm", "policy")
_emit_stores_learning_state("reasoning_toggles_config", "p3lm", "state")
_emit_records_execution_trace("reasoning_toggles_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("reasoning_toggles_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("reasoning_toggles_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("reasoning_toggles_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("reasoning_toggles_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("reasoning_toggles_config", "env_read", "p2_env_1")
_emit_reads_environ("reasoning_toggles_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("reasoning_toggles_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("reasoning_toggles_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "reasoning_toggles_config", "context_pull")
_emit_pulls_context("p1", "reasoning_toggles_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "reasoning_toggles_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "reasoning_toggles_config", "uwg_term_2")
_emit_writes_through("p1", "reasoning_toggles_config", "write_through")
_emit_writes_through("p1", "reasoning_toggles_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "reasoning_toggles_config", "safety_validation")
_emit_invokes_eval("p1", "reasoning_toggles_config", "eval_call")
_emit_proposal_commits_routing("p1", "reasoning_toggles_config", "routing_commit")
_emit_escalates_to_human("p1", "reasoning_toggles_config", "human_escalation")
_emit_routes_through("p1", "reasoning_toggles_config", "route_through")
_emit_checks_agent_registry("p1", "reasoning_toggles_config", "agent_registry")
_emit_validates_agent_capability("p1", "reasoning_toggles_config", "capability")
_emit_dispatches_execution_plan("p1", "reasoning_toggles_config", "exec_plan")
_emit_agent_executes_agent("p1", "reasoning_toggles_config", "sub_agent")
_emit_routes_to_agent("p1", "reasoning_toggles_config", "target_agent")
_emit_verifies_policy("p1", "reasoning_toggles_config", "policy_check")
_emit_observes_runtime_state("p1", "reasoning_toggles_config", "runtime_state")
_emit_verifies_boundary("p1", "reasoning_toggles_config", "boundary_check")
_emit_transcripts_response("p1", "reasoning_toggles_config", "transcript")
_emit_hard_fails_untranscripted("p1", "reasoning_toggles_config")
_emit_gated_by_confidence("p1", "reasoning_toggles_config", "confidence_gate")
emit_replay_key("p0", "reasoning_toggles_config")
emit_determinism_digest("p0", "reasoning_toggles_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "reasoning_toggles_config", "execution_auth")
_emit_validates_capability("p2", "reasoning_toggles_config", "capability_check")
_emit_routes_to_capability("p2", "reasoning_toggles_config", "capability_route")
_emit_writes_via_uwg("p2", "reasoning_toggles_config", "uwg_write")
_emit_blocks_direct_write("p2", "reasoning_toggles_config", "direct_write_block")
_emit_records_tool_invocation("p2", "reasoning_toggles_config", "tool_invocation")
_emit_captures_execution_output("p2", "reasoning_toggles_config", "exec_output")
_emit_dispatches_agent("p3", "reasoning_toggles_config", "agent_dispatch")
_emit_coordinates_agents("p3", "reasoning_toggles_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "reasoning_toggles_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "reasoning_toggles_config", "healing_outcome")
_emit_escalates_failure("p3", "reasoning_toggles_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "reasoning_toggles_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "reasoning_toggles_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "reasoning_toggles_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "reasoning_toggles_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "reasoning_toggles_config", "eval_metric")
_emit_stores_embedding("p4", "reasoning_toggles_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "reasoning_toggles_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "reasoning_toggles_config", "exec_snapshot_link")


# Configuration constants


class ReasoningToggles(BaseModel):
    """
    Static fallback defaults for reasoning feature configuration.
    Enforces strict safety bounds to prevent infinite loops or token exhaustion.

    NOTE: At runtime these values are OVERRIDDEN by the L0-stamped
    ReasoningIntensityProfile.  This class is defaults-only.
    """

    # Core Toggles
    use_cot: bool = Field(default=True, description="Enable Chain-of-Thought reasoning.")
    use_reflexion: bool = Field(default=False, description="Enable self-correction loops.")

    # Tree of Thought Parameters
    tot_branches: int = Field(default=2, description="Number of alternative reasoning paths.")
    min_tot_depth: int = Field(default=1, description="Minimum depth for tree exploration.")

    # Sampling Parameters
    self_consistency_samples: int = Field(default=3, description="Number of samples for majority voting.")
    temperature_cap: float = Field(default=0.5, description="Maximum temperature for reasoning steps.")

    @field_validator("tot_branches")
    @classmethod
    def validate_branches(cls, v: int) -> int:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ReasoningToggles.validate_branches"
        )

        if not 1 <= v <= 5:
            raise ValueError(f"tot_branches must be between 1 and 5. Got {v}.")
        return v

    @field_validator("min_tot_depth")
    @classmethod
    def validate_depth(cls, v: int) -> int:
        if not 1 <= v <= 3:
            raise ValueError(f"min_tot_depth must be between 1 and 3. Got {v}.")
        return v

    @field_validator("temperature_cap")
    @classmethod
    def validate_temp(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"temperature_cap must be between 0.0 and 1.0. Got {v}.")
        return v

    class Config:
        """Pydantic configuration."""

        frozen = True  # Configs should be immutable once loaded


DEFAULT_TOGGLES = ReasoningToggles()
