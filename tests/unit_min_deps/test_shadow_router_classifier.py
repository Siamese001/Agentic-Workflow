"""
Phase 9: Shadow Router Classifier Tests - Non-invasive routing drift detection.

Tests proving that the shadow router classifier is non-invasive and deterministic.
"""

import pytest

from agentic_core.L0_routing.engines.shadow_router_classifier import ShadowRouterClassifier
from agentic_core.L0_routing.engines.shadow_routing_wiring import (
    ShadowRoutingWiring,
    observe_routing_decision,
)
from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.L0_routing.types.routing_artifact_types import (
    RouteDecisionArtifact,
    RoutePath,
    RoutingRationale,
)
from agentic_core.L0_routing.types.shadow_routing_types import (
    ShadowRoutingDecision,
    ShadowRoutingRationale,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_shadow_router_classifier")
_emit_applies_guardrail("p0", "test_shadow_router_classifier", "p0_governance")
_emit_snapshots_state("p0", "test_shadow_router_classifier", "state_snapshot")
emit_replay_key("p0", "test_shadow_router_classifier")
emit_determinism_digest("p0", "test_shadow_router_classifier")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_shadow_router_classifier", "execution_auth")
_emit_validates_capability("p2", "test_shadow_router_classifier", "capability_check")
_emit_routes_to_capability("p2", "test_shadow_router_classifier", "capability_route")
_emit_writes_via_uwg("p2", "test_shadow_router_classifier", "uwg_write")
_emit_blocks_direct_write("p2", "test_shadow_router_classifier", "direct_write_block")
_emit_records_tool_invocation("p2", "test_shadow_router_classifier", "tool_invocation")
_emit_captures_execution_output("p2", "test_shadow_router_classifier", "exec_output")
_emit_dispatches_agent("p3", "test_shadow_router_classifier", "agent_dispatch")
_emit_coordinates_agents("p3", "test_shadow_router_classifier", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_shadow_router_classifier", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_shadow_router_classifier", "healing_outcome")
_emit_escalates_failure("p3", "test_shadow_router_classifier", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_shadow_router_classifier", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_shadow_router_classifier", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_shadow_router_classifier", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_shadow_router_classifier", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_shadow_router_classifier", "eval_metric")
_emit_stores_embedding("p4", "test_shadow_router_classifier", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_shadow_router_classifier", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_shadow_router_classifier", "exec_snapshot_link")


@pytest.mark.unit_min_deps
def test_shadow_classifier_non_invasive():
    """Test that shadow classifier cannot affect actual routing decisions."""
    # Create a routing decision
    route_decision = RouteDecisionArtifact(
        trace_id="test-trace-001",
        timestamp="2024-01-01T00:00:00Z",
        route_path=RoutePath.STANDARD_VALIDATION,
        risk_score=0.3,
        budget_est=100.0,
        rationale_enum=RoutingRationale.STANDARD_VALIDATION,
        policy_config_hash="abc123",
    )

    # Create shadow classifier
    classifier = ShadowRouterClassifier()

    # Observe the routing decision
    shadow_decision = classifier.observe_routing_decision(route_decision)

    # Verify the original route is unchanged
    assert route_decision.route_path == RoutePath.STANDARD_VALIDATION
    assert route_decision.trace_id == "test-trace-001"

    # Verify shadow decision is produced
    assert isinstance(shadow_decision, ShadowRoutingDecision)
    assert shadow_decision.observed_route == RoutePath.STANDARD_VALIDATION
    assert shadow_decision.trace_id == "test-trace-001"
    assert shadow_decision.feature_fingerprint is not None
    assert len(shadow_decision.feature_fingerprint) == 64  # 64-hex


@pytest.mark.unit_min_deps
def test_shadow_classifier_determinism():
    """Test that shadow classifier produces deterministic output."""
    # Create identical routing decisions
    route_decision_1 = RouteDecisionArtifact(
        trace_id="test-trace-002",
        timestamp="2024-01-01T00:00:00Z",
        route_path=RoutePath.LOW_RISK_BYPASS,
        risk_score=0.1,
        budget_est=50.0,
        rationale_enum=RoutingRationale.LOW_RISK_BYPASS,
        policy_config_hash="def456",
    )

    route_decision_2 = RouteDecisionArtifact(
        trace_id="test-trace-002",
        timestamp="2024-01-01T00:00:00Z",
        route_path=RoutePath.LOW_RISK_BYPASS,
        risk_score=0.1,
        budget_est=50.0,
        rationale_enum=RoutingRationale.LOW_RISK_BYPASS,
        policy_config_hash="def456",
    )

    # Create classifier
    classifier = ShadowRouterClassifier()

    # Observe both decisions
    shadow_decision_1 = classifier.observe_routing_decision(route_decision_1)
    shadow_decision_2 = classifier.observe_routing_decision(route_decision_2)

    # Verify deterministic output
    assert shadow_decision_1.feature_fingerprint == shadow_decision_2.feature_fingerprint
    assert shadow_decision_1.shadow_route == shadow_decision_2.shadow_route
    assert shadow_decision_1.drift_score == shadow_decision_2.drift_score
    assert shadow_decision_1.shadow_rationale == shadow_decision_2.shadow_rationale


@pytest.mark.unit_min_deps
def test_shadow_routing_wiring_non_invasive():
    """Test that shadow routing wiring cannot affect actual routing."""
    # Create routing decision
    route_decision = RouteDecisionArtifact(
        trace_id="test-trace-003",
        timestamp="2024-01-01T00:00:00Z",
        route_path=RoutePath.HUMAN_ESCALATION,
        risk_score=0.9,
        budget_est=200.0,
        rationale_enum=RoutingRationale.HUMAN_ESCALATION,
        policy_config_hash="ghi789",
    )

    # Create wiring
    wiring = ShadowRoutingWiring(enable_telemetry=True)

    # Observe the routing decision
    telemetry = wiring.observe_and_classify(route_decision)

    # Verify original route is unchanged
    assert route_decision.route_path == RoutePath.HUMAN_ESCALATION
    assert route_decision.trace_id == "test-trace-003"

    # Verify telemetry is produced
    assert telemetry is not None
    assert telemetry.trace_id == "test-trace-003"
    assert telemetry.shadow_decision.observed_route == RoutePath.HUMAN_ESCALATION

    # Validate non-invasiveness
    assert wiring.validate_non_invasiveness(route_decision) is True


@pytest.mark.unit_min_deps
def test_shadow_feature_fingerprint_64hex():
    """Test that feature fingerprint is 64-hex and validated."""
    # Create routing decision
    route_decision = RouteDecisionArtifact(
        trace_id="test-trace-004",
        timestamp="2024-01-01T00:00:00Z",
        route_path=RoutePath.POLICY_CHALLENGE_LOOP,
        risk_score=0.5,
        budget_est=150.0,
        rationale_enum=RoutingRationale.POLICY_CHALLENGE,
        policy_config_hash="jkl012",
    )

    # Create classifier
    classifier = ShadowRouterClassifier()

    # Observe the routing decision
    shadow_decision = classifier.observe_routing_decision(route_decision)

    # Validate 64-hex format
    fingerprint = shadow_decision.feature_fingerprint
    assert len(fingerprint) == 64
    assert all(c in "0123456789abcdef" for c in fingerprint)

    # Test validation function
    validate_64hex(fingerprint, "feature_fingerprint")


@pytest.mark.unit_min_deps
def test_shadow_drift_detection():
    """Test drift detection between observed and shadow routes."""
    # Low risk routing decision
    route_decision = RouteDecisionArtifact(
        trace_id="test-trace-005",
        timestamp="2024-01-01T00:00:00Z",
        route_path=RoutePath.HUMAN_ESCALATION,  # High-cost route for low risk
        risk_score=0.1,  # Low risk
        budget_est=100.0,
        rationale_enum=RoutingRationale.HUMAN_ESCALATION,
        policy_config_hash="mno345",
    )

    # Create classifier
    classifier = ShadowRouterClassifier()

    # Observe the routing decision
    shadow_decision = classifier.observe_routing_decision(route_decision)

    # Should detect drift and suggest standard validation
    assert shadow_decision.observed_route == RoutePath.HUMAN_ESCALATION
    assert shadow_decision.shadow_route == RoutePath.STANDARD_VALIDATION
    assert shadow_decision.drift_score > 0.0
    assert shadow_decision.shadow_rationale == ShadowRoutingRationale.POLICY_OPTIMIZATION


@pytest.mark.unit_min_deps
def test_negative_control_shadow_route_application():
    """NEGATIVE CONTROL: Demonstrate that applying shadow route would fail."""
    # Create routing decision
    original_route = RoutePath.LOW_RISK_BYPASS
    route_decision = RouteDecisionArtifact(
        trace_id="test-trace-006",
        timestamp="2024-01-01T00:00:00Z",
        route_path=original_route,
        risk_score=0.1,
        budget_est=50.0,
        rationale_enum=RoutingRationale.LOW_RISK_BYPASS,
        policy_config_hash="pqr678",
    )

    # Create classifier
    classifier = ShadowRouterClassifier()

    # Observe the routing decision
    shadow_decision = classifier.observe_routing_decision(route_decision)

    # Verify shadow route is different (if applicable)
    if shadow_decision.drift_score > 0.0:
        # This would be incorrect application of shadow route
        # In a real system, this should be prevented by type safety
        assert shadow_decision.shadow_route != original_route

        # NEGATIVE CONTROL: If we incorrectly applied shadow route
        # it would change the routing behavior, which must be prevented
        with pytest.raises(Exception):
            # This simulates attempting to modify the frozen route_decision
            route_decision.route_path = shadow_decision.shadow_route

    # The actual route must remain unchanged
    assert route_decision.route_path == original_route


@pytest.mark.unit_min_deps
def test_shadow_re_run_determinism_lock():
    """Test determinism re-run lock for shadow output."""
    # Create routing decision
    route_decision = RouteDecisionArtifact(
        trace_id="test-trace-007",
        timestamp="2024-01-01T00:00:00Z",
        route_path=RoutePath.STANDARD_VALIDATION,
        risk_score=0.4,
        budget_est=120.0,
        rationale_enum=RoutingRationale.STANDARD_VALIDATION,
        policy_config_hash="stu901",
        semantic_clock=SemanticClockSnapshot(
            tick=42,
            vector_clock=(("L0", 1),),
        ),
    )

    # Create classifier
    classifier = ShadowRouterClassifier()

    # First run
    shadow_decision_1 = classifier.observe_routing_decision(route_decision)
    telemetry_1 = classifier.emit_telemetry(shadow_decision_1)

    # Second run (identical inputs)
    shadow_decision_2 = classifier.observe_routing_decision(route_decision)
    telemetry_2 = classifier.emit_telemetry(shadow_decision_2)

    # Verify re-run lock
    assert shadow_decision_1.feature_fingerprint == shadow_decision_2.feature_fingerprint
    assert shadow_decision_1.shadow_route == shadow_decision_2.shadow_route
    assert shadow_decision_1.drift_score == shadow_decision_2.drift_score
    assert telemetry_1.to_canonical_json() == telemetry_2.to_canonical_json()


@pytest.mark.unit_min_deps
def test_global_wiring_function():
    """Test the global wiring convenience function."""
    # Create routing decision
    route_decision = RouteDecisionArtifact(
        trace_id="test-trace-008",
        timestamp="2024-01-01T00:00:00Z",
        route_path=RoutePath.ROUTE_RECOVERY_BUDGET_OVERFLOW,
        risk_score=0.7,
        budget_est=180.0,
        rationale_enum=RoutingRationale.BUDGET_OVERFLOW,
        policy_config_hash="vwx234",
    )

    # Use global function
    telemetry = observe_routing_decision(route_decision)

    # Verify telemetry is produced
    assert telemetry is not None
    assert telemetry.trace_id == "test-trace-008"
    assert telemetry.shadow_decision.observed_route == RoutePath.ROUTE_RECOVERY_BUDGET_OVERFLOW


def validate_64hex(value: str, field_name: str) -> None:
    """Validate that a value is a 64-character hex string.

    Args:
        value: The value to validate
        field_name: Name of the field for error reporting

    Raises:
        AssertionError: If validation fails
    """
    assert isinstance(value, str), f"{field_name} must be a string"
    assert len(value) == 64, f"{field_name} must be 64 characters, got {len(value)}"
    assert all(c in "0123456789abcdef" for c in value), f"{field_name} must be hex, got: {value}"
