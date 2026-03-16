"""Tests for healing_tier_router meta-learning integration (Phase 1)."""

from __future__ import annotations

from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
from agentic_core.L2_execution.healers.healing_tier_router import (
    compute_heal_confidence,
    get_historical_success_rate,
    route_healing_tier,
)
from agentic_core.L2_execution.healers.healing_tier_types import (
    HealingInput,
    HealingTier,
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
    _emit_reads_policy_state,  # noqa: E402
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

_emit_authorize_and_execute("p2", "test_healing_tier_router_meta_integration", "execution_auth")
_emit_validates_capability("p2", "test_healing_tier_router_meta_integration", "capability_check")
_emit_routes_to_capability("p2", "test_healing_tier_router_meta_integration", "capability_route")
_emit_writes_via_uwg("p2", "test_healing_tier_router_meta_integration", "uwg_write")
_emit_blocks_direct_write("p2", "test_healing_tier_router_meta_integration", "direct_write_block")
_emit_records_tool_invocation("p2", "test_healing_tier_router_meta_integration", "tool_invocation")
_emit_captures_execution_output("p2", "test_healing_tier_router_meta_integration", "exec_output")
_emit_dispatches_agent("p3", "test_healing_tier_router_meta_integration", "agent_dispatch")
_emit_coordinates_agents("p3", "test_healing_tier_router_meta_integration", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_healing_tier_router_meta_integration", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_healing_tier_router_meta_integration", "healing_outcome")
_emit_escalates_failure("p3", "test_healing_tier_router_meta_integration", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_healing_tier_router_meta_integration", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_healing_tier_router_meta_integration", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_healing_tier_router_meta_integration", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_healing_tier_router_meta_integration", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_healing_tier_router_meta_integration", "eval_metric")
_emit_stores_embedding("p4", "test_healing_tier_router_meta_integration", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_healing_tier_router_meta_integration", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_healing_tier_router_meta_integration", "exec_snapshot_link")
from system_learning.ports.meta_prior_provider import (
    NeutralMetaPriorProvider,
)

_emit_records_execution_trace("p0", "evidence", "test_healing_tier_router_meta_integration")
_emit_applies_guardrail("p0", "test_healing_tier_router_meta_integration", "p0_governance")
_emit_reads_policy_state("p0", "test_healing_tier_router_meta_integration", "policy_binding")
_emit_snapshots_state("p0", "test_healing_tier_router_meta_integration", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("test_healing_tier_router_meta_integration", "p4obs", "metric_1")
_emit_emits_metric_event("test_healing_tier_router_meta_integration", "p4obs", "metric_2")
_emit_emits_metric_event("test_healing_tier_router_meta_integration", "p4obs", "metric_3")
_emit_emits_metric_event("test_healing_tier_router_meta_integration", "p4obs", "metric_4")
_emit_emits_metric_event("test_healing_tier_router_meta_integration", "p4obs", "metric_5")
_emit_emits_metric_event("test_healing_tier_router_meta_integration", "p4obs", "metric_6")
_emit_records_incident_event("test_healing_tier_router_meta_integration", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_healing_tier_router_meta_integration", "p4obs", "anomaly")
_emit_writes_observability_log("test_healing_tier_router_meta_integration", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_healing_tier_router_meta_integration", "p4obs", "mon_state")
_emit_triggers_alert("test_healing_tier_router_meta_integration", "p4obs", "alert")
_emit_links_incident_trace("test_healing_tier_router_meta_integration", "p4obs", "trace_link")
_emit_captures_pattern("test_healing_tier_router_meta_integration", "p3lm", "pattern")
_emit_records_learning_event("test_healing_tier_router_meta_integration", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_healing_tier_router_meta_integration", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_healing_tier_router_meta_integration", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_healing_tier_router_meta_integration", "p3lm", "routing")
_emit_improves_agent_policy("test_healing_tier_router_meta_integration", "p3lm", "policy")
_emit_stores_learning_state("test_healing_tier_router_meta_integration", "p3lm", "state")
_emit_records_execution_trace("test_healing_tier_router_meta_integration", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_healing_tier_router_meta_integration", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_healing_tier_router_meta_integration", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_healing_tier_router_meta_integration", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_healing_tier_router_meta_integration", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_healing_tier_router_meta_integration", "env_read", "p2_env_1")
_emit_reads_environ("test_healing_tier_router_meta_integration", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_healing_tier_router_meta_integration", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_healing_tier_router_meta_integration", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_healing_tier_router_meta_integration", "context_pull")
_emit_pulls_context("p1", "test_healing_tier_router_meta_integration", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_healing_tier_router_meta_integration", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_healing_tier_router_meta_integration", "uwg_term_2")
_emit_writes_through("p1", "test_healing_tier_router_meta_integration", "write_through")
_emit_writes_through("p1", "test_healing_tier_router_meta_integration", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_healing_tier_router_meta_integration", "safety_validation")
_emit_invokes_eval("p1", "test_healing_tier_router_meta_integration", "eval_call")
_emit_proposal_commits_routing("p1", "test_healing_tier_router_meta_integration", "routing_commit")
emit_replay_key("p0", "test_healing_tier_router_meta_integration")
emit_determinism_digest("p0", "test_healing_tier_router_meta_integration")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class MockMetaPriorProvider:
    """Mock provider with configurable priors."""

    def __init__(self, priors: dict[str, float]) -> None:
        self._priors = priors

    def get_prior(self, error_signature: str) -> float:
        return self._priors.get(error_signature, 0.50)


def test_get_historical_success_rate_with_provider() -> None:
    """get_historical_success_rate uses MetaPriorProvider when available."""
    provider = MockMetaPriorProvider({"sig1": 0.75, "sig2": 0.25})

    assert get_historical_success_rate("sig1", meta_prior_provider=provider) == 0.75
    assert get_historical_success_rate("sig2", meta_prior_provider=provider) == 0.25
    assert get_historical_success_rate("unknown", meta_prior_provider=provider) == 0.50


def test_get_historical_success_rate_fallback_to_stub() -> None:
    """Falls back to module stub when no provider."""
    # Set a stub value
    from agentic_core.L2_execution.healers.healing_tier_router import set_historical_success_rate

    set_historical_success_rate("stub_sig", 0.80)

    assert get_historical_success_rate("stub_sig") == 0.80
    assert get_historical_success_rate("truly_novel_sig") == 0.50

    # Clean up
    from agentic_core.L2_execution.healers.healing_tier_router import clear_historical_success_rates

    clear_historical_success_rates()


def test_compute_heal_confidence_uses_provider() -> None:
    """compute_heal_confidence incorporates MetaPriorProvider data."""
    provider = MockMetaPriorProvider({"high_success_sig": 0.90})

    healing_input = HealingInput(
        error_signature="high_success_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        retry_count=0,
        trace_id="test-trace",
    )

    confidence, reason_codes = compute_heal_confidence(
        healing_input,
        meta_prior_provider=provider,
    )

    assert 0.0 <= confidence <= 1.0
    assert any("historical_success_rate=0.9000" in code for code in reason_codes)


def test_route_healing_tier_uses_provider() -> None:
    """route_healing_tier passes MetaPriorProvider through."""
    provider = MockMetaPriorProvider({"high_success_sig": 0.90})
    config = HealingTierConfig()

    healing_input = HealingInput(
        error_signature="high_success_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        retry_count=0,
        trace_id="test-trace",
    )

    decision = route_healing_tier(
        healing_input,
        config,
        meta_prior_provider=provider,
    )

    assert decision.tier in HealingTier
    assert 0.0 <= decision.heal_confidence <= 1.0
    assert any("historical_success_rate=0.9000" in code for code in decision.reason_codes)


def test_neutral_provider_default() -> None:
    """NeutralMetaPriorProvider returns 0.50 for all signatures."""
    provider = NeutralMetaPriorProvider()

    assert provider.get_prior("any_sig") == 0.50
    assert provider.get_prior("another_sig") == 0.50


def test_backward_compatibility_without_provider() -> None:
    """Router works without MetaPriorProvider (backward compatibility)."""
    config = HealingTierConfig()

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        retry_count=0,
        trace_id="test-trace",
    )

    # Should not raise exception
    decision = route_healing_tier(healing_input, config)
    assert decision.tier in HealingTier
