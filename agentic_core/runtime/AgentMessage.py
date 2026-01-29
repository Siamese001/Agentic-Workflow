# Agent Execution State
# Strategy: Immutable-ish state tracking for the execution loop

from typing import Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class AgentMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentState(BaseModel):
    """
    Tracks the current context of the agent's execution.
    """

    task_id: str
    user_input: str
    messages: list[AgentMessage] = Field(default_factory=list)
    turn_count: int = Field(default=0)
    is_terminated: bool = Field(default=False)
    termination_reason: str | None = None

    # Scratchpad for data shared between steps
    context_variables: dict[str, Any] = Field(default_factory=dict)

    def add_message(self, role: str, content: str):
        self.messages.append(AgentMessage(role=role, content=content))

    def increment_turn(self):
        self.turn_count += 1
