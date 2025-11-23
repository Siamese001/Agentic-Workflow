from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from models import AgentMessage


@dataclass
class AgentBus:
    """Simple in-memory agent message bus.

    This is intentionally deterministic and side-effect free outside of
    process memory. It is suitable for tests and small-scale orchestration.
    """

    _queues: Dict[str, List[AgentMessage]] = field(default_factory=dict)

    def send_message(self, message: AgentMessage) -> None:
        queue = self._queues.setdefault(message.target_agent_id, [])
        queue.append(message)

    def get_messages_for(self, agent_id: str) -> List[AgentMessage]:
        return list(self._queues.get(agent_id, []))

    def clear(self) -> None:
        self._queues.clear()

    # Phase-1 compatibility helpers -------------------------------------

    def send(self, message: AgentMessage) -> None:
        """Alias for send_message used by Phase-1 AgentBus API."""

        self.send_message(message)

    def get_for(self, agent_id: str) -> List[AgentMessage]:
        """Alias for get_messages_for used by Phase-1 AgentBus API."""

        return self.get_messages_for(agent_id)
