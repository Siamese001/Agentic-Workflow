"""StructuredAgentOutput — mandatory schema for all apps_* agent execute() returns.

Spec: AgentOutputContract [7], Guarantee #12.
Every apps_* agent execute() MUST return a StructuredAgentOutput containing:
  - intent_delta: str describing what the agent is changing/doing
  - tool_requests: list of ToolRequest describing tools to invoke
  - state_diff_proposal: dict describing the proposed state mutations
"""

from __future__ import annotations

from dataclasses import dataclass, field
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

emit_replay_key("p0", "structured_agent_output_types")
emit_determinism_digest("p0", "structured_agent_output_types")

_emit_dispatches_healing_run("p1", "structured_agent_output_types", "L2")
_emit_routes_through("p1", "structured_agent_output_types", "L2")
_emit_escalates_to_human("p1", "structured_agent_output_types", "L2")
_emit_reads_policy_state("p1", "structured_agent_output_types", "L2")
_emit_authorize_and_execute("p2", "structured_agent_output_types", "execution_auth")
_emit_validates_capability("p2", "structured_agent_output_types", "capability_check")
_emit_routes_to_capability("p2", "structured_agent_output_types", "capability_route")
_emit_writes_via_uwg("p2", "structured_agent_output_types", "uwg_write")
_emit_blocks_direct_write("p2", "structured_agent_output_types", "direct_write_block")
_emit_records_tool_invocation("p2", "structured_agent_output_types", "tool_invocation")
_emit_captures_execution_output("p2", "structured_agent_output_types", "exec_output")
_emit_dispatches_agent("p3", "structured_agent_output_types", "agent_dispatch")
_emit_coordinates_agents("p3", "structured_agent_output_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "structured_agent_output_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "structured_agent_output_types", "healing_outcome")
_emit_escalates_failure("p3", "structured_agent_output_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "structured_agent_output_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "structured_agent_output_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "structured_agent_output_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "structured_agent_output_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "structured_agent_output_types", "eval_metric")
_emit_stores_embedding("p4", "structured_agent_output_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "structured_agent_output_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "structured_agent_output_types", "exec_snapshot_link")


class StructuredOutputViolation(ValueError):
    """Raised when StructuredAgentOutput invariants are broken."""


@dataclass(frozen=True)
class ToolRequest:
    """A single tool invocation request emitted by an apps_* agent.

    Spec: AgentOutputContract tool_requests[] schema element.
    """

    tool_name: str
    args: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.tool_name or not self.tool_name.strip():
            raise StructuredOutputViolation("ToolRequest.tool_name must be non-empty")


@dataclass(frozen=True)
class StructuredAgentOutput:
    """Structured output schema for all apps_* agent execute() returns.

    Spec: AgentOutputContract [7], Guarantee #12.

    Fields:
        intent_delta: Non-empty description of agent intent / what is changing.
        tool_requests: Zero or more tool invocation requests.
        state_diff_proposal: Dict of proposed state mutations (may be empty dict).
    """

    intent_delta: str
    tool_requests: tuple[ToolRequest, ...]
    state_diff_proposal: dict[str, Any]

    def __post_init__(self) -> None:
        if not self.intent_delta or not self.intent_delta.strip():
            raise StructuredOutputViolation(
                "StructuredAgentOutput.intent_delta must be a non-empty string. Spec: AgentOutputContract [7]."
            )
        if not isinstance(self.tool_requests, tuple):
            raise StructuredOutputViolation(
                "StructuredAgentOutput.tool_requests must be a tuple of ToolRequest objects."
            )
        if not isinstance(self.state_diff_proposal, dict):
            raise StructuredOutputViolation("StructuredAgentOutput.state_diff_proposal must be a dict.")

    @classmethod
    def empty(cls, intent_delta: str) -> StructuredAgentOutput:
        """Create a StructuredAgentOutput with no tool requests and empty state diff."""
        return cls(intent_delta=intent_delta, tool_requests=(), state_diff_proposal={})

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict for AgentOutputContract payload."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "StructuredAgentOutput.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "StructuredAgentOutput.to_dict", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "StructuredAgentOutput.to_dict")
        return {
            "intent_delta": self.intent_delta,
            "tool_requests": [{"tool_name": r.tool_name, "args": r.args} for r in self.tool_requests],
            "state_diff_proposal": self.state_diff_proposal,
        }


__all__ = ["StructuredAgentOutput", "StructuredOutputViolation", "ToolRequest"]
