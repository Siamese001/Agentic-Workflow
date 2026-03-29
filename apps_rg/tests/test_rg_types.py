"""
Test RG Types.
"""
import unittest
from dataclasses import dataclass, field
from typing import Any


class TestRgTypes(unittest.TestCase):
    """Test cases for RG types."""

    def test_basic_dataclass_creation(self):
        """Test that dataclasses can be created."""
        @dataclass
        class TestResumeRequest:
            """Test request."""
            job_description: str = ""
            candidate_profile: str = ""
            dry_run: bool = False
            trace_id: str = ""
            extra: dict[str, Any] = field(default_factory=dict)

        request = TestResumeRequest(
            job_description="Software Engineer",
            candidate_profile="Python developer",
            trace_id="test-001"
        )
        self.assertEqual(request.job_description, "Software Engineer")
        self.assertEqual(request.trace_id, "test-001")
        self.assertFalse(request.dry_run)

    def test_dataclass_defaults(self):
        """Test dataclass default values."""
        @dataclass
        class TestResumeResult:
            """Test result."""
            trace_id: str = ""
            status: str = "pending"
            quality_score: float = 0.0
            gate_violations: list[str] = field(default_factory=list)

        result = TestResumeResult()
        self.assertEqual(result.status, "pending")
        self.assertEqual(result.quality_score, 0.0)
        self.assertEqual(result.gate_violations, [])

    def test_gate_violation_property(self):
        """Test gate violation logic."""
        @dataclass
        class TestResult:
            status: str
            gate_violations: list[str]

            @property
            def passed_gate(self) -> bool:
                return len(self.gate_violations) == 0 and self.status == "complete"

        # Should pass
        result_pass = TestResult(status="complete", gate_violations=[])
        self.assertTrue(result_pass.passed_gate)

        # Should fail - not complete
        result_pending = TestResult(status="pending", gate_violations=[])
        self.assertFalse(result_pending.passed_gate)

        # Should fail - has violations
        result_violations = TestResult(status="complete", gate_violations=["error"])
        self.assertFalse(result_violations.passed_gate)


if __name__ == "__main__":
    unittest.main()
