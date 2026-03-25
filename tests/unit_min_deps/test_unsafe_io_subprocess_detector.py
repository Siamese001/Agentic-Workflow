"""
AST-based detector for unsafe I/O and subprocess usage in agent-executed code paths.

This test ensures that agent code does not use direct file I/O or subprocess primitives
that could bypass the mutation fence and write to protected roots.
"""

import sys
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TOOLS_DIR,
)
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_unsafe_io_subprocess_detector")
# REMOVED: _emit_applies_guardrail("p0", "test_unsafe_io_subprocess_detector", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_unsafe_io_subprocess_detector", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_unsafe_io_subprocess_detector", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_unsafe_io_subprocess_detector")
# REMOVED: emit_determinism_digest("p0", "test_unsafe_io_subprocess_detector")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_unsafe_io_subprocess_detector", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_unsafe_io_subprocess_detector", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_unsafe_io_subprocess_detector", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_unsafe_io_subprocess_detector", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_unsafe_io_subprocess_detector", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_unsafe_io_subprocess_detector", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_unsafe_io_subprocess_detector", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_unsafe_io_subprocess_detector", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_unsafe_io_subprocess_detector", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_unsafe_io_subprocess_detector", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_unsafe_io_subprocess_detector", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_unsafe_io_subprocess_detector", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_unsafe_io_subprocess_detector", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_unsafe_io_subprocess_detector", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_unsafe_io_subprocess_detector", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_unsafe_io_subprocess_detector", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_unsafe_io_subprocess_detector", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_unsafe_io_subprocess_detector", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_unsafe_io_subprocess_detector", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_unsafe_io_subprocess_detector", "exec_snapshot_link")

# Add repo root to path for imports
repo_root = Path(__file__).resolve().parents[3]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from agentic_core.L2_execution.tools.unsafe_io_detector import (
    scan_for_unsafe_patterns,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_links_incident_trace,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
)

# REMOVED: _emit_emits_metric_event("test_unsafe_io_subprocess_detector", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_unsafe_io_subprocess_detector", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_unsafe_io_subprocess_detector", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_unsafe_io_subprocess_detector", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_unsafe_io_subprocess_detector", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_unsafe_io_subprocess_detector", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_unsafe_io_subprocess_detector", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_unsafe_io_subprocess_detector", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_unsafe_io_subprocess_detector", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_unsafe_io_subprocess_detector", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_unsafe_io_subprocess_detector", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_unsafe_io_subprocess_detector", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_unsafe_io_subprocess_detector", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_unsafe_io_subprocess_detector", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_unsafe_io_subprocess_detector", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_unsafe_io_subprocess_detector", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_unsafe_io_subprocess_detector", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_unsafe_io_subprocess_detector", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_unsafe_io_subprocess_detector", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_unsafe_io_subprocess_detector", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_unsafe_io_subprocess_detector", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_unsafe_io_subprocess_detector", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_unsafe_io_subprocess_detector", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_unsafe_io_subprocess_detector", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_unsafe_io_subprocess_detector", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_unsafe_io_subprocess_detector", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_unsafe_io_subprocess_detector", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_unsafe_io_subprocess_detector", "runtime_state", "p2_rt_2")
# REMOVED: _emit_escalates_to_human("p1", "test_unsafe_io_subprocess_detector", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_unsafe_io_subprocess_detector", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_unsafe_io_subprocess_detector", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_unsafe_io_subprocess_detector", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_unsafe_io_subprocess_detector", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_unsafe_io_subprocess_detector", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_unsafe_io_subprocess_detector", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_unsafe_io_subprocess_detector", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_unsafe_io_subprocess_detector", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_unsafe_io_subprocess_detector", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_unsafe_io_subprocess_detector", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_unsafe_io_subprocess_detector")
# REMOVED: _emit_gated_by_confidence("p1", "test_unsafe_io_subprocess_detector", "confidence_gate")


