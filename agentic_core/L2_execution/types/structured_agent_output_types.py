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
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

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
            raise StructuredOutputViolation('ToolRequest.tool_name must be non-empty')

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
            raise StructuredOutputViolation('StructuredAgentOutput.intent_delta must be a non-empty string. Spec: AgentOutputContract [7].')
        if not isinstance(self.tool_requests, tuple):
            raise StructuredOutputViolation('StructuredAgentOutput.tool_requests must be a tuple of ToolRequest objects.')
        if not isinstance(self.state_diff_proposal, dict):
            raise StructuredOutputViolation('StructuredAgentOutput.state_diff_proposal must be a dict.')

    @classmethod
    def empty(cls, intent_delta: str) -> 'StructuredAgentOutput':
        """Create a StructuredAgentOutput with no tool requests and empty state diff."""
        return cls(intent_delta=intent_delta, tool_requests=(), state_diff_proposal={})

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict for AgentOutputContract payload."""
        return {'intent_delta': self.intent_delta, 'tool_requests': [{'tool_name': r.tool_name, 'args': r.args} for r in self.tool_requests], 'state_diff_proposal': self.state_diff_proposal}
__all__ = ['StructuredAgentOutput', 'StructuredOutputViolation', 'ToolRequest']
