"""Risk correlation tests for deterministic multi-signal correlation."""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_risk_correlator")
# REMOVED: _emit_applies_guardrail("p0", "test_risk_correlator", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_risk_correlator", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_risk_correlator")
# REMOVED: emit_determinism_digest("p0", "test_risk_correlator")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_risk_correlator", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_risk_correlator", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_risk_correlator", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_risk_correlator", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_risk_correlator", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_risk_correlator", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_risk_correlator", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_risk_correlator", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_risk_correlator", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_risk_correlator", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_risk_correlator", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_risk_correlator", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_risk_correlator", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_risk_correlator", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_risk_correlator", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_risk_correlator", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_risk_correlator", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_risk_correlator", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_risk_correlator", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_risk_correlator", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

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
#  # MOVED: from system_learning.correlation.engine import RiskCorrelator
#  # MOVED: from system_learning.correlation.types import CorrelatedRiskReport

# REMOVED: _emit_emits_metric_event("test_risk_correlator", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_risk_correlator", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_risk_correlator", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_risk_correlator", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_risk_correlator", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_risk_correlator", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_risk_correlator", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_risk_correlator", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_risk_correlator", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_risk_correlator", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_risk_correlator", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_risk_correlator", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_risk_correlator", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_risk_correlator", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_risk_correlator", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_risk_correlator", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_risk_correlator", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_risk_correlator", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_risk_correlator", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_risk_correlator", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_risk_correlator", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_risk_correlator", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_risk_correlator", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_risk_correlator", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_risk_correlator", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_risk_correlator", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_risk_correlator", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_risk_correlator", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_risk_correlator", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_risk_correlator", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_risk_correlator", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_risk_correlator", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_risk_correlator", "write_through")
# REMOVED: _emit_writes_through("p1", "test_risk_correlator", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_risk_correlator", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_risk_correlator", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_risk_correlator", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_risk_correlator", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_risk_correlator", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_risk_correlator", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_risk_correlator", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_risk_correlator", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_risk_correlator", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_risk_correlator", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_risk_correlator", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_risk_correlator", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_risk_correlator", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_risk_correlator", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_risk_correlator")
# REMOVED: _emit_gated_by_confidence("p1", "test_risk_correlator", "confidence_gate")


# Mock DriftEvent for testing
class MockDriftEvent:
    def __init__(self, policy_id: str, drift_type: str, severity: float):
        self.policy_id = policy_id
        self.drift_type = drift_type
        self.severity = severity


class TestRiskCorrelator:
    """Test risk correlation deterministic behavior."""

    def test_deterministic_fingerprint_same_input(self):
                from system_learning.correlation.engine import RiskCorrelator
                from system_learning.correlation.engine import RiskCorrelator
                from system_learning.correlation.engine import RiskCorrelator
                from system_learning.correlation.engine import RiskCorrelator
                from system_learning.correlation.engine import RiskCorrelator
                from system_learning.correlation.engine import RiskCorrelator
                from system_learning.correlation.types import CorrelatedRiskReport
                from system_learning.correlation.engine import RiskCorrelator
                from system_learning.correlation.engine import RiskCorrelator
                """Proves same input twice yields identical SHA256."""
                correlator = RiskCorrelator()

        correlator = RiskCorrelator()

        fingerprints = ["fp1_policyA", "fp2_policyB"]
        drift_events = [
            MockDriftEvent("policyA", "NEW_POLICY", 1.0),
            MockDriftEvent("policyB", "VERSION_CHANGED", 0.7),
        ]

        # Generate report twice
        report1 = correlator.build(fingerprints, drift_events)
        report2 = correlator.build(fingerprints, drift_events)

        # Should be identical
        assert report1.correlation_fingerprint == report2.correlation_fingerprint
        assert report1.canonical_bytes == report2.canonical_bytes

    def test_permutation_invariance_inputs_order(self):
        """Proves shuffling input order yields same SHA256."""
#  # MOVED: from system_learning.correlation.engine import RiskCorrelator
        correlator = RiskCorrelator()

        fingerprints = ["fp1_policyA", "fp2_policyB"]
        drift_events = [
            MockDriftEvent("policyA", "NEW_POLICY", 1.0),
            MockDriftEvent("policyB", "VERSION_CHANGED", 0.7),
        ]

        # Same inputs in different order
        fingerprints_shuffled = list(reversed(fingerprints))
        drift_events_shuffled = list(reversed(drift_events))

        report1 = correlator.build(fingerprints, drift_events)
        report2 = correlator.build(fingerprints_shuffled, drift_events_shuffled)

        # Should be identical despite different input order
        assert report1.correlation_fingerprint == report2.correlation_fingerprint

    def test_cross_process_determinism(self):
        """Proves subprocess SHA256 equals parent process SHA256."""
