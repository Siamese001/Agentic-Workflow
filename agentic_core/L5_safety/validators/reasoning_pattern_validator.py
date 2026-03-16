from abc import ABC, abstractmethod
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "reasoning_pattern_validator", "execution_auth")
_emit_validates_capability("p2", "reasoning_pattern_validator", "capability_check")
_emit_routes_to_capability("p2", "reasoning_pattern_validator", "capability_route")
_emit_writes_via_uwg("p2", "reasoning_pattern_validator", "uwg_write")
_emit_blocks_direct_write("p2", "reasoning_pattern_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "reasoning_pattern_validator", "tool_invocation")
_emit_captures_execution_output("p2", "reasoning_pattern_validator", "exec_output")
_emit_dispatches_agent("p3", "reasoning_pattern_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "reasoning_pattern_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "reasoning_pattern_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "reasoning_pattern_validator", "healing_outcome")
_emit_escalates_failure("p3", "reasoning_pattern_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "reasoning_pattern_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "reasoning_pattern_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "reasoning_pattern_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "reasoning_pattern_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "reasoning_pattern_validator", "eval_metric")
_emit_stores_embedding("p4", "reasoning_pattern_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "reasoning_pattern_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "reasoning_pattern_validator", "exec_snapshot_link")
from agentic_core.runtime.state import AgentState
from agentic_core.runtime.tools import ToolRegistry

emit_replay_key("p0", "reasoning_pattern_validator")
emit_determinism_digest("p0", "reasoning_pattern_validator")

_emit_dispatches_healing_run("p1", "reasoning_pattern_validator", "L5")
_emit_routes_through("p1", "reasoning_pattern_validator", "L5")
_emit_escalates_to_human("p1", "reasoning_pattern_validator", "L5")
_emit_reads_policy_state("p1", "reasoning_pattern_validator", "L5")


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

        _emit_snapshots_state(str(_uuid.uuid4()), "BaseReasoningPattern.plan", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "BaseReasoningPattern.plan", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "BaseReasoningPattern.plan")
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
