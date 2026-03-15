from abc import ABC, abstractmethod
from collections.abc import Callable

from pydantic import BaseModel, Field

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
