"""Behavioral tests for L0RoutingConfidenceMonitor.

Covers:
- propose_routing_confidence_change returns None when p10 >= trigger
- propose_routing_confidence_change returns package when p10 < trigger
- Proposal surface_name is 'routing_min_confidence'
- new_value > old_value (threshold increases when confidence is low)
- Bounded: new_value <= MAX_CONFIDENCE (0.80)
- Bounded: new_value >= MIN_CONFIDENCE (0.10)
- Cooldown suppresses repeat proposals
- Sample-size suppresses proposals with insufficient data
- Empty confidence_values returns None
- Missing config key returns None
- RoutingConfidenceChangePackage content_hash is deterministic
- L0RoutingConfidenceProposerAdapter.propose() delegates correctly
"""

from __future__ import annotations

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
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
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_l0_routing_confidence_monitor")
# REMOVED: _emit_applies_guardrail("p0", "test_l0_routing_confidence_monitor", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_l0_routing_confidence_monitor", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_l0_routing_confidence_monitor")
# REMOVED: emit_determinism_digest("p0", "test_l0_routing_confidence_monitor")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_l0_routing_confidence_monitor", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_l0_routing_confidence_monitor", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_l0_routing_confidence_monitor", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_l0_routing_confidence_monitor", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_l0_routing_confidence_monitor", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_l0_routing_confidence_monitor", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_l0_routing_confidence_monitor", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_l0_routing_confidence_monitor", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_l0_routing_confidence_monitor", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_l0_routing_confidence_monitor", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_l0_routing_confidence_monitor", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_l0_routing_confidence_monitor", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_l0_routing_confidence_monitor", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_l0_routing_confidence_monitor", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_l0_routing_confidence_monitor", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_l0_routing_confidence_monitor", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_l0_routing_confidence_monitor", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_l0_routing_confidence_monitor", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_l0_routing_confidence_monitor", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_l0_routing_confidence_monitor", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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
    _emit_writes_through,  # noqa: E402
)
from system_learning.engines.l0_routing_confidence_monitor import (
    L0RoutingConfidenceProposerAdapter,
    RoutingConfidenceChangePackage,
    _compute_p10,
    propose_routing_confidence_change,
)
from system_learning.validators.dampening import CooldownPolicy, SampleSizePolicy

# REMOVED: _emit_emits_metric_event("test_l0_routing_confidence_monitor", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_l0_routing_confidence_monitor", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_l0_routing_confidence_monitor", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_l0_routing_confidence_monitor", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_l0_routing_confidence_monitor", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_l0_routing_confidence_monitor", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_l0_routing_confidence_monitor", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_l0_routing_confidence_monitor", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_l0_routing_confidence_monitor", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_l0_routing_confidence_monitor", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_l0_routing_confidence_monitor", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_l0_routing_confidence_monitor", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_l0_routing_confidence_monitor", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_l0_routing_confidence_monitor", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_l0_routing_confidence_monitor", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_l0_routing_confidence_monitor", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_l0_routing_confidence_monitor", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_l0_routing_confidence_monitor", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_l0_routing_confidence_monitor", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_l0_routing_confidence_monitor", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_l0_routing_confidence_monitor", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_l0_routing_confidence_monitor", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_l0_routing_confidence_monitor", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_l0_routing_confidence_monitor", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_l0_routing_confidence_monitor", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_l0_routing_confidence_monitor", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_l0_routing_confidence_monitor", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_l0_routing_confidence_monitor", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_l0_routing_confidence_monitor", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_l0_routing_confidence_monitor", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_l0_routing_confidence_monitor", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_l0_routing_confidence_monitor", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_l0_routing_confidence_monitor", "write_through")
# REMOVED: _emit_writes_through("p1", "test_l0_routing_confidence_monitor", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_l0_routing_confidence_monitor", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_l0_routing_confidence_monitor", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_l0_routing_confidence_monitor", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_l0_routing_confidence_monitor", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_l0_routing_confidence_monitor", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_l0_routing_confidence_monitor", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_l0_routing_confidence_monitor", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_l0_routing_confidence_monitor", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_l0_routing_confidence_monitor", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_l0_routing_confidence_monitor", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_l0_routing_confidence_monitor", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_l0_routing_confidence_monitor", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_l0_routing_confidence_monitor", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_l0_routing_confidence_monitor", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_l0_routing_confidence_monitor")
# REMOVED: _emit_gated_by_confidence("p1", "test_l0_routing_confidence_monitor", "confidence_gate")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ZERO_COOLDOWN = CooldownPolicy(min_seconds_between_updates=0)
_MIN_SAMPLE = SampleSizePolicy(min_observations=1)
_HIGH_SAMPLE = SampleSizePolicy(min_observations=10_000)
_HIGH_COOLDOWN = CooldownPolicy(min_seconds_between_updates=999_999)

