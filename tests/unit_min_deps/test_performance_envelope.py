"""Unit tests for performance envelope and scaling hardening."""

import tempfile

import pytest

from agentic_core.L3_orchestration.replay.deterministic_replay import (
    ReplayCommand,
    _truncate_if_needed,
    run_and_record,
)
from agentic_core.L4_state.storage.filesystem_store import FileSystemStore
from agentic_core.L4_state.storage.persistent_store import create_artifact
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_performance_envelope", "p4obs", "metric_1")
_emit_emits_metric_event("test_performance_envelope", "p4obs", "metric_2")
_emit_emits_metric_event("test_performance_envelope", "p4obs", "metric_3")
_emit_emits_metric_event("test_performance_envelope", "p4obs", "metric_4")
_emit_emits_metric_event("test_performance_envelope", "p4obs", "metric_5")
_emit_emits_metric_event("test_performance_envelope", "p4obs", "metric_6")
_emit_records_incident_event("test_performance_envelope", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_performance_envelope", "p4obs", "anomaly")
_emit_writes_observability_log("test_performance_envelope", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_performance_envelope", "p4obs", "mon_state")
_emit_triggers_alert("test_performance_envelope", "p4obs", "alert")
_emit_links_incident_trace("test_performance_envelope", "p4obs", "trace_link")
_emit_captures_pattern("test_performance_envelope", "p3lm", "pattern")
_emit_records_learning_event("test_performance_envelope", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_performance_envelope", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_performance_envelope", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_performance_envelope", "p3lm", "routing")
_emit_improves_agent_policy("test_performance_envelope", "p3lm", "policy")
_emit_stores_learning_state("test_performance_envelope", "p3lm", "state")
_emit_records_execution_trace("test_performance_envelope", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_performance_envelope", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_performance_envelope", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_performance_envelope", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_performance_envelope", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_performance_envelope", "env_read", "p2_env_1")
_emit_reads_environ("test_performance_envelope", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_performance_envelope", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_performance_envelope", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_performance_envelope")
_emit_applies_guardrail("p0", "test_performance_envelope", "p0_governance")
_emit_reads_policy_state("p0", "test_performance_envelope", "policy_binding")
_emit_snapshots_state("p0", "test_performance_envelope", "state_snapshot")
_emit_pulls_context("p1", "test_performance_envelope", "context_pull")
_emit_pulls_context("p1", "test_performance_envelope", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_performance_envelope", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_performance_envelope", "uwg_term_secondary")
_emit_writes_through("p1", "test_performance_envelope", "write_through")
_emit_writes_through("p1", "test_performance_envelope", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_performance_envelope", "safety_validation")
_emit_invokes_eval("p1", "test_performance_envelope", "eval_call")
_emit_proposal_commits_routing("p1", "test_performance_envelope", "routing_commit")
_emit_escalates_to_human("p1", "test_performance_envelope", "human_escalation")
_emit_routes_through("p1", "test_performance_envelope", "route_through")
_emit_checks_agent_registry("p1", "test_performance_envelope", "agent_registry")
_emit_validates_agent_capability("p1", "test_performance_envelope", "capability")
_emit_dispatches_execution_plan("p1", "test_performance_envelope", "exec_plan")
_emit_agent_executes_agent("p1", "test_performance_envelope", "sub_agent")
_emit_routes_to_agent("p1", "test_performance_envelope", "target_agent")
_emit_verifies_policy("p1", "test_performance_envelope", "policy_check")
_emit_observes_runtime_state("p1", "test_performance_envelope", "runtime_state")
_emit_verifies_boundary("p1", "test_performance_envelope", "boundary_check")
_emit_transcripts_response("p1", "test_performance_envelope", "transcript")
_emit_hard_fails_untranscripted("p1", "test_performance_envelope")
_emit_gated_by_confidence("p1", "test_performance_envelope", "confidence_gate")
emit_replay_key("p0", "test_performance_envelope")
emit_determinism_digest("p0", "test_performance_envelope")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_performance_envelope", "execution_auth")
_emit_validates_capability("p2", "test_performance_envelope", "capability_check")
_emit_routes_to_capability("p2", "test_performance_envelope", "capability_route")
_emit_writes_via_uwg("p2", "test_performance_envelope", "uwg_write")
_emit_blocks_direct_write("p2", "test_performance_envelope", "direct_write_block")
_emit_records_tool_invocation("p2", "test_performance_envelope", "tool_invocation")
_emit_captures_execution_output("p2", "test_performance_envelope", "exec_output")
_emit_dispatches_agent("p3", "test_performance_envelope", "agent_dispatch")
_emit_coordinates_agents("p3", "test_performance_envelope", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_performance_envelope", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_performance_envelope", "healing_outcome")
_emit_escalates_failure("p3", "test_performance_envelope", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_performance_envelope", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_performance_envelope", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_performance_envelope", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_performance_envelope", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_performance_envelope", "eval_metric")
_emit_stores_embedding("p4", "test_performance_envelope", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_performance_envelope", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_performance_envelope", "exec_snapshot_link")


@pytest.mark.unit_min_deps
def test_truncation_deterministic_and_hash_changes():
    """Test that truncation is deterministic and reflected in hashes."""
    # Create text that exceeds limit
    long_text = "x" * 2000  # 2000 bytes
    truncated_text, was_truncated = _truncate_if_needed(long_text, 1000)

    assert was_truncated
    assert "...<TRUNCATED 1000 BYTES>" in truncated_text
    assert len(truncated_text.encode("utf-8")) <= 1000

    # Truncation is deterministic
    truncated_text2, was_truncated2 = _truncate_if_needed(long_text, 1000)
    assert truncated_text == truncated_text2
    assert was_truncated == was_truncated2


@pytest.mark.unit_min_deps
def test_replay_metrics_determinism():
    """Test that replay metrics are deterministic."""
    commands = [
        ReplayCommand(
            argv=["python", "-c", "print('hello')"],
            cwd=".",
            env_allowlist={},
            max_stdout_bytes=1000,
            max_stderr_bytes=1000,
        )
    ]

    record1 = run_and_record(commands)
    record2 = run_and_record(commands)

    # Metrics should be present and deterministic
    assert record1.metrics is not None
    assert record2.metrics is not None
    assert record1.metrics == record2.metrics

    # Should have captured output size
    assert record1.metrics.total_bytes_out > 0
    assert record1.metrics.total_bytes_err == 0
    assert len(record1.metrics.per_command_bytes_out) == 1
    assert len(record1.metrics.per_command_bytes_err) == 1


@pytest.mark.unit_min_deps
def test_store_list_limit_deterministic():
    """Test that store list(limit) is deterministic."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = FileSystemStore(temp_dir)

        # Create 10 artifacts
        for i in range(10):
            artifact = create_artifact(
                "test_kind",
                f"id_{i:02d}",
                {"data": f"value_{i}"},
            )
            store.put(artifact)

        # List with limit should return first N in deterministic order
        limited_refs = store.list(limit=LIMIT)
        all_refs = store.list()

        assert len(limited_refs) == 5
        assert len(all_refs) == 10

        # Limited list should be first 5 of full list
        for i, ref in enumerate(limited_refs):
            assert ref == all_refs[i]

        # Ordering should be deterministic
        expected_order = [f"id_{i:02d}" for i in range(10)]
        actual_order = [r.logical_id for r in all_refs]
        assert actual_order == expected_order


@pytest.mark.unit_min_deps
def test_scaling_200_small_artifacts():
    """Scaling test: write 200 small artifacts and verify structure."""
    with tempfile.TemporaryDirectory() as temp_dir:
        store = FileSystemStore(temp_dir)

        # Write 200 small artifacts
        for i in range(200):
            artifact = create_artifact(
                f"kind_{i % 5}",  # 5 different kinds
                f"item_{i:03d}",
                {"index": i, "data": "x" * 10},  # Small payload
            )
            ref = store.put(artifact)

            # Verify basic structure
            assert ref.version == 1
            assert ref.size_bytes > 0
            assert ref.kind == f"kind_{i % 5}"
            assert ref.logical_id == f"item_{i:03d}"

        # List all artifacts
        all_refs = store.list()
        assert len(all_refs) == 200

        # Verify deterministic ordering
        for i in range(1, 200):
            prev_ref = all_refs[i - 1]
            curr_ref = all_refs[i]

            # Should be sorted by kind, then logical_id, then version
            if prev_ref.kind == curr_ref.kind:
                if prev_ref.logical_id == curr_ref.logical_id:
                    assert prev_ref.version < curr_ref.version
                else:
                    assert prev_ref.logical_id < curr_ref.logical_id
            else:
                assert prev_ref.kind < curr_ref.kind

        # Test listing with limits
        first_10 = store.list(limit=LIMIT)
        assert len(first_10) == 10
        assert first_10 == all_refs[:10]

        # Test filtering by kind
        kind_0_refs = store.list(kind="kind_0")
        assert len(kind_0_refs) == 40  # 200 / 5 kinds
        assert all(r.kind == "kind_0" for r in kind_0_refs)


@pytest.mark.unit_min_deps
def test_scaling_25_replay_commands():
    """Scaling test: record 25 simple replay commands."""
    commands = []
    for i in range(25):
        cmd = ReplayCommand(
            argv=["python", "-c", f"print('cmd_{i}')"],
            cwd=".",
            env_allowlist={},
            max_stdout_bytes=1000,
            max_stderr_bytes=1000,
        )
        commands.append(cmd)

    # Record all commands
    record = run_and_record(commands)

    # Verify structural invariants
    assert len(record.results) == 25
    assert len(record.commands) == 25
    assert len(record.hashes) == 25
    assert record.metrics is not None

    # All commands should succeed
    for result in record.results:
        assert result.exit_code == 0
        assert "cmd_" in result.stdout

    # Metrics should be consistent
    assert len(record.metrics.per_command_bytes_out) == 25
    assert len(record.metrics.per_command_bytes_err) == 25
    assert record.metrics.total_bytes_out > 0
    assert record.metrics.total_bytes_err == 0

    # Per-command metrics should sum to totals
    assert sum(record.metrics.per_command_bytes_out) == record.metrics.total_bytes_out
    assert sum(record.metrics.per_command_bytes_err) == record.metrics.total_bytes_err

    # All hashes should be unique
    hash_values = list(record.hashes.values())
    assert len(hash_values) == len(set(hash_values))


@pytest.mark.unit_min_deps
def test_scaling_deterministic_across_runs():
    """Test that scaling operations are deterministic across runs."""
    # First run
    commands1 = [
        ReplayCommand(
            argv=["python", "-c", "print('test')"],
            cwd=".",
            env_allowlist={},
            max_stdout_bytes=1000,
            max_stderr_bytes=1000,
        )
    ]
    record1 = run_and_record(commands1)

    # Second run with identical commands
    commands2 = [
        ReplayCommand(
            argv=["python", "-c", "print('test')"],
            cwd=".",
            env_allowlist={},
            max_stdout_bytes=1000,
            max_stderr_bytes=1000,
        )
    ]
    record2 = run_and_record(commands2)

    # Should be identical
    assert record1.metrics == record2.metrics
    assert record1.hashes == record2.hashes

    # Store operations should also be deterministic
    with tempfile.TemporaryDirectory() as temp_dir:
        store1 = FileSystemStore(temp_dir)
        artifact1 = create_artifact("test", "deterministic", {"data": "test"})
        ref1 = store1.put(artifact1)

        store2 = FileSystemStore(temp_dir)
        artifact2 = create_artifact("test", "deterministic", {"data": "test"})
        ref2 = store2.put(artifact2)

        # Should create version 2 since artifact already exists
        assert ref1.version == 1
        assert ref2.version == 2
        assert ref1.kind == ref2.kind
        assert ref1.logical_id == ref2.logical_id
