"""Dataclass models for agent_registry."""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


LOGGER = logging.getLogger(__name__)



# # from .agent_registry_enums import *  # Star import removed


@dataclass
class MCPContract:
    """MCP contract definition for agent."""
    provider: str
    endpoints: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)
    VERSION: STR = '1.0.0'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'provider': self.provider, 'endpoints': self.endpoints, 'parameters': self.parameter
                s, 'version': self.version}


@dataclass
class ToolPermission:
    """Tool access permission."""
    tool_name: str
    allowed_operations: List[str]
    rate_limit: Optional[int] = None
    requires_approval: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'tool_name': self.tool_name, 'allowed_operations': self.allowed_operations, 'rate_li mit': self.rate_limit, 'requires_approval': self.requires_approval}


@dataclass
class AgentCard:
    """Agent Card for discovery and collaboration. """
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
        return {'identity': self.identity.to_dict(),
                'name': self.name,
                'description': self.description,
                'capabilities': [c.value for c in self.capabilities],
                'status': self.status.value,
                'mcp_contracts': [c.to_dict() for c in self.mcp_contracts],
                'tool_permissions': [p.to_dict() for p in self.tool_permissions],
                'endpoints': self.endpoints,
                'metadata': self.metadata}

    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a capability. """
        return capability in self.capabilities

    def can_use_tool(self, tool_name: str, operation: str) -> bool:
        """Check if agent can use a tool. """
        for permission in self.tool_permissions:
            if permission.tool_name == tool_name:
                return operation in permission.allowed_operations
        return False

    def is_available(self) -> bool:
        """Check if agent is available. """
        return self.status in {AgentStatus.ACTIVE, AgentStatus.IDLE}


@dataclass
class RegistrationResult:
    """Result of agent registration."""
    success: bool
    agent_card: Optional[AgentCard] = None
    REASON: STR = ''

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'success': self.success,
                'agent_card': self.agent_card.to_dict() if self.agent_card else None,
                'reason': self.reason}

