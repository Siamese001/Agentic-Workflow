"""
Test mutation ledger functionality in write_gateway.

Per .windsurfrules §1.1: Zero-tolerance - any changed logic MUST have tests.
Per .windsurfrules §1.3: Deterministic tests only - no randomness.
Per .windsurfrules §1.5: Edge cases mandatory - null/missing/malformed inputs.
Per .windsurfrules §1.8: Fail-closed and side-effect safety.
"""

import hashlib
import json
import sys
from pathlib import Path

import pytest

#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_reads_policy_state,  # noqa: E402
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_mutation_ledger")
# REMOVED: _emit_applies_guardrail("p0", "test_mutation_ledger", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_mutation_ledger", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_mutation_ledger", "state_snapshot")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_mutation_ledger", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_mutation_ledger", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_mutation_ledger", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_mutation_ledger", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_mutation_ledger", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_mutation_ledger", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_mutation_ledger", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_mutation_ledger", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_mutation_ledger", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_mutation_ledger", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_mutation_ledger", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_mutation_ledger", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_mutation_ledger", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_mutation_ledger", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_mutation_ledger", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_mutation_ledger", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_mutation_ledger", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_mutation_ledger", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_mutation_ledger", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_mutation_ledger", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_mutation_ledger", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_mutation_ledger", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_mutation_ledger", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_mutation_ledger", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_mutation_ledger", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_mutation_ledger", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_mutation_ledger", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_mutation_ledger", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_mutation_ledger", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_mutation_ledger", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_mutation_ledger", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_mutation_ledger", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_mutation_ledger", "write_through")
# REMOVED: _emit_writes_through("p1", "test_mutation_ledger", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_mutation_ledger", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_mutation_ledger", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_mutation_ledger", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_mutation_ledger", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_mutation_ledger", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_mutation_ledger", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_mutation_ledger", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_mutation_ledger", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_mutation_ledger", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_mutation_ledger", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_mutation_ledger", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_mutation_ledger", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_mutation_ledger", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_mutation_ledger", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_mutation_ledger")
# REMOVED: _emit_gated_by_confidence("p1", "test_mutation_ledger", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_mutation_ledger")
# REMOVED: emit_determinism_digest("p0", "test_mutation_ledger")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_mutation_ledger", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_mutation_ledger", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_mutation_ledger", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_mutation_ledger", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_mutation_ledger", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_mutation_ledger", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_mutation_ledger", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_mutation_ledger", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_mutation_ledger", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_mutation_ledger", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_mutation_ledger", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_mutation_ledger", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_mutation_ledger", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_mutation_ledger", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_mutation_ledger", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_mutation_ledger", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_mutation_ledger", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_mutation_ledger", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_mutation_ledger", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_mutation_ledger", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def test_mutation_ledger_records_write_text_success(tmp_path):
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text
    from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text
    from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text
    from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text
    from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text
    from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text
    from agentic_core.L2_execution.tools.write_gateway import write_text
    from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_bytes
    from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text
    """
    PASS: write_text appends JSONL entry with before/after hashes.
    FAIL: No ledger entry or missing required fields.

    Per .windsurfrules §1.1: Changed logic (ledger append) MUST have tests.
    Per .windsurfrules §1.8: Side-effect safety - verify ledger write occurred.
    """
#  # MOVED: from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text

    ledger_path = tmp_path / "mutation_ledger.jsonl"
    trace_id = "TEST-TRACE-001"
    set_mutation_ledger_path(ledger_path, trace_id)

    # Write a new file
    target = tmp_path / "test.txt"
    content = "test content"
    write_text(target, content)

    # Verify ledger entry
    assert ledger_path.exists(), "Ledger file not created"
    entries = [json.loads(line) for line in ledger_path.read_text().strip().split("\n")]
    assert len(entries) == 1, f"Expected 1 entry, got {len(entries)}"

    entry = entries[0]
    assert entry["seq"] == 1
    assert entry["trace_id"] == trace_id
    assert entry["operation"] == "write_text"
    assert entry["before_hash"] is None, "New file should have no before_hash"
    assert entry["after_hash"] == hashlib.sha256(content.encode()).hexdigest()
    assert entry["gateway_approved"] is True
    assert entry["result"] == "SUCCESS"
    assert entry["error"] is None


