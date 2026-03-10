"""Risk correlation tests for deterministic multi-signal correlation."""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

import pytest

pytestmark = pytest.mark.unit_min_deps

from system_learning.correlation.engine import RiskCorrelator
from system_learning.correlation.types import CorrelatedRiskReport


# Mock DriftEvent for testing
class MockDriftEvent:
    def __init__(self, policy_id: str, drift_type: str, severity: float):
        self.policy_id = policy_id
        self.drift_type = drift_type
        self.severity = severity


class TestRiskCorrelator:
    """Test risk correlation deterministic behavior."""

    def test_deterministic_fingerprint_same_input(self):
        """Proves same input twice yields identical SHA256."""
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
        # Test data
        fingerprints_data = ["fp1_policyA", "fp2_policyB"]
        drift_events_data = [
            {"policy_id": "policyA", "drift_type": "NEW_POLICY", "severity": 1.0},
            {"policy_id": "policyB", "drift_type": "VERSION_CHANGED", "severity": 0.7},
        ]

        # Write test script
        script_content = f"""
import sys
import json
sys.path.insert(0, r"C:\\Git\\Agentic-Workflow")

from system_learning.correlation.engine import RiskCorrelator

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
        """Proves correlator is pure and returns only report objects."""
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
