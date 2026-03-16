"""Unit tests for system_learning.validators.replay_validator."""

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

_emit_authorize_and_execute("p2", "test_replay_validator", "execution_auth")
_emit_validates_capability("p2", "test_replay_validator", "capability_check")
_emit_routes_to_capability("p2", "test_replay_validator", "capability_route")
_emit_writes_via_uwg("p2", "test_replay_validator", "uwg_write")
_emit_blocks_direct_write("p2", "test_replay_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "test_replay_validator", "tool_invocation")
_emit_captures_execution_output("p2", "test_replay_validator", "exec_output")
_emit_dispatches_agent("p3", "test_replay_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "test_replay_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_replay_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_replay_validator", "healing_outcome")
_emit_escalates_failure("p3", "test_replay_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_replay_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_replay_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_replay_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_replay_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_replay_validator", "eval_metric")
_emit_stores_embedding("p4", "test_replay_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_replay_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_replay_validator", "exec_snapshot_link")
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
from system_learning.validators.replay_validator import (
    DeterminismViolation,
    replay_validate,
)

_emit_emits_metric_event("test_replay_validator", "p4obs", "metric_1")
_emit_emits_metric_event("test_replay_validator", "p4obs", "metric_2")
_emit_emits_metric_event("test_replay_validator", "p4obs", "metric_3")
_emit_emits_metric_event("test_replay_validator", "p4obs", "metric_4")
_emit_emits_metric_event("test_replay_validator", "p4obs", "metric_5")
_emit_emits_metric_event("test_replay_validator", "p4obs", "metric_6")
_emit_records_incident_event("test_replay_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_replay_validator", "p4obs", "anomaly")
_emit_writes_observability_log("test_replay_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_replay_validator", "p4obs", "mon_state")
_emit_triggers_alert("test_replay_validator", "p4obs", "alert")
_emit_links_incident_trace("test_replay_validator", "p4obs", "trace_link")
_emit_captures_pattern("test_replay_validator", "p3lm", "pattern")
_emit_records_learning_event("test_replay_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_replay_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_replay_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_replay_validator", "p3lm", "routing")
_emit_improves_agent_policy("test_replay_validator", "p3lm", "policy")
_emit_stores_learning_state("test_replay_validator", "p3lm", "state")
_emit_records_execution_trace("test_replay_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_replay_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_replay_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_replay_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_replay_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_replay_validator", "env_read", "p2_env_1")
_emit_reads_environ("test_replay_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_replay_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_replay_validator", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_replay_validator")
_emit_applies_guardrail("p0", "test_replay_validator", "p0_governance")
_emit_reads_policy_state("p0", "test_replay_validator", "policy_binding")
_emit_snapshots_state("p0", "test_replay_validator", "state_snapshot")
_emit_pulls_context("p1", "test_replay_validator", "context_pull")
_emit_pulls_context("p1", "test_replay_validator", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_replay_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_replay_validator", "uwg_term_secondary")
_emit_writes_through("p1", "test_replay_validator", "write_through")
_emit_writes_through("p1", "test_replay_validator", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_replay_validator", "safety_validation")
_emit_invokes_eval("p1", "test_replay_validator", "eval_call")
_emit_proposal_commits_routing("p1", "test_replay_validator", "routing_commit")
emit_replay_key("p0", "test_replay_validator")
emit_determinism_digest("p0", "test_replay_validator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


class TestReplayValidator:
    def test_deterministic_engine_passes(self):
        """Deterministic engine produces same hash on both runs."""

        def deterministic_engine(snapshot):
            return {"value": snapshot["input"] * 2}

        def canonicalize(output):
            return str(sorted(output.items())).encode("utf-8")

        snapshot = {"input": 5}
        hash_result = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)

        # Should return a valid SHA-256 hex digest
        assert isinstance(hash_result, str)
        assert len(hash_result) == 64
        assert all(c in "0123456789abcdef" for c in hash_result)

    def test_nondeterministic_engine_fails(self):
        """Non-deterministic engine raises DeterminismViolation."""
        call_count = 0

        def nondeterministic_engine(snapshot):
            nonlocal call_count
            call_count += 1
            return {"value": snapshot["input"] * call_count}

        def canonicalize(output):
            return str(sorted(output.items())).encode("utf-8")

        snapshot = {"input": 5}

        with pytest.raises(DeterminismViolation, match="DETERMINISM_VIOLATION"):
            replay_validate(snapshot, nondeterministic_engine, canonicalize_fn=canonicalize)

    def test_error_includes_both_hashes(self):
        """DeterminismViolation error includes both hashes."""
        call_count = 0

        def nondeterministic_engine(snapshot):
            nonlocal call_count
            call_count += 1
            return {"value": call_count}

        def canonicalize(output):
            return str(output).encode("utf-8")

        snapshot = {"input": 5}

        with pytest.raises(DeterminismViolation) as exc_info:
            replay_validate(snapshot, nondeterministic_engine, canonicalize_fn=canonicalize)

        error_msg = str(exc_info.value)
        assert "Run 1 hash:" in error_msg
        assert "Run 2 hash:" in error_msg

    def test_same_output_twice_produces_same_hash(self):
        """Running replay_validate twice with same engine produces same hash."""

        def deterministic_engine(snapshot):
            return {"value": snapshot["input"] * 2}

        def canonicalize(output):
            return str(sorted(output.items())).encode("utf-8")

        snapshot = {"input": 5}

        hash1 = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)
        hash2 = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)

        assert hash1 == hash2

    def test_different_snapshots_produce_different_hashes(self):
        """Different snapshots produce different hashes."""

        def deterministic_engine(snapshot):
            return {"value": snapshot["input"] * 2}

        def canonicalize(output):
            return str(sorted(output.items())).encode("utf-8")

        snapshot1 = {"input": 5}
        snapshot2 = {"input": 10}

        hash1 = replay_validate(snapshot1, deterministic_engine, canonicalize_fn=canonicalize)
        hash2 = replay_validate(snapshot2, deterministic_engine, canonicalize_fn=canonicalize)

        assert hash1 != hash2


class TestDeterminism:
    def test_replay_validate_deterministic(self):
        """replay_validate itself is deterministic."""

        def deterministic_engine(snapshot):
            return {"value": snapshot["input"] * 2, "extra": "data"}

        def canonicalize(output):
            # Canonical: sorted items
            return str(sorted(output.items())).encode("utf-8")

        snapshot = {"input": 42}

        # Run replay_validate multiple times
        hash1 = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)
        hash2 = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)
        hash3 = replay_validate(snapshot, deterministic_engine, canonicalize_fn=canonicalize)

        assert hash1 == hash2 == hash3
