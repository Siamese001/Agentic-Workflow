"""
Unit tests for tools/capture_evidence.py - PowerShell detection.
"""

from unittest.mock import MagicMock, patch

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_capture_evidence")
# REMOVED: _emit_applies_guardrail("p0", "test_capture_evidence", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_capture_evidence", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_capture_evidence", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_capture_evidence")
# REMOVED: emit_determinism_digest("p0", "test_capture_evidence")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_capture_evidence", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_capture_evidence", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_capture_evidence", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_capture_evidence", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_capture_evidence", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_capture_evidence", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_capture_evidence", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_capture_evidence", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_capture_evidence", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_capture_evidence", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_capture_evidence", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_capture_evidence", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_capture_evidence", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_capture_evidence", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_capture_evidence", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_capture_evidence", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_capture_evidence", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_capture_evidence", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_capture_evidence", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_capture_evidence", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Import the module under test via proper package path
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
from tools.capture_evidence import capture_command

# REMOVED: _emit_emits_metric_event("test_capture_evidence", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_capture_evidence", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_capture_evidence", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_capture_evidence", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_capture_evidence", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_capture_evidence", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_capture_evidence", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_capture_evidence", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_capture_evidence", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_capture_evidence", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_capture_evidence", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_capture_evidence", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_capture_evidence", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_capture_evidence", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_capture_evidence", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_capture_evidence", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_capture_evidence", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_capture_evidence", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_capture_evidence", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_capture_evidence", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_capture_evidence", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_capture_evidence", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_capture_evidence", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_capture_evidence", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_capture_evidence", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_capture_evidence", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_capture_evidence", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_capture_evidence", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_capture_evidence", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_capture_evidence", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_capture_evidence", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_capture_evidence", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_capture_evidence", "write_through")
# REMOVED: _emit_writes_through("p1", "test_capture_evidence", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_capture_evidence", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_capture_evidence", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_capture_evidence", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_capture_evidence", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_capture_evidence", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_capture_evidence", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_capture_evidence", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_capture_evidence", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_capture_evidence", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_capture_evidence", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_capture_evidence", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_capture_evidence", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_capture_evidence", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_capture_evidence", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_capture_evidence")
# REMOVED: _emit_gated_by_confidence("p1", "test_capture_evidence", "confidence_gate")


@pytest.mark.unit_min_deps
class TestCaptureEvidence:
    """Test suite for capture_evidence.py."""

    def test_powershell_string_abort(self, tmp_path):
        """Test that capture_command aborts if output contains 'powershell' or 'pwsh'."""
        evidence_file = tmp_path / "evidence.md"

        # Mock subprocess.run to return output with "powershell"
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "This output contains powershell in it"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(RuntimeError, match="PowerShell detected"):
                capture_command(["echo", "test"], evidence_file)

    def test_pwsh_string_abort(self, tmp_path):
        """Test that capture_command aborts if output contains 'pwsh'."""
        evidence_file = tmp_path / "evidence.md"

        # Mock subprocess.run to return output with "pwsh"
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = "pwsh: command not found"

        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(RuntimeError, match="PowerShell detected"):
                capture_command(["echo", "test"], evidence_file)

    def test_clean_output_no_abort(self, tmp_path):
        """Test that capture_command succeeds with clean output."""
        evidence_file = tmp_path / "evidence.md"

        # Mock subprocess.run to return clean output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Clean output without shell references"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            exit_code = capture_command(["echo", "test"], evidence_file)
            assert exit_code == 0

            # Verify evidence file was created
            assert evidence_file.exists()
            content = evidence_file.read_text()
            assert "Clean output without shell references" in content

    def test_case_insensitive_detection(self, tmp_path):
        """Test that PowerShell detection is case-insensitive."""
        evidence_file = tmp_path / "evidence.md"

        # Mock subprocess.run to return output with "PowerShell" (mixed case)
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "PowerShell is detected"
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            with pytest.raises(RuntimeError, match="PowerShell detected"):
                capture_command(["echo", "test"], evidence_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
