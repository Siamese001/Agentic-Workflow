from __future__ import annotations
"""
Agent Capabilities Registry - Functional Role-based Agent System.

This module defines the functional capabilities that replace the legacy K-node
numbered system. Agents are identified by their function, not by numbers.
"""
from dataclasses import dataclass, field
from enum import Enum, auto
import logging
from typing import Any, Callable, Dict, List, Optional
from pathlib import Path

Logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Functional roles for agents in the system."""
    RESEARCHER = auto()
    WRITER = auto()
    VALIDATOR = auto()
    ORCHESTRATOR = auto()
    CONTEXT_GATHERER = auto()
    STRATEGIC_PLANNER = auto()
    CONTENT_DRAFTER = auto()
    QUALITY_CRITIC = auto()
    MESSAGE_CRAFTER = auto()
    PROTOCOL_ENFORCER = auto()


@dataclass
class AgentCapability:
    """Defines the capability of an agent role."""
    role: AgentRole
    display_name: str = ""
    description: str = ""
    primary_function: str = ""
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    system_prompt_template: str = ""
    legacy_k_nodes: List[str] = field(default_factory=list)


class AgentSpec:
    """Specification for creating an agent instance."""

    def __init__(self, role: AgentRole, hop_function: Callable = None, config: Any = None, **kwargs) -> None:
        """Initialize agent specification."""
        self.role = role
        self.hop_function = hop_function
        self.config = config
        self.parameters = kwargs

    def _configure_for_role(self) -> None:
        """Configure the agent spec based on its role."""
        pass


# NOT_AN_AGENT — registry utility class, not a true agent — excluded from agent discovery
class AgentRegistry:
    """Registry for managing agent capabilities and specifications."""

    def __init__(self) -> None:
        """Initialize the agent registry."""
        self._capabilities: Dict[AgentRole, AgentCapability] = {}
        self._specs: Dict[AgentRole, AgentSpec] = {}
        Logger.info("Initialized AgentRegistry")

    def get_capability(self, role: AgentRole) -> Optional[AgentCapability]:
        """Get the capability definition for a role."""
        return self._capabilities.get(role)

    def register_agent(self, spec: AgentSpec) -> None:
        """Register an agent specification."""
        self._specs[spec.role] = spec
        Logger.info(f"Registered agent for role: {spec.role.value}")

    def get_agent_spec(self, role: AgentRole) -> Optional[AgentSpec]:
        """Get a registered agent specification."""
        return self._specs.get(role)

    def list_roles(self) -> List[AgentRole]:
        """List all available agent roles."""
        return list(self._capabilities.keys())

    def run(self) -> Dict[str, Any]:
        """Execute registry validation."""
        return {
            "total_roles": len(self.list_roles()),
            "registered_specs": len(self._specs),
            "status": "healthy"
        }


# Aliases for discovery
