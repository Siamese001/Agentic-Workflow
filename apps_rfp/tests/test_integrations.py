"""
Test RFP Integrations.
"""
import unittest

from apps_rfp.integrations import ExecutionAdapter, ObservabilityAdapter
from apps_rfp.types import (
    ProposalSection,
    RfpRequest,
    RfpResult,
)


class TestExecutionAdapter(unittest.TestCase):
    """Test cases for ExecutionAdapter."""

    def setUp(self):
        self.adapter = ExecutionAdapter()

    def test_submit_passed(self):
        """Test submitting passed RFP."""
        request = RfpRequest(
            problem_statement="We need to modernize infrastructure with proper length description",
            industry="technology",
            trace_id="rfp-001",
        )
        result = RfpResult(
            trace_id="rfp-001",
            industry="technology",
            status="complete",
            quality_score=0.85,
            gate_violations=[],
        )
        receipt = self.adapter.submit(request, result)
        self.assertEqual(receipt["status"], "submitted")
        self.assertEqual(receipt["app"], "apps_rfp")
        self.assertTrue(receipt["provenance"]["gate_passed"])

    def test_submit_failed(self):
        """Test submitting failed RFP."""
        request = RfpRequest(
            problem_statement="We need to modernize infrastructure with proper length description",
            trace_id="rfp-002",
        )
        result = RfpResult(
            trace_id="rfp-002",
            status="failed",
            gate_violations=["quality too low"],
        )
        receipt = self.adapter.submit(request, result)
        self.assertFalse(receipt["provenance"]["gate_passed"])

    def test_get_execution_log(self):
        """Test execution log retrieval."""
        request = RfpRequest(
            problem_statement="We need to modernize infrastructure with proper length description",
            trace_id="rfp-003",
        )
        result = RfpResult(trace_id="rfp-003", status="complete")
        self.adapter.submit(request, result)
        log = self.adapter.get_execution_log()
        self.assertEqual(len(log), 1)


class TestObservabilityAdapter(unittest.TestCase):
    """Test cases for ObservabilityAdapter."""

    def setUp(self):
        self.adapter = ObservabilityAdapter()

    def test_emit_rfp_start(self):
        """Test RFP start event."""
        request = RfpRequest(
            problem_statement="We need to modernize infrastructure with proper length description",
            industry="healthcare",
            architecture_posture="hybrid",
            dry_run=True,
        )
        event = self.adapter.emit_rfp_start(request)
        self.assertEqual(event["event_type"], "rfp_start")
        self.assertEqual(event["industry"], "healthcare")
        self.assertEqual(event["architecture_posture"], "hybrid")
        self.assertTrue(event["dry_run"])

    def test_emit_rfp_complete(self):
        """Test RFP complete event."""
        result = RfpResult(
            trace_id="rfp-001",
            industry="technology",
            status="complete",
            quality_score=0.85,
            gate_violations=[],
        )
        event = self.adapter.emit_rfp_complete(result)
        self.assertEqual(event["event_type"], "rfp_complete")
        self.assertEqual(event["quality_score"], 0.85)
        self.assertTrue(event["gate_passed"])

    def test_emit_section_generated(self):
        """Test section generated event."""
        section = ProposalSection(
            section_id="sec-001",
            heading="Executive Summary",
            body="This is a comprehensive executive summary that meets the minimum length requirement.",
            word_count=150,
        )
        event = self.adapter.emit_section_generated(section)
        self.assertEqual(event["event_type"], "section_generated")
        self.assertEqual(event["section_id"], "sec-001")
        self.assertEqual(event["word_count"], 150)

    def test_get_metrics(self):
        """Test metrics retrieval."""
        result = RfpResult(trace_id="rfp-001", status="complete")
        self.adapter.emit_rfp_complete(result)
        metrics = self.adapter.get_metrics()
        self.assertEqual(len(metrics), 1)


if __name__ == "__main__":
    unittest.main()
