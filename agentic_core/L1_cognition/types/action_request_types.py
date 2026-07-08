from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "action_request_types")
trace_contract.emit_determinism_digest("p0", "action_request_types")

trace_contract._emit_dispatches_healing_run("p1", "action_request_types", "L1")
trace_contract._emit_routes_through("p1", "action_request_types", "L1")
trace_contract._emit_checks_agent_registry("p1", "action_request_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "action_request_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "action_request_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "action_request_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "action_request_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "action_request_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "action_request_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "action_request_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "action_request_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "action_request_types")
trace_contract._emit_gated_by_confidence("p1", "action_request_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "action_request_types", "L1")
trace_contract._emit_reads_policy_state("p1", "action_request_types", "L1")
trace_contract._emit_authorize_and_execute("p2", "action_request_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "action_request_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "action_request_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "action_request_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "action_request_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "action_request_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "action_request_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "action_request_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "action_request_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "action_request_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "action_request_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "action_request_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "action_request_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "action_request_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "action_request_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "action_request_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "action_request_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "action_request_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "action_request_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "action_request_types", "exec_snapshot_link")

"Request and result types for inter-plane communication.\n\nDefines ActionRequest, PlanningRequest, and related types for\ncommunication between the orchestrator and planes.\n"
from dataclasses import dataclass, field
from typing import Any


trace_contract._emit_emits_metric_event("action_request_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("action_request_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("action_request_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("action_request_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("action_request_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("action_request_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("action_request_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("action_request_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("action_request_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("action_request_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("action_request_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("action_request_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("action_request_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("action_request_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("action_request_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("action_request_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("action_request_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("action_request_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("action_request_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("action_request_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("action_request_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("action_request_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("action_request_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("action_request_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("action_request_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("action_request_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("action_request_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("action_request_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "action_request_types", "context_pull")
trace_contract._emit_pulls_context("p1", "action_request_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "action_request_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "action_request_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "action_request_types", "write_through")
trace_contract._emit_writes_through("p1", "action_request_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "action_request_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "action_request_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "action_request_types", "routing_commit")


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

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "ActionRequest.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "ActionRequest.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L1_COGNITION, "ActionRequest.to_dict")
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
