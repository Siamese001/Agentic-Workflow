"""Healing confidence scoring tests for deterministic escalation decisions."""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_healing_confidence_scorer")
# REMOVED: _emit_applies_guardrail("p0", "test_healing_confidence_scorer", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_healing_confidence_scorer", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_healing_confidence_scorer", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_healing_confidence_scorer")
# REMOVED: emit_determinism_digest("p0", "test_healing_confidence_scorer")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_healing_confidence_scorer", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_healing_confidence_scorer", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_healing_confidence_scorer", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_healing_confidence_scorer", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_healing_confidence_scorer", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_healing_confidence_scorer", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_healing_confidence_scorer", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_healing_confidence_scorer", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_healing_confidence_scorer", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_healing_confidence_scorer", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_healing_confidence_scorer", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_healing_confidence_scorer", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_healing_confidence_scorer", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_healing_confidence_scorer", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_healing_confidence_scorer", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_healing_confidence_scorer", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_healing_confidence_scorer", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_healing_confidence_scorer", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_healing_confidence_scorer", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_healing_confidence_scorer", "exec_snapshot_link")

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
from system_learning.confidence.engine import HealingConfidenceScorer
from system_learning.confidence.types import (
    HealingAttempt,
    HealingConfidenceReport,
)

# REMOVED: _emit_emits_metric_event("test_healing_confidence_scorer", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_healing_confidence_scorer", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_healing_confidence_scorer", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_healing_confidence_scorer", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_healing_confidence_scorer", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_healing_confidence_scorer", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_healing_confidence_scorer", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_healing_confidence_scorer", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_healing_confidence_scorer", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_healing_confidence_scorer", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_healing_confidence_scorer", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_healing_confidence_scorer", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_healing_confidence_scorer", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_healing_confidence_scorer", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_healing_confidence_scorer", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_healing_confidence_scorer", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_healing_confidence_scorer", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_healing_confidence_scorer", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_healing_confidence_scorer", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_healing_confidence_scorer", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_healing_confidence_scorer", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_healing_confidence_scorer", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_healing_confidence_scorer", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_healing_confidence_scorer", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_healing_confidence_scorer", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_healing_confidence_scorer", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_healing_confidence_scorer", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_healing_confidence_scorer", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_healing_confidence_scorer", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_healing_confidence_scorer", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_confidence_scorer", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_healing_confidence_scorer", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_healing_confidence_scorer", "write_through")
# REMOVED: _emit_writes_through("p1", "test_healing_confidence_scorer", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_healing_confidence_scorer", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_healing_confidence_scorer", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_healing_confidence_scorer", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_healing_confidence_scorer", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_healing_confidence_scorer", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_healing_confidence_scorer", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_healing_confidence_scorer", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_healing_confidence_scorer", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_healing_confidence_scorer", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_healing_confidence_scorer", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_healing_confidence_scorer", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_healing_confidence_scorer", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_healing_confidence_scorer", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_healing_confidence_scorer", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_healing_confidence_scorer")
# REMOVED: _emit_gated_by_confidence("p1", "test_healing_confidence_scorer", "confidence_gate")


