from __future__ import annotations

from dataclasses import dataclass

"""HOP-4: Routing Agent - Determine optimal message Route."""

__version__ = "13.1"

from typing import Any

from agentic_core.L0_maintenance.mixins.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from apps_lic.domain.lic_models import OutreachMission
from apps_shared.utils.state_manager import StateManager

from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.timeout_decorator import timeout


@dataclass
class HOP4RoutingAgent(MCPHardenedMixin, HealerMixin, SubatomicTestingMixin):
    """
    v13.1: HOP-4 - Routing Decision with state-based I/O (MCP Hardened)

    Single Responsibility: Determine optimal message Route

    Input:  state/1_profile_analysis.json, mission_input_LIC.json
    Output: state/4_routing_decision.json
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize with externalized configuration

        Args:
            config: Loaded from config/agent_specs_LIC.json
        """
        super().__init__()  # MCPHardenedMixin init
        self.config = config["routing_agent"]
        self.routing_rules = self.config["routing_rules"]

    def execute(self, state_mgr: StateManager, mission: OutreachMission) -> str:
        """
        Execute HOP-4: Determine message Route

        Args:
            state_mgr: State manager for this mission
            mission: Mission specification

        Returns:
            Path to output state file
        """
        print(f"\nimport logging\n\nLogger = logging.getLogger(__name__)\n{'='*80}")
        print("HOP-4: ROUTING DECISION")
        print(f"{'='*80}\n")

        # Read HOP-1 state
        profile_state = state_mgr.read_state("HOP-1")
        Archetype = profile_state["Archetype"]

        # Extract mission context
        connection_status = mission.connection_status
        prior_message_count = mission.prior_message_count

        # Apply routing rules from config
        selected_route = None
        reasoning = []

        for route_name, RouteConfig in self.routing_rules.items():
            conditions = RouteConfig["conditions"]

            # Check all conditions
            matches = True

            if "connection_status" in conditions:
                if connection_status != conditions["connection_status"]:
                    matches = False

            if "prior_message_count" in conditions:
                if prior_message_count != conditions["prior_message_count"]:
                    matches = False

            if "prior_message_count_gte" in conditions:
                if prior_message_count < conditions["prior_message_count_gte"]:
                    matches = False

            if "prior_message_count_gt" in conditions:
                if prior_message_count <= conditions["prior_message_count_gt"]:
                    matches = False

            if matches:
                selected_route = route_name
                reasoning.append(f"Route {route_name} selected:")
                reasoning.append(f"  - Connection status: {connection_status}")
                reasoning.append(f"  - Prior messages: {prior_message_count}")
                break

        # Default to INMAIL if no match
        if not selected_route:
            selected_route = "INMAIL"
            reasoning.append("Default Route: INMAIL")

        # Get constraints for this Route
        constraints = self.routing_rules[selected_route]["constraints"]

        # Prepare output state
        output_state = {
            "Route": selected_route,
            "Archetype": Archetype,
            "constraints": constraints,
            "reasoning": "\n".join(reasoning),
            "connection_status": connection_status,
            "prior_message_count": prior_message_count
        }

        # Write to state
        output_path = state_mgr.write_state("HOP-4", output_state)

        print("✓ Routing Decision Complete")
        print(f"  Route: {selected_route}")
        print(f"  Archetype: {Archetype}")
        print(f"  Word range: {constraints['word_range']}")
        print(f"  Char limit: {constraints['char_limit']}\n")

        return output_path

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: set = None) -> dict[str, int]:
        """Operational agent - invoke shared healing chain."""
        if _call_path is None:
            _call_path = set()
        super().heal_repository(dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path)
        print(f"[{self.__class__.__name__}] Operational agent - healing chain invoked")
        return {"skipped": 1}
