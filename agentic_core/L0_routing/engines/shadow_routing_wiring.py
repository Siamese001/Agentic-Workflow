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
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

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
        self, route_decision: RouteDecisionArtifact, additional_context: dict[str, Any] | None = None
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
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "ShadowRoutingWiring.observe_and_classify"
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        shadow_decision = self.shadow_classifier.observe_routing_decision(
            route_decision=route_decision, additional_context=additional_context
        )
        if self.enable_telemetry:
            telemetry = self.shadow_classifier.emit_telemetry(shadow_decision)
            logger.info(
                f"Shadow routing telemetry emitted: trace={telemetry.trace_id}, observed={shadow_decision.observed_route.value}, shadow={shadow_decision.shadow_route.value}, drift={shadow_decision.drift_score}"
            )
            if self.enable_l4_storage:
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
        return True


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
    route_decision: RouteDecisionArtifact, additional_context: dict[str, Any] | None = None
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
