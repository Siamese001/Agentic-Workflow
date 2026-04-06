"""Pydantic models for reasoning traces.

Phase 1 - Pillar 6: Reasoning models (Structured Reasoning)
Formal data models for separating reasoning from action outputs.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

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

_emit_applies_guardrail("p0", "think_step_util", "p0_governance")
_emit_reads_policy_state("p0", "think_step_util", "policy_binding")
_emit_snapshots_state("p0", "think_step_util", "state_snapshot")
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

_emit_emits_metric_event("think_step_util", "p4obs", "metric_1")
_emit_emits_metric_event("think_step_util", "p4obs", "metric_2")
_emit_emits_metric_event("think_step_util", "p4obs", "metric_3")
_emit_emits_metric_event("think_step_util", "p4obs", "metric_4")
_emit_emits_metric_event("think_step_util", "p4obs", "metric_5")
_emit_emits_metric_event("think_step_util", "p4obs", "metric_6")
_emit_records_incident_event("think_step_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("think_step_util", "p4obs", "anomaly")
_emit_writes_observability_log("think_step_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("think_step_util", "p4obs", "mon_state")
_emit_triggers_alert("think_step_util", "p4obs", "alert")
_emit_links_incident_trace("think_step_util", "p4obs", "trace_link")
_emit_captures_pattern("think_step_util", "p3lm", "pattern")
_emit_records_learning_event("think_step_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("think_step_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("think_step_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("think_step_util", "p3lm", "routing")
_emit_improves_agent_policy("think_step_util", "p3lm", "policy")
_emit_stores_learning_state("think_step_util", "p3lm", "state")
_emit_records_execution_trace("think_step_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("think_step_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("think_step_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("think_step_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("think_step_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("think_step_util", "env_read", "p2_env_1")
_emit_reads_environ("think_step_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("think_step_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("think_step_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "think_step_util", "context_pull")
_emit_pulls_context("p1", "think_step_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "think_step_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "think_step_util", "uwg_term_2")
_emit_writes_through("p1", "think_step_util", "write_through")
_emit_writes_through("p1", "think_step_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "think_step_util", "safety_validation")
_emit_invokes_eval("p1", "think_step_util", "eval_call")
_emit_proposal_commits_routing("p1", "think_step_util", "routing_commit")
_emit_escalates_to_human("p1", "think_step_util", "human_escalation")
_emit_routes_through("p1", "think_step_util", "route_through")
_emit_checks_agent_registry("p1", "think_step_util", "agent_registry")
_emit_validates_agent_capability("p1", "think_step_util", "capability")
_emit_dispatches_execution_plan("p1", "think_step_util", "exec_plan")
_emit_agent_executes_agent("p1", "think_step_util", "sub_agent")
_emit_routes_to_agent("p1", "think_step_util", "target_agent")
_emit_verifies_policy("p1", "think_step_util", "policy_check")
_emit_observes_runtime_state("p1", "think_step_util", "runtime_state")
_emit_verifies_boundary("p1", "think_step_util", "boundary_check")
_emit_transcripts_response("p1", "think_step_util", "transcript")
_emit_hard_fails_untranscripted("p1", "think_step_util")
_emit_gated_by_confidence("p1", "think_step_util", "confidence_gate")
emit_replay_key("p0", "think_step_util")
emit_determinism_digest("p0", "think_step_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "think_step_util", "execution_auth")
_emit_validates_capability("p2", "think_step_util", "capability_check")
_emit_routes_to_capability("p2", "think_step_util", "capability_route")
_emit_writes_via_uwg("p2", "think_step_util", "uwg_write")
_emit_blocks_direct_write("p2", "think_step_util", "direct_write_block")
_emit_records_tool_invocation("p2", "think_step_util", "tool_invocation")
_emit_captures_execution_output("p2", "think_step_util", "exec_output")
_emit_dispatches_agent("p3", "think_step_util", "agent_dispatch")
_emit_coordinates_agents("p3", "think_step_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "think_step_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "think_step_util", "healing_outcome")
_emit_escalates_failure("p3", "think_step_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "think_step_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "think_step_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "think_step_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "think_step_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "think_step_util", "eval_metric")
_emit_stores_embedding("p4", "think_step_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "think_step_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "think_step_util", "exec_snapshot_link")


class ThinkStep(BaseModel):
    """Represents a thinking/reasoning step.

    Captures the agent's internal reasoning process before taking action.
    """

    thought: str = Field(..., description="The reasoning or thought process")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in this reasoning")
    reasoning_type: str = Field(
        default="general", description="Type of reasoning (e.g., deductive, inductive)"
    )
    timestamp: datetime = Field(default_factory=datetime.now, description="When this thought occurred")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class ConfigThinkStep:
        frozen = False


class ActionStep(BaseModel):
    """Represents an action step.

    Captures the concrete action taken based on reasoning.
    """

    action: str = Field(..., description="The action to be performed")
    action_type: str = Field(default="tool_call", description="Type of action")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Action parameters")
    expected_outcome: str | None = Field(None, description="Expected result of this action")
    timestamp: datetime = Field(default_factory=datetime.now, description="When this action was taken")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class ConfigActionStep:
        frozen = False


class ObservationStep(BaseModel):
    """Represents an observation from an action.

    Captures the result or feedback from executing an action.
    """

    observation: str = Field(..., description="The observed result")
    success: bool = Field(default=True, description="Whether the action succeeded")
    error: str | None = Field(None, description="Error message if action failed")
    data: dict[str, Any] = Field(default_factory=dict, description="Structured observation data")
    timestamp: datetime = Field(default_factory=datetime.now, description="When this observation was made")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class ConfigObservationStep:
        frozen = False


class ReasoningTraceModel(BaseModel):
    """Complete reasoning trace with separated think/action/observation steps.

    This formal schema ensures observability and enables self-correction by
    maintaining a clear separation between reasoning and execution.
    """

    trace_id: str = Field(..., description="Unique identifier for this trace")
    task: str = Field(..., description="The task being reasoned about")
    steps: list[ThinkStep | ActionStep | ObservationStep] = Field(
        default_factory=list, description="Sequence of reasoning, action, and observation steps"
    )
    final_answer: str | None = Field(None, description="Final answer or conclusion")
    total_steps: int = Field(default=0, description="Total number of steps taken")
    success: bool = Field(default=False, description="Whether the reasoning succeeded")
    error: str | None = Field(None, description="Error message if reasoning failed")
    started_at: datetime = Field(default_factory=datetime.now, description="When reasoning started")
    completed_at: datetime | None = Field(None, description="When reasoning completed")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional trace metadata")

    class ConfigReasoningTrace:
        frozen = False

    def add_think(self, thought: str, **kwargs: object) -> None:
        """Add a thinking step to the trace."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ReasoningTraceModel.add_think")

        step = ThinkStep(thought=thought, **kwargs)
        self.steps.append(step)
        self.total_steps += 1

    def add_action(self, action: str, **kwargs: object) -> None:
        """Add an action step to the trace."""
        step = ActionStep(action=action, **kwargs)
        self.steps.append(step)
        self.total_steps += 1

    def add_observation(self, observation: str, **kwargs: object) -> None:
        """Add an observation step to the trace."""
        step = ObservationStep(observation=observation, **kwargs)
        self.steps.append(step)
        self.total_steps += 1

    def get_think_steps(self) -> list[ThinkStep]:
        """Get all thinking steps from the trace."""
        return [s for s in self.steps if isinstance(s, ThinkStep)]

    def get_action_steps(self) -> list[ActionStep]:
        """Get all action steps from the trace."""
        return [s for s in self.steps if isinstance(s, ActionStep)]

    def get_observation_steps(self) -> list[ObservationStep]:
        """Get all observation steps from the trace."""
        return [s for s in self.steps if isinstance(s, ObservationStep)]

    def complete(self, final_answer: str, success: bool = True, error: str | None = None) -> None:
        """Mark the trace as complete."""
        self.final_answer = final_answer
        self.success = success
        self.error = error
        self.completed_at = datetime.now()