_LOW_CONF = [0.10, 0.12, 0.11, 0.13, 0.09, 0.14, 0.10, 0.11, 0.12, 0.10]  # p10 ≈ 0.09
_HIGH_CONF = [0.80, 0.85, 0.90, 0.75, 0.88, 0.92, 0.78, 0.86, 0.91, 0.83]  # p10 > 0.30


def _propose(
    values=None,
    config=None,
    history=None,
    cooldown=None,
    sample=None,
    now_utc=10_000,
):
    return propose_routing_confidence_change(
        snapshot_id="test-snap",
        confidence_values=values if values is not None else _LOW_CONF,
        current_config=config if config is not None else {"routing_min_confidence": 0.20},
        now_utc=now_utc,
        history=history if history is not None else {"routing_min_confidence_n_obs": 50},
        cooldown_policy=cooldown if cooldown is not None else _ZERO_COOLDOWN,
        sample_policy=sample if sample is not None else _MIN_SAMPLE,
    )


# ---------------------------------------------------------------------------
# _compute_p10 unit tests
# ---------------------------------------------------------------------------


class TestComputeP10:
    def test_empty_list_returns_1(self):
        assert _compute_p10([]) == 1.0

    def test_single_value_returns_that_value(self):
        assert _compute_p10([0.5]) == 0.5

    def test_ten_equal_values(self):
        result = _compute_p10([0.5] * 10)
        assert abs(result - 0.5) < 1e-6

    def test_p10_below_median(self):
        values = list(range(1, 11))  # 1..10
        p10 = _compute_p10(values)
        assert p10 < 5.5  # must be below median

    def test_sorted_input_invariant(self):
        a = _compute_p10([3, 1, 2, 5, 4])
        b = _compute_p10([1, 2, 3, 4, 5])
        assert abs(a - b) < 1e-6


# ---------------------------------------------------------------------------
# propose_routing_confidence_change
# ---------------------------------------------------------------------------


class TestProposeReturnNone:
    def test_high_confidence_no_proposal(self):
        result = _propose(values=_HIGH_CONF)
        assert result is None

    def test_empty_values_no_proposal(self):
        result = _propose(values=[])
        assert result is None

    def test_missing_config_key_no_proposal(self):
        result = _propose(config={})
        assert result is None

    def test_cooldown_suppresses_proposal(self):
        history = {
            "routing_min_confidence_last_update": 9_999,  # 1s ago, cooldown=999_999
            "routing_min_confidence_n_obs": 50,
        }
        result = _propose(history=history, cooldown=_HIGH_COOLDOWN, now_utc=10_000)
        assert result is None

    def test_insufficient_sample_suppresses_proposal(self):
        result = _propose(sample=_HIGH_SAMPLE)
        assert result is None

    def test_no_change_when_already_at_max(self):
        result = _propose(config={"routing_min_confidence": 0.80})
        # 0.80 + 0.03 = 0.83 → capped to 0.80, so no change
        assert result is None


