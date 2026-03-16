"""Failure fingerprinting tests for deterministic failure clustering."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile

import pytest

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

_emit_records_execution_trace("p0", "evidence", "test_failure_fingerprinting")
_emit_applies_guardrail("p0", "test_failure_fingerprinting", "p0_governance")
_emit_reads_policy_state("p0", "test_failure_fingerprinting", "policy_binding")
_emit_snapshots_state("p0", "test_failure_fingerprinting", "state_snapshot")
emit_replay_key("p0", "test_failure_fingerprinting")
emit_determinism_digest("p0", "test_failure_fingerprinting")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_failure_fingerprinting", "execution_auth")
_emit_validates_capability("p2", "test_failure_fingerprinting", "capability_check")
_emit_routes_to_capability("p2", "test_failure_fingerprinting", "capability_route")
_emit_writes_via_uwg("p2", "test_failure_fingerprinting", "uwg_write")
_emit_blocks_direct_write("p2", "test_failure_fingerprinting", "direct_write_block")
_emit_records_tool_invocation("p2", "test_failure_fingerprinting", "tool_invocation")
_emit_captures_execution_output("p2", "test_failure_fingerprinting", "exec_output")
_emit_dispatches_agent("p3", "test_failure_fingerprinting", "agent_dispatch")
_emit_coordinates_agents("p3", "test_failure_fingerprinting", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_failure_fingerprinting", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_failure_fingerprinting", "healing_outcome")
_emit_escalates_failure("p3", "test_failure_fingerprinting", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_failure_fingerprinting", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_failure_fingerprinting", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_failure_fingerprinting", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_failure_fingerprinting", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_failure_fingerprinting", "eval_metric")
_emit_stores_embedding("p4", "test_failure_fingerprinting", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_failure_fingerprinting", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_failure_fingerprinting", "exec_snapshot_link")

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

from system_learning.fingerprinting.engine import FailureFingerprinter
from system_learning.fingerprinting.types import FailureEvent


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