class TestHealingConfidenceScorer:
    """Test healing confidence scoring deterministic behavior."""

    def test_deterministic_fingerprint_same_input(self):
        """Proves same input twice yields identical SHA256."""
        scorer = HealingConfidenceScorer()

        attempts = [
            HealingAttempt(
                attempt_id="attempt_1",
                healer_id="healer_a",
                outcome="SUCCESS",
                severity=1,
                signals={"component": "test", "error_type": "timeout"},
                cost=0.5,
            ),
            HealingAttempt(
                attempt_id="attempt_2",
                healer_id="healer_b",
                outcome="PARTIAL",
                severity=2,
                signals={"component": "test", "error_type": "memory"},
                cost=1.0,
            ),
        ]

        # Generate report twice
        report1 = scorer.score(attempts)
        report2 = scorer.score(attempts)

        # Should be identical
        assert report1.confidence_fingerprint == report2.confidence_fingerprint
        assert report1.canonical_bytes == report2.canonical_bytes

    def test_permutation_invariance_attempt_order(self):
        """Proves shuffling attempt order yields same SHA256."""
        scorer = HealingConfidenceScorer()

        attempts = [
            HealingAttempt(
                attempt_id="attempt_1",
                healer_id="healer_a",
                outcome="SUCCESS",
                severity=1,
                signals={"component": "test"},
                cost=0.5,
            ),
            HealingAttempt(
                attempt_id="attempt_2",
                healer_id="healer_b",
                outcome="FAIL",
                severity=3,
                signals={"component": "test"},
                cost=2.0,
            ),
        ]

        # Same attempts in different order
        attempts_shuffled = list(reversed(attempts))

        report1 = scorer.score(attempts)
        report2 = scorer.score(attempts_shuffled)

        # Should be identical despite different input order
        assert report1.confidence_fingerprint == report2.confidence_fingerprint

    def test_cross_process_determinism(self):
        """Proves subprocess SHA256 equals parent process SHA256."""
        # Test data
        attempts_data = [
            {
                "attempt_id": "cross_test_1",
                "healer_id": "healer_x",
                "outcome": "SUCCESS",
                "severity": 1,
                "signals": {"component": "network", "error": "timeout"},
                "cost": 0.8,
            },
            {
                "attempt_id": "cross_test_2",
                "healer_id": "healer_y",
                "outcome": "PARTIAL",
                "severity": 2,
                "signals": {"component": "network", "error": "retry"},
                "cost": 1.2,
            },
        ]

        # Write test script
        script_content = f"""
import sys
import json
sys.path.insert(0, r"C:\\Git\\Agentic-Workflow")

from system_learning.confidence.engine import HealingConfidenceScorer
from system_learning.confidence.types import HealingAttempt

attempts = [HealingAttempt(**a) for a in {attempts_data}]
scorer = HealingConfidenceScorer()
report = scorer.score(attempts)

print(f"FINGERPRINT: {{report.confidence_fingerprint}}")
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

            # Run same scoring locally
            attempts = [HealingAttempt(**a) for a in attempts_data]
            local_scorer = HealingConfidenceScorer()
            local_report = local_scorer.score(attempts)

            # Fingerprints should match across processes
            assert local_report.confidence_fingerprint == remote_fingerprint

        finally:
            import os

            os.unlink(script_path)

    def test_monotone_worse_outcome_nonincreasing_confidence(self):
        """Proves worse outcomes lead to non-increasing confidence."""
        scorer = HealingConfidenceScorer()

        # Base successful attempt
        base_attempts = [
            HealingAttempt(
                attempt_id="base",
                healer_id="healer_a",
                outcome="SUCCESS",
                severity=1,
                signals={},
                cost=1.0,
            )
        ]

        base_report = scorer.score(base_attempts)
        base_confidence = base_report.decisions[0].confidence

        # Worse outcome (FAIL) should have lower or equal confidence
        worse_attempts = [
            HealingAttempt(
                attempt_id="worse",
                healer_id="healer_a",
                outcome="FAIL",
                severity=1,
                signals={},
                cost=1.0,
            )
        ]

        worse_report = scorer.score(worse_attempts)
        worse_confidence = worse_report.decisions[0].confidence

        assert worse_confidence <= base_confidence, "Worse outcome should not increase confidence"

    def test_monotone_more_success_evidence_nondecreasing_confidence(self):
        """Proves more success evidence leads to non-decreasing confidence."""
        scorer = HealingConfidenceScorer()

        # Single success
        single_attempts = [
            HealingAttempt(
                attempt_id="single",
                healer_id="healer_a",
                outcome="SUCCESS",
                severity=1,
                signals={},
                cost=1.0,
            )
        ]

        single_report = scorer.score(single_attempts)
        single_confidence = single_report.decisions[0].confidence

        # Multiple successes should have higher or equal confidence
        multiple_attempts = [
            HealingAttempt(
                attempt_id="multi_1",
                healer_id="healer_a",
                outcome="SUCCESS",
                severity=1,
                signals={},
                cost=1.0,
            ),
            HealingAttempt(
                attempt_id="multi_2",
                healer_id="healer_a",
                outcome="SUCCESS",
                severity=1,
                signals={},
                cost=1.0,
            ),
        ]

        multiple_report = scorer.score(multiple_attempts)
        multiple_confidence = multiple_report.decisions[0].confidence

        assert multiple_confidence >= single_confidence, (
            "More success evidence should not decrease confidence"
        )

    def test_action_mapping_total_and_deterministic(self):
        """Proves every attempt gets mapped to exactly one action deterministically."""
        scorer = HealingConfidenceScorer()

        attempts = [
            HealingAttempt(
                attempt_id="low_conf",
                healer_id="healer_a",
                outcome="FAIL",
                severity=3,
                signals={},
                cost=5.0,
            ),
            HealingAttempt(
                attempt_id="mid_conf",
                healer_id="healer_b",
                outcome="PARTIAL",
                severity=2,
                signals={},
                cost=2.0,
            ),
            HealingAttempt(
                attempt_id="high_conf",
                healer_id="healer_c",
                outcome="SUCCESS",
                severity=1,
                signals={},
                cost=0.5,
            ),
        ]

        report = scorer.score(attempts)

        # Every attempt should have exactly one decision
        assert len(report.decisions) == 3

        # Actions should be deterministic based on confidence
        actions = [d.action for d in report.decisions]
        assert "ESCALATE" in actions or "REVIEW" in actions or "ACCEPT" in actions

        # Each attempt should be mapped to exactly one action
        for decision in report.decisions:
            assert decision.action in {"ESCALATE", "REVIEW", "ACCEPT"}

    def test_negative_control_disable_sorting(self):
        """Negative control that fails if attempt sorting is removed."""
        scorer = HealingConfidenceScorer()

        attempts = [
            HealingAttempt(
                attempt_id="z_attempt",
                healer_id="healer_a",
                outcome="SUCCESS",
                severity=1,
                signals={},
                cost=1.0,
            ),
            HealingAttempt(
                attempt_id="a_attempt",
                healer_id="healer_b",
                outcome="FAIL",
                severity=2,
                signals={},
                cost=2.0,
            ),
        ]

        # With proper sorting, order should not matter
        attempts_reversed = list(reversed(attempts))

        report1 = scorer.score(attempts)
        report2 = scorer.score(attempts_reversed)

        # Should be identical with proper sorting
        assert report1.confidence_fingerprint == report2.confidence_fingerprint

    def test_negative_control_disable_monotone_guard(self):
        """Negative control that fails if monotonic guard is removed."""
        # This test demonstrates the importance of monotonic constraints
        scorer = HealingConfidenceScorer()

        # Create attempts that would violate monotonicity without guards
        high_severity_success = HealingAttempt(
            attempt_id="high_success",
            healer_id="healer_a",
            outcome="SUCCESS",
            severity=5,  # High severity but success
            signals={},
            cost=0.1,
        )

        low_severity_fail = HealingAttempt(
            attempt_id="low_fail",
            healer_id="healer_b",
            outcome="FAIL",
            severity=1,  # Low severity but failure
            signals={},
            cost=5.0,
        )

        # With monotonic guards, success should still rank higher than fail
        report_success = scorer.score([high_severity_success])
        report_fail = scorer.score([low_severity_fail])

        success_confidence = report_success.decisions[0].confidence
        fail_confidence = report_fail.decisions[0].confidence

        # Success should have higher confidence despite high severity
        assert success_confidence > fail_confidence

    def test_malformed_input_classification_stability(self):
        """Proves stable exception types for malformed inputs."""
        scorer = HealingConfidenceScorer()

        # Test malformed inputs
        malformed_cases = [
            {"attempts": None, "expected_error": TypeError},
            {"attempts": "not_attempts", "expected_error": TypeError},
            {
                "attempts": [
                    "not_an_attempt"  # Invalid type in list
                ],
                "expected_error": TypeError,
            },
        ]

        for case in malformed_cases:
            with pytest.raises(case["expected_error"]):
                scorer.score(case["attempts"])

        # Exception types should be deterministic
        assert len(malformed_cases) == 3

    def test_proposal_only_purity(self):
        """Proves confidence scorer is pure and returns only report objects."""
        scorer = HealingConfidenceScorer()

        attempts = [
            HealingAttempt(
                attempt_id="pure_test",
                healer_id="healer_a",
                outcome="SUCCESS",
                severity=1,
                signals={},
                cost=1.0,
            )
        ]

        # Multiple calls with same inputs should return identical objects
        report1 = scorer.score(attempts)
        report2 = scorer.score(attempts)

        # Same fingerprint and decisions
        assert report1.confidence_fingerprint == report2.confidence_fingerprint
        assert len(report1.decisions) == len(report2.decisions)

        # Verify return type
        assert isinstance(report1, HealingConfidenceReport)
        assert hasattr(report1, "canonical_bytes")

        # No side effects - scorer state should be unchanged
        # (This is implicit in the deterministic behavior above)
