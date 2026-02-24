"""Failure fingerprinting tests for deterministic failure clustering."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile

import pytest

pytestmark = pytest.mark.unit_min_deps

from agentic_core.system_learning.fingerprinting.engine import FailureFingerprinter
from agentic_core.system_learning.fingerprinting.types import FailureEvent


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
        script_content = f'''
import sys
import json
import hashlib
sys.path.insert(0, r"{sys.path[0]}")

from agentic_core.system_learning.fingerprinting.engine import FailureFingerprinter
from agentic_core.system_learning.fingerprinting.types import FailureEvent

event = FailureEvent(**{event_data})
fingerprinter = FailureFingerprinter()
fp = fingerprinter.fingerprint(event)

print(f"FINGERPRINT: {{fp.fingerprint_sha256}}")
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(script_content)
            script_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                cwd=sys.path[0],
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
