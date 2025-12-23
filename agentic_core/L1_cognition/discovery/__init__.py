"""Agent Discovery and Registry.


Phase 3 - Pillar 2: Agent Boundaries (Identity & Discovery)
Agent Card registry for multi-agent collaboration and capability discovery.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentic_core.L1_cognition.discovery.agent_registry_enums import AgentCapability
    from agentic_core.L1_cognition.discovery.agent_registry_impl import AgentRegistry, create_agent_registry
    from agentic_core.L1_cognition.discovery.agent_registry_models import AgentCard, RegistrationResult

__all__ = [
    "AgentCard",
    "AgentRegistry",
    "AgentCapability",
    "RegistrationResult",
    "create_agent_registry",
]