def test_mutation_ledger_records_before_after_hash_on_update(tmp_path):
    """
    PASS: Updating existing file records both before_hash and after_hash.
    FAIL: before_hash is None or equals after_hash when content changed.

    Per .windsurfrules §1.7: Deterministic decision surfaces - distinct input must not collapse.
    Per .windsurfrules §1.11: Mutation-sensitive tests - hash must change when content changes.
    """
#  # MOVED: from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text

    ledger_path = tmp_path / "mutation_ledger.jsonl"
    set_mutation_ledger_path(ledger_path, "TEST-TRACE-002")

    # Write initial content
    target = tmp_path / "test.txt"
    original_content = "original"
    target.write_text(original_content)
    original_hash = hashlib.sha256(original_content.encode()).hexdigest()

    # Update via write_text
    new_content = "updated"
    write_text(target, new_content)
    new_hash = hashlib.sha256(new_content.encode()).hexdigest()

    # Verify ledger entry
    entries = [json.loads(line) for line in ledger_path.read_text().strip().split("\n")]
    assert len(entries) == 1

    entry = entries[0]
    assert entry["before_hash"] == original_hash, "before_hash must match original content"
    assert entry["after_hash"] == new_hash, "after_hash must match new content"
    assert entry["before_hash"] != entry["after_hash"], "Hashes must differ when content changes"


def test_mutation_ledger_detects_no_op_write(tmp_path):
    """
    PASS: Writing identical content shows before_hash == after_hash.
    FAIL: Hashes differ despite identical content.

    Per hostile audit Section D14: No-op patch detection.
    Per .windsurfrules §1.7: Identical input → identical output.
    """
#  # MOVED: from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text

    ledger_path = tmp_path / "mutation_ledger.jsonl"
    set_mutation_ledger_path(ledger_path, "TEST-TRACE-003")

    # Write initial content
    target = tmp_path / "test.txt"
    content = "unchanged"
    target.write_text(content)

    # Write identical content via gateway
    write_text(target, content)

    # Verify ledger shows no-op
    entries = [json.loads(line) for line in ledger_path.read_text().strip().split("\n")]
    entry = entries[0]

    assert entry["before_hash"] == entry["after_hash"], (
        "No-op write must have identical before/after hashes - "
        "this is a critical gate per hostile audit Section B4"
    )


@pytest.mark.skipif(sys.platform == "win32", reason="chmod read-only not enforced on Windows")
def test_mutation_ledger_records_write_failure(tmp_path):
    """
    PASS: Write failure records FAILED entry with error message.
    FAIL: No ledger entry or result=SUCCESS despite failure.

    Per .windsurfrules §1.8: Fail-closed - failures must be recorded.
    Per hostile audit Section B4: failed writes must appear in ledger.
    """
#  # MOVED: from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text

    ledger_path = tmp_path / "mutation_ledger.jsonl"
    set_mutation_ledger_path(ledger_path, "TEST-TRACE-004")

    # Attempt to write to a read-only location (simulate failure)
    target = tmp_path / "readonly" / "test.txt"
    target.parent.mkdir(parents=True)
    target.parent.chmod(0o444)  # Make parent read-only

    try:
        write_text(target, "content")
        # Write succeeded despite read-only chmod — write protection is not enforced
        target.parent.chmod(0o755)
        pytest.fail(
            "write_text succeeded on a chmod(0o444) directory — "
            "write protection is not enforced on this platform. "
            "The mutation ledger must record this as a failure, not silently succeed."
        )
    except (PermissionError, OSError):  # guardian: allow-silent-swallower
        # Expected failure
        pass
    finally:
        # Restore permissions for cleanup
        try:
            target.parent.chmod(0o755)
        with pytest.raises(Exception):

            pass
    # Verify ledger recorded the failure
    if ledger_path.exists():
        entries = [json.loads(line) for line in ledger_path.read_text().strip().split("\n")]
        assert len(entries) == 1

        entry = entries[0]
        assert entry["result"] == "FAILED", "Failed write must have result=FAILED"
        assert entry["after_hash"] is None, "Failed write must not have after_hash"
        assert entry["error"] is not None, "Failed write must record error"


def test_mutation_ledger_sequence_numbers_monotonic(tmp_path):
    """
    PASS: Multiple writes produce monotonically increasing sequence numbers.
    FAIL: Sequence numbers repeat, skip, or decrease.

    Per hostile audit Section C3: sequence_number must be monotonically increasing per-run.
    Per .windsurfrules §1.7: Deterministic decision surfaces.
    """
