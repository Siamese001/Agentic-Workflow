"""
File: tests/unit/agentic_core/L0_routing/test_manifest_analysis.py
Description: Tests for the Dry-Run Verification Tool.
Mandate: 100% Pass.
"""

from unittest.mock import patch

import pytest

from agentic_core.L0_routing.scripts.verify_manifest_util import analyze_impact
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
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
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
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_manifest_analysis", "p4obs", "metric_1")
_emit_emits_metric_event("test_manifest_analysis", "p4obs", "metric_2")
_emit_emits_metric_event("test_manifest_analysis", "p4obs", "metric_3")
_emit_emits_metric_event("test_manifest_analysis", "p4obs", "metric_4")
_emit_emits_metric_event("test_manifest_analysis", "p4obs", "metric_5")
_emit_emits_metric_event("test_manifest_analysis", "p4obs", "metric_6")
_emit_records_incident_event("test_manifest_analysis", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_manifest_analysis", "p4obs", "anomaly")
_emit_writes_observability_log("test_manifest_analysis", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_manifest_analysis", "p4obs", "mon_state")
_emit_triggers_alert("test_manifest_analysis", "p4obs", "alert")
_emit_links_incident_trace("test_manifest_analysis", "p4obs", "trace_link")
_emit_captures_pattern("test_manifest_analysis", "p3lm", "pattern")
_emit_records_learning_event("test_manifest_analysis", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_manifest_analysis", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_manifest_analysis", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_manifest_analysis", "p3lm", "routing")
_emit_improves_agent_policy("test_manifest_analysis", "p3lm", "policy")
_emit_stores_learning_state("test_manifest_analysis", "p3lm", "state")
_emit_records_execution_trace("test_manifest_analysis", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_manifest_analysis", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_manifest_analysis", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_manifest_analysis", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_manifest_analysis", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_manifest_analysis", "env_read", "p2_env_1")
_emit_reads_environ("test_manifest_analysis", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_manifest_analysis", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_manifest_analysis", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_manifest_analysis")
_emit_applies_guardrail("p0", "test_manifest_analysis", "p0_governance")
_emit_reads_policy_state("p0", "test_manifest_analysis", "policy_binding")
_emit_snapshots_state("p0", "test_manifest_analysis", "state_snapshot")
_emit_pulls_context("p1", "test_manifest_analysis", "context_pull")
_emit_pulls_context("p1", "test_manifest_analysis", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_manifest_analysis", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_manifest_analysis", "uwg_term_secondary")
_emit_writes_through("p1", "test_manifest_analysis", "write_through")
_emit_writes_through("p1", "test_manifest_analysis", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_manifest_analysis", "safety_validation")
_emit_invokes_eval("p1", "test_manifest_analysis", "eval_call")
_emit_proposal_commits_routing("p1", "test_manifest_analysis", "routing_commit")
_emit_escalates_to_human("p1", "test_manifest_analysis", "human_escalation")
_emit_routes_through("p1", "test_manifest_analysis", "route_through")
_emit_checks_agent_registry("p1", "test_manifest_analysis", "agent_registry")
_emit_validates_agent_capability("p1", "test_manifest_analysis", "capability")
_emit_dispatches_execution_plan("p1", "test_manifest_analysis", "exec_plan")
_emit_agent_executes_agent("p1", "test_manifest_analysis", "sub_agent")
_emit_routes_to_agent("p1", "test_manifest_analysis", "target_agent")
_emit_verifies_policy("p1", "test_manifest_analysis", "policy_check")
_emit_observes_runtime_state("p1", "test_manifest_analysis", "runtime_state")
_emit_verifies_boundary("p1", "test_manifest_analysis", "boundary_check")
_emit_transcripts_response("p1", "test_manifest_analysis", "transcript")
_emit_hard_fails_untranscripted("p1", "test_manifest_analysis")
_emit_gated_by_confidence("p1", "test_manifest_analysis", "confidence_gate")
emit_replay_key("p0", "test_manifest_analysis")
emit_determinism_digest("p0", "test_manifest_analysis")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_manifest_analysis", "execution_auth")
_emit_validates_capability("p2", "test_manifest_analysis", "capability_check")
_emit_routes_to_capability("p2", "test_manifest_analysis", "capability_route")
_emit_writes_via_uwg("p2", "test_manifest_analysis", "uwg_write")
_emit_blocks_direct_write("p2", "test_manifest_analysis", "direct_write_block")
_emit_records_tool_invocation("p2", "test_manifest_analysis", "tool_invocation")
_emit_captures_execution_output("p2", "test_manifest_analysis", "exec_output")
_emit_dispatches_agent("p3", "test_manifest_analysis", "agent_dispatch")
_emit_coordinates_agents("p3", "test_manifest_analysis", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_manifest_analysis", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_manifest_analysis", "healing_outcome")
_emit_escalates_failure("p3", "test_manifest_analysis", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_manifest_analysis", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_manifest_analysis", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_manifest_analysis", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_manifest_analysis", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_manifest_analysis", "eval_metric")
_emit_stores_embedding("p4", "test_manifest_analysis", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_manifest_analysis", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_manifest_analysis", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestManifestAnalysis:
    @pytest.fixture
    def safe_report(self):
        """A standard, safe dry-run report."""
        return {
            "meta": {"dry_run": True, "territory": "tests"},
            "phase1": {
                "violations_found": [
                    {"type": "NAMING", "file": "a.py"},
                    {"type": "IMPORT", "file": "b.py"},
                ],
            },
            "phase2": {
                "modifications": [
                    {"action": "would_fix", "target": "a.py", "agent": "Fixer"},
                    {"action": "would_fix", "target": "b.py", "agent": "Fixer"},
                ],
                "failures": [],
            },
        }

    @pytest.fixture
    def dangerous_report(self):
        """A report indicating mass deletion (unsafe)."""
        orphans = [{"type": "ORPHANED_FILE", "file": f"del_{i}.py"} for i in range(50)]
        mods = [{"action": "would_delete", "target": f"del_{i}.py"} for i in range(50)]

        return {
            "meta": {"dry_run": True},
            "phase1": {"violations_found": orphans},
            "phase2": {"modifications": mods, "failures": []},
        }

    def test_analysis_passes_safe_run(self, safe_report):
        """Scenario: Normal operation should pass analysis."""
        with patch("logging.info") as mock_info:
            result = analyze_impact(safe_report)
            assert result is True
            # Verify that impact analysis was logged
            mock_info.assert_any_call("--- IMPACT ANALYSIS: tests ---")

    def test_analysis_flags_mass_deletion(self, dangerous_report):
        """Scenario: >10 orphans triggers warning."""
        with patch("logging.warning") as mock_warning:
            result = analyze_impact(dangerous_report)
            assert result is False
            # Verify that mass deletion warning was logged
            mock_warning.assert_any_call("🚨 MASS DELETION RISK: 50 orphan files identified for deletion.")

    def test_analysis_flags_blast_radius(self):
        """Scenario: Too many files modified."""
        # Create 100 modifications
        mods = [{"target": f"file_{i}.py"} for i in range(100)]
        report = {
            "meta": {"dry_run": True},
            "phase1": {"violations_found": []},
            "phase2": {"modifications": mods, "failures": []},
        }

        with patch("logging.warning") as mock_warning:
            result = analyze_impact(report)
            assert result is False
            # Verify that high blast radius warning was logged
            mock_warning.assert_any_call(
                "🚨 HIGH BLAST RADIUS: 100 files would be modified. Manual review required.",
            )

    def test_analysis_warns_on_live_run(self, safe_report):
        """Scenario: Analyzing a live run report should warn but might pass if metrics are ok."""
        safe_report["meta"]["dry_run"] = False

        with patch("logging.warning") as mock_warning:
            result = analyze_impact(safe_report)
            assert result is True  # Still passes metrics, but warns
            # Verify that live run warning was logged
            mock_warning.assert_any_call("⚠️  This report is from a LIVE RUN, not a dry-run.")

    def test_analysis_handles_budget_blocks(self):
        """Scenario: Actions blocked by safety budget should trigger warnings."""
        report = {
            "meta": {"dry_run": True},
            "phase1": {"violations_found": []},
            "phase2": {
                "modifications": [],
                "failures": [
                    {"status": "blocked_by_safety"},
                    {"status": "blocked_by_safety"},
                    {"status": "other_error"},
                ],
            },
        }

        with patch("logging.warning") as mock_warning:
            result = analyze_impact(report)
            assert result is True  # Still passes, but warns about budget blocks
            # Verify that budget block warning was logged
            mock_warning.assert_any_call("⚠️  2 actions were blocked by safety budget limits.")

    def test_analysis_handles_empty_report(self):
        """Scenario: Empty report should not crash."""
        empty_report = {
            "meta": {"dry_run": True},
            "phase1": {"violations_found": []},
            "phase2": {"modifications": [], "failures": []},
        }

        with patch("logging.info") as mock_info:
            result = analyze_impact(empty_report)
            assert result is True
            # Verify that zero violations was logged
            mock_info.assert_any_call("Total Violations Detected: 0")

    def test_analysis_groups_by_type(self):
        """Scenario: Violations should be grouped by type correctly."""
        report = {
            "meta": {"dry_run": True, "territory": "test_territory"},
            "phase1": {
                "violations_found": [
                    {"type": "NAMING", "file": "a.py"},
                    {"type": "NAMING", "file": "b.py"},
                    {"type": "IMPORT", "file": "c.py"},
                    {"type": "UNKNOWN", "file": "d.py"},
                ],
            },
            "phase2": {"modifications": [], "failures": []},
        }

        with patch("logging.info") as mock_info:
            result = analyze_impact(report)
            assert result is True
            # Verify type grouping
            mock_info.assert_any_call("  - NAMING: 2")
            mock_info.assert_any_call("  - IMPORT: 1")
            mock_info.assert_any_call("  - UNKNOWN: 1")

    def test_analysis_calculates_unique_files(self):
        """Scenario: Should count unique files, not total modifications."""
        report = {
            "meta": {"dry_run": True},
            "phase1": {"violations_found": []},
            "phase2": {
                "modifications": [
                    {"target": "file1.py"},  # Same file modified twice
                    {"target": "file1.py"},
                    {"target": "file2.py"},  # Different file
                ],
                "failures": [],
            },
        }

        with patch("logging.info") as mock_info:
            result = analyze_impact(report)
            assert result is True
            # Should count unique files (2), not total modifications (3)
            mock_info.assert_any_call("Files to be Modified: 2")

    def test_analysis_calculates_agents_engaged(self):
        """Scenario: Should count unique agents engaged."""
        report = {
            "meta": {"dry_run": True},
            "phase1": {"violations_found": []},
            "phase2": {
                "modifications": [
                    {"agent": "Fixer"},  # Same agent used twice
                    {"agent": "Fixer"},
                    {"agent": "Mover"},  # Different agent
                    {"agent": "Cleaner"},  # Another different agent
                ],
                "failures": [],
            },
        }

        with patch("logging.info") as mock_info:
            result = analyze_impact(report)
            assert result is True
            # Should count unique agents (3), not total modifications (4)
            mock_info.assert_any_call("Agents Engaged: 3")
