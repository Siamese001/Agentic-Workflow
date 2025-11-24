from __future__ import annotations

"""Provides a lightweight in-memory channel for agents to share messages so resume steps stay coordinated and important context is not lost between planning, drafting, and review."""

from dataclasses import dataclass, field
from typing import Dict, List

from core.models.models import AgentMessage


@dataclass
class AgentBus:
    """Acts as an in-memory mailbox so agents can pass results and insights, keeping later resume steps aware of earlier decisions and preserving a coherent story for the candidate."""

    _queues: Dict[str, List[AgentMessage]] = field(default_factory=dict)

    def send_message(self, message: AgentMessage) -> None:
        """Deliver a message to the agent responsible for the next step.

        Each message typically carries context or results from an earlier
        stage of the workflow. Routing it through this bus means downstream
        agents can pick up exactly what they need to refine, review, or score
        the resume without redoing work or guessing about prior decisions.
        """

        queue = self._queues.setdefault(message.target_agent_id, [])
        queue.append(message)

    def get_messages_for(self, agent_id: str) -> List[AgentMessage]:
        """Retrieve all messages waiting for a given agent.

        In practice this lets an agent see everything that earlier steps have
        discovered or decided about the candidate and role. That shared view
        supports better judgments about what to highlight, clarify, or remove
        in the resume.
        """

        return list(self._queues.get(agent_id, []))

    def clear(self) -> None:
        """Reset all agent queues.

        This is mainly used when starting a fresh workflow run or cleaning up
        between tests, so each resume is processed independently without
        leaking information from previous runs.

        This helps to ensure that each resume is produced in isolation, without
        any residual information from previous runs that could impact its quality.
        """

        self._queues.clear()

    # Phase-1 compatibility helpers -------------------------------------

    def send(self, message: AgentMessage) -> None:
        """Compatibility alias that forwards to ``send_message``.

        This keeps older code paths working while still benefiting from the
        same, predictable message handling that newer parts of the workflow
        rely on to coordinate resume improvements.
        """

        self.send_message(message)

    def get_for(self, agent_id: str) -> List[AgentMessage]:
        """Compatibility alias that forwards to ``get_messages_for``.

        Older callers can still retrieve all messages for an agent without
        being aware of newer APIs. This helps maintain stability as the
        workflow evolves, which is important for keeping resume outputs
        consistent over time.
        """

        return self.get_messages_for(agent_id)



