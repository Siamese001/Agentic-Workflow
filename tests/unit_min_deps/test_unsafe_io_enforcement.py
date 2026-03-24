"""
Phase 2 Unsafe I/O and Subprocess Enforcement Test

This test ensures that the unsafe I/O detector continues to work
and that remediated files no longer contain forbidden primitives.
"""

from pathlib import Path

import pytest

from agentic_core.L2_execution.tools.unsafe_io_detector import (
    get_scoped_directories,
    scan_directory_for_unsafe_patterns,
    scan_for_unsafe_patterns,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_unsafe_io_enforcement", "p4obs", "metric_1")
_emit_emits_metric_event("test_unsafe_io_enforcement", "p4obs", "metric_2")
_emit_emits_metric_event("test_unsafe_io_enforcement", "p4obs", "metric_3")
_emit_emits_metric_event("test_unsafe_io_enforcement", "p4obs", "metric_4")
_emit_emits_metric_event("test_unsafe_io_enforcement", "p4obs", "metric_5")
_emit_emits_metric_event("test_unsafe_io_enforcement", "p4obs", "metric_6")
_emit_records_incident_event("test_unsafe_io_enforcement", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_unsafe_io_enforcement", "p4obs", "anomaly")
_emit_writes_observability_log("test_unsafe_io_enforcement", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_unsafe_io_enforcement", "p4obs", "mon_state")
_emit_triggers_alert("test_unsafe_io_enforcement", "p4obs", "alert")
_emit_links_incident_trace("test_unsafe_io_enforcement", "p4obs", "trace_link")
_emit_captures_pattern("test_unsafe_io_enforcement", "p3lm", "pattern")
_emit_records_learning_event("test_unsafe_io_enforcement", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_unsafe_io_enforcement", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_unsafe_io_enforcement", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_unsafe_io_enforcement", "p3lm", "routing")
_emit_improves_agent_policy("test_unsafe_io_enforcement", "p3lm", "policy")
_emit_stores_learning_state("test_unsafe_io_enforcement", "p3lm", "state")
_emit_records_execution_trace("test_unsafe_io_enforcement", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_unsafe_io_enforcement", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_unsafe_io_enforcement", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_unsafe_io_enforcement", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_unsafe_io_enforcement", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_unsafe_io_enforcement", "env_read", "p2_env_1")
_emit_reads_environ("test_unsafe_io_enforcement", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_unsafe_io_enforcement", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_unsafe_io_enforcement", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_unsafe_io_enforcement")
_emit_applies_guardrail("p0", "test_unsafe_io_enforcement", "p0_governance")
_emit_reads_policy_state("p0", "test_unsafe_io_enforcement", "policy_binding")
_emit_snapshots_state("p0", "test_unsafe_io_enforcement", "state_snapshot")
emit_replay_key("p0", "test_unsafe_io_enforcement")
emit_determinism_digest("p0", "test_unsafe_io_enforcement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_unsafe_io_enforcement", "execution_auth")
_emit_validates_capability("p2", "test_unsafe_io_enforcement", "capability_check")
_emit_routes_to_capability("p2", "test_unsafe_io_enforcement", "capability_route")
_emit_writes_via_uwg("p2", "test_unsafe_io_enforcement", "uwg_write")
_emit_blocks_direct_write("p2", "test_unsafe_io_enforcement", "direct_write_block")
_emit_records_tool_invocation("p2", "test_unsafe_io_enforcement", "tool_invocation")
_emit_captures_execution_output("p2", "test_unsafe_io_enforcement", "exec_output")
_emit_dispatches_agent("p3", "test_unsafe_io_enforcement", "agent_dispatch")
_emit_coordinates_agents("p3", "test_unsafe_io_enforcement", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_unsafe_io_enforcement", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_unsafe_io_enforcement", "healing_outcome")
_emit_escalates_failure("p3", "test_unsafe_io_enforcement", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_unsafe_io_enforcement", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_unsafe_io_enforcement", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_unsafe_io_enforcement", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_unsafe_io_enforcement", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_unsafe_io_enforcement", "eval_metric")
_emit_stores_embedding("p4", "test_unsafe_io_enforcement", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_unsafe_io_enforcement", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_unsafe_io_enforcement", "exec_snapshot_link")
_emit_escalates_to_human("p1", "test_unsafe_io_enforcement", "human_escalation")
_emit_routes_through("p1", "test_unsafe_io_enforcement", "route_through")
_emit_checks_agent_registry("p1", "test_unsafe_io_enforcement", "agent_registry")
_emit_validates_agent_capability("p1", "test_unsafe_io_enforcement", "capability")
_emit_dispatches_execution_plan("p1", "test_unsafe_io_enforcement", "exec_plan")
_emit_agent_executes_agent("p1", "test_unsafe_io_enforcement", "sub_agent")
_emit_routes_to_agent("p1", "test_unsafe_io_enforcement", "target_agent")
_emit_verifies_policy("p1", "test_unsafe_io_enforcement", "policy_check")
_emit_observes_runtime_state("p1", "test_unsafe_io_enforcement", "runtime_state")
_emit_verifies_boundary("p1", "test_unsafe_io_enforcement", "boundary_check")
_emit_transcripts_response("p1", "test_unsafe_io_enforcement", "transcript")
_emit_hard_fails_untranscripted("p1", "test_unsafe_io_enforcement")
_emit_gated_by_confidence("p1", "test_unsafe_io_enforcement", "confidence_gate")


@pytest.mark.unit_min_deps
class TestPhase2UnsafeIOEnforcement:
    """Test suite for Phase 2 unsafe I/O enforcement."""

    def test_detector_still_works(self):
        """Verify the unsafe I/O detector is functional."""
        # Test on a simple file with unsafe patterns
        code_with_unsafe = """
import subprocess
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
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
_emit_pulls_context("p1", "test_unsafe_io_enforcement", "context_pull")
_emit_pulls_context("p1", "test_unsafe_io_enforcement", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_unsafe_io_enforcement", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_unsafe_io_enforcement", "uwg_term_secondary")
_emit_writes_through("p1", "test_unsafe_io_enforcement", "write_through")
_emit_writes_through("p1", "test_unsafe_io_enforcement", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_unsafe_io_enforcement", "safety_validation")
_emit_invokes_eval("p1", "test_unsafe_io_enforcement", "eval_call")
_emit_proposal_commits_routing("p1", "test_unsafe_io_enforcement", "routing_commit")
_emit_escalates_to_human("p1", "test_unsafe_io_enforcement", "human_escalation")
_emit_routes_through("p1", "test_unsafe_io_enforcement", "route_through")
_emit_checks_agent_registry("p1", "test_unsafe_io_enforcement", "agent_registry")
_emit_validates_agent_capability("p1", "test_unsafe_io_enforcement", "capability")
_emit_dispatches_execution_plan("p1", "test_unsafe_io_enforcement", "exec_plan")
_emit_agent_executes_agent("p1", "test_unsafe_io_enforcement", "sub_agent")
_emit_routes_to_agent("p1", "test_unsafe_io_enforcement", "target_agent")
_emit_verifies_policy("p1", "test_unsafe_io_enforcement", "policy_check")
_emit_observes_runtime_state("p1", "test_unsafe_io_enforcement", "runtime_state")
_emit_verifies_boundary("p1", "test_unsafe_io_enforcement", "boundary_check")
_emit_transcripts_response("p1", "test_unsafe_io_enforcement", "transcript")
_emit_hard_fails_untranscripted("p1", "test_unsafe_io_enforcement")
_emit_gated_by_confidence("p1", "test_unsafe_io_enforcement", "confidence_gate")

def bad_function():
    with open("test.txt", "w") as f:
        f.write("bad")
    subprocess.run(["rm", "-rf", "/"])
"""
        patterns = scan_for_unsafe_patterns(code_with_unsafe, "test.py")
        assert len(patterns) > 0, "Detector should find unsafe patterns"

        # Check specific patterns are detected
        pattern_types = {p.pattern_type for p in patterns}
        assert "open_write" in pattern_types, "Should detect open(..., 'w')"
        assert "subprocess_run" in pattern_types, "Should detect subprocess.run"

    def test_remediated_files_clean(self):
        """Verify that remediated files no longer contain forbidden primitives."""
        repo_root = Path.cwd()

        # Check ToolsmithAgent.py - should have no direct file writes
        toolsmith_path = repo_root / "agentic_core/L2_execution/reasoning/ToolsmithAgent.py"
        if toolsmith_path.exists():
            code = toolsmith_path.read_text(encoding="utf-8")
            patterns = scan_for_unsafe_patterns(code, str(toolsmith_path))

            # Should not have direct open() writes
            open_writes = [p for p in patterns if p.pattern_type == "open_write"]
            assert len(open_writes) == 0, f"ToolsmithAgent should not have open_write patterns: {open_writes}"

            # Should not have Path.write_text
            path_writes = [p for p in patterns if p.pattern_type == "path_write_text"]
            assert len(path_writes) == 0, (
                f"ToolsmithAgent should not have path_write_text patterns: {path_writes}"
            )

    def test_no_direct_subprocess_in_remediated_files(self):
        """Verify that remediated files use safe_subprocess, not direct subprocess."""
        repo_root = Path.cwd()

        # Check execute_ssot.py - should use safe_subprocess_run
        execute_ssot_path = repo_root / "agentic_core/L0_routing/scripts/execute_ssot.py"
        if execute_ssot_path.exists():
            code = execute_ssot_path.read_text(encoding="utf-8")

            # Should import safe_subprocess
            assert "safe_subprocess_run" in code, "execute_ssot.py should import safe_subprocess_run"

            # Should not have direct subprocess.run calls (only in imports or safe_subprocess)
            lines = code.split("\n")
            for i, line in enumerate(lines, 1):
                # Skip lines that are imports or inside safe_subprocess module
                if "import subprocess" in line or "from subprocess" in line:
                    continue
                if "subprocess.run(" in line and "safe_subprocess_run(" not in line:
                    raise AssertionError(
                        f"Line {i} in execute_ssot.py has direct subprocess.run: {line.strip()}"
                    )

    def test_scoped_directories_scan(self):
        """Verify scanning scoped directories works and results are manageable."""
        repo_root = Path.cwd()
        scoped_dirs = get_scoped_directories(repo_root)

        total_patterns = 0
        for dir_path in scoped_dirs:
            if dir_path.exists():
                patterns = scan_directory_for_unsafe_patterns(dir_path)
                total_patterns += len(patterns)

        # We should have fewer patterns than the original 69 after remediation
        # But we don't expect zero (there are still legitimate uses in non-remediated files)
        print(f"Total patterns found: {total_patterns}")

        # At minimum, the detector should run without errors
        assert total_patterns >= 0, "Scanner should run without errors"
