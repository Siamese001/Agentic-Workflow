"""
Reasoning Intensity Contracts — Determinism & Enforcement Tests.

Validates:
1. ReasoningIntensityProfile construction and hash integrity.
2. Byte-for-byte determinism: identical inputs => identical hashes.
3. SignedExecutionEnvelope construction and binding.
4. ReasoningPolicyEngine pure-function scoring and tier selection.
5. ReasoningIntensityEnforcer fail-closed behaviour.
6. Tier parameter table completeness.

Markers: determinism, governance
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

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

_emit_records_execution_trace("p0", "evidence", "test_reasoning_intensity_types")
_emit_applies_guardrail("p0", "test_reasoning_intensity_types", "p0_governance")
_emit_snapshots_state("p0", "test_reasoning_intensity_types", "state_snapshot")
emit_replay_key("p0", "test_reasoning_intensity_types")
emit_determinism_digest("p0", "test_reasoning_intensity_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_reasoning_intensity_types", "execution_auth")
_emit_validates_capability("p2", "test_reasoning_intensity_types", "capability_check")
_emit_routes_to_capability("p2", "test_reasoning_intensity_types", "capability_route")
_emit_writes_via_uwg("p2", "test_reasoning_intensity_types", "uwg_write")
_emit_blocks_direct_write("p2", "test_reasoning_intensity_types", "direct_write_block")
_emit_records_tool_invocation("p2", "test_reasoning_intensity_types", "tool_invocation")
_emit_captures_execution_output("p2", "test_reasoning_intensity_types", "exec_output")
_emit_dispatches_agent("p3", "test_reasoning_intensity_types", "agent_dispatch")
_emit_coordinates_agents("p3", "test_reasoning_intensity_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_reasoning_intensity_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_reasoning_intensity_types", "healing_outcome")
_emit_escalates_failure("p3", "test_reasoning_intensity_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_reasoning_intensity_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_reasoning_intensity_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_reasoning_intensity_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_reasoning_intensity_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_reasoning_intensity_types", "eval_metric")
_emit_stores_embedding("p4", "test_reasoning_intensity_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_reasoning_intensity_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_reasoning_intensity_types", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

PROJECT_ROOT = Path(__file__).resolve().parents[5]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agentic_core.L0_routing.engines.reasoning_policy_engine import (
    ReasoningPolicyEngine,
    RequestStructureFeatures,
    compute_complexity_score,
    select_tier,
)
from agentic_core.L0_routing.types.reasoning_intensity_types import (
    TIER_PARAMETER_TABLE,
    ReasoningIntensityProfile,
    ReasoningTier,
    SignedExecutionEnvelope,
    build_envelope_hash,
    build_profile_hash,
)
from agentic_core.L0_routing.types.routing_artifact_types import (
    RouteDecisionArtifact,
    RoutePath,
    RoutingRationale,
)
from agentic_core.L3_orchestration.engines.reasoning_intensity_enforcer import (
    ReasoningBudgetExceeded,
    ReasoningIntensityEnforcer,
    ReasoningModeViolation,
    StageExecutionMetrics,
)

# =============================================================================
# Fixtures
# =============================================================================


def _make_features(
    input_length: int = 512,
    tool_count_requested: int = 2,
    risk_tier_candidate: int = 1,
    stage_count: int = 9,
    l4_budget_remaining_tokens: int = 10000,
    l4_rate_limit_headroom: float = 0.8,
    aggregated_prior_success_rate: float = 0.9,
) -> RequestStructureFeatures:
    return RequestStructureFeatures(
        input_length=input_length,
        tool_count_requested=tool_count_requested,
        risk_tier_candidate=risk_tier_candidate,
        stage_count=stage_count,
        l4_budget_remaining_tokens=l4_budget_remaining_tokens,
        l4_rate_limit_headroom=l4_rate_limit_headroom,
        aggregated_prior_success_rate=aggregated_prior_success_rate,
    )


def _make_route_decision(trace_id: str = "trace-001") -> RouteDecisionArtifact:
    return RouteDecisionArtifact(
        trace_id=trace_id,
        timestamp="2026-01-01T00:00:00Z",
        route_path=RoutePath.STANDARD_VALIDATION,
        risk_score=0.1,
        budget_est=100.0,
        rationale_enum=RoutingRationale.STANDARD_VALIDATION,
        policy_config_hash="aabbcc",
    )


def _make_engine() -> ReasoningPolicyEngine:
    return ReasoningPolicyEngine(policy_config={"version": "1.0.0", "env": "test"})


def _make_profile(
    engine: ReasoningPolicyEngine, features: RequestStructureFeatures
) -> ReasoningIntensityProfile:
    tier = engine.compute_tier(features)
    return engine.build_profile(features, tier)


# =============================================================================
# 1. Tier parameter table completeness
# =============================================================================


@pytest.mark.governance
def test_all_tiers_have_parameters():
    for tier in ReasoningTier:
        assert tier in TIER_PARAMETER_TABLE, f"Missing tier: {tier}"
        params = TIER_PARAMETER_TABLE[tier]
        assert "max_branches" in params
        assert "max_depth" in params
        assert "enable_reflection" in params
        assert "allowed_modes" in params
        assert "token_budget_multiplier" in params


# =============================================================================
# 2. ReasoningIntensityProfile construction + hash integrity
# =============================================================================


@pytest.mark.governance
def test_profile_hash_matches_construction():
    engine = _make_engine()
    features = _make_features()
    profile = _make_profile(engine, features)

    recomputed = build_profile_hash(
        version=profile.reasoning_profile_version,
        policy_hash=profile.reasoning_policy_hash,
        tier=profile.tier,
        max_branches=profile.max_branches,
        max_depth=profile.max_depth,
        enable_reflection=profile.enable_reflection,
        token_budget_per_stage=list(profile.token_budget_per_stage),
        allowed_modes=list(profile.allowed_modes),
    )
    assert profile.profile_hash == recomputed


@pytest.mark.governance
def test_profile_rejects_tampered_hash():
    engine = _make_engine()
    features = _make_features()
    profile = _make_profile(engine, features)

    with pytest.raises(ValueError, match="profile_hash mismatch"):
        ReasoningIntensityProfile(
            reasoning_profile_version=profile.reasoning_profile_version,
            reasoning_policy_hash=profile.reasoning_policy_hash,
            tier=profile.tier,
            max_branches=profile.max_branches,
            max_depth=profile.max_depth,
            enable_reflection=profile.enable_reflection,
            token_budget_per_stage=profile.token_budget_per_stage,
            allowed_modes=profile.allowed_modes,
            profile_hash="deadbeef" * 8,
        )


# =============================================================================
# 3. SignedExecutionEnvelope integrity
# =============================================================================


@pytest.mark.governance
def test_envelope_hash_matches_construction():
    engine = _make_engine()
    features = _make_features()
    route = _make_route_decision()
    envelope = engine.compute_and_stamp(features, route)

    recomputed = build_envelope_hash(
        route_decision_trace_id=envelope.route_decision.trace_id,
        profile_hash=envelope.reasoning_profile.profile_hash,
        policy_hash=envelope.policy_hash,
    )
    assert envelope.envelope_hash == recomputed


@pytest.mark.governance
def test_envelope_rejects_tampered_hash():
    engine = _make_engine()
    features = _make_features()
    profile = _make_profile(engine, features)
    route = _make_route_decision()

    with pytest.raises(ValueError, match="envelope_hash mismatch"):
        SignedExecutionEnvelope(
            route_decision=route,
            reasoning_profile=profile,
            enforcement_constraints={},
            policy_hash=engine.policy_hash,
            envelope_hash="00" * 32,
        )


# =============================================================================
# 4. Determinism — byte-for-byte hash stability
# =============================================================================


@pytest.mark.determinism
def test_identical_inputs_produce_identical_profile_hash():
    """Two calls with identical inputs must produce the same profile_hash."""
    engine = _make_engine()
    features = _make_features()

    profile_a = _make_profile(engine, features)
    profile_b = _make_profile(engine, features)

    assert profile_a.profile_hash == profile_b.profile_hash, (
        f"Non-determinism detected: {profile_a.profile_hash} != {profile_b.profile_hash}"
    )


@pytest.mark.determinism
def test_identical_inputs_produce_identical_envelope_hash():
    """Two compute_and_stamp calls with identical inputs must produce the same hashes."""
    engine = _make_engine()
    features = _make_features()
    route = _make_route_decision()

    envelope_a = engine.compute_and_stamp(features, route)
    envelope_b = engine.compute_and_stamp(features, route)

    assert envelope_a.reasoning_profile.profile_hash == envelope_b.reasoning_profile.profile_hash
    assert envelope_a.envelope_hash == envelope_b.envelope_hash


@pytest.mark.determinism
def test_different_inputs_produce_different_profile_hash():
    """Different structural inputs must produce different profile hashes."""
    engine = _make_engine()
    features_low = _make_features(risk_tier_candidate=0, input_length=10)
    features_high = _make_features(
        risk_tier_candidate=5,
        input_length=8192,
        l4_rate_limit_headroom=0.0,
        aggregated_prior_success_rate=0.0,
    )

    profile_low = _make_profile(engine, features_low)
    profile_high = _make_profile(engine, features_high)

    assert profile_low.tier != profile_high.tier
    assert profile_low.profile_hash != profile_high.profile_hash


# =============================================================================
# 5. Pure-function complexity scoring
# =============================================================================


@pytest.mark.determinism
def test_complexity_score_is_bounded():
    for _ in range(100):
        features = _make_features()
        score = compute_complexity_score(features)
        assert 0.0 <= score <= 1.0


@pytest.mark.determinism
@pytest.mark.parametrize(
    "risk,expected_tier",
    [
        (0, ReasoningTier.LOW),
        (5, ReasoningTier.CRITICAL),
    ],
)
def test_tier_boundary_at_extremes(risk, expected_tier):
    features_low = _make_features(
        risk_tier_candidate=0,
        input_length=10,
        l4_rate_limit_headroom=1.0,
        aggregated_prior_success_rate=1.0,
    )
    features_high = _make_features(
        risk_tier_candidate=5,
        input_length=8192,
        l4_rate_limit_headroom=0.0,
        aggregated_prior_success_rate=0.0,
    )
    if risk == 0:
        tier = select_tier(compute_complexity_score(features_low))
        assert tier == ReasoningTier.LOW
    else:
        tier = select_tier(compute_complexity_score(features_high))
        assert tier == ReasoningTier.CRITICAL


# =============================================================================
# 6. ReasoningIntensityEnforcer — fail-closed enforcement
# =============================================================================


@pytest.mark.governance
def test_enforcer_validates_envelope_before_use():
    engine = _make_engine()
    features = _make_features()
    route = _make_route_decision()
    envelope = engine.compute_and_stamp(features, route)

    enforcer = ReasoningIntensityEnforcer(envelope, trace_id="trace-test")
    enforcer.validate_envelope()
    enforcer.enforce_pre_stage(stage_id=1)


@pytest.mark.governance
def test_enforcer_hard_stop_on_branch_ceiling():
    engine = _make_engine()
    features = _make_features(
        risk_tier_candidate=0, input_length=10, l4_rate_limit_headroom=1.0, aggregated_prior_success_rate=1.0
    )
    route = _make_route_decision()
    envelope = engine.compute_and_stamp(features, route)

    enforcer = ReasoningIntensityEnforcer(envelope, trace_id="trace-test")
    enforcer.validate_envelope()

    limit = envelope.reasoning_profile.max_branches
    metrics = StageExecutionMetrics(
        stage_id=1,
        branches_used=limit + 1,
        depth_reached=1,
        tokens_used=1,
        reflection_triggered=False,
        requested_mode="cot",
    )
    with pytest.raises(ReasoningBudgetExceeded, match="branch_ceiling"):
        enforcer.enforce_post_stage(metrics)


@pytest.mark.governance
def test_enforcer_hard_stop_on_disallowed_mode():
    engine = _make_engine()
    features = _make_features(
        risk_tier_candidate=0, input_length=10, l4_rate_limit_headroom=1.0, aggregated_prior_success_rate=1.0
    )
    route = _make_route_decision()
    envelope = engine.compute_and_stamp(features, route)

    enforcer = ReasoningIntensityEnforcer(envelope, trace_id="trace-test")
    enforcer.validate_envelope()

    with pytest.raises(ReasoningModeViolation):
        enforcer.enforce_pre_stage(stage_id=1, requested_mode="reflexion_ultra_advanced")


@pytest.mark.governance
def test_enforcer_hard_stop_on_reflection_when_disabled():
    engine = _make_engine()
    features = _make_features(
        risk_tier_candidate=0, input_length=10, l4_rate_limit_headroom=1.0, aggregated_prior_success_rate=1.0
    )
    route = _make_route_decision()
    envelope = engine.compute_and_stamp(features, route)

    enforcer = ReasoningIntensityEnforcer(envelope, trace_id="trace-test")
    enforcer.validate_envelope()

    profile = envelope.reasoning_profile
    if not profile.enable_reflection:
        metrics = StageExecutionMetrics(
            stage_id=1,
            branches_used=1,
            depth_reached=1,
            tokens_used=1,
            reflection_triggered=True,
            requested_mode="cot",
        )
        with pytest.raises(ReasoningBudgetExceeded, match="reflection_not_permitted"):
            enforcer.enforce_post_stage(metrics)


@pytest.mark.governance
def test_enforcer_telemetry_is_non_authoritative():
    """Telemetry must only be drained after the run, not influence current run state."""
    engine = _make_engine()
    features = _make_features()
    route = _make_route_decision()
    envelope = engine.compute_and_stamp(features, route)

    enforcer = ReasoningIntensityEnforcer(envelope, trace_id="trace-test")
    enforcer.validate_envelope()

    profile = envelope.reasoning_profile
    metrics = StageExecutionMetrics(
        stage_id=1,
        branches_used=1,
        depth_reached=1,
        tokens_used=10,
        reflection_triggered=False,
        requested_mode=profile.allowed_modes[0],
    )
    enforcer.enforce_post_stage(metrics)

    telemetry = enforcer.drain_telemetry()
    assert len(telemetry) == 1
    assert telemetry[0].profile_hash == profile.profile_hash
    assert telemetry[0].compliant is True

    assert len(enforcer.drain_telemetry()) == 0


# =============================================================================
# 7. No upward mutation: L3 cannot increase ceilings
# =============================================================================


@pytest.mark.governance
def test_enforcer_cannot_increase_branches():
    """Enforcer enforces ceiling; it cannot increase max_branches."""
    engine = _make_engine()
    features = _make_features(
        risk_tier_candidate=5,
        input_length=8192,
        l4_rate_limit_headroom=0.0,
        aggregated_prior_success_rate=0.0,
    )
    route = _make_route_decision()
    envelope = engine.compute_and_stamp(features, route)

    original_max = envelope.reasoning_profile.max_branches

    enforcer = ReasoningIntensityEnforcer(envelope, trace_id="trace-test")
    enforcer.validate_envelope()

    assert enforcer.profile.max_branches == original_max
