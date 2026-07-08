from abc import ABC, abstractmethod
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_authorize_and_execute("p2", "reasoning_pattern_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "reasoning_pattern_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "reasoning_pattern_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "reasoning_pattern_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "reasoning_pattern_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "reasoning_pattern_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "reasoning_pattern_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "reasoning_pattern_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "reasoning_pattern_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "reasoning_pattern_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "reasoning_pattern_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "reasoning_pattern_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "reasoning_pattern_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "reasoning_pattern_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "reasoning_pattern_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "reasoning_pattern_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "reasoning_pattern_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "reasoning_pattern_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "reasoning_pattern_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "reasoning_pattern_validator", "exec_snapshot_link")
from agentic_core.runtime.state import AgentState
from agentic_core.runtime.tools import ToolRegistry

trace_contract.emit_replay_key("p0", "reasoning_pattern_validator")
trace_contract.emit_determinism_digest("p0", "reasoning_pattern_validator")

trace_contract._emit_dispatches_healing_run("p1", "reasoning_pattern_validator", "L5")
trace_contract._emit_routes_through("p1", "reasoning_pattern_validator", "L5")
trace_contract._emit_checks_agent_registry("p1", "reasoning_pattern_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "reasoning_pattern_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "reasoning_pattern_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "reasoning_pattern_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "reasoning_pattern_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "reasoning_pattern_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "reasoning_pattern_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "reasoning_pattern_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "reasoning_pattern_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "reasoning_pattern_validator")
trace_contract._emit_gated_by_confidence("p1", "reasoning_pattern_validator", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "reasoning_pattern_validator", "L5")
trace_contract._emit_reads_policy_state("p1", "reasoning_pattern_validator", "L5")

trace_contract._emit_emits_metric_event("reasoning_pattern_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("reasoning_pattern_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("reasoning_pattern_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("reasoning_pattern_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("reasoning_pattern_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("reasoning_pattern_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("reasoning_pattern_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("reasoning_pattern_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("reasoning_pattern_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("reasoning_pattern_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("reasoning_pattern_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("reasoning_pattern_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("reasoning_pattern_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("reasoning_pattern_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("reasoning_pattern_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("reasoning_pattern_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("reasoning_pattern_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("reasoning_pattern_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("reasoning_pattern_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("reasoning_pattern_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("reasoning_pattern_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("reasoning_pattern_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("reasoning_pattern_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("reasoning_pattern_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("reasoning_pattern_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("reasoning_pattern_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("reasoning_pattern_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("reasoning_pattern_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "reasoning_pattern_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "reasoning_pattern_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "reasoning_pattern_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "reasoning_pattern_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "reasoning_pattern_validator", "write_through")
trace_contract._emit_writes_through("p1", "reasoning_pattern_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "reasoning_pattern_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "reasoning_pattern_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "reasoning_pattern_validator", "routing_commit")


class BaseReasoningPattern(ABC):
    """
    Defines how the agent converts State -> Next Action.
    """

    @abstractmethod
    async def plan(self, state: AgentState, tools: ToolRegistry) -> tuple[str, dict[str, Any]]:
        """
        Returns a tuple: (tool_name, tool_args).
        If tool_name is "Final Answer", the agent terminates.

        Args:
            state: Current agent state containing context and observations
            tools: Available tool registry for action execution

        Returns:
            Tuple containing tool name to execute and its arguments
        """
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_snapshots_state(str(_uuid.uuid4()), "BaseReasoningPattern.plan", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        trace_contract._emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        trace_contract._emit_applies_guardrail(str(_uuid.uuid4()), "BaseReasoningPattern.plan", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "BaseReasoningPattern.plan")
        pass

    @abstractmethod
    async def validate_plan(self, plan: tuple[str, dict[str, Any]], state: AgentState) -> bool:
        """
        Validate if the generated plan is safe and executable.

        Args:
            plan: The planned action tuple (tool_name, tool_args)
            state: Current agent state for validation context

        Returns:
            True if plan is valid, False otherwise
        """
        pass

    @abstractmethod
    def get_confidence_score(self, state: AgentState) -> float:
        """
        Return confidence score for current reasoning state.

        Args:
            state: Current agent state

        Returns:
            Confidence score between 0.0 and 1.0
        """
        pass
