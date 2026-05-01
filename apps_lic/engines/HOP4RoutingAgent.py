"""
HOP-4: Routing Agent (V2.5 Architecture).

LIC Sovereign Navigator.
Implements Gate 5 (Route Selection) and Gate 6 (Premium Mismatch).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps_lic.utils.lic_agent_base_util import LICAgentBase
from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
from apps_lic.types.TraceRegistry import TraceRegistry

from agentic_core.mixins.subatomic_testing_mixin import SubatomicTestingMixin


@dataclass
class HOP4RoutingAgent(LICAgentBase, SubatomicTestingMixin):
    """
    LIC Sovereign Navigator.

    Architecture:
    - Base: LICAgentBase
    - Input: 'mission_input', 'hop1_analysis'
    - Logic: Gate 5 (Route Selection) -> Gate 6 (Premium Mismatch)
    - Output: 'hop4_routing' (route, constraints, metadata)
    """

    # Sovereign Configuration
    routing_rules: dict[str, Any] = field(
        default_factory=lambda: {"default_route": "INMAIL", "premium_required": False}
    )

    def __post_init__(self) -> None:
        """Initialize Sovereign Capabilities."""
        super().__post_init__()

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Execute routing logic.

        1. Read Sovereign Context.
        2. Gate 5: Route Selection Logic.
        3. Gate 6: Premium Routing Mismatch Detection.
        4. Fetch Route Constraints.
        5. Write to Immutable Buffer.
        """
        # 1. Read Sovereign Context
        mission_input = buffer.read("mission_input")
        if not mission_input:
            registry.add_trace("DATA_ERROR", {"msg": "Missing mission_input"})
            raise RuntimeError("HOP-4 missing critical mission input")

        hop1 = buffer.read("hop1_analysis")
        premium_available = mission_input.get("premium_available", False)
        route_override = mission_input.get("route_override")
        connection_status = mission_input.get("connection_status", "NOT_CONNECTED")

        registry.add_trace("PHASE_STEP", {"action": "executing_gate_5_selection"})

        # 2. Gate 5: Route Selection Logic
        # Prioritize Override -> Connection Status -> Premium Availability
        selected_route = "CONNECTION_REQ"

        if route_override:
            selected_route = route_override
            registry.add_trace("ROUTE_OVERRIDE_APPLIED", {"route": selected_route})
            # Skepticism: Ensure overrides still respect Gate 6 safety
        elif connection_status == "CONNECTED":
            selected_route = "FOLLOW_UP"
        elif premium_available:
            selected_route = "INMAIL"

        # 3. Gate 6: Premium Routing Mismatch Detection (CRITICAL)
        if selected_route == "INMAIL" and not premium_available:
            registry.add_trace("GATE_6_FAILED", {"reason": "premium_unavailable_for_inmail"})
            raise ValueError(
                "GATE_6_BLOCKED: INMAIL route selected but Premium InMail not available"
            )

        # 4. Fetch Route Constraints from Specs
        config = self.config.routing_agent
        route_config = None

        # Map selected route to config key
        route_key_map = {
            "CONNECTION_REQ": "CONNECTION_REQUEST",
            "FOLLOW_UP": "DIRECT_MESSAGE",
            "INMAIL": "INMAIL",
        }
        config_key = route_key_map.get(selected_route, selected_route)

        if config_key in config.routing_rules:
            route_config = config.routing_rules[config_key]
            constraints = route_config.constraints.model_dump()
        else:
            # Fallback to CONNECTION_REQUEST constraints
            fallback = config.routing_rules.get("CONNECTION_REQUEST")
            if fallback:
                constraints = fallback.constraints.model_dump()
            else:
                constraints = {"word_range": [0, 2000], "char_limit": 2000}

        # 5. Write to Immutable Buffer
        archetype = hop1.get("Archetype", "UNKNOWN") if hop1 else "UNKNOWN"
        output_data = {
            "route": selected_route,
            "constraints": constraints,
            "metadata": {"premium_validated": True, "archetype_aligned": archetype},
        }

        buffer.write_once("hop4_routing", output_data)
        registry.add_trace("DECISION_FINAL", {"route": selected_route})

    def _check_conditions(self, conditions, status, msg_count) -> bool:
        """
        Check if conditions match current context.

        Args:
            conditions: RouteConditions from config
            status: Connection status string
            msg_count: Prior message count

        Returns:
            True if all conditions match, False otherwise
        """
        if conditions.connection_status and conditions.connection_status != status:
            return False
        if (
            conditions.prior_message_count is not None
            and conditions.prior_message_count != msg_count
        ):
            return False
        if (
            conditions.prior_message_count_gt is not None
            and msg_count <= conditions.prior_message_count_gt
        ):
            return False
        if (
            conditions.prior_message_count_gte is not None
            and msg_count < conditions.prior_message_count_gte
        ):
            return False
        return True
