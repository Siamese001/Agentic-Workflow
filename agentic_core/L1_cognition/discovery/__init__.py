"""Agent Discovery and Registry. """
import logging

logger = logging.getLogger(__name__)  # GLOBAL: Review if this should be constant


__all__ = [
    "AgentCard",
    "AgentRegistry",
    "AgentCapability",
    "RegistrationResult",
    "create_agent_registry",
]

