from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from core.models.models import AgentCard, AgentRole

"""Keeps a catalog of available agents so each resume step can be routed to the right specialist for planning, drafting, review, or safety checks."""


@dataclass
class AgentRegistry:
    """Stores agent definitions so orchestration can assemble the right mix of planners, drafters, reviewers, and safety checkers to improve each resume."""

    _agents: Dict[str, AgentCard] = field(default_factory=dict)

    @property
    def agents(self) -> Dict[str, AgentCard]:
        """Public view of all known agents.

        Other components use this mapping when they need to see the full set
        of agents that can participate in a workflow. This supports routing
        and selection logic that keeps each resume step handled by a suitable
        specialist instead of a generic catch-all.
        """

        return self._agents

    def register_agent(self, agent_card: AgentCard) -> None:
        """Add or update an agent so it can be used in workflows.

        Registering an agent makes its capabilities available to the routing
        policies. This is how new skills or behaviors are introduced into the
        system so they can help produce better, more tailored resumes.
        """

        self._agents[agent_card.agent_id] = agent_card

    def get_agent(self, agent_id: str) -> AgentCard:
        """Look up a specific agent by its identifier.

        This is used when orchestration needs to invoke a particular agent for
        a well-defined role in the resume workflow, such as a dedicated
        quality reviewer or a job-matching specialist.
        """

        if agent_id not in self._agents:
            raise KeyError(f"Unknown agent_id: {agent_id}")
        return self._agents[agent_id]

    def find_agents_by_role(self, role: AgentRole | str) -> List[AgentCard]:
        """Find agents that play a given role in the resume workflow.

        For example, callers can ask for all "planner" or all "drafter" agents
        when they want to assemble a pipeline focused on strategy, rewriting,
        or review. This supports flexible configurations without hard-coding
        specific agent names.
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



