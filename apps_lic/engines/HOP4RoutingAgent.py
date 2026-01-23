"""
HOP-4: Routing Agent (V2 Architecture).

Determines optimal outreach route based on connection status and history.
"""

from __future__ import annotations
from apps_lic.shared.v2_patterns.agent_base import V2AgentBase
from apps_lic.shared.v2_patterns.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.v2_patterns.trace_registry import TraceRegistry


class HOP4RoutingAgent(V2AgentBase):
    """
    V2 Implementation of HOP-4 Rule Engine.

    Architecture:
    - Base: V2AgentBase
    - Input: 'mission_input' (connection status, message count)
    - Logic: Rule-based routing evaluation
    - Output: 'hop4_routing' (route, constraints, reasoning)
    """

    def _process(self, buffer: ImmutableStagingBuffer, registry: TraceRegistry) -> None:
        """
        Execute routing logic.

        1. Read mission input (connection status, message count).
        2. Evaluate routing rules in order.
        3. Select first matching route or fallback to default.
        4. Write immutable routing decision.
        """
        # 1. Read Inputs
        mission_input = buffer.read("mission_input")
        if not mission_input:
            registry.add_trace("DATA_ERROR", {"msg": "Missing 'mission_input'"})
            raise ValueError("HOP-4 requires 'mission_input'")

        hop1 = buffer.read("hop1_analysis")
        # hop1 is optional for routing logic but good for context

        status = mission_input.get("connection_status", "UNKNOWN")
        msg_count = mission_input.get("prior_message_count", 0)

        registry.add_trace(
            "PHASE_STEP", {"action": "evaluating_routes", "status": status, "msgs": msg_count}
        )

        # 2. Evaluate Rules
        selected_route = "INMAIL"  # Default
        constraints = {"word_range": [0, 2000], "char_limit": 2000}
        match_reason = "Default Fallback"

        config = self.config.routing_agent

        for route_name, rules in config.routing_rules.items():
            if self._check_conditions(rules.conditions, status, msg_count):
                selected_route = route_name
                constraints = rules.constraints.model_dump()
                match_reason = f"Matched rules for {route_name}"
                break

        # 3. Write Output
        output = {
            "route": selected_route,
            "constraints": constraints,
            "reasoning": match_reason,
            "context": {"status": status, "msg_count": msg_count},
        }

        buffer.write_once("hop4_routing", output)
        registry.add_trace("DECISION_FINAL", {"route": selected_route, "reason": match_reason})

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
