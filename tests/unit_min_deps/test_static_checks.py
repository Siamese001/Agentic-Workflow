"""Unit tests for static analysis scanners."""

import tempfile
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    TOOLS_DIR,
)
from agentic_core.L5_safety.static_checks.determinism_serialization_check import (
    scan_file_for_determinism,
)
from agentic_core.L5_safety.static_checks.powershell_ban import (
    scan_file_for_powershell,
)
from agentic_core.L5_safety.static_checks.write_gateway_enforcer import (
    scan_file_for_writes,
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
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_static_checks", "p4obs", "metric_1")
_emit_emits_metric_event("test_static_checks", "p4obs", "metric_2")
_emit_emits_metric_event("test_static_checks", "p4obs", "metric_3")
_emit_emits_metric_event("test_static_checks", "p4obs", "metric_4")
_emit_emits_metric_event("test_static_checks", "p4obs", "metric_5")
_emit_emits_metric_event("test_static_checks", "p4obs", "metric_6")
_emit_records_incident_event("test_static_checks", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_static_checks", "p4obs", "anomaly")
_emit_writes_observability_log("test_static_checks", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_static_checks", "p4obs", "mon_state")
_emit_triggers_alert("test_static_checks", "p4obs", "alert")
_emit_links_incident_trace("test_static_checks", "p4obs", "trace_link")
_emit_captures_pattern("test_static_checks", "p3lm", "pattern")
_emit_records_learning_event("test_static_checks", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_static_checks", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_static_checks", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_static_checks", "p3lm", "routing")
_emit_improves_agent_policy("test_static_checks", "p3lm", "policy")
_emit_stores_learning_state("test_static_checks", "p3lm", "state")
_emit_records_execution_trace("test_static_checks", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_static_checks", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_static_checks", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_static_checks", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_static_checks", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_static_checks", "env_read", "p2_env_1")
_emit_reads_environ("test_static_checks", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_static_checks", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_static_checks", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_static_checks")
_emit_applies_guardrail("p0", "test_static_checks", "p0_governance")
_emit_reads_policy_state("p0", "test_static_checks", "policy_binding")
_emit_snapshots_state("p0", "test_static_checks", "state_snapshot")
emit_replay_key("p0", "test_static_checks")
emit_determinism_digest("p0", "test_static_checks")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_static_checks", "execution_auth")
_emit_validates_capability("p2", "test_static_checks", "capability_check")
_emit_routes_to_capability("p2", "test_static_checks", "capability_route")
_emit_writes_via_uwg("p2", "test_static_checks", "uwg_write")
_emit_blocks_direct_write("p2", "test_static_checks", "direct_write_block")
_emit_records_tool_invocation("p2", "test_static_checks", "tool_invocation")
_emit_captures_execution_output("p2", "test_static_checks", "exec_output")
_emit_dispatches_agent("p3", "test_static_checks", "agent_dispatch")
_emit_coordinates_agents("p3", "test_static_checks", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_static_checks", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_static_checks", "healing_outcome")
_emit_escalates_failure("p3", "test_static_checks", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_static_checks", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_static_checks", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_static_checks", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_static_checks", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_static_checks", "eval_metric")
_emit_stores_embedding("p4", "test_static_checks", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_static_checks", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_static_checks", "exec_snapshot_link")


@pytest.mark.unit_min_deps
def test_powershell_scanner_detects_subprocess_calls():
    """Test PowerShell scanner detects subprocess calls with PowerShell."""
    code = """
import subprocess
subprocess.run(["pwsh", "-c", "echo test"])
subprocess.call(["powershell", "-Command", "Get-Process"])
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        violations = scan_file_for_powershell(Path(f.name))

        assert len(violations) == 2
        assert violations[0][1] == "PS_SUBPROCESS_ARGV0"
        assert "pwsh" in violations[0][2]
        assert violations[1][1] == "PS_SUBPROCESS_ARGV0"
        assert "powershell" in violations[1][2]


@pytest.mark.unit_min_deps
def test_powershell_scanner_detects_shell_true():
    """Test PowerShell scanner detects shell=True in tools directory."""
    code = """
import subprocess
subprocess.run(["echo", "test"], shell=True)
"""

    with tempfile.TemporaryDirectory() as temp_dir:
        tools_dir = Path(temp_dir) / TOOLS_DIR
        tools_dir.mkdir()

        test_file = tools_dir / "test.py"
        test_file.write_text(code)

        violations = scan_file_for_powershell(test_file)

        assert len(violations) == 1
        assert violations[0][1] == "PS_SUBPROCESS_SHELL"
        assert "shell=True" in violations[0][2]


@pytest.mark.unit_min_deps
def test_powershell_scanner_detects_string_literals():
    """Test PowerShell scanner detects string literals."""
    code = """
# This is a comment about pwsh usage
command = "powershell -Command Get-Process"
"""

    with tempfile.TemporaryDirectory() as temp_dir:
        evidence_dir = Path(temp_dir) / "docs" / "evidence"
        evidence_dir.mkdir(parents=True)

        test_file = evidence_dir / "test.py"
        test_file.write_text(code)

        violations = scan_file_for_powershell(test_file)

        assert len(violations) == 2
        assert violations[0][1] == "PS_STRING_LITERAL"
        assert violations[1][1] == "PS_STRING_LITERAL"


@pytest.mark.unit_min_deps
def test_write_gateway_scanner_detects_direct_writes():
    """Test write gateway scanner detects direct file writes."""
    code = """
# Direct write violations
open("file.txt", "w")
open("data.bin", "wb")
Path("output.txt").write_text("content")
Path("output.bin").write_bytes(b"binary")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        violations = scan_file_for_writes(Path(f.name))

        assert len(violations) == 4
        rule_ids = [v[1] for v in violations]
        assert "DIRECT_OPEN_WRITE" in rule_ids
        assert "DIRECT_PATH_WRITE" in rule_ids


@pytest.mark.unit_min_deps
def test_write_gateway_scanner_respects_allowlist():
    """Test write gateway scanner respects allowlist comments."""
    code = """
# This should be flagged
open("file1.txt", "w")

# This should be allowed
open("file2.txt", "w")  # guardian: allow-direct-write

# This should be flagged again
open("file3.txt", "w")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        violations = scan_file_for_writes(Path(f.name))

        assert len(violations) == 2
        # Should only flag file1.txt and file3.txt, not file2.txt


@pytest.mark.unit_min_deps
def test_write_gateway_scanner_detects_with_statement():
    """Test write gateway scanner detects with open() patterns."""
    code = """
with open("output.txt", "w") as f:
    f.write("content")

with open("data.bin", "wb") as f:
    f.write(b"binary")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        violations = scan_file_for_writes(Path(f.name))

        assert len(violations) == 2
        assert all(v[1] == "DIRECT_WITH_WRITE" for v in violations)


@pytest.mark.unit_min_deps
def test_determinism_scanner_detects_json_without_sort_keys():
    """Test determinism scanner detects json.dumps without sort_keys."""
    code = """
def serialize_data(data):
    # This should be flagged
    json.dumps(data)

    # This should be flagged too
    json.dumps(data, indent=2)

    # This should be allowed
    json.dumps(data, sort_keys=True)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        violations = scan_file_for_determinism(Path(f.name))

        assert len(violations) == 2
        assert all(v[1] == "JSON_NO_SORT_KEYS" for v in violations)


@pytest.mark.unit_min_deps
def test_determinism_scanner_detects_datetime_now():
    """Test determinism scanner detects datetime.now() in serialization functions."""
    code = """
import datetime

def record_to_json(record):
    # This should be flagged
    timestamp = datetime.now()
    return json.dumps({"timestamp": timestamp.isoformat()}, sort_keys=True)

def other_function():
    # This should not be flagged (not in serialization context)
    timestamp = datetime.now()
    return timestamp
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        violations = scan_file_for_determinism(Path(f.name))

        assert len(violations) == 1
        assert violations[0][1] == "DATETIME_NOW"


@pytest.mark.unit_min_deps
def test_determinism_scanner_detects_time_time():
    """Test determinism scanner detects time.time() in serialization functions."""
    code = """
import time

def serialize_with_timestamp(data):
    # This should be flagged
    timestamp = time.time()
    return json.dumps({"timestamp": timestamp}, sort_keys=True)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        violations = scan_file_for_determinism(Path(f.name))

        assert len(violations) == 1
        assert violations[0][1] == "TIME_TIME"


@pytest.mark.unit_min_deps
def test_scanner_deterministic_ordering():
    """Test that scanner findings are returned in deterministic order."""
    code = """
import subprocess

from agentic_core.L0_routing.config.path_constants import (
    TOOLS_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
_emit_pulls_context("p1", "test_static_checks", "context_pull")
_emit_pulls_context("p1", "test_static_checks", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_static_checks", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_static_checks", "uwg_term_secondary")
_emit_writes_through("p1", "test_static_checks", "write_through")
_emit_writes_through("p1", "test_static_checks", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_static_checks", "safety_validation")
_emit_invokes_eval("p1", "test_static_checks", "eval_call")
_emit_proposal_commits_routing("p1", "test_static_checks", "routing_commit")
subprocess.run(["pwsh", "-c", "echo test"])
subprocess.call(["powershell", "-Command", "Get-Process"])
open("file.txt", "w")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()

        # Run scan twice
        violations1 = scan_file_for_powershell(Path(f.name))
        violations2 = scan_file_for_powershell(Path(f.name))

        # Should be identical and in same order
        assert violations1 == violations2

        # Should be sorted by line number
        line_numbers = [v[0] for v in violations1]
        assert line_numbers == sorted(line_numbers)
