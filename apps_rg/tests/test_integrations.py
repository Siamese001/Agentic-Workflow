"""
Test RG Integrations.
"""
import unittest

from apps_rg.integrations import ExecutionAdapter, ObservabilityAdapter
from apps_rg.types import ResumeRequest, ResumeResult, ResumeSection


class TestExecutionAdapter(unittest.TestCase):
    """Test cases for ExecutionAdapter."""

    def setUp(self):
        self.adapter = ExecutionAdapter()

    def test_submit_passed(self):
        """Test submitting passed resume."""
        request = ResumeRequest(
            candidate_name="Jane Smith",
            target_role="Senior Engineer",
            trace_id="rg-001",
        )
        result = ResumeResult(
            trace_id="rg-001",
            candidate_name="Jane Smith",
            target_role="Senior Engineer",
            status="complete",
            ats_score=85.5,
            quality_score=0.88,
            gate_violations=[],
        )
        receipt = self.adapter.submit(request, result)
        self.assertEqual(receipt["status"], "submitted")
        self.assertEqual(receipt["app"], "apps_rg")
        self.assertTrue(receipt["provenance"]["gate_passed"])

    def test_submit_failed(self):
        """Test submitting failed resume."""
        request = ResumeRequest(
            candidate_name="Test",
            target_role="Role",
            trace_id="rg-002",
        )
        result = ResumeResult(
            trace_id="rg-002",
            status="failed",
            gate_violations=["quality too low"],
        )
        receipt = self.adapter.submit(request, result)
        self.assertFalse(receipt["provenance"]["gate_passed"])

    def test_get_execution_log(self):
        """Test execution log retrieval."""
        request = ResumeRequest(
            candidate_name="Test",
            target_role="Role",
            trace_id="rg-003",
        )
        result = ResumeResult(trace_id="rg-003", status="complete")
        self.adapter.submit(request, result)
        log = self.adapter.get_execution_log()
        self.assertEqual(len(log), 1)


class TestObservabilityAdapter(unittest.TestCase):
    """Test cases for ObservabilityAdapter."""

    def setUp(self):
        self.adapter = ObservabilityAdapter()

    def test_emit_resume_start(self):
        """Test resume start event."""
        request = ResumeRequest(
            candidate_name="Jane Smith",
            target_role="Senior Engineer",
            target_industry="tech",
            experience_level="senior",
            dry_run=True,
        )
        event = self.adapter.emit_resume_start(request)
        self.assertEqual(event["event_type"], "resume_start")
        self.assertEqual(event["candidate_name"], "Jane Smith")
        self.assertTrue(event["dry_run"])

    def test_emit_resume_complete(self):
        """Test resume complete event."""
        result = ResumeResult(
            trace_id="rg-001",
            candidate_name="Jane Smith",
            target_role="Senior Engineer",
            status="complete",
            ats_score=85.5,
            quality_score=0.88,
            gate_violations=[],
        )
        event = self.adapter.emit_resume_complete(result)
        self.assertEqual(event["event_type"], "resume_complete")
        self.assertEqual(event["ats_score"], 85.5)
        self.assertTrue(event["gate_passed"])

    def test_emit_section_generated(self):
        """Test section generated event."""
        section = ResumeSection(
            section_id="sec-001",
            section_type="summary",
            content="Professional summary that meets minimum requirements for testing.",
            word_count=50,
        )
        event = self.adapter.emit_section_generated(section)
        self.assertEqual(event["event_type"], "section_generated")
        self.assertEqual(event["section_id"], "sec-001")

    def test_get_metrics(self):
        """Test metrics retrieval."""
        result = ResumeResult(trace_id="rg-001", status="complete")
        self.adapter.emit_resume_complete(result)
        metrics = self.adapter.get_metrics()
        self.assertEqual(len(metrics), 1)


if __name__ == "__main__":
    unittest.main()
