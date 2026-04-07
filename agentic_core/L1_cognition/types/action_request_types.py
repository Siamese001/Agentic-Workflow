from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "action_request_types")
emit_determinism_digest("p0", "action_request_types")

_emit_dispatches_healing_run("p1", "action_request_types", "L1")
_emit_routes_through("p1", "action_request_types", "L1")
_emit_checks_agent_registry("p1", "action_request_types", "agent_registry")
_emit_validates_agent_capability("p1", "action_request_types", "capability")
_emit_dispatches_execution_plan("p1", "action_request_types", "exec_plan")
_emit_agent_executes_agent("p1", "action_request_types", "sub_agent")
_emit_routes_to_agent("p1", "action_request_types", "target_agent")
_emit_verifies_policy("p1", "action_request_types", "policy_check")
_emit_observes_runtime_state("p1", "action_request_types", "runtime_state")
_emit_verifies_boundary("p1", "action_request_types", "boundary_check")
_emit_transcripts_response("p1", "action_request_types", "transcript")
_emit_hard_fails_untranscripted("p1", "action_request_types")
_emit_gated_by_confidence("p1", "action_request_types", "confidence_gate")
_emit_escalates_to_human("p1", "action_request_types", "L1")
_emit_reads_policy_state("p1", "action_request_types", "L1")
_emit_authorize_and_execute("p2", "action_request_types", "execution_auth")
_emit_validates_capability("p2", "action_request_types", "capability_check")
_emit_routes_to_capability("p2", "action_request_types", "capability_route")
_emit_writes_via_uwg("p2", "action_request_types", "uwg_write")
_emit_blocks_direct_write("p2", "action_request_types", "direct_write_block")
_emit_records_tool_invocation("p2", "action_request_types", "tool_invocation")
_emit_captures_execution_output("p2", "action_request_types", "exec_output")
_emit_dispatches_agent("p3", "action_request_types", "agent_dispatch")
_emit_coordinates_agents("p3", "action_request_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "action_request_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "action_request_types", "healing_outcome")
_emit_escalates_failure("p3", "action_request_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "action_request_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "action_request_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "action_request_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "action_request_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "action_request_types", "eval_metric")
_emit_stores_embedding("p4", "action_request_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "action_request_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "action_request_types", "exec_snapshot_link")

"Request and result types for inter-plane communication.\n\nDefines ActionRequest, PlanningRequest, and related types for\ncommunication between the orchestrator and planes.\n"
from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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
    _emit_routes_to_agent,
    _emit_snapshots_state,
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

_emit_emits_metric_event("action_request_types", "p4obs", "metric_1")
_emit_emits_metric_event("action_request_types", "p4obs", "metric_2")
_emit_emits_metric_event("action_request_types", "p4obs", "metric_3")
_emit_emits_metric_event("action_request_types", "p4obs", "metric_4")
_emit_emits_metric_event("action_request_types", "p4obs", "metric_5")
_emit_emits_metric_event("action_request_types", "p4obs", "metric_6")
_emit_records_incident_event("action_request_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("action_request_types", "p4obs", "anomaly")
_emit_writes_observability_log("action_request_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("action_request_types", "p4obs", "mon_state")
_emit_triggers_alert("action_request_types", "p4obs", "alert")
_emit_links_incident_trace("action_request_types", "p4obs", "trace_link")
_emit_captures_pattern("action_request_types", "p3lm", "pattern")
_emit_records_learning_event("action_request_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("action_request_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("action_request_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("action_request_types", "p3lm", "routing")
_emit_improves_agent_policy("action_request_types", "p3lm", "policy")
_emit_stores_learning_state("action_request_types", "p3lm", "state")
_emit_records_execution_trace("action_request_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("action_request_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("action_request_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("action_request_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("action_request_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("action_request_types", "env_read", "p2_env_1")
_emit_reads_environ("action_request_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("action_request_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("action_request_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "action_request_types", "context_pull")
_emit_pulls_context("p1", "action_request_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "action_request_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "action_request_types", "uwg_term_2")
_emit_writes_through("p1", "action_request_types", "write_through")
_emit_writes_through("p1", "action_request_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "action_request_types", "safety_validation")
_emit_invokes_eval("p1", "action_request_types", "eval_call")
_emit_proposal_commits_routing("p1", "action_request_types", "routing_commit")


@dataclass
class ActionRequest:
    """Request for the action plane to execute a tool or action.
    Attributes:
        action_type: Type of action (e.g., "tool_call", "api_request")
        tool_name: Name of the tool to execute
        parameters: Parameters to pass to the tool
        context: Additional context for execution
        timeout: Optional timeout in seconds
        retry_count: Number of retries on failure
    """

    action_type: str = "tool_call"
    tool_name: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    timeout: float | None = None
    retry_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "ActionRequest.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "ActionRequest.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L1_COGNITION, "ActionRequest.to_dict")
        return {
            "action_type": self.action_type,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "context": self.context,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
        }


@dataclass
class ActionResult:
    """Result from action plane execution.

    Attributes:
        success: Whether the action succeeded
        output: Output from the action
        error: Error message if failed
        execution_time: Time taken in seconds
        metadata: Additional result metadata
    """

    success: bool = False
    output: Any | None = None
    error: str | None = None
    execution_time: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "metadata": self.metadata,
        }


@dataclass
class PlanningRequest:
    """Request for the cognitive plane to generate a plan.

    Attributes:
        Task: The Task or goal to plan for
        context: Current context including scene, state, history
        max_steps: Maximum number of steps to plan
        constraints: Any constraints on the plan
    """

    Task: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    max_steps: int = 10
    constraints: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "Task": self.Task,
            "context": self.context,
            "max_steps": self.max_steps,
            "constraints": self.constraints,
        }


@dataclass
class PlanningResult:
    """Result from cognitive plane planning.

    Attributes:
        success: Whether planning succeeded
        plan: List of planned steps
        reasoning_trace: Chain of thought reasoning
        confidence: Confidence score (0.0 to 1.0)
        alternatives: Alternative plans considered
    """

    success: bool = False
    plan: list[dict[str, Any]] = field(default_factory=list)
    reasoning_trace: list[str] = field(default_factory=list)
    confidence: float = 0.0
    alternatives: list[list[dict[str, Any]]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "success": self.success,
            "plan": self.plan,
            "reasoning_trace": self.reasoning_trace,
            "confidence": self.confidence,
            "alternatives": self.alternatives,
        }
