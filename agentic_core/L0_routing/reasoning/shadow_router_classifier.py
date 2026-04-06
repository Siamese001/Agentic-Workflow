"""
Phase 9: Shadow Router Classifier - Non-invasive routing drift detection.

A shadow classifier that observes L0 routing decisions and produces
shadow routing suggestions with drift scores, without affecting live traffic.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any

from agentic_core.L0_routing.types.routing_artifact_types import (
    RouteDecisionArtifact,
    RoutePath,
)
from agentic_core.L0_routing.types.shadow_routing_types import (
    ShadowRoutingDecision,
    ShadowRoutingRationale,
    ShadowRoutingTelemetry,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

def _get_canonical_json():
    from agentic_core.L2_execution.types.vllm_infrastructure_fingerprint_types import canonical_json as _cj

    return _cj


canonical_json = _get_canonical_json()

logger = logging.getLogger(__name__)


class ShadowRouterClassifier:
    """Non-invasive shadow router classifier for drift detection.

    This classifier observes routing decisions and produces shadow suggestions
    without affecting the actual routing. It's strictly read-only and
    emits telemetry to L6 and optionally stores to L4.
    """

    def __init__(
        self,
        model_version: str = "shadow-router-v1.0",
        ruleset_version: str = "phase9-initial",
    ):
        """Initialize shadow router classifier.

        Args:
            model_version: Version identifier for the shadow model
            ruleset_version: Version identifier for the ruleset
        """
        self.model_version = model_version
        self.ruleset_version = ruleset_version

    def compute_routing_features(
        self,
        route_decision: RouteDecisionArtifact,
        additional_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Compute deterministic features from routing decision.

        Args:
            route_decision: The actual routing decision made by L0
            additional_context: Optional additional context for feature computation

        Returns:
            Dictionary of deterministic routing features
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L0_ROUTING, "ShadowRouterClassifier.compute_routing_features"
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        features = {
            "trace_id": route_decision.trace_id,
            "observed_route": route_decision.route_path.value,
            "risk_score": route_decision.risk_score,
            "budget_est": route_decision.budget_est,
            "rationale": route_decision.rationale_enum.value,
            "policy_config_hash": route_decision.policy_config_hash,
        }

        # Add semantic clock if present
        if route_decision.semantic_clock is not None:
            features["semantic_clock"] = route_decision.semantic_clock.to_dict()

        # Add additional context if provided
        if additional_context:
            features["additional_context"] = additional_context

        return features

    def classify_shadow_route(
        self,
        features: dict[str, Any],
    ) -> tuple[RoutePath, ShadowRoutingRationale, float]:
        """Classify shadow route suggestion and compute drift score.

        This is a simple rule-based classifier for Phase 9. In production,
        this could be a machine learning model or more sophisticated rules.

        Args:
            features: Routing features computed from actual decision

        Returns:
            Tuple of (shadow_route, shadow_rationale, drift_score)
        """
        observed_route = RoutePath(features["observed_route"])
        risk_score = features["risk_score"]

        # Simple rule-based classification
        if risk_score < 0.2:
            # Low risk - suggest standard validation if not already chosen
            if observed_route != RoutePath.STANDARD_VALIDATION:
                return (
                    RoutePath.STANDARD_VALIDATION,
                    ShadowRoutingRationale.POLICY_OPTIMIZATION,
                    0.3,  # Moderate drift
                )
            else:
                return (
                    observed_route,
                    ShadowRoutingRationale.ALIGN_WITH_LIVE,
                    0.0,  # No drift
                )
        elif risk_score > 0.8:
            # High risk - suggest human escalation if not already chosen
            if observed_route != RoutePath.HUMAN_ESCALATION:
                return (
                    RoutePath.HUMAN_ESCALATION,
                    ShadowRoutingRationale.RISK_MITIGATION,
                    0.5,  # Higher drift
                )
            else:
                return (
                    observed_route,
                    ShadowRoutingRationale.ALIGN_WITH_LIVE,
                    0.0,  # No drift
                )
        else:
            # Medium risk - align with live routing
            return (
                observed_route,
                ShadowRoutingRationale.ALIGN_WITH_LIVE,
                0.0,  # No drift
            )

    def observe_routing_decision(
        self,
        route_decision: RouteDecisionArtifact,
        additional_context: dict[str, Any] | None = None,
        timestamp: str | None = None,
    ) -> ShadowRoutingDecision:
        """Observe a routing decision and produce shadow classification.

        This is the main entry point for shadow classification. It's called
        after the actual routing decision is made and cannot affect it.

        Args:
            route_decision: The actual routing decision made by L0
            additional_context: Optional additional context
            timestamp: Deterministic timestamp (defaults to route_decision.timestamp)

        Returns:
            Shadow routing decision with drift analysis
        """
        # Use deterministic timestamp
        if timestamp is None:
            timestamp = route_decision.timestamp

        # Compute features
        features = self.compute_routing_features(route_decision, additional_context)

        # Classify shadow route
        shadow_route, shadow_rationale, drift_score = self.classify_shadow_route(features)

        # Compute feature fingerprint
        feature_fingerprint = hashlib.sha256(canonical_json(features).encode("utf-8")).hexdigest()

        # Create shadow decision
        shadow_decision = ShadowRoutingDecision(
            trace_id=route_decision.trace_id,
            observed_route=route_decision.route_path,
            shadow_route=shadow_route,
            drift_score=drift_score,
            feature_fingerprint=feature_fingerprint,
            model_version=self.model_version,
            ruleset_version=self.ruleset_version,
            timestamp=timestamp,
            shadow_rationale=shadow_rationale,
            semantic_clock=route_decision.semantic_clock,
            feature_snapshot=features,  # For debugging, not used in hashing
        )

        logger.debug(
            f"Shadow classification for {route_decision.trace_id}: "
            f"observed={route_decision.route_path.value}, "
            f"shadow={shadow_route.value}, "
            f"drift={drift_score}"
        )

        return shadow_decision

    def emit_telemetry(
        self,
        shadow_decision: ShadowRoutingDecision,
        emitted_at: str | None = None,
    ) -> ShadowRoutingTelemetry:
        """Emit telemetry for shadow routing decision.

        Args:
            shadow_decision: The shadow routing decision
            emitted_at: Deterministic timestamp (defaults to shadow_decision.timestamp)

        Returns:
            Telemetry artifact for L6/L4 emission
        """
        if emitted_at is None:
            emitted_at = shadow_decision.timestamp

        telemetry = ShadowRoutingTelemetry(
            trace_id=shadow_decision.trace_id,
            shadow_decision=shadow_decision,
            emitted_at=emitted_at,
        )

        logger.debug(f"Emitted shadow telemetry for {shadow_decision.trace_id}")

        return telemetry