class TestProposeReturnsPackage:
    def test_returns_package_when_p10_below_trigger(self):
        result = _propose()
        assert result is not None

    def test_surface_name_correct(self):
        result = _propose()
        assert result.surface_name == "routing_min_confidence"

    def test_new_value_greater_than_old(self):
        result = _propose()
        assert result.new_value > result.old_value

    def test_new_value_bounded_by_max(self):
        result = _propose(config={"routing_min_confidence": 0.78})
        assert result.new_value <= 0.80

    def test_new_value_bounded_by_min(self):
        result = _propose(config={"routing_min_confidence": 0.10})
        assert result.new_value >= 0.10

    def test_snapshot_id_preserved(self):
        result = propose_routing_confidence_change(
            snapshot_id="custom-snap-abc",
            confidence_values=_LOW_CONF,
            current_config={"routing_min_confidence": 0.20},
            now_utc=10_000,
            history={"routing_min_confidence_n_obs": 50},
            cooldown_policy=_ZERO_COOLDOWN,
            sample_policy=_MIN_SAMPLE,
        )
        assert result is not None
        assert result.snapshot_id == "custom-snap-abc"

    def test_justification_non_empty(self):
        result = _propose()
        assert len(result.justification) > 0

    def test_delta_capped_at_max_delta(self):
        result = _propose(config={"routing_min_confidence": 0.20})
        assert result is not None
        delta = abs(result.new_value - result.old_value)
        assert delta <= 0.05  # _MAX_DELTA

    def test_value_rounded_to_4_places(self):
        result = _propose()
        assert round(result.new_value, 4) == result.new_value


# ---------------------------------------------------------------------------
# RoutingConfidenceChangePackage
# ---------------------------------------------------------------------------


class TestRoutingConfidenceChangePackage:
    def _make(self, **kwargs) -> RoutingConfidenceChangePackage:
        defaults = {
            "surface_name": "routing_min_confidence",
            "old_value": 0.20,
            "new_value": 0.23,
            "justification": "test",
            "snapshot_id": "snap-1",
        }
        defaults.update(kwargs)
        return RoutingConfidenceChangePackage(**defaults)

    def test_content_hash_is_64_chars(self):
        pkg = self._make()
        assert len(pkg.content_hash()) == 64

    def test_content_hash_deterministic(self):
        p1 = self._make()
        p2 = self._make()
        assert p1.content_hash() == p2.content_hash()

    def test_different_values_different_hash(self):
        p1 = self._make(new_value=0.23)
        p2 = self._make(new_value=0.24)
        assert p1.content_hash() != p2.content_hash()

    def test_frozen_immutable(self):
        pkg = self._make()
        with pytest.raises((AttributeError, TypeError)):
            pkg.new_value = 0.99  # type: ignore[misc]


# ---------------------------------------------------------------------------
# L0RoutingConfidenceProposerAdapter
# ---------------------------------------------------------------------------


class TestL0RoutingConfidenceProposerAdapter:
    def test_propose_returns_package_for_low_conf(self):
        adapter = L0RoutingConfidenceProposerAdapter()

        class FakeSnapshot:
            snapshot_id = "adapter-snap"

        result = adapter.propose(
            snapshot=FakeSnapshot(),
            confidence_values=_LOW_CONF,
            config={"routing_min_confidence": 0.20},
            now_utc=10_000,
            history={"routing_min_confidence_n_obs": 50},
            cooldown=_ZERO_COOLDOWN,
            sample=_MIN_SAMPLE,
        )
        assert result is not None

    def test_propose_returns_none_for_high_conf(self):
        adapter = L0RoutingConfidenceProposerAdapter()

        class FakeSnapshot:
            snapshot_id = "adapter-snap"

        result = adapter.propose(
            snapshot=FakeSnapshot(),
            confidence_values=_HIGH_CONF,
            config={"routing_min_confidence": 0.20},
            now_utc=10_000,
            history={"routing_min_confidence_n_obs": 50},
            cooldown=_ZERO_COOLDOWN,
            sample=_MIN_SAMPLE,
        )
        assert result is None

    def test_propose_handles_none_cooldown_and_sample(self):
    """Test propose_handles_none_cooldown_and_sample runtime behavior."""
    # Arrange
    # TODO: Set up processing data
    raw_data = []  # Replace with actual test data

    # Act
    # TODO: Process data with propose_handles_none_cooldown_and_sample
    processed_result = None  # Replace with actual processing

    # Assert
    assert processed_result is not None, "Processing should produce a result"
    assert len(processed_result) >= 0, "Processed result should be measurable"
    # TODO: Add specific processing assertions
                cooldown=None,
                sample=None,
            )
        except Exception as exc:
            pytest.fail(f"Adapter raised with None cooldown/sample: {exc}")