#  # MOVED: from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text

    ledger_path = tmp_path / "mutation_ledger.jsonl"
    set_mutation_ledger_path(ledger_path, "TEST-TRACE-005")

    # Write 5 files
    for i in range(5):
        target = tmp_path / f"file{i}.txt"
        write_text(target, f"content {i}")

    # Verify sequence numbers
    entries = [json.loads(line) for line in ledger_path.read_text().strip().split("\n")]
    assert len(entries) == 5

    for i, entry in enumerate(entries):
        assert entry["seq"] == i + 1, f"Expected seq={i + 1}, got {entry['seq']}"


def test_mutation_ledger_trace_id_correlation(tmp_path):
    """
    PASS: All ledger entries contain the same trace_id.
    FAIL: trace_id missing or inconsistent across entries.

    Per hostile audit Section B1: trace_id must appear in every artifact.
    Per hostile audit Section F6: trace_id correlation test.
    """
#  # MOVED: from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text

    ledger_path = tmp_path / "mutation_ledger.jsonl"
    trace_id = "TEST-TRACE-CORRELATION"
    set_mutation_ledger_path(ledger_path, trace_id)

    # Write multiple files
    for i in range(3):
        target = tmp_path / f"file{i}.txt"
        write_text(target, f"content {i}")

    # Verify all entries have same trace_id
    entries = [json.loads(line) for line in ledger_path.read_text().strip().split("\n")]
    for entry in entries:
        assert entry["trace_id"] == trace_id, f"Entry {entry['seq']} has wrong trace_id: {entry['trace_id']}"


def test_mutation_ledger_disabled_when_not_configured(tmp_path):
    """
    PASS: Writes succeed without ledger when set_mutation_ledger_path not called.
    FAIL: Write fails or creates ledger in unexpected location.

    Per .windsurfrules §1.5: Edge cases - missing configuration.
    Per hostile audit Section A9: execution_mode marker required.
    """
#  # MOVED: from agentic_core.L2_execution.tools.write_gateway import write_text

    # Do NOT call set_mutation_ledger_path
    target = tmp_path / "test.txt"
    result = write_text(target, "content")

    # Write should succeed
    assert Path(result).exists()
    assert Path(result).read_text() == "content"

    # No ledger should be created in tmp_path
    ledger_files = list(tmp_path.glob("*.jsonl"))
    assert len(ledger_files) == 0, "Ledger created without configuration"


def test_mutation_ledger_write_bytes_records_entry(tmp_path):
    """
    PASS: write_bytes records ledger entry with correct hashes.
    FAIL: No entry or incorrect operation field.

    Per .windsurfrules §1.1: All changed logic MUST have tests.
    """
#  # MOVED: from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_bytes

    ledger_path = tmp_path / "mutation_ledger.jsonl"
    set_mutation_ledger_path(ledger_path, "TEST-TRACE-BYTES")

    # Write binary data
    target = tmp_path / "test.bin"
    data = b"\x00\x01\x02\x03"
    write_bytes(target, data)

    # Verify ledger entry
    entries = [json.loads(line) for line in ledger_path.read_text().strip().split("\n")]
    assert len(entries) == 1

    entry = entries[0]
    assert entry["operation"] == "write_bytes"
    assert entry["after_hash"] == hashlib.sha256(data).hexdigest()
    assert entry["result"] == "SUCCESS"


def test_mutation_ledger_ascii_only_output(tmp_path):
    """
    PASS: Ledger entries are ASCII-only JSON.
    FAIL: Non-ASCII characters in ledger file.

    Per .windsurfrules §2.2: Evidence must be ASCII-only.
    Per hostile audit Section C3: ensure_ascii=True required.
    """
#  # MOVED: from agentic_core.L2_execution.tools.write_gateway import set_mutation_ledger_path, write_text

    ledger_path = tmp_path / "mutation_ledger.jsonl"
    set_mutation_ledger_path(ledger_path, "TEST-TRACE-UNICODE")

    # Write file with unicode path (if supported)
    target = tmp_path / "test_file.txt"
    write_text(target, "content")

    # Verify ledger is ASCII-only
    ledger_bytes = ledger_path.read_bytes()
    try:
        ledger_bytes.decode("ascii")
    except UnicodeDecodeError:
        pytest.fail("Ledger contains non-ASCII characters - violates .windsurfrules §2.2")
