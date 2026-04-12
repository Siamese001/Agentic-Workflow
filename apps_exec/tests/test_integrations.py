"""
Test Exec Integrations.
"""

import unittest

from apps_exec.integrations import ExecutionAdapter, ObservabilityAdapter
from apps_exec.types import (
    BriefSection,
    ExecBriefRequest,
    ExecBriefResult,
)


class TestExecutionAdapter(unittest.TestCase):
    """Test cases for ExecutionAdapter."""

    def setUp(self):
        self.adapter = ExecutionAdapter()

    def test_submit_passed(self):
        """Test submitting passed brief."""
        request = ExecBriefRequest(
            audience="board",
            tone="board-ready",
            trace_id="exec-001",
        )
        result = ExecBriefResult(
            trace_id="exec-001",
            audience="board",
            tone="board-ready",
            status="complete",
            quality_score=0.85,
            gate_violations=[],
        )
        receipt = self.adapter.submit(request, result)
        self.assertEqual(receipt["status"], "submitted")
        self.assertEqual(receipt["app"], "apps_exec")
        self.assertTrue(receipt["provenance"]["gate_passed"])

    def test_submit_failed(self):
        """Test submitting failed brief."""
        request = ExecBriefRequest(
            audience="cto",
            trace_id="exec-002",
        )
        result = ExecBriefResult(
            trace_id="exec-002",
            status="failed",
            gate_violations=["quality too low"],
        )
        receipt = self.adapter.submit(request, result)
        self.assertFalse(receipt["provenance"]["gate_passed"])

    def test_get_execution_log(self):
        """Test execution log retrieval."""
        request = ExecBriefRequest(audience="board", trace_id="exec-003")
        result = ExecBriefResult(trace_id="exec-003", status="complete")
        self.adapter.submit(request, result)
        log = self.adapter.get_execution_log()
        self.assertEqual(len(log), 1)


class TestObservabilityAdapter(unittest.TestCase):
    """Test cases for ObservabilityAdapter."""

    def setUp(self):
        self.adapter = ObservabilityAdapter()

    def test_emit_brief_start(self):
        """Test brief start event."""
        request = ExecBriefRequest(
            audience="board",
            tone="board-ready",
            emphasis_areas=["governance", "safety"],
            dry_run=True,
        )
        event = self.adapter.emit_brief_start(request)
        self.assertEqual(event["event_type"], "brief_start")
        self.assertEqual(event["audience"], "board")
        self.assertEqual(event["tone"], "board-ready")
        self.assertTrue(event["dry_run"])

    def test_emit_brief_complete(self):
        """Test brief complete event."""
        result = ExecBriefResult(
            trace_id="exec-001",
            audience="board",
            tone="board-ready",
            status="complete",
            quality_score=0.85,
            gate_violations=[],
        )
        event = self.adapter.emit_brief_complete(result)
        self.assertEqual(event["event_type"], "brief_complete")
        self.assertEqual(event["quality_score"], 0.85)
        self.assertTrue(event["gate_passed"])

    def test_emit_section_generated(self):
        """Test section generated event."""
        section = BriefSection(
            section_id="sec-001",
            heading="Executive Summary",
            body="This is a comprehensive executive summary that meets the minimum length requirement for the brief.",
            word_count=150,
            evidence_anchors=["doc1", "doc2"],
        )
        event = self.adapter.emit_section_generated(section)
        self.assertEqual(event["event_type"], "section_generated")
        self.assertEqual(event["section_id"], "sec-001")
        self.assertEqual(event["word_count"], 150)
        self.assertEqual(event["evidence_count"], 2)

    def test_get_metrics(self):
        """Test metrics retrieval."""
        result = ExecBriefResult(trace_id="exec-001", status="complete")
        self.adapter.emit_brief_complete(result)
        metrics = self.adapter.get_metrics()
        self.assertEqual(len(metrics), 1)


if __name__ == "__main__":
    unittest.main()