@pytest.mark.unit_min_deps
class TestUnsafeIOSubprocessDetector:
    """Test suite for unsafe I/O and subprocess detection."""

    def test_detector_finds_direct_file_writes(self):
        """Test that detector flags direct file write operations."""
        code = """
import os
from pathlib import Path

def write_something():
    # These should be flagged
    with open("file.txt", "w") as f:
        f.write("test")

    Path("file.txt").write_text("test")
    os.remove("file.txt")
    os.rename("old.txt", "new.txt")
    """
        findings = scan_for_unsafe_patterns(code, "test.py")

        # Should find multiple unsafe patterns
        assert len(findings) >= 4
        patterns = [f.pattern_type for f in findings]
        assert "open_write" in patterns
        assert "path_write_text" in patterns
        assert "os_remove" in patterns
        assert "os_rename" in patterns

    def test_detector_finds_subprocess_calls(self):
        """Test that detector flags subprocess execution primitives."""
        code = """
import subprocess

def run_something():
    # These should be flagged
    subprocess.run(["ls", "-la"])
    subprocess.call(["git", "status"])
    subprocess.Popen(["python", "script.py"])
    """
        findings = scan_for_unsafe_patterns(code, "test.py")

        # Should find subprocess patterns
        assert len(findings) >= 3
        patterns = [f.pattern_type for f in findings]
        assert "subprocess_run" in patterns
        assert "subprocess_call" in patterns
        assert "subprocess_Popen" in patterns

    def test_detector_ignores_safe_operations(self):
        """Test that detector ignores read-only operations and safe paths."""
        code = """
import os
from pathlib import Path
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
# REMOVED: _emit_pulls_context("p1", "test_unsafe_io_subprocess_detector", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_unsafe_io_subprocess_detector", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_unsafe_io_subprocess_detector", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_unsafe_io_subprocess_detector", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_unsafe_io_subprocess_detector", "write_through")
# REMOVED: _emit_writes_through("p1", "test_unsafe_io_subprocess_detector", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_unsafe_io_subprocess_detector", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_unsafe_io_subprocess_detector", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_unsafe_io_subprocess_detector", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_unsafe_io_subprocess_detector", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_unsafe_io_subprocess_detector", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_unsafe_io_subprocess_detector", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_unsafe_io_subprocess_detector", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_unsafe_io_subprocess_detector", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_unsafe_io_subprocess_detector", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_unsafe_io_subprocess_detector", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_unsafe_io_subprocess_detector", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_unsafe_io_subprocess_detector", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_unsafe_io_subprocess_detector", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_unsafe_io_subprocess_detector", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_unsafe_io_subprocess_detector")
# REMOVED: _emit_gated_by_confidence("p1", "test_unsafe_io_subprocess_detector", "confidence_gate")

def read_something():
    # These should NOT be flagged (read-only)
    with open("file.txt", "r") as f:
        content = f.read()

    Path("file.txt").read_text()

    # Safe path operations (no mutation)
    Path("file.txt").exists()
    os.path.exists("file.txt")
    """
        findings = scan_for_unsafe_patterns(code, "test.py")

        # Should not find any unsafe patterns
        assert len(findings) == 0

    def test_detector_scans_actual_agent_code(self):
        """Test that detector can scan actual agent code paths."""
        # Scan scoped areas for actual findings
        scoped_dirs = [
            repo_root / AGENTIC_CORE_DIR / "L0_routing" / "reasoning",
            repo_root / AGENTIC_CORE_DIR / "L1_cognition" / "reasoning",
            repo_root / AGENTIC_CORE_DIR / "L2_execution" / "reasoning",
            repo_root / AGENTIC_CORE_DIR / "L3_orchestration" / "reasoning",
            repo_root / APPS_LIC_DIR / "reasoning",
            repo_root / APPS_RG_DIR / "reasoning",
            repo_root / APPS_SHARED_DIR / "reasoning",
            repo_root / TOOLS_DIR,
            repo_root / AGENTIC_CORE_DIR / "L0_routing" / "scripts",
            repo_root / AGENTIC_CORE_DIR / "L1_cognition" / "scripts",
            repo_root / AGENTIC_CORE_DIR / "L2_execution" / "scripts",
        ]

        all_findings = []
        for dir_path in scoped_dirs:
            if dir_path.exists():
                for py_file in dir_path.rglob("*.py"):
                    if py_file.is_file():
                        try:
                            with open(py_file, encoding="utf-8") as f:
                                content = f.read()
                            findings = scan_for_unsafe_patterns(content, str(py_file.relative_to(repo_root)))
                            all_findings.extend(findings)
                        except (ValueError, TypeError, RuntimeError) as e:  # guardian: allow-silent-swallower
                            # Skip files that can't be read
                            pass

        # At minimum, we should find some patterns in the codebase
        # (This test documents the current state)
        print(f"\nFound {len(all_findings)} unsafe patterns in scoped areas:")
        for finding in all_findings[:10]:  # Show first 10
            print(f"  {finding.file_path}:{finding.line_number} - {finding.pattern_type}")

        if len(all_findings) > 10:
            print(f"  ... and {len(all_findings) - 10} more")

        # Store findings for evidence
        self.scoped_findings = all_findings

    def test_detector_enforcement(self):
        """Test that detector enforcement fails when unsafe patterns are present."""
        code_with_unsafe = """
def unsafe_function():
    open("test.txt", "w").write("bad")
"""

        # This should fail if we add enforcement
        findings = scan_for_unsafe_patterns(code_with_unsafe, "test.py")
        assert len(findings) > 0
        assert findings[0].pattern_type == "open_write"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
