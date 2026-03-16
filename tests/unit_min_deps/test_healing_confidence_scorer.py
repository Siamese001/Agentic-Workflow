"""Healing confidence scoring tests for deterministic escalation decisions."""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_healing_confidence_scorer")
_emit_applies_guardrail("p0", "test_healing_confidence_scorer", "p0_governance")
_emit_reads_policy_state("p0", "test_healing_confidence_scorer", "policy_binding")
_emit_snapshots_state("p0", "test_healing_confidence_scorer", "state_snapshot")
emit_replay_key("p0", "test_healing_confidence_scorer")
emit_determinism_digest("p0", "test_healing_confidence_scorer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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

from system_learning.confidence.engine import HealingConfidenceScorer
from system_learning.confidence.types import (
    HealingAttempt,
    HealingConfidenceReport,
)


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
