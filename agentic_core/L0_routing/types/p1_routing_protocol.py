"""P1 routing protocols and core types."""

from __future__ import annotations

from typing import Any, Protocol


class P1RoutingProtocol(Protocol):
    """Protocol for P1 routing operations."""

    def route_to_agent(self, agent_id: str, context: dict[str, Any]) -> bool:
        """Route execution to specified agent."""
        ...

    def validate_capability(self, agent_id: str, capability: str) -> bool:
        """Validate agent has required capability."""
        ...


class P1Core:
    """Core P1 routing functionality."""

    def __init__(self) -> None:
        self._agents: dict[str, dict[str, Any]] = {}

    def register_agent(self, agent_id: str, capabilities: list[str]) -> None:
        """Register an agent with capabilities."""
        self._agents[agent_id] = {
            "capabilities": capabilities,
            "status": "active",
        }

    def route_to_agent(self, agent_id: str, context: dict[str, Any]) -> bool:
        """Route execution to specified agent."""
        if agent_id not in self._agents:
            return False
        return self._agents[agent_id]["status"] == "active"

    def validate_capability(self, agent_id: str, capability: str) -> bool:
        """Validate agent has required capability."""
        if agent_id not in self._agents:
            return False
        return capability in self._agents[agent_id]["capabilities"]

    def get_agent_status(self, agent_id: str) -> str | None:
        """Get agent status."""
        agent = self._agents.get(agent_id)
        return agent["status"] if agent else None


__all__ = [
    "P1Core",
    "P1RoutingProtocol",
]
