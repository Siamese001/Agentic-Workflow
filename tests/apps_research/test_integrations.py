"""
Test Research Integrations.
"""

import unittest

from apps_research.integrations import ExecutionAdapter, ObservabilityAdapter
from apps_research.types import (
    ResearchRequest,
    ResearchResult,
    ResearchSection,
)


class TestExecutionAdapter(unittest.TestCase):
    """Test cases for ExecutionAdapter."""

    def setUp(self):
        self.adapter = ExecutionAdapter()

    def test_submit_passed(self):
        """Test submitting passed research."""
        request = ResearchRequest(
            topic="AI Governance",
            mode="brief",
            trace_id="res-001",
        )
        result = ResearchResult(
            trace_id="res-001",
            topic="AI Governance",
            mode="brief",
            status="complete",
            quality_score=0.85,
            gate_violations=[],
        )
        receipt = self.adapter.submit(request, result)
        self.assertEqual(receipt["status"], "submitted")
        self.assertEqual(receipt["app"], "apps_research")
        self.assertTrue(receipt["provenance"]["gate_passed"])

    def test_submit_failed(self):
        """Test submitting failed research."""
        request = ResearchRequest(topic="Test", trace_id="res-002")
        result = ResearchResult(
            trace_id="res-002",
            status="failed",
            gate_violations=["quality too low"],
        )
        receipt = self.adapter.submit(request, result)
        self.assertFalse(receipt["provenance"]["gate_passed"])

    def test_get_execution_log(self):
        """Test execution log retrieval."""
        request = ResearchRequest(topic="Test", trace_id="res-003")
        result = ResearchResult(trace_id="res-003", status="complete")
        self.adapter.submit(request, result)
        log = self.adapter.get_execution_log()
        self.assertEqual(len(log), 1)


class TestObservabilityAdapter(unittest.TestCase):
    """Test cases for ObservabilityAdapter."""

    def setUp(self):
        self.adapter = ObservabilityAdapter()

    def test_emit_research_start(self):
        """Test research start event."""
        request = ResearchRequest(
            topic="AI Governance",
            mode="brief",
            audience_style="executive",
            dry_run=True,
        )
        event = self.adapter.emit_research_start(request)
        self.assertEqual(event["event_type"], "research_start")
        self.assertEqual(event["topic"], "AI Governance")
        self.assertTrue(event["dry_run"])

    def test_emit_research_complete(self):
        """Test research complete event."""
        result = ResearchResult(
            trace_id="res-001",
            topic="AI Governance",
            mode="brief",
            status="complete",
            quality_score=0.85,
            gate_violations=[],
        )
        event = self.adapter.emit_research_complete(result)
        self.assertEqual(event["event_type"], "research_complete")
        self.assertEqual(event["quality_score"], 0.85)
        self.assertTrue(event["gate_passed"])

    def test_emit_section_generated(self):
        """Test section generated event."""
        section = ResearchSection(
            section_id="sec-001",
            heading="Evidence Review",
            body="This is a comprehensive evidence review that meets the minimum length requirement for testing.",
            word_count=200,
            sources=["src1", "src2"],
        )
        event = self.adapter.emit_section_generated(section)
        self.assertEqual(event["event_type"], "section_generated")
        self.assertEqual(event["section_id"], "sec-001")
        self.assertEqual(event["source_count"], 2)

    def test_get_metrics(self):
        """Test metrics retrieval."""
        result = ResearchResult(trace_id="res-001", status="complete")
        self.adapter.emit_research_complete(result)
        metrics = self.adapter.get_metrics()
        self.assertEqual(len(metrics), 1)


if __name__ == "__main__":
    unittest.main()
