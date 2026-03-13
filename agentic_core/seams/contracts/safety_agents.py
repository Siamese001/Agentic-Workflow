"""
Safety agent seam contracts — Protocol definition for L5 healing agents,
plus an AgentFactory for injection into L3 consumers.

This module sits outside the layer hierarchy so imports from here
do not count as upward seams in the gravity scanner.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class HealingAgentProtocol(Protocol):
    """Protocol for any agent that can heal a repository."""

    def heal_repository(
        self, dry_run: bool = True, execute: bool = False, **kwargs: Any
    ) -> dict[str, Any]: ...


class SafetyAgentFactory:
    """
    Factory that instantiates L5 safety agents by name.

    Holds all upward imports in one place (seam boundary).
    Consumers receive a HealingAgentProtocol-compatible instance.
    """

    def __init__(self, project_root: Any) -> None:
        self.project_root = project_root

    def get(self, agent_name: str) -> HealingAgentProtocol | None:
        """Return an agent instance by name, or None if unavailable."""
        try:
            if agent_name == "HygieneGuardianAgent":
                from agentic_core.L5_safety.validators.HygieneGuardianAgent import HygieneGuardianAgent

                return HygieneGuardianAgent(project_root=self.project_root)
            elif agent_name == "NamingAgent":
                from agentic_core.L5_safety.reasoning.NamingAgent import NamingAgent

                return NamingAgent(project_root=self.project_root)
            elif agent_name == "LocationAgent":
                from agentic_core.L5_safety.reasoning.LocationHealerAgent import LocationHealerAgent

                return LocationHealerAgent(project_root=self.project_root)
            elif agent_name == "StructureEnforcerAgent":
                from agentic_core.L5_safety.reasoning.StructureEnforcerAgent import StructureEnforcerAgent

                return StructureEnforcerAgent(project_root=self.project_root)
            elif agent_name == "StructuralHealerAgent":
                from agentic_core.L5_safety.validators.StructuralHealerAgent import StructuralHealerAgent

                return StructuralHealerAgent(project_root=self.project_root)
            elif agent_name == "GovernanceAgent":
                from agentic_core.L5_safety.validators.GovernanceAgent import GovernanceAgent

                return GovernanceAgent(project_root=self.project_root)
            elif agent_name == "HierarchyAgent":
                from agentic_core.L5_safety.reasoning.hierarchy_healer import HierarchyAgent

                return HierarchyAgent(project_root=self.project_root)
        except ImportError:
            return None
        return None

    def get_legacy_import_healer_factory(self):
        """Return create_legacy_import_healer callable, or None."""
        try:
            from agentic_core.L5_safety.reasoning.CodeHealerAgent import create_legacy_import_healer

            return create_legacy_import_healer
        except ImportError:
            return None


__all__ = ["HealingAgentProtocol", "SafetyAgentFactory"]
