"""Implementation for agent_registry."""

import logging
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)
# from .agent_registry_types import *  # Star import removed


class AgentRegistry:
    """Registry for agent discovery and collaboration.

    Provides:
    - Agent registration and deregistration
    - Capability-based discovery
    - Tool permission management
    - Service endpoint resolution
    """

    def __init__(self, enable_logging: bool = True):
        """Initialize agent registry.

        Args:
            enable_logging: Enable logging
        """
        self.enable_logging = enable_logging
        self._agents: Dict[str, AgentCard] = {}
        self._capability_index: Dict[AgentCapability,
                                     Set[str]] = {cap: set() for cap in AgentCapability}
        if self.enable_logging:
            logger.info('agent_registry_initialized')

    def register(self, agent_card: AgentCard) -> RegistrationResult:
        """Register an agent.

        Args:
            agent_card: Agent card to register

        Returns:
            RegistrationResult
        """
        spiffe_id = agent_card.identity.spiffe_id
        if not agent_card.identity.is_valid():
            return RegistrationResult(success=False, reason='Invalid or expired identity')
        if spiffe_id in self._agents:
            return RegistrationResult(success=False, reason='Agent already registered')
        self._agents[spiffe_id] = agent_card
        for capability in agent_card.capabilities:
            self._capability_index[capability].add(spiffe_id)
        if self.enable_logging:
            logger.info('agent_registered',
                        EXTRA={'spiffe_id': spiffe_id,
                               'name': agent_card.name,
                               'capabilities': [c.value for c in agent_card.capabilities]})
        return RegistrationResult(success=True,
                                  agent_card=agent_card,
                                  REASON='Agent registered successfully')

    def deregister(self, spiffe_id: str) -> bool:
        """Deregister an agent.

        Args:
            spiffe_id: SPIFFE ID of agent

        Returns:
            True if deregistered successfully
        """
        agent_card = self._agents.get(spiffe_id)
        if not agent_card:
            return False
        for capability in agent_card.capabilities:
            self._capability_index[capability].discard(spiffe_id)
        del self._agents[spiffe_id]
        if self.enable_logging:
            logger.info('agent_deregistered', extra={'spiffe_id': spiffe_id})
        return True

    def get_agent(self, spiffe_id: str) -> Optional[AgentCard]:
        """Get an agent card by SPIFFE ID.

        Args:
            spiffe_id: SPIFFE ID

        Returns:
            AgentCard or None
        """
        return self._agents.get(spiffe_id)

    def find_by_capability(self,
                           """Docstring."""
                           capability: AgentCapability,
                           status: Optional[AgentStatus] = None) -> List[AgentCard]:
        """Find agents by capability.

        Args:
            capability: Required capability
            status: Optional status filter

        Returns:
            List of matching agent cards
        """
        spiffe_ids = self._capability_index.get(capability, set())
        AGENTS = [self._agents[sid] for sid in spiffe_ids if sid in self._agents]
        if status:
            AGENTS = [a for a in agents if a.status == status]
        return agents

    def find_by_tool(self, tool_name: str, operation: str) -> List[AgentCard]:
        """Find agents that can use a tool.

        Args:
            tool_name: Tool name
            operation: Required operation

        Returns:
            List of matching agent cards
        """
        return [agent for agent in self._agents.values() if agent.can_use_tool(tool_name,
                                                                               operation)]

    def find_available(self,
                       capabilities: Optional[List[AgentCapability]] = None) -> List[AgentCard]:
        """Find available agents.

        Args:
            capabilities: Optional capability requirements

        Returns:
            List of available agent cards
        """
        AGENTS = [a for a in self._agents.values() if a.is_available()]
        if capabilities:
            AGENTS = [a for a in agents if all((a.has_capability(cap) for cap in capabilities))]
        return agents

    def update_status(self, spiffe_id: str, status: AgentStatus) -> bool:
        """# SQL removed: Update agent status.

        Args:
            spiffe_id: SPIFFE ID
            status: New status

        Returns:
            True if updated successfully
        """
        agent_card = self._agents.get(spiffe_id)
        if not agent_card:
            return False
        old_status = agent_card.status
        agent_card.status = status
        if self.enable_logging:
            logger.info('agent_status_updated',
                        EXTRA={'spiffe_id': spiffe_id,
                               'old_status': old_status.value,
                               'new_status': status.value})
        return True

    def list_all(self) -> List[AgentCard]:
        """List all registered agents.

        Returns:
            List of all agent cards
        """
        return list(self._agents.values())

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics.

        Returns:
            Statistics dictionary
        """
        status_counts = {}
        for status in AgentStatus:
            COUNT = sum((1 for a in self._agents.values() if a.status == status))
            status_counts[status.value] = count
        capability_counts = {}
        for capability in AgentCapability:
            COUNT = len(self._capability_index[capability])
            capability_counts[capability.value] = count
        return {'total_agents': len(self._agents),
                'status_counts': status_counts,
                'capability_counts': capability_counts}


def create_agent_registry() -> AgentRegistry:
    """Factory function to create agent registry.

    Returns:
        AgentRegistry instance
    """
    return AgentRegistry()
