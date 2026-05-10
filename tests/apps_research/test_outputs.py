"""
Test Research Outputs.
"""

import unittest

from apps_research.outputs import ResearchRenderer, ResearchSummaryRenderer, SectionRenderer
from apps_research.types import ResearchResult, ResearchRunSummary, ResearchSection


class TestResearchRenderer(unittest.TestCase):
    """Test cases for ResearchRenderer."""

    def setUp(self):
        self.renderer = ResearchRenderer()

    def test_render_json(self):
        """Test JSON rendering."""
        result = ResearchResult(
            trace_id="res-001",
            topic="AI Governance",
            mode="brief",
            status="complete",
            quality_score=0.85,
        )
        json_output = self.renderer.render_json(result)
        self.assertIn("res-001", json_output)
        self.assertIn("AI Governance", json_output)

    def test_render_markdown(self):
        """Test Markdown rendering."""
        result = ResearchResult(
            trace_id="res-001",
            topic="AI Governance",
            mode="brief",
            status="complete",
            quality_score=0.85,
            gate_violations=[],
        )
        md_output = self.renderer.render_markdown(result)
        self.assertIn("AI Governance", md_output)
        self.assertIn("PASSED", md_output)

    def test_render_compact(self):
        """Test compact rendering."""
        result = ResearchResult(
            trace_id="res-001",
            status="complete",
            quality_score=0.85,
        )
        compact = self.renderer.render_compact(result)
        self.assertEqual(compact["trace_id"], "res-001")
        self.assertEqual(compact["score"], 0.85)


class TestResearchSummaryRenderer(unittest.TestCase):
    """Test cases for ResearchSummaryRenderer."""

    def setUp(self):
        self.renderer = ResearchSummaryRenderer()

    def test_render_json(self):
        """Test JSON rendering."""
        summary = ResearchRunSummary(trace_id="trace-001", quality_score=0.85)
        json_output = self.renderer.render_json(summary)
        self.assertIn("trace-001", json_output)

    def test_render_markdown(self):
        """Test Markdown rendering."""
        summary = ResearchRunSummary(
            trace_id="trace-001",
            topic="AI Governance",
            status="complete",
            sections_generated=5,
        )
        md_output = self.renderer.render_markdown(summary)
        self.assertIn("trace-001", md_output)
        self.assertIn("apps_research", md_output)


class TestSectionRenderer(unittest.TestCase):
    """Test cases for SectionRenderer."""

    def setUp(self):
        self.renderer = SectionRenderer()

    def test_render_json(self):
        """Test JSON rendering."""
        section = ResearchSection(
            section_id="sec-001",
            heading="Evidence Review",
            body="This is a comprehensive evidence review that meets the minimum length requirement for testing.",
            word_count=200,
        )
        json_output = self.renderer.render_json(section)
        self.assertIn("sec-001", json_output)
        self.assertIn("Evidence Review", json_output)

    def test_render_markdown(self):
        """Test Markdown rendering."""
        section = ResearchSection(
            section_id="sec-001",
            heading="Evidence Review",
            body="This is a comprehensive evidence review that meets the minimum length requirement for testing.",
            word_count=200,
        )
        md_output = self.renderer.render_markdown(section)
        self.assertIn("Evidence Review", md_output)
        self.assertIn("Word count: 200", md_output)

    def test_render_compact(self):
        """Test compact rendering."""
        section = ResearchSection(
            section_id="sec-001",
            heading="Evidence Review",
            body="This is a comprehensive evidence review that meets the minimum length requirement for testing.",
            word_count=200,
        )
        compact = self.renderer.render_compact(section)
        self.assertEqual(compact["section_id"], "sec-001")
        self.assertEqual(compact["word_count"], 200)

    def test_render_html(self):
        """Test HTML rendering."""
        section = ResearchSection(
            section_id="sec-001",
            heading="Evidence Review",
            body="This is a comprehensive evidence review that meets the minimum length requirement for testing.",
            word_count=200,
        )
        html_output = self.renderer.render_html(section)
        self.assertIn("<h1>Evidence Review</h1>", html_output)
        self.assertIn("minimum length requirement", html_output)


if __name__ == "__main__":
    unittest.main()
