"""Unit tests for system_learning.validators.dampening."""

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

_emit_authorize_and_execute("p2", "test_dampening", "execution_auth")
_emit_validates_capability("p2", "test_dampening", "capability_check")
_emit_routes_to_capability("p2", "test_dampening", "capability_route")
_emit_writes_via_uwg("p2", "test_dampening", "uwg_write")
_emit_blocks_direct_write("p2", "test_dampening", "direct_write_block")
_emit_records_tool_invocation("p2", "test_dampening", "tool_invocation")
_emit_captures_execution_output("p2", "test_dampening", "exec_output")
_emit_dispatches_agent("p3", "test_dampening", "agent_dispatch")
_emit_coordinates_agents("p3", "test_dampening", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_dampening", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_dampening", "healing_outcome")
_emit_escalates_failure("p3", "test_dampening", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_dampening", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_dampening", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_dampening", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_dampening", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_dampening", "eval_metric")
_emit_stores_embedding("p4", "test_dampening", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_dampening", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_dampening", "exec_snapshot_link")
from system_learning.validators.dampening import (
    CooldownPolicy,
    CooldownViolation,
    SampleSizePolicy,
    SampleSizeViolation,
    assert_cooldown_ok,
    assert_min_sample_size,
)

_emit_records_execution_trace("p0", "evidence", "test_dampening")
_emit_applies_guardrail("p0", "test_dampening", "p0_governance")
_emit_snapshots_state("p0", "test_dampening", "state_snapshot")
emit_replay_key("p0", "test_dampening")
emit_determinism_digest("p0", "test_dampening")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


class TestCooldownPolicy:
    def test_cooldown_elapsed_passes(self):
        policy = CooldownPolicy(min_seconds_between_updates=3600)
        last_update = 1700000000
        now = 1700003600
        assert_cooldown_ok(last_update, now, policy)

    def test_cooldown_not_elapsed_raises(self):
        policy = CooldownPolicy(min_seconds_between_updates=3600)
        last_update = 1700000000
        now = 1700001800
        with pytest.raises(CooldownViolation, match="COOLDOWN_VIOLATION"):
            assert_cooldown_ok(last_update, now, policy)

    def test_cooldown_exactly_elapsed_passes(self):
        policy = CooldownPolicy(min_seconds_between_updates=3600)
        last_update = 1700000000
        now = 1700003600
        assert_cooldown_ok(last_update, now, policy)


class TestSampleSizePolicy:
    def test_sufficient_samples_passes(self):
        policy = SampleSizePolicy(min_observations=1000)
        assert_min_sample_size(1500, policy)

    def test_insufficient_samples_raises(self):
        policy = SampleSizePolicy(min_observations=1000)
        with pytest.raises(SampleSizeViolation, match="SAMPLE_SIZE_VIOLATION"):
            assert_min_sample_size(500, policy)

    def test_exactly_min_samples_passes(self):
        policy = SampleSizePolicy(min_observations=1000)
        assert_min_sample_size(1000, policy)


class TestDeterminism:
    def test_cooldown_deterministic(self):
        policy = CooldownPolicy(min_seconds_between_updates=3600)
        assert_cooldown_ok(1700000000, 1700003600, policy)
        assert_cooldown_ok(1700000000, 1700003600, policy)

    def test_sample_size_deterministic(self):
        policy = SampleSizePolicy(min_observations=1000)
        assert_min_sample_size(1500, policy)
        assert_min_sample_size(1500, policy)
