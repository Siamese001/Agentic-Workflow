"""Test SectionRenderer functionality."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSectionRenderer:
    """Test SectionRenderer functionality."""

    def test_render_json(self):
        """Test rendering section as JSON."""
        from apps_exec.outputs.section_renderer import SectionRenderer

        mock_section = MagicMock()
        mock_section.model_dump.return_value = {
            "section_id": "sec_1",
            "heading": "Introduction",
            "body": "Test content"
        }

        renderer = SectionRenderer()
        json_output = renderer.render_json(mock_section)

        assert "Introduction" in json_output
        assert "Test content" in json_output

    def test_render_markdown(self):
        """Test rendering section as Markdown."""
        from apps_exec.outputs.section_renderer import SectionRenderer

        mock_section = MagicMock()
        mock_section.heading = "Introduction"
        mock_section.body = "This is the introduction."
        mock_section.why_this_matters = "Important context"
        mock_section.evidence_anchors = ["evidence1"]
        mock_section.word_count = 5
        mock_section.is_deterministic = True

        renderer = SectionRenderer()
        markdown = renderer.render_markdown(mock_section)

        assert "# Introduction" in markdown
        assert "This is the introduction." in markdown
        assert "Why this matters:" in markdown
        assert "## Evidence" in markdown
        assert "evidence1" in markdown

    def test_render_markdown_no_evidence(self):
        """Test rendering Markdown without evidence."""
        from apps_exec.outputs.section_renderer import SectionRenderer

        mock_section = MagicMock()
        mock_section.heading = "Introduction"
        mock_section.body = "This is the introduction."
        mock_section.why_this_matters = None
        mock_section.evidence_anchors = []
        mock_section.word_count = 5
        mock_section.is_deterministic = True

        renderer = SectionRenderer()
        markdown = renderer.render_markdown(mock_section)

        assert "# Introduction" in markdown
        assert "## Evidence" not in markdown

    def test_render_compact(self):
        """Test rendering section as compact dict."""
        from apps_exec.outputs.section_renderer import SectionRenderer

        mock_section = MagicMock()
        mock_section.section_id = "sec_1"
        mock_section.heading = "Introduction"
        mock_section.word_count = 100
        mock_section.is_deterministic = True
        mock_section.evidence_anchors = ["ev1", "ev2"]
        mock_section.why_this_matters = "Important"

        renderer = SectionRenderer()
        compact = renderer.render_compact(mock_section)

        assert compact["section_id"] == "sec_1"
        assert compact["heading"] == "Introduction"
        assert compact["word_count"] == 100
        assert compact["is_deterministic"] is True
        assert compact["evidence_count"] == 2
        assert compact["has_significance"] is True

    def test_render_compact_no_significance(self):
        """Test rendering compact without significance."""
        from apps_exec.outputs.section_renderer import SectionRenderer

        mock_section = MagicMock()
        mock_section.section_id = "sec_1"
        mock_section.heading = "Introduction"
        mock_section.word_count = 100
        mock_section.is_deterministic = True
        mock_section.evidence_anchors = []
        mock_section.why_this_matters = None

        renderer = SectionRenderer()
        compact = renderer.render_compact(mock_section)

        assert compact["has_significance"] is False

    def test_render_html(self):
        """Test rendering section as HTML."""
        from apps_exec.outputs.section_renderer import SectionRenderer

        mock_section = MagicMock()
        mock_section.heading = "Introduction"
        mock_section.body = "This is the introduction."
        mock_section.why_this_matters = "Important"
        mock_section.evidence_anchors = ["ev1"]
        mock_section.word_count = 5
        mock_section.is_deterministic = True

        renderer = SectionRenderer()
        html = renderer.render_html(mock_section)

        assert "<h1>Introduction</h1>" in html
        assert "<p>This is the introduction.</p>" in html
        assert "<strong>Why this matters:</strong>" in html
        assert "<h2>Evidence</h2>" in html
        assert "<li>ev1</li>" in html
