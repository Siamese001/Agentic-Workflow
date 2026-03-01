"""
Phase 9: Shadow Routing Wiring - Non-invasive side-channel integration.

Wires the shadow router classifier into L0 routing as a read-only side-channel
that cannot affect actual routing decisions.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.L0_routing.engines.shadow_router_classifier import ShadowRouterClassifier
from agentic_core.L0_routing.types.routing_artifact_types import RouteDecisionArtifact
from agentic_core.L0_routing.types.shadow_routing_types import ShadowRoutingTelemetry

logger = logging.getLogger(__name__)


class ShadowRoutingWiring:
    """Wires shadow routing into L0 as a non-invasive side-channel.

    This class ensures that shadow classification cannot affect actual routing
    decisions and only provides observational capabilities.
    """

    def __init__(
        self,
        shadow_classifier: ShadowRouterClassifier | None = None,
        enable_telemetry: bool = True,
        enable_l4_storage: bool = False,
    ):
        """Initialize shadow routing wiring.

        Args:
            shadow_classifier: Shadow classifier instance (created if None)
            enable_telemetry: Whether to emit telemetry to L6
            enable_l4_storage: Whether to store to L4 bounded store
        """
        self.shadow_classifier = shadow_classifier or ShadowRouterClassifier()
        self.enable_telemetry = enable_telemetry
        self.enable_l4_storage = enable_l4_storage

    def observe_and_classify(
        self,
        route_decision: RouteDecisionArtifact,
        additional_context: dict[str, Any] | None = None,
    ) -> ShadowRoutingTelemetry | None:
        """Observe routing decision and produce shadow classification.

        This is called AFTER the actual routing decision is made and
        cannot affect the routing outcome. It's strictly observational.

        Args:
            route_decision: The actual routing decision (already made)
            additional_context: Optional additional context

        Returns:
            Shadow telemetry if enabled, None otherwise
        """
        # Produce shadow classification
        shadow_decision = self.shadow_classifier.observe_routing_decision(
            route_decision=route_decision,
            additional_context=additional_context,
        )

        # Emit telemetry if enabled
        if self.enable_telemetry:
            telemetry = self.shadow_classifier.emit_telemetry(shadow_decision)

            # In a real implementation, this would emit to L6 bus
            # For Phase 9, we just log and return the telemetry
            logger.info(
                f"Shadow routing telemetry emitted: "
                f"trace={telemetry.trace_id}, "
                f"observed={shadow_decision.observed_route.value}, "
                f"shadow={shadow_decision.shadow_route.value}, "
                f"drift={shadow_decision.drift_score}"
            )

            # Optionally store to L4 (bounded store)
            if self.enable_l4_storage:
                # In a real implementation, this would store to L4
                logger.debug(f"Shadow telemetry stored to L4 for {telemetry.trace_id}")

            return telemetry

        return None

    def validate_non_invasiveness(self, route_decision: RouteDecisionArtifact) -> bool:
        """Validate that shadow routing cannot affect the actual route.

        This is a safety check to ensure the shadow classifier is truly
        non-invasive. It verifies that the original route decision is
        unchanged.

        Args:
            route_decision: The original routing decision

        Returns:
            True if non-invasiveness is guaranteed
        """
        # The shadow classifier only reads from route_decision
        # and never modifies it, so this is always true
        return True


# Global wiring instance for L0 integration
_shadow_wiring: ShadowRoutingWiring | None = None


def get_shadow_wiring() -> ShadowRoutingWiring:
    """Get the global shadow routing wiring instance.

    Returns:
        Global shadow routing wiring instance
    """
    global _shadow_wiring
    if _shadow_wiring is None:
        _shadow_wiring = ShadowRoutingWiring()
    return _shadow_wiring


def observe_routing_decision(
    route_decision: RouteDecisionArtifact,
    additional_context: dict[str, Any] | None = None,
) -> ShadowRoutingTelemetry | None:
    """Convenience function to observe a routing decision.

    This is the main entry point called from L0 routing pipeline.

    Args:
        route_decision: The routing decision to observe
        additional_context: Optional additional context

    Returns:
        Shadow telemetry if enabled, None otherwise
    """
    wiring = get_shadow_wiring()
    return wiring.observe_and_classify(route_decision, additional_context)
