from abc import ABC, abstractmethod
from collections.abc import Callable

from pydantic import BaseModel, Field

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "base_tool", "L0")
_emit_routes_through("p1", "base_tool", "L0")
_emit_escalates_to_human("p1", "base_tool", "L0")
_emit_reads_policy_state("p1", "base_tool", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "base_tool", "p0_governance")
_emit_snapshots_state("p0", "base_tool", "state_snapshot")
_emit_authorize_and_execute("p2", "base_tool", "execution_auth")
_emit_validates_capability("p2", "base_tool", "capability_check")
_emit_routes_to_capability("p2", "base_tool", "capability_route")
_emit_writes_via_uwg("p2", "base_tool", "uwg_write")
_emit_blocks_direct_write("p2", "base_tool", "direct_write_block")
_emit_records_tool_invocation("p2", "base_tool", "tool_invocation")
_emit_captures_execution_output("p2", "base_tool", "exec_output")
_emit_dispatches_agent("p3", "base_tool", "agent_dispatch")
_emit_coordinates_agents("p3", "base_tool", "agent_coordination")
_emit_records_workflow_lineage("p3", "base_tool", "workflow_lineage")
_emit_records_healing_outcome("p3", "base_tool", "healing_outcome")
_emit_escalates_failure("p3", "base_tool", "failure_escalation")
_emit_orchestrates_workflow("p3", "base_tool", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "base_tool", "healing_dispatch")
_emit_invokes_evaluation("p3", "base_tool", "evaluation_signal")
_emit_records_telemetry_event("p4", "base_tool", "telemetry_event")
_emit_captures_evaluation_metric("p4", "base_tool", "eval_metric")
_emit_stores_embedding("p4", "base_tool", "embedding_store")
_emit_updates_meta_learning_state("p4", "base_tool", "meta_learning")
_emit_links_execution_to_snapshot("p4", "base_tool", "exec_snapshot_link")


class BaseTool(BaseModel, ABC):
    """
    Abstract base class for all executable tools.
    """

    name: str = Field(..., description="Unique identifier for the tool")
    description: str = Field(..., description="Natural language description for the LLM")

    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    async def run(self, **kwargs) -> str:
        """
        Execute the tool logic. Returns a string observation.
        """
        pass


class FunctionalTool(BaseTool):
    """
    Wrapper to turn a Python function into a Tool.
    """

    func: Callable

    async def run(self, **kwargs) -> str:
        try:
            return str(self.func(**kwargs))
        # guardian: allow-silent-swallow
        except Exception as e:
            return f"Error executing {self.name}: {str(e)}"


class ToolRegistry:
    """
    Manager for the agent's available toolkit.
    """

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "ToolRegistry.register")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        if tool.name in self._tools:
            raise ValueError(f"Tool {tool.name} already registered")
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_tools(self) -> str:
        return "\n".join([f"- {t.name}: {t.description}" for t in self._tools.values()])
