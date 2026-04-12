"""
Test RG Outputs.
"""

import unittest

from apps_rg.outputs import ResumeRenderer, ResumeSummaryRenderer, SectionRenderer
from apps_rg.types import ResumeResult, ResumeRunSummary, ResumeSection


class TestResumeRenderer(unittest.TestCase):
    """Test cases for ResumeRenderer."""

    def setUp(self):
        self.renderer = ResumeRenderer()

    def test_render_json(self):
        """Test JSON rendering."""
        result = ResumeResult(
            trace_id="rg-001",
            candidate_name="Jane Smith",
            target_role="Senior Engineer",
            status="complete",
            ats_score=85.5,
            quality_score=0.88,
        )
        json_output = self.renderer.render_json(result)
        self.assertIn("rg-001", json_output)
        self.assertIn("Jane Smith", json_output)

    def test_render_markdown(self):
        """Test Markdown rendering."""
        result = ResumeResult(
            trace_id="rg-001",
            candidate_name="Jane Smith",
            target_role="Senior Engineer",
            status="complete",
            ats_score=85.5,
            quality_score=0.88,
            gate_violations=[],
        )
        md_output = self.renderer.render_markdown(result)
        self.assertIn("Jane Smith", md_output)
        self.assertIn("PASSED", md_output)

    def test_render_compact(self):
        """Test compact rendering."""
        result = ResumeResult(
            trace_id="rg-001",
            status="complete",
            ats_score=85.5,
            quality_score=0.88,
        )
        compact = self.renderer.render_compact(result)
        self.assertEqual(compact["trace_id"], "rg-001")
        self.assertEqual(compact["ats_score"], 85.5)


class TestResumeSummaryRenderer(unittest.TestCase):
    """Test cases for ResumeSummaryRenderer."""

    def setUp(self):
        self.renderer = ResumeSummaryRenderer()

    def test_render_json(self):
        """Test JSON rendering."""
        summary = ResumeRunSummary(trace_id="trace-001", quality_score=0.88)
        json_output = self.renderer.render_json(summary)
        self.assertIn("trace-001", json_output)

    def test_render_markdown(self):
        """Test Markdown rendering."""
        summary = ResumeRunSummary(
            trace_id="trace-001",
            candidate_name="Jane Smith",
            target_role="Senior Engineer",
            status="complete",
            ats_score=85.5,
        )
        md_output = self.renderer.render_markdown(summary)
        self.assertIn("trace-001", md_output)
        self.assertIn("apps_rg", md_output)


class TestSectionRenderer(unittest.TestCase):
    """Test cases for SectionRenderer."""

    def setUp(self):
        self.renderer = SectionRenderer()

    def test_render_json(self):
        """Test JSON rendering."""
        section = ResumeSection(
            section_id="sec-001",
            section_type="summary",
            content="Professional summary that meets minimum requirements for testing.",
            word_count=50,
        )
        json_output = self.renderer.render_json(section)
        self.assertIn("sec-001", json_output)
        self.assertIn("summary", json_output)

    def test_render_markdown(self):
        """Test Markdown rendering."""
        section = ResumeSection(
            section_id="sec-001",
            section_type="summary",
            content="Professional summary that meets minimum requirements for testing.",
            word_count=50,
        )
        md_output = self.renderer.render_markdown(section)
        self.assertIn("Professional Summary", md_output)
        self.assertIn("Word count: 50", md_output)

    def test_render_compact(self):
        """Test compact rendering."""
        section = ResumeSection(
            section_id="sec-001",
            section_type="summary",
            content="Professional summary that meets minimum requirements for testing.",
            word_count=50,
        )
        compact = self.renderer.render_compact(section)
        self.assertEqual(compact["section_id"], "sec-001")
        self.assertEqual(compact["word_count"], 50)

    def test_render_html(self):
        """Test HTML rendering."""
        section = ResumeSection(
            section_id="sec-001",
            section_type="summary",
            content="Professional summary that meets minimum requirements for testing.",
            word_count=50,
        )
        html_output = self.renderer.render_html(section)
        self.assertIn("<h2>Professional Summary</h2>", html_output)
        self.assertIn("minimum requirements", html_output)


if __name__ == "__main__":
    unittest.main()
