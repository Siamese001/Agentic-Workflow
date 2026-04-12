"""
Test Exec Outputs.
"""

import unittest

from apps_exec.outputs import BriefRenderer, BriefSummaryRenderer, SectionRenderer
from apps_exec.types import BriefSection, ExecBriefResult, RunSummary


class TestBriefRenderer(unittest.TestCase):
    """Test cases for BriefRenderer."""

    def setUp(self):
        self.renderer = BriefRenderer()

    def test_render_json(self):
        """Test JSON rendering."""
        result = ExecBriefResult(
            trace_id="exec-001",
            audience="board",
            tone="board-ready",
            status="complete",
            quality_score=0.85,
        )
        json_output = self.renderer.render_json(result)
        self.assertIn("exec-001", json_output)
        self.assertIn("board", json_output)

    def test_render_markdown(self):
        """Test Markdown rendering."""
        result = ExecBriefResult(
            trace_id="exec-001",
            audience="board",
            tone="board-ready",
            status="complete",
            quality_score=0.85,
            gate_violations=[],
        )
        md_output = self.renderer.render_markdown(result)
        self.assertIn("board", md_output)
        self.assertIn("PASSED", md_output)

    def test_render_compact(self):
        """Test compact rendering."""
        result = ExecBriefResult(
            trace_id="exec-001",
            status="complete",
            quality_score=0.85,
        )
        compact = self.renderer.render_compact(result)
        self.assertEqual(compact["trace_id"], "exec-001")
        self.assertEqual(compact["score"], 0.85)


class TestBriefSummaryRenderer(unittest.TestCase):
    """Test cases for BriefSummaryRenderer."""

    def setUp(self):
        self.renderer = BriefSummaryRenderer()

    def test_render_json(self):
        """Test JSON rendering."""
        summary = RunSummary(trace_id="trace-001", quality_score=0.85)
        json_output = self.renderer.render_json(summary)
        self.assertIn("trace-001", json_output)

    def test_render_markdown(self):
        """Test Markdown rendering."""
        summary = RunSummary(
            trace_id="trace-001",
            audience="board",
            status="complete",
            sections_generated=6,
        )
        md_output = self.renderer.render_markdown(summary)
        self.assertIn("trace-001", md_output)
        self.assertIn("apps_exec", md_output)


class TestSectionRenderer(unittest.TestCase):
    """Test cases for SectionRenderer."""

    def setUp(self):
        self.renderer = SectionRenderer()

    def test_render_json(self):
        """Test JSON rendering."""
        section = BriefSection(
            section_id="sec-001",
            heading="Executive Summary",
            body="This is a comprehensive executive summary that meets the minimum length requirement for the brief.",
            word_count=150,
        )
        json_output = self.renderer.render_json(section)
        self.assertIn("sec-001", json_output)
        self.assertIn("Executive Summary", json_output)

    def test_render_markdown(self):
        """Test Markdown rendering."""
        section = BriefSection(
            section_id="sec-001",
            heading="Executive Summary",
            body="This is a comprehensive executive summary that meets the minimum length requirement for the brief.",
            word_count=150,
        )
        md_output = self.renderer.render_markdown(section)
        self.assertIn("Executive Summary", md_output)
        self.assertIn("Word count: 150", md_output)

    def test_render_compact(self):
        """Test compact rendering."""
        section = BriefSection(
            section_id="sec-001",
            heading="Executive Summary",
            body="This is a comprehensive executive summary that meets the minimum length requirement for the brief.",
            word_count=150,
        )
        compact = self.renderer.render_compact(section)
        self.assertEqual(compact["section_id"], "sec-001")
        self.assertEqual(compact["word_count"], 150)

    def test_render_html(self):
        """Test HTML rendering."""
        section = BriefSection(
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