#  # MOVED: from system_learning.correlation.engine import RiskCorrelator
        # Test data
        fingerprints_data = ["fp1_policyA", "fp2_policyB"]
        drift_events_data = [
            {"policy_id": "policyA", "drift_type": "NEW_POLICY", "severity": 1.0},
            {"policy_id": "policyB", "drift_type": "VERSION_CHANGED", "severity": 0.7},
        ]

        # Write test script
        script_content = f"""
#  # MOVED: from system_learning.correlation.engine import RiskCorrelator
import sys
import json
sys.path.insert(0, r"C:\\Git\\Agentic-Workflow")

#  # MOVED: from system_learning.correlation.engine import RiskCorrelator

class MockDriftEvent:
    def __init__(self, policy_id, drift_type, severity):
        self.policy_id = policy_id
        self.drift_type = drift_type
        self.severity = severity

fingerprints = {fingerprints_data}
drift_events = [MockDriftEvent(**e) for e in {drift_events_data}]
correlator = RiskCorrelator()
report = correlator.build(fingerprints, drift_events)

print(f"FINGERPRINT: {{report.correlation_fingerprint}}")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(script_content)
            script_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                cwd=str(pathlib.Path(__file__).resolve().parents[2]),
            )

            assert result.returncode == 0

            # Parse output
            remote_fingerprint = result.stdout.strip().split(": ")[1]

            # Run same correlation locally
            drift_events = [MockDriftEvent(**e) for e in drift_events_data]
            local_correlator = RiskCorrelator()
            local_report = local_correlator.build(fingerprints_data, drift_events)

            # Fingerprints should match across processes
            assert local_report.correlation_fingerprint == remote_fingerprint

        finally:
            import os

            os.unlink(script_path)

    def test_total_mapping_deterministic(self):
        """Proves each fingerprint maps to 0..N drift events deterministically."""
        correlator = RiskCorrelator()

        fingerprints = ["fp1_policyA", "fp2_policyC", "fp3_no_match"]
        drift_events = [
            MockDriftEvent("policyA", "NEW_POLICY", 1.0),
            MockDriftEvent("policyB", "VERSION_CHANGED", 0.7),
            MockDriftEvent("policyC", "CONTENT_CHANGED", 0.5),
        ]

        report = correlator.build(fingerprints, drift_events)

        # Should have 3 correlations (fp1->policyA, fp2->policyC, fp3->none)
        assert len(report.rows) == 2  # Only actual correlations

        # Verify deterministic mapping
        policy_ids = [row.policy_id for row in report.rows]
        assert "policyA" in policy_ids
        assert "policyC" in policy_ids
        assert "policyB" not in policy_ids  # No fingerprint contains policyB

    def test_stable_ordering_rows(self):
        """Proves rows are sorted by (fingerprint, policy_id, drift_type)."""
#  # MOVED: from system_learning.correlation.engine import RiskCorrelator
        correlator = RiskCorrelator()

        fingerprints = ["fp2_policyB", "fp1_policyA"]  # Intentionally unsorted
        drift_events = [
            MockDriftEvent("policyB", "VERSION_CHANGED", 0.7),
            MockDriftEvent("policyA", "NEW_POLICY", 1.0),
        ]

        report = correlator.build(fingerprints, drift_events)

        # Rows should be sorted by fingerprint first
        assert len(report.rows) == 2
        assert report.rows[0].fingerprint == "fp1_policyA"
        assert report.rows[1].fingerprint == "fp2_policyB"

        # Within same fingerprint, sorted by policy_id
        assert report.rows[0].policy_id == "policyA"
        assert report.rows[1].policy_id == "policyB"

    def test_negative_control_disable_sorting(self):
        """Negative control that fails if sorting is removed."""
#  # MOVED: from system_learning.correlation.engine import RiskCorrelator
        correlator = RiskCorrelator()

        fingerprints = ["fp2_policyB", "fp1_policyA"]
        drift_events = [
            MockDriftEvent("policyB", "VERSION_CHANGED", 0.7),
            MockDriftEvent("policyA", "NEW_POLICY", 1.0),
        ]

        # With proper sorting, order should not matter
        fingerprints_reversed = list(reversed(fingerprints))
        drift_events_reversed = list(reversed(drift_events))

        report1 = correlator.build(fingerprints, drift_events)
        report2 = correlator.build(fingerprints_reversed, drift_events_reversed)

        # Should be identical with proper sorting
        assert report1.correlation_fingerprint == report2.correlation_fingerprint

    def test_malformed_input_classification_stability(self):
        """Proves stable exception types for malformed inputs."""
#  # MOVED: from system_learning.correlation.engine import RiskCorrelator
        correlator = RiskCorrelator()

        # Test malformed inputs
        malformed_cases = [
            {"fingerprints": None, "drift_events": [], "expected_error": TypeError},
            {"fingerprints": [], "drift_events": None, "expected_error": TypeError},
            {"fingerprints": "not_list", "drift_events": [], "expected_error": TypeError},
        ]

        for case in malformed_cases:
            with pytest.raises(case["expected_error"]):
                correlator.build(case["fingerprints"], case["drift_events"])

        # Exception types should be deterministic
        assert len(malformed_cases) == 3

    def test_proposal_only_purity(self):
#  # MOVED: from system_learning.correlation.types import CorrelatedRiskReport
#  # MOVED: from system_learning.correlation.engine import RiskCorrelator
        """Proves correlator is pure and returns only report objects."""
#  # MOVED: from system_learning.correlation.engine import RiskCorrelator
        correlator = RiskCorrelator()

        fingerprints = ["fp1_policyA"]
        drift_events = [MockDriftEvent("policyA", "NEW_POLICY", 1.0)]

        # Multiple calls with same inputs should return identical objects
        report1 = correlator.build(fingerprints, drift_events)
        report2 = correlator.build(fingerprints, drift_events)

        # Same fingerprint and rows
        assert report1.correlation_fingerprint == report2.correlation_fingerprint
        assert len(report1.rows) == len(report2.rows)

        # Verify return type
        assert isinstance(report1, CorrelatedRiskReport)
        assert hasattr(report1, "canonical_bytes")

        # No side effects - correlator state should be unchanged
        # (This is implicit in the deterministic behavior above)
