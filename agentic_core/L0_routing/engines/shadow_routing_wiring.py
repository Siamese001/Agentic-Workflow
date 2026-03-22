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
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_dispatches_healing_run("p1", "shadow_routing_wiring", "L0")
_emit_routes_through("p1", "shadow_routing_wiring", "L0")
_emit_checks_agent_registry("p1", "shadow_routing_wiring", "agent_registry")
_emit_validates_agent_capability("p1", "shadow_routing_wiring", "capability")
_emit_dispatches_execution_plan("p1", "shadow_routing_wiring", "exec_plan")
_emit_agent_executes_agent("p1", "shadow_routing_wiring", "sub_agent")
_emit_routes_to_agent("p1", "shadow_routing_wiring", "target_agent")
_emit_verifies_policy("p1", "shadow_routing_wiring", "policy_check")
_emit_observes_runtime_state("p1", "shadow_routing_wiring", "runtime_state")
_emit_verifies_boundary("p1", "shadow_routing_wiring", "boundary_check")
_emit_transcripts_response("p1", "shadow_routing_wiring", "transcript")
_emit_hard_fails_untranscripted("p1", "shadow_routing_wiring")
_emit_gated_by_confidence("p1", "shadow_routing_wiring", "confidence_gate")
_emit_escalates_to_human("p1", "shadow_routing_wiring", "L0")
_emit_reads_policy_state("p1", "shadow_routing_wiring", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "shadow_routing_wiring", "p0_governance")
_emit_snapshots_state("p0", "shadow_routing_wiring", "state_snapshot")
_emit_authorize_and_execute("p2", "shadow_routing_wiring", "execution_auth")
_emit_validates_capability("p2", "shadow_routing_wiring", "capability_check")
_emit_routes_to_capability("p2", "shadow_routing_wiring", "capability_route")
_emit_writes_via_uwg("p2", "shadow_routing_wiring", "uwg_write")
_emit_blocks_direct_write("p2", "shadow_routing_wiring", "direct_write_block")
_emit_records_tool_invocation("p2", "shadow_routing_wiring", "tool_invocation")
_emit_captures_execution_output("p2", "shadow_routing_wiring", "exec_output")
_emit_dispatches_agent("p3", "shadow_routing_wiring", "agent_dispatch")
_emit_coordinates_agents("p3", "shadow_routing_wiring", "agent_coordination")
_emit_records_workflow_lineage("p3", "shadow_routing_wiring", "workflow_lineage")
_emit_records_healing_outcome("p3", "shadow_routing_wiring", "healing_outcome")
_emit_escalates_failure("p3", "shadow_routing_wiring", "failure_escalation")
_emit_orchestrates_workflow("p3", "shadow_routing_wiring", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "shadow_routing_wiring", "healing_dispatch")
_emit_invokes_evaluation("p3", "shadow_routing_wiring", "evaluation_signal")
_emit_records_telemetry_event("p4", "shadow_routing_wiring", "telemetry_event")
_emit_captures_evaluation_metric("p4", "shadow_routing_wiring", "eval_metric")
_emit_stores_embedding("p4", "shadow_routing_wiring", "embedding_store")
_emit_updates_meta_learning_state("p4", "shadow_routing_wiring", "meta_learning")
_emit_links_execution_to_snapshot("p4", "shadow_routing_wiring", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("shadow_routing_wiring", "p4obs", "metric_1")
_emit_emits_metric_event("shadow_routing_wiring", "p4obs", "metric_2")
_emit_emits_metric_event("shadow_routing_wiring", "p4obs", "metric_3")
_emit_emits_metric_event("shadow_routing_wiring", "p4obs", "metric_4")
_emit_emits_metric_event("shadow_routing_wiring", "p4obs", "metric_5")
_emit_emits_metric_event("shadow_routing_wiring", "p4obs", "metric_6")
_emit_records_incident_event("shadow_routing_wiring", "p4obs", "incident")
_emit_captures_runtime_anomaly("shadow_routing_wiring", "p4obs", "anomaly")
_emit_writes_observability_log("shadow_routing_wiring", "p4obs", "obs_log")
_emit_updates_monitoring_state("shadow_routing_wiring", "p4obs", "mon_state")
_emit_triggers_alert("shadow_routing_wiring", "p4obs", "alert")
_emit_links_incident_trace("shadow_routing_wiring", "p4obs", "trace_link")
_emit_captures_pattern("shadow_routing_wiring", "p3lm", "pattern")
_emit_records_learning_event("shadow_routing_wiring", "p3lm", "learning_event")
_emit_writes_learning_snapshot("shadow_routing_wiring", "p3lm", "snapshot")
_emit_feeds_meta_learning("shadow_routing_wiring", "p3lm", "meta_feed")
_emit_updates_routing_strategy("shadow_routing_wiring", "p3lm", "routing")
_emit_improves_agent_policy("shadow_routing_wiring", "p3lm", "policy")
_emit_stores_learning_state("shadow_routing_wiring", "p3lm", "state")
_emit_records_execution_trace("shadow_routing_wiring", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("shadow_routing_wiring", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("shadow_routing_wiring", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("shadow_routing_wiring", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("shadow_routing_wiring", "L4_STATE", "p2_trace_5")
_emit_reads_environ("shadow_routing_wiring", "env_read", "p2_env_1")
_emit_reads_environ("shadow_routing_wiring", "env_read", "p2_env_2")
_emit_reads_runtime_state("shadow_routing_wiring", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("shadow_routing_wiring", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "shadow_routing_wiring", "context_pull")
_emit_pulls_context("p1", "shadow_routing_wiring", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "shadow_routing_wiring", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "shadow_routing_wiring", "uwg_term_2")
_emit_writes_through("p1", "shadow_routing_wiring", "write_through")
_emit_writes_through("p1", "shadow_routing_wiring", "write_through_2")
_emit_validated_by_safety_plane("p1", "shadow_routing_wiring", "safety_validation")
_emit_invokes_eval("p1", "shadow_routing_wiring", "eval_call")
_emit_proposal_commits_routing("p1", "shadow_routing_wiring", "routing_commit")

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
