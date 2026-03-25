"""Failure fingerprinting tests for deterministic failure clustering."""

from __future__ import annotations

import json
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_failure_fingerprinting")
# REMOVED: _emit_applies_guardrail("p0", "test_failure_fingerprinting", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_failure_fingerprinting", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_failure_fingerprinting", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_failure_fingerprinting")
# REMOVED: emit_determinism_digest("p0", "test_failure_fingerprinting")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_failure_fingerprinting", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_failure_fingerprinting", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_failure_fingerprinting", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_failure_fingerprinting", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_failure_fingerprinting", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_failure_fingerprinting", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_failure_fingerprinting", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_failure_fingerprinting", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_failure_fingerprinting", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_failure_fingerprinting", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_failure_fingerprinting", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_failure_fingerprinting", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_failure_fingerprinting", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_failure_fingerprinting", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_failure_fingerprinting", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_failure_fingerprinting", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_failure_fingerprinting", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_failure_fingerprinting", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_failure_fingerprinting", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_failure_fingerprinting", "exec_snapshot_link")

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
from system_learning.fingerprinting.engine import FailureFingerprinter
from system_learning.fingerprinting.types import FailureEvent

# REMOVED: _emit_emits_metric_event("test_failure_fingerprinting", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_failure_fingerprinting", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_failure_fingerprinting", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_failure_fingerprinting", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_failure_fingerprinting", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_failure_fingerprinting", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_failure_fingerprinting", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_failure_fingerprinting", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_failure_fingerprinting", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_failure_fingerprinting", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_failure_fingerprinting", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_failure_fingerprinting", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_failure_fingerprinting", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_failure_fingerprinting", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_failure_fingerprinting", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_failure_fingerprinting", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_failure_fingerprinting", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_failure_fingerprinting", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_failure_fingerprinting", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_failure_fingerprinting", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_failure_fingerprinting", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_failure_fingerprinting", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_failure_fingerprinting", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_failure_fingerprinting", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_failure_fingerprinting", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_failure_fingerprinting", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_failure_fingerprinting", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_failure_fingerprinting", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_failure_fingerprinting", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_failure_fingerprinting", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_failure_fingerprinting", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_failure_fingerprinting", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_failure_fingerprinting", "write_through")
# REMOVED: _emit_writes_through("p1", "test_failure_fingerprinting", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_failure_fingerprinting", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_failure_fingerprinting", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_failure_fingerprinting", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_failure_fingerprinting", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_failure_fingerprinting", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_failure_fingerprinting", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_failure_fingerprinting", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_failure_fingerprinting", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_failure_fingerprinting", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_failure_fingerprinting", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_failure_fingerprinting", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_failure_fingerprinting", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_failure_fingerprinting", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_failure_fingerprinting", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_failure_fingerprinting")
# REMOVED: _emit_gated_by_confidence("p1", "test_failure_fingerprinting", "confidence_gate")


