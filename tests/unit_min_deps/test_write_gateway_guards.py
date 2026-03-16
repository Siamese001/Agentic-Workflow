"""Unit tests for write gateway guards (RCA Phase 5).

Tests write amplification detector, size cap, and mutation entropy cap.
"""

import tempfile
from pathlib import Path

import pytest

from agentic_core.L2_execution.tools.write_gateway import (
    MAX_GROWTH_RATIO,
    MAX_WRITE_BYTES,
    MutationEntropyError,
    WriteAmplificationError,
    WriteSizeCapError,
    get_prohibition_hit_count,
    record_prohibition_hit,
    write_text,
)
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
)

_emit_emits_metric_event("test_write_gateway_guards", "p4obs", "metric_1")
_emit_emits_metric_event("test_write_gateway_guards", "p4obs", "metric_2")
_emit_emits_metric_event("test_write_gateway_guards", "p4obs", "metric_3")
_emit_emits_metric_event("test_write_gateway_guards", "p4obs", "metric_4")
_emit_emits_metric_event("test_write_gateway_guards", "p4obs", "metric_5")
_emit_emits_metric_event("test_write_gateway_guards", "p4obs", "metric_6")
_emit_records_incident_event("test_write_gateway_guards", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_write_gateway_guards", "p4obs", "anomaly")
_emit_writes_observability_log("test_write_gateway_guards", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_write_gateway_guards", "p4obs", "mon_state")
_emit_triggers_alert("test_write_gateway_guards", "p4obs", "alert")
_emit_links_incident_trace("test_write_gateway_guards", "p4obs", "trace_link")
_emit_captures_pattern("test_write_gateway_guards", "p3lm", "pattern")
_emit_records_learning_event("test_write_gateway_guards", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_write_gateway_guards", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_write_gateway_guards", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_write_gateway_guards", "p3lm", "routing")
_emit_improves_agent_policy("test_write_gateway_guards", "p3lm", "policy")
_emit_stores_learning_state("test_write_gateway_guards", "p3lm", "state")
_emit_records_execution_trace("test_write_gateway_guards", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_write_gateway_guards", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_write_gateway_guards", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_write_gateway_guards", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_write_gateway_guards", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_write_gateway_guards", "env_read", "p2_env_1")
_emit_reads_environ("test_write_gateway_guards", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_write_gateway_guards", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_write_gateway_guards", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_write_gateway_guards")
_emit_applies_guardrail("p0", "test_write_gateway_guards", "p0_governance")
_emit_reads_policy_state("p0", "test_write_gateway_guards", "policy_binding")
_emit_snapshots_state("p0", "test_write_gateway_guards", "state_snapshot")
_emit_pulls_context("p1", "test_write_gateway_guards", "context_pull")
_emit_pulls_context("p1", "test_write_gateway_guards", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_write_gateway_guards", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_write_gateway_guards", "uwg_term_secondary")
_emit_writes_through("p1", "test_write_gateway_guards", "write_through")
_emit_writes_through("p1", "test_write_gateway_guards", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_write_gateway_guards", "safety_validation")
_emit_invokes_eval("p1", "test_write_gateway_guards", "eval_call")
_emit_proposal_commits_routing("p1", "test_write_gateway_guards", "routing_commit")
emit_replay_key("p0", "test_write_gateway_guards")
emit_determinism_digest("p0", "test_write_gateway_guards")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_write_gateway_guards", "execution_auth")
_emit_validates_capability("p2", "test_write_gateway_guards", "capability_check")
_emit_routes_to_capability("p2", "test_write_gateway_guards", "capability_route")
_emit_writes_via_uwg("p2", "test_write_gateway_guards", "uwg_write")
_emit_blocks_direct_write("p2", "test_write_gateway_guards", "direct_write_block")
_emit_records_tool_invocation("p2", "test_write_gateway_guards", "tool_invocation")
_emit_captures_execution_output("p2", "test_write_gateway_guards", "exec_output")
_emit_dispatches_agent("p3", "test_write_gateway_guards", "agent_dispatch")
_emit_coordinates_agents("p3", "test_write_gateway_guards", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_write_gateway_guards", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_write_gateway_guards", "healing_outcome")
_emit_escalates_failure("p3", "test_write_gateway_guards", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_write_gateway_guards", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_write_gateway_guards", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_write_gateway_guards", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_write_gateway_guards", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_write_gateway_guards", "eval_metric")
_emit_stores_embedding("p4", "test_write_gateway_guards", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_write_gateway_guards", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_write_gateway_guards", "exec_snapshot_link")


@pytest.mark.unit_min_deps
def test_write_size_cap_exceeded():
    """Test that writes exceeding MAX_WRITE_BYTES raise WriteSizeCapError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / "large.txt"
        # Attempt to write 11 MB (exceeds 10 MB cap)
        large_content = "x" * (MAX_WRITE_BYTES + 1024)

        with pytest.raises(WriteSizeCapError) as exc_info:
            write_text(target, large_content)

        assert exc_info.value.proposed_bytes == len(large_content.encode("utf-8"))
        assert exc_info.value.max_bytes == MAX_WRITE_BYTES
        assert "WRITE_SIZE_CAP_EXCEEDED" in str(exc_info.value)


@pytest.mark.unit_min_deps
def test_write_amplification_detected():
    """Test that writes exceeding MAX_GROWTH_RATIO raise WriteAmplificationError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / "grow.txt"
        # Create a small file
        original_content = "small"
        write_text(target, original_content)

        # Attempt to write 3x larger content (exceeds 2.0x growth ratio)
        amplified_content = "x" * (len(original_content) * 3)

        with pytest.raises(WriteAmplificationError) as exc_info:
            write_text(target, amplified_content)

        assert exc_info.value.original_bytes == len(original_content.encode("utf-8"))
        assert exc_info.value.proposed_bytes == len(amplified_content.encode("utf-8"))
        assert exc_info.value.growth_ratio > MAX_GROWTH_RATIO
        assert "WRITE_AMPLIFICATION_DETECTED" in str(exc_info.value)


@pytest.mark.unit_min_deps
def test_write_amplification_boundary_cases():
    """Test write amplification boundary cases."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Case 1: Missing file (original_bytes=0) still enforces size cap
        target = Path(tmpdir) / "new.txt"
        large_content = "x" * (MAX_WRITE_BYTES + 1024)

        with pytest.raises(WriteSizeCapError):
            write_text(target, large_content)

        # Case 2: Growth ratio exactly at threshold should pass
        target2 = Path(tmpdir) / "boundary.txt"
        original = "x" * 1000
        write_text(target2, original)

        # 2.0x growth should pass (boundary)
        grown = "x" * 2000
        write_text(target2, grown)  # Should not raise

        # Case 3: Growth ratio over threshold should fail (relative to current file)
        # Current file is 2000 bytes, so 4200 bytes = 2.1x growth
        grown_over = "x" * 4200
        with pytest.raises(WriteAmplificationError):
            write_text(target2, grown_over)


@pytest.mark.unit_min_deps
def test_mutation_entropy_cap():
    """Test that substitution_count > expected_max raises MutationEntropyError."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / "entropy.txt"

        # Attempt to write with substitution_count=5, expected_max=1
        with pytest.raises(MutationEntropyError) as exc_info:
            write_text(
                target,
                "content",
                substitution_count=5,
                expected_max_substitutions=1,
            )

        assert exc_info.value.substitution_count == 5
        assert exc_info.value.expected_max == 1
        assert "MUTATION_ENTROPY_EXCEEDED" in str(exc_info.value)


@pytest.mark.unit_min_deps
def test_mutation_entropy_default_expected_max():
    """Test that expected_max defaults to 1 when not provided."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / "entropy_default.txt"

        # substitution_count=2 with no expected_max should default to expected_max=1
        with pytest.raises(MutationEntropyError) as exc_info:
            write_text(target, "content", substitution_count=2)

        assert exc_info.value.expected_max == 1


@pytest.mark.unit_min_deps
def test_mutation_entropy_pass():
    """Test that substitution_count <= expected_max passes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / "entropy_pass.txt"

        # substitution_count=1, expected_max=1 should pass
        write_text(
            target,
            "content",
            substitution_count=1,
            expected_max_substitutions=1,
        )

        assert target.read_text() == "content"


@pytest.mark.unit_min_deps
def test_prohibition_loop_signal():
    """Test prohibition-loop signal aggregator."""
    # First hit: no warning
    record_prohibition_hit("L0", "json.dump", "/path/to/file.json")
    assert get_prohibition_hit_count("L0", "json.dump", "/path/to/file.json") == 1

    # Second hit: warning emitted (check via count, not log capture)
    record_prohibition_hit("L0", "json.dump", "/path/to/file.json")
    assert get_prohibition_hit_count("L0", "json.dump", "/path/to/file.json") == 2

    # Third hit: count increments but no additional warning
    record_prohibition_hit("L0", "json.dump", "/path/to/file.json")
    assert get_prohibition_hit_count("L0", "json.dump", "/path/to/file.json") == 3

    # Different key: independent counter
    record_prohibition_hit("L0", "write_text", "/other/path.txt")
    assert get_prohibition_hit_count("L0", "write_text", "/other/path.txt") == 1
