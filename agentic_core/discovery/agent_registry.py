"""Agent Card Registry for Discovery and Collaboration.

Phase 3 - Pillar 2: Agent Boundaries (Identity & Discovery)
Modernized Agent Card system for multi-agent ecosystems.

Agent Cards provide:
- Capability advertisement
- MCP contract definitions
- Tool access permissions
- Service discovery
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from agentic_core.identity.spiffe_manager import AgentIdentity, IdentityType

logger = logging.getLogger(__name__)


class AgentCapability(Enum):
    """Standard agent capabilities."""
    PLANNING = "planning"
    REASONING = "reasoning"
    TOOL_EXECUTION = "tool_execution"
    CODE_GENERATION = "code_generation"
    DATA_ANALYSIS = "data_analysis"
    SEARCH = "search"
    RETRIEVAL = "retrieval"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"
    ORCHESTRATION = "orchestration"


class AgentStatus(Enum):
    """Agent operational status."""
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


@dataclass
class MCPContract:
    """MCP contract definition for agent."""
    provider: str
    endpoints: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "provider": self.provider,
            "endpoints": self.endpoints,
            "parameters": self.parameters,
            "version": self.version,
        }


@dataclass
class ToolPermission:
    """Tool access permission."""
    tool_name: str
    allowed_operations: List[str]
    rate_limit: Optional[int] = None
    requires_approval: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "tool_name": self.tool_name,
            "allowed_operations": self.allowed_operations,
            "rate_limit": self.rate_limit,
            "requires_approval": self.requires_approval,
        }


@dataclass
class AgentCard:
    """Agent Card for discovery and collaboration.
    
    Modernized version of legacy Agent Card system.
    Integrates with SPIFFE identity and MCP contracts.
    """
    identity: AgentIdentity
    name: str
    description: str
    capabilities: List[AgentCapability]
    status: AgentStatus = AgentStatus.ACTIVE
    mcp_contracts: List[MCPContract] = field(default_factory=list)
    tool_permissions: List[ToolPermission] = field(default_factory=list)
    endpoints: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "identity": self.identity.to_dict(),
            "name": self.name,
            "description": self.description,
            "capabilities": [c.value for c in self.capabilities],
            "status": self.status.value,
            "mcp_contracts": [c.to_dict() for c in self.mcp_contracts],
            "tool_permissions": [p.to_dict() for p in self.tool_permissions],
            "endpoints": self.endpoints,
            "metadata": self.metadata,
        }
    
    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a capability.
        
        Args:
            capability: Capability to check
            
        Returns:
            True if agent has capability
        """
        return capability in self.capabilities
    
    def can_use_tool(self, tool_name: str, operation: str) -> bool:
        """Check if agent can use a tool.
        
        Args:
            tool_name: Name of tool
            operation: Operation to perform
            
        Returns:
            True if allowed
        """
        for permission in self.tool_permissions:
            if permission.tool_name == tool_name:
                return operation in permission.allowed_operations
        return False
    
    def is_available(self) -> bool:
        """Check if agent is available.
        
        Returns:
            True if agent is active or idle
        """
        return self.status in {AgentStatus.ACTIVE, AgentStatus.IDLE}


@dataclass
class RegistrationResult:
    """Result of agent registration."""
    success: bool
    agent_card: Optional[AgentCard] = None
    reason: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "agent_card": self.agent_card.to_dict() if self.agent_card else None,
            "reason": self.reason,
        }


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
        self._capability_index: Dict[AgentCapability, Set[str]] = {
            cap: set() for cap in AgentCapability
        }
        
        if self.enable_logging:
            logger.info("agent_registry_initialized")
    
    def register(self, agent_card: AgentCard) -> RegistrationResult:
        """Register an agent.
        
        Args:
            agent_card: Agent card to register
            
        Returns:
            RegistrationResult
        """
        spiffe_id = agent_card.identity.spiffe_id
        
        # Check if identity is valid
        if not agent_card.identity.is_valid():
            return RegistrationResult(
                success=False,
                reason="Invalid or expired identity",
            )
        
        # Check if already registered
        if spiffe_id in self._agents:
            return RegistrationResult(
                success=False,
                reason="Agent already registered",
            )
        
        # Register agent
        self._agents[spiffe_id] = agent_card
        
        # Update capability index
        for capability in agent_card.capabilities:
            self._capability_index[capability].add(spiffe_id)
        
        if self.enable_logging:
            logger.info(
                "agent_registered",
                extra={
                    "spiffe_id": spiffe_id,
                    "name": agent_card.name,
                    "capabilities": [c.value for c in agent_card.capabilities],
                }
            )
        
        return RegistrationResult(
            success=True,
            agent_card=agent_card,
            reason="Agent registered successfully",
        )
    
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
        
        # Remove from capability index
        for capability in agent_card.capabilities:
            self._capability_index[capability].discard(spiffe_id)
        
        # Remove from registry
        del self._agents[spiffe_id]
        
        if self.enable_logging:
            logger.info(
                "agent_deregistered",
                extra={"spiffe_id": spiffe_id}
            )
        
        return True
    
    def get_agent(self, spiffe_id: str) -> Optional[AgentCard]:
        """Get an agent card by SPIFFE ID.
        
        Args:
            spiffe_id: SPIFFE ID
            
        Returns:
            AgentCard or None
        """
        return self._agents.get(spiffe_id)
    
    def find_by_capability(
        self,
        capability: AgentCapability,
        status: Optional[AgentStatus] = None,
    ) -> List[AgentCard]:
        """Find agents by capability.
        
        Args:
            capability: Required capability
            status: Optional status filter
            
        Returns:
            List of matching agent cards
        """
        spiffe_ids = self._capability_index.get(capability, set())
        agents = [self._agents[sid] for sid in spiffe_ids if sid in self._agents]
        
        if status:
            agents = [a for a in agents if a.status == status]
        
        return agents
    
    def find_by_tool(
        self,
        tool_name: str,
        operation: str,
    ) -> List[AgentCard]:
        """Find agents that can use a tool.
        
        Args:
            tool_name: Tool name
            operation: Required operation
            
        Returns:
            List of matching agent cards
        """
        return [
            agent for agent in self._agents.values()
            if agent.can_use_tool(tool_name, operation)
        ]
    
    def find_available(
        self,
        capabilities: Optional[List[AgentCapability]] = None,
    ) -> List[AgentCard]:
        """Find available agents.
        
        Args:
            capabilities: Optional capability requirements
            
        Returns:
            List of available agent cards
        """
        agents = [a for a in self._agents.values() if a.is_available()]
        
        if capabilities:
            agents = [
                a for a in agents
                if all(a.has_capability(cap) for cap in capabilities)
            ]
        
        return agents
    
    def update_status(
        self,
        spiffe_id: str,
        status: AgentStatus,
    ) -> bool:
        """Update agent status.
        
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
            logger.info(
                "agent_status_updated",
                extra={
                    "spiffe_id": spiffe_id,
                    "old_status": old_status.value,
                    "new_status": status.value,
                }
            )
        
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
            count = sum(1 for a in self._agents.values() if a.status == status)
            status_counts[status.value] = count
        
        capability_counts = {}
        for capability in AgentCapability:
            count = len(self._capability_index[capability])
            capability_counts[capability.value] = count
        
        return {
            "total_agents": len(self._agents),
            "status_counts": status_counts,
            "capability_counts": capability_counts,
        }


def create_agent_registry() -> AgentRegistry:
    """Factory function to create agent registry.
    
    Returns:
        AgentRegistry instance
    """
    return AgentRegistry()