class TestFailureFingerprinting:
    """Test failure fingerprinting deterministic behavior."""

    def test_deterministic_sha_same_input(self):
        """Proves same input twice yields identical SHA256."""
        fingerprinter = FailureFingerprinter()

        event = FailureEvent(
            exc_type="ValueError",
            error_code="INVALID_INPUT",
            component="test_component",
            symbols=["function_a", "function_b"],
            metadata={"message": "test error", "retry_count": 3},
        )

        # Generate fingerprint twice
        fp1 = fingerprinter.fingerprint(event)
        fp2 = fingerprinter.fingerprint(event)

        # Should be identical
        assert fp1.fingerprint_sha256 == fp2.fingerprint_sha256
        assert fp1.canonical_bytes == fp2.canonical_bytes

    def test_permutation_invariance_symbols_metadata(self):
        """Proves shuffling symbols/metadata order yields same SHA256."""
        fingerprinter = FailureFingerprinter()

        # Create event with unsorted symbols and metadata
        event1 = FailureEvent(
            exc_type="RuntimeError",
            error_code="RESOURCE_EXHAUSTED",
            component="processor",
            symbols=["func_z", "func_a", "func_m"],
            metadata={"retry_count": 5, "message": "error", "severity": "high"},
        )

        # Same event with different order
        event2 = FailureEvent(
            exc_type="RuntimeError",
            error_code="RESOURCE_EXHAUSTED",
            component="processor",
            symbols=["func_m", "func_z", "func_a"],
            metadata={"severity": "high", "message": "error", "retry_count": 5},
        )

        fp1 = fingerprinter.fingerprint(event1)
        fp2 = fingerprinter.fingerprint(event2)

        # Should be identical despite different input order
        assert fp1.fingerprint_sha256 == fp2.fingerprint_sha256

    def test_cross_process_determinism(self):
        """Proves subprocess SHA256 equals parent process SHA256."""
        # Test data
        event_data = {
            "exc_type": "TimeoutError",
            "error_code": "TIMEOUT",
            "component": "network_client",
            "symbols": ["connect", "send_request"],
            "metadata": {"timeout": 30, "message": "connection timeout"},
        }

        # Write test script
        script_content = f"""
import sys
import json
import hashlib
sys.path.insert(0, r"C:\\Git\\Agentic-Workflow")

from system_learning.fingerprinting.engine import FailureFingerprinter
from system_learning.fingerprinting.types import FailureEvent

event = FailureEvent(**{event_data})
fingerprinter = FailureFingerprinter()
fp = fingerprinter.fingerprint(event)

print(f"FINGERPRINT: {{fp.fingerprint_sha256}}")
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

            # Run same fingerprinting locally
            event = FailureEvent(**event_data)
            local_fingerprinter = FailureFingerprinter()
            local_fp = local_fingerprinter.fingerprint(event)

            # Fingerprints should match across processes
            assert local_fp.fingerprint_sha256 == remote_fingerprint

        finally:
            import os

            os.unlink(script_path)

    def test_drift_stability_line_numbers_paths(self):
        """Proves same failure with different line numbers/paths yields same SHA256."""
        fingerprinter = FailureFingerprinter()

        # Same logical failure with different line numbers and paths
        event1 = FailureEvent(
            exc_type="KeyError",
            error_code="MISSING_KEY",
            component="C:/project/src/data_processor.py",
            symbols=["process_data:145", "validate_input:89"],
            metadata={"message": "Key not found in data structure at line 145"},
        )

        event2 = FailureEvent(
            exc_type="KeyError",
            error_code="MISSING_KEY",
            component="/home/user/project/src/data_processor.py",
            symbols=["process_data:200", "validate_input:120"],  # Different line numbers
            metadata={"message": "Key not found in data structure at line 200"},
        )

        fp1 = fingerprinter.fingerprint(event1)
        fp2 = fingerprinter.fingerprint(event2)

        # Should be identical after normalization
        assert fp1.fingerprint_sha256 == fp2.fingerprint_sha256

    def test_negative_control_symbol_sorting(self):
        """Negative control that fails if symbol normalization sorting is removed."""
        # This test demonstrates the importance of symbol sorting
        fingerprinter = FailureFingerprinter()

        event1 = FailureEvent(
            exc_type="AttributeError",
            error_code="NULL_ATTRIBUTE",
            component="test_module",
            symbols=["z_func", "a_func", "m_func"],
            metadata={},
        )

        event2 = FailureEvent(
            exc_type="AttributeError",
            error_code="NULL_ATTRIBUTE",
            component="test_module",
            symbols=["m_func", "z_func", "a_func"],  # Different order
            metadata={},
        )

        fp1 = fingerprinter.fingerprint(event1)
        fp2 = fingerprinter.fingerprint(event2)

        # With proper sorting, these should be identical
        assert fp1.fingerprint_sha256 == fp2.fingerprint_sha256

        # Verify canonical bytes are sorted
        canonical_data = json.loads(fp1.canonical_bytes.decode("ascii"))
        assert canonical_data["symbols"] == ["a_func", "m_func", "z_func"]  # Sorted

    def test_malformed_input_classification_stability(self):
        """Proves stable exception types for malformed inputs."""
        fingerprinter = FailureFingerprinter()

        # Test malformed inputs
        malformed_cases = [
            {"event": None, "expected_error": TypeError},
            {"event": "not_an_event", "expected_error": TypeError},
            {
                "event": FailureEvent(
                    exc_type="",  # Empty type
                    error_code="TEST",
                    component="test",
                    symbols=[],
                    metadata={},
                ),
                "expected_error": ValueError,
            },
        ]

        for case in malformed_cases:
            with pytest.raises(case["expected_error"]):
                fingerprinter.fingerprint(case["event"])

        # Exception types should be deterministic
        assert len(malformed_cases) == 3
