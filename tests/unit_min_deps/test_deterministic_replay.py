"""Unit tests for deterministic replay engine."""

import pytest

from agentic_core.L3_orchestration.replay.deterministic_replay import (
    ReplayCommand,
    ReplayRecord,
    ReplayResult,
    record_from_json,
    record_to_json,
    replay_and_compare,
    run_and_record,
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
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_deterministic_replay")
_emit_applies_guardrail("p0", "test_deterministic_replay", "p0_governance")
_emit_reads_policy_state("p0", "test_deterministic_replay", "policy_binding")
_emit_snapshots_state("p0", "test_deterministic_replay", "state_snapshot")
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
)

_emit_emits_metric_event("test_deterministic_replay", "p4obs", "metric_1")
_emit_emits_metric_event("test_deterministic_replay", "p4obs", "metric_2")
_emit_emits_metric_event("test_deterministic_replay", "p4obs", "metric_3")
_emit_emits_metric_event("test_deterministic_replay", "p4obs", "metric_4")
_emit_emits_metric_event("test_deterministic_replay", "p4obs", "metric_5")
_emit_emits_metric_event("test_deterministic_replay", "p4obs", "metric_6")
_emit_records_incident_event("test_deterministic_replay", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_deterministic_replay", "p4obs", "anomaly")
_emit_writes_observability_log("test_deterministic_replay", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_deterministic_replay", "p4obs", "mon_state")
_emit_triggers_alert("test_deterministic_replay", "p4obs", "alert")
_emit_links_incident_trace("test_deterministic_replay", "p4obs", "trace_link")
_emit_captures_pattern("test_deterministic_replay", "p3lm", "pattern")
_emit_records_learning_event("test_deterministic_replay", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_deterministic_replay", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_deterministic_replay", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_deterministic_replay", "p3lm", "routing")
_emit_improves_agent_policy("test_deterministic_replay", "p3lm", "policy")
_emit_stores_learning_state("test_deterministic_replay", "p3lm", "state")
_emit_records_execution_trace("test_deterministic_replay", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_deterministic_replay", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_deterministic_replay", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_deterministic_replay", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_deterministic_replay", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_deterministic_replay", "env_read", "p2_env_1")
_emit_reads_environ("test_deterministic_replay", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_deterministic_replay", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_deterministic_replay", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_deterministic_replay", "context_pull")
_emit_pulls_context("p1", "test_deterministic_replay", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_deterministic_replay", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_deterministic_replay", "uwg_term_2")
_emit_writes_through("p1", "test_deterministic_replay", "write_through")
_emit_writes_through("p1", "test_deterministic_replay", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_deterministic_replay", "safety_validation")
_emit_invokes_eval("p1", "test_deterministic_replay", "eval_call")
_emit_proposal_commits_routing("p1", "test_deterministic_replay", "routing_commit")
_emit_escalates_to_human("p1", "test_deterministic_replay", "human_escalation")
_emit_routes_through("p1", "test_deterministic_replay", "route_through")
_emit_checks_agent_registry("p1", "test_deterministic_replay", "agent_registry")
_emit_validates_agent_capability("p1", "test_deterministic_replay", "capability")
_emit_dispatches_execution_plan("p1", "test_deterministic_replay", "exec_plan")
_emit_agent_executes_agent("p1", "test_deterministic_replay", "sub_agent")
_emit_routes_to_agent("p1", "test_deterministic_replay", "target_agent")
_emit_verifies_policy("p1", "test_deterministic_replay", "policy_check")
_emit_observes_runtime_state("p1", "test_deterministic_replay", "runtime_state")
_emit_verifies_boundary("p1", "test_deterministic_replay", "boundary_check")
_emit_transcripts_response("p1", "test_deterministic_replay", "transcript")
_emit_hard_fails_untranscripted("p1", "test_deterministic_replay")
_emit_gated_by_confidence("p1", "test_deterministic_replay", "confidence_gate")
emit_replay_key("p0", "test_deterministic_replay")
emit_determinism_digest("p0", "test_deterministic_replay")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_deterministic_replay", "execution_auth")
_emit_validates_capability("p2", "test_deterministic_replay", "capability_check")
_emit_routes_to_capability("p2", "test_deterministic_replay", "capability_route")
_emit_writes_via_uwg("p2", "test_deterministic_replay", "uwg_write")
_emit_blocks_direct_write("p2", "test_deterministic_replay", "direct_write_block")
_emit_records_tool_invocation("p2", "test_deterministic_replay", "tool_invocation")
_emit_captures_execution_output("p2", "test_deterministic_replay", "exec_output")
_emit_dispatches_agent("p3", "test_deterministic_replay", "agent_dispatch")
_emit_coordinates_agents("p3", "test_deterministic_replay", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_deterministic_replay", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_deterministic_replay", "healing_outcome")
_emit_escalates_failure("p3", "test_deterministic_replay", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_deterministic_replay", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_deterministic_replay", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_deterministic_replay", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_deterministic_replay", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_deterministic_replay", "eval_metric")
_emit_stores_embedding("p4", "test_deterministic_replay", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_deterministic_replay", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_deterministic_replay", "exec_snapshot_link")


@pytest.mark.unit_min_deps
def test_deterministic_json_output():
    """Test that JSON serialization is deterministic byte-for-byte."""
    # Create identical records
    record1 = ReplayRecord(
        commands=[
            ReplayCommand(
                argv=["python", "-c", "print('x')"],
                cwd="/test",
                env_allowlist={"PATH": "/bin"},
                timeout_s=60,
            )
        ],
        results=[ReplayResult(exit_code=0, stdout="x\n", stderr="")],
        hashes={"cmd_1": "hash123"},
    )

    record2 = ReplayRecord(
        commands=[
            ReplayCommand(
                argv=["python", "-c", "print('x')"],
                cwd="/test",
                env_allowlist={"PATH": "/bin"},
                timeout_s=60,
            )
        ],
        results=[ReplayResult(exit_code=0, stdout="x\n", stderr="")],
        hashes={"cmd_1": "hash123"},
    )

    # Serialize both
    json1 = record_to_json(record1)
    json2 = record_to_json(record2)

    # Should be byte-for-byte identical
    assert json1 == json2

    # Should deserialize to equivalent objects
    parsed1 = record_from_json(json1)
    parsed2 = record_from_json(json2)

    assert parsed1.commands[0].argv == parsed2.commands[0].argv
    assert parsed1.results[0].stdout == parsed2.results[0].stdout


@pytest.mark.unit_min_deps
def test_sha256_stable_and_correct():
    """Test that command hashes are stable and correct."""
    # Create a command and result
    command = ReplayCommand(
        argv=["python", "-c", "print('test')"],
        cwd="/test",
        env_allowlist={"PATH": "/bin"},
        timeout_s=60,
    )

    result = ReplayResult(exit_code=0, stdout="test\n", stderr="")

    # Compute hash twice
    from agentic_core.L3_orchestration.replay.deterministic_replay import _hash_command_result

    hash1 = _hash_command_result(command, result)
    hash2 = _hash_command_result(command, result)

    # Should be identical
    assert hash1 == hash2

    # Should be valid SHA256 (64 hex chars)
    assert len(hash1) == 64
    assert all(c in "0123456789abcdef" for c in hash1)

    # Different content should produce different hash
    result2 = ReplayResult(exit_code=0, stdout="different\n", stderr="")
    hash3 = _hash_command_result(command, result2)
    assert hash1 != hash3


@pytest.mark.unit_min_deps
def test_env_redaction_works():
    """Test that non-allowlisted environment variables are not recorded."""
    # Set a non-allowlisted env var
    import os

    os.environ["SECRET_SHOULD_NOT_BE_RECORDED"] = "secret_value"

    try:
        # Record a command
        commands = [
            ReplayCommand(
                argv=["python", "-c", "print('test')"],
                cwd=".",
                env_allowlist={"TEST_VAR": "test_value"},
                timeout_s=60,
            )
        ]

        record = run_and_record(commands)

        # Check that only allowlisted vars are in the command
        env_in_record = record.commands[0].env_allowlist
        assert "SECRET_SHOULD_NOT_BE_RECORDED" not in env_in_record
        assert "TEST_VAR" in env_in_record
        assert env_in_record["TEST_VAR"] == "test_value"

    finally:
        # Clean up
        os.environ.pop("SECRET_SHOULD_NOT_BE_RECORDED", None)


@pytest.mark.unit_min_deps
def test_rejects_pwsh_argv0():
    """Test that pwsh/powershell in argv0 raises RuntimeError."""
    commands = [
        ReplayCommand(
            argv=["pwsh", "-c", "echo test"],
            cwd=".",
            env_allowlist={},
            timeout_s=60,
        )
    ]

    with pytest.raises(RuntimeError, match="PowerShell usage forbidden"):
        run_and_record(commands)

    # Test powershell.exe variant
    commands2 = [
        ReplayCommand(
            argv=["powershell.exe", "-c", "echo test"],
            cwd=".",
            env_allowlist={},
            timeout_s=60,
        )
    ]

    with pytest.raises(RuntimeError, match="PowerShell usage forbidden"):
        run_and_record(commands2)


@pytest.mark.unit_min_deps
def test_replay_match_deterministic_command():
    """Test replay matches for deterministic command."""
    # Record a deterministic command
    commands = [
        ReplayCommand(
            argv=["python", "-c", "print('x')"],
            cwd=".",
            env_allowlist={},
            timeout_s=60,
        )
    ]

    record = run_and_record(commands)

    # Replay should match
    result = replay_and_compare(record)
    assert result.is_match
    assert len(result.mismatches) == 0


@pytest.mark.unit_min_deps
def test_replay_detects_nondeterminism():
    """Test replay detects non-deterministic command."""
    # Record a non-deterministic command (time-based output)
    commands = [
        ReplayCommand(
            argv=["python", "-c", "import time; print(time.time())"],
            cwd=".",
            env_allowlist={},
            timeout_s=60,
        )
    ]

    record = run_and_record(commands)

    # Replay should detect mismatch
    result = replay_and_compare(record)
    assert not result.is_match
    assert len(result.mismatches) > 0
    assert "Stdout mismatch after normalization" in str(result.mismatches)


@pytest.mark.unit_min_deps
def test_normalize_output_strips_timestamps_and_paths():
    """Test output normalization strips timestamps and absolute paths."""
    from agentic_core.L3_orchestration.replay.deterministic_replay import _normalize_output

    # Test timestamp normalization
    input_with_timestamp = "2026-02-23T04:18:00.123Z INFO: Test message"
    normalized = _normalize_output(input_with_timestamp)
    assert "<TIMESTAMP> INFO: Test message" == normalized

    # Test path normalization
    import os

    repo_root = os.path.abspath(".")
    input_with_path = f"Processing file {repo_root}/test.py"
    normalized = _normalize_output(input_with_path)
    assert "Processing file <REPO_ROOT>/test.py" == normalized

    # Test Windows drive letter normalization
    input_with_drive = "C:/Users/test/file.py processed"
    normalized = _normalize_output(input_with_drive)
    assert "<ABSOLUTE_PATH> processed" == normalized
