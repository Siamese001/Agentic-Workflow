from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from models import AgentCard, AgentRole


@dataclass
class AgentRegistry:
    """In-memory registry of AgentCard definitions.

    This is a lightweight helper used by L3 orchestration and META routing
    to look up agents by id, role, or capability. It is deterministic and
    has no side effects.
    """

    _agents: Dict[str, AgentCard] = field(default_factory=dict)

    @property
    def agents(self) -> Dict[str, AgentCard]:
        """Public view of the registry mapping (Phase-1 compatibility).

        Exposes the underlying in-memory mapping so helper policies such as
        agent_router_policy can iterate over all registered agents without
        depending on private attributes.
        """

        return self._agents

    def register_agent(self, agent_card: AgentCard) -> None:
        """Register or overwrite an AgentCard by its agent_id."""

        self._agents[agent_card.agent_id] = agent_card

    def get_agent(self, agent_id: str) -> AgentCard:
        """Return the AgentCard for agent_id or raise KeyError."""

        if agent_id not in self._agents:
            raise KeyError(f"Unknown agent_id: {agent_id}")
        return self._agents[agent_id]

    def find_agents_by_role(self, role: AgentRole | str) -> List[AgentCard]:
        """Return all agents matching the given role value.

        Accepts either an AgentRole enum or its string value.
        """

        role_value = role.value if isinstance(role, AgentRole) else str(role)
        return [a for a in self._agents.values() if a.role.value == role_value]


    # Phase-1 compatibility helpers -------------------------------------

    def find_agents_by_type(self, agent_type: str) -> List[AgentCard]:
        """Return all agents whose agent_type matches the given string."""

        matches: List[AgentCard] = []
        for a in self._agents.values():
            atype = getattr(a, "agent_type", None)
            if atype == agent_type:
                matches.append(a)
                continue

            # Fallback: infer from role when agent_type is not explicitly set.
            try:
                role_val = a.role.value  # type: ignore[union-attr]
            except Exception:  # pragma: no cover - defensive
                role_val = None
            if role_val == agent_type:
                matches.append(a)
        return matches

    def find_agents_by_capability(self, capability: str) -> List[AgentCard]:
        """Return all agents whose capabilities include the given string."""

        return [a for a in self._agents.values() if capability in (a.capabilities or [])]
