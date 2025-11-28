from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from core.models.models import AgentCard, AgentRole

"""
Maintains catalog of specialized agents for résumé analysis workflow routing and coordination.

Improves résumé processing by directing each analysis step to the appropriate specialist agent for optimal job matching results.
"""


@dataclass
class AgentRegistry:
    """
    Stores specialized agent definitions for coordinating résumé analysis workflows with optimal specialist routing.

    Improves résumé processing by assembling the right mix of planners, drafters, reviewers, and safety checkers for each job application.
    """

    _agents: Dict[str, AgentCard] = field(default_factory=dict)

    @property
    def agents(self) -> Dict[str, AgentCard]:
        """
        Provides access to all available résumé analysis agents for workflow routing and selection.

        Improves résumé processing by enabling proper agent selection for each specialized analysis step in job matching workflows.
        """

        return self._agents

    def register_agent(self, agent_card: AgentCard) -> None:
        """
        Adds specialized résumé analysis agent to the registry for workflow routing and coordination.

        Improves résumé processing by introducing new analysis capabilities and skills for better job matching results.
        """

        self._agents[agent_card.agent_id] = agent_card

    def get_agent(self, agent_id: str) -> AgentCard:
        """
        Retrieves specific résumé analysis agent for targeted workflow execution and coordination.

        Improves résumé processing by enabling precise agent selection for specialized roles like quality review and job matching.
        """

        if agent_id not in self._agents:
            raise KeyError(f"Unknown agent_id: {agent_id}")
        return self._agents[agent_id]

    def find_agents_by_role(self, role: AgentRole | str) -> List[AgentCard]:
        """
        Finds résumé analysis agents by specialized role for targeted workflow coordination and execution.

        Improves résumé processing by enabling selection of appropriate planners, drafters, reviewers, and safety checkers for specific analysis tasks.
        """

        role_value = role.value if isinstance(role, AgentRole) else str(role)
        return [a for a in self._agents.values() if a.role.value == role_value]


    # Phase-1 compatibility helpers -------------------------------------

    def find_agents_by_type(self, agent_type: str) -> List[AgentCard]:
        """Return all agents whose type matches a requested category.

        This is a compatibility helper that lets older routing logic ask for
        agents by a simple type label such as "planner" or "qa". It keeps
        those flows working while still benefiting from the shared registry of
        capabilities.
        """

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
        """Find agents that can perform a specific kind of improvement.

        Capabilities might include things like "rewrite bullets", "summarize
        experience", or "check safety". Selecting by capability lets the
        system pull in specialized help for targeted resume improvements.
        """

        return [a for a in self._agents.values() if capability in (a.capabilities or [])]



