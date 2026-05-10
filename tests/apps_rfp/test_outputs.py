"""
Test RFP Outputs.
"""

import unittest

from apps_rfp.outputs import ProposalRenderer, ProposalSummaryRenderer, SectionRenderer
from apps_rfp.types import ProposalSection, RfpResult, RfpRunSummary


class TestProposalRenderer(unittest.TestCase):
    """Test cases for ProposalRenderer."""

    def setUp(self):
        self.renderer = ProposalRenderer()

    def test_render_json(self):
        """Test JSON rendering."""
        result = RfpResult(
            trace_id="rfp-001",
            industry="technology",
            status="complete",
            quality_score=0.85,
        )
        json_output = self.renderer.render_json(result)
        self.assertIn("rfp-001", json_output)
        self.assertIn("technology", json_output)

    def test_render_markdown(self):
        """Test Markdown rendering."""
        result = RfpResult(
            trace_id="rfp-001",
            industry="technology",
            status="complete",
            quality_score=0.85,
            gate_violations=[],
        )
        md_output = self.renderer.render_markdown(result)
        self.assertIn("technology", md_output)
        self.assertIn("85%", md_output or "0.85")  # Quality score

    def test_render_compact(self):
        """Test compact rendering."""
        result = RfpResult(
            trace_id="rfp-001",
            status="complete",
            quality_score=0.85,
        )
        compact = self.renderer.render_compact(result)
        self.assertEqual(compact["trace_id"], "rfp-001")
        self.assertEqual(compact["score"], 0.85)


class TestProposalSummaryRenderer(unittest.TestCase):
    """Test cases for ProposalSummaryRenderer."""

    def setUp(self):
        self.renderer = ProposalSummaryRenderer()

    def test_render_json(self):
        """Test JSON rendering."""
        summary = RfpRunSummary(trace_id="trace-001", quality_score=0.85)
        json_output = self.renderer.render_json(summary)
        self.assertIn("trace-001", json_output)

    def test_render_markdown(self):
        """Test Markdown rendering."""
        summary = RfpRunSummary(
            trace_id="trace-001",
            industry="technology",
            status="complete",
            sections_generated=8,
        )
        md_output = self.renderer.render_markdown(summary)
        self.assertIn("trace-001", md_output)
        self.assertIn("apps_rfp", md_output)


class TestSectionRenderer(unittest.TestCase):
    """Test cases for SectionRenderer."""

    def setUp(self):
        self.renderer = SectionRenderer()

    def test_render_json(self):
        """Test JSON rendering."""
        section = ProposalSection(
            section_id="sec-001",
            heading="Executive Summary",
            body="This is a comprehensive executive summary that meets the minimum length requirement for testing.",
            word_count=150,
        )
        json_output = self.renderer.render_json(section)
        self.assertIn("sec-001", json_output)
        self.assertIn("Executive Summary", json_output)

    def test_render_markdown(self):
        """Test Markdown rendering."""
        section = ProposalSection(
            section_id="sec-001",
            heading="Executive Summary",
            body="This is a comprehensive executive summary that meets the minimum length requirement for testing.",
            word_count=150,
        )
        md_output = self.renderer.render_markdown(section)
        self.assertIn("Executive Summary", md_output)
        self.assertIn("Word count: 150", md_output)

    def test_render_compact(self):
        """Test compact rendering."""
        section = ProposalSection(
            section_id="sec-001",
            heading="Executive Summary",
            body="This is a comprehensive executive summary that meets the minimum length requirement for testing.",
            word_count=150,
        )
        compact = self.renderer.render_compact(section)
        self.assertEqual(compact["section_id"], "sec-001")
        self.assertEqual(compact["word_count"], 150)

    def test_render_html(self):
        """Test HTML rendering."""
        section = ProposalSection(
            section_id="sec-001",
            heading="Executive Summary",
            body="This is a comprehensive executive summary that meets the minimum length requirement for testing.",
            word_count=150,
        )
        html_output = self.renderer.render_html(section)
        self.assertIn("<h1>Executive Summary</h1>", html_output)
        self.assertIn("minimum length requirement", html_output)


if __name__ == "__main__":
    unittest.main()
