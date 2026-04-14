"""Test consolidated outputs for apps_research."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestResearchOutputs:
    """Test apps_research output renderers."""

    def test_research_renderer_json(self):
        """Test ResearchRenderer JSON output."""
        from apps_research.outputs.research_renderer import ResearchRenderer

        mock_report = MagicMock()
        mock_report.model_dump = MagicMock(return_value={"topic": "Test Topic", "mode": "comprehensive"})

        renderer = ResearchRenderer()
        json_output = renderer.render_json(mock_report)
        assert "Test Topic" in json_output

    def test_research_renderer_markdown(self):
        """Test ResearchRenderer Markdown output."""
        from apps_research.outputs.research_renderer import ResearchRenderer

        mock_report = MagicMock()
        mock_report.topic = "Test Topic"
        mock_report.mode = "comprehensive"
        mock_report.status = "completed"
        mock_report.quality_score = 0.85
        mock_report.sections = []

        renderer = ResearchRenderer()
        markdown = renderer.render_markdown(mock_report)
        assert "Test Topic" in markdown

    def test_section_renderer_json(self):
        """Test SectionRenderer JSON output."""
        from apps_research.outputs.section_renderer import SectionRenderer

        mock_section = MagicMock()
        mock_section.model_dump.return_value = {"heading": "Test Section"}

        renderer = SectionRenderer()
        json_output = renderer.render_json(mock_section)
        assert "Test Section" in json_output

    def test_section_renderer_markdown(self):
        """Test SectionRenderer Markdown output."""
        from apps_research.outputs.section_renderer import SectionRenderer

        mock_section = MagicMock()
        mock_section.heading = "Test Section"
        mock_section.body = "Test content"
        mock_section.word_count = 100
        mock_section.sources = []
        mock_section.claim_type = "fact"

        renderer = SectionRenderer()
        markdown = renderer.render_markdown(mock_section)
        assert "Test Section" in markdown


@pytest.mark.unit
class TestSafeMarkdownEscaping:
    """G6: _safe_markdown correctness tests for phase-added escaping logic."""

    def test_research_renderer_safe_markdown_null_byte(self):
        """G6: null bytes are removed from output."""
        from apps_research.outputs.research_renderer import ResearchRenderer

        result = ResearchRenderer._safe_markdown("before\x00after")
        assert "\x00" not in result
        assert "beforeafter" == result

    def test_research_renderer_safe_markdown_crlf_normalised(self):
        """G6: CRLF is collapsed to LF."""
        from apps_research.outputs.research_renderer import ResearchRenderer

        result = ResearchRenderer._safe_markdown("line1\r\nline2")
        assert "\r\n" not in result
        assert "line1\nline2" == result

    def test_research_renderer_safe_markdown_backtick_injection(self):
        """G6 edge: triple backtick is broken up to prevent code-fence injection."""
        from apps_research.outputs.research_renderer import ResearchRenderer

        result = ResearchRenderer._safe_markdown("evil ```rm -rf /``` payload")
        assert "```rm" not in result
        assert "rm -rf /" in result

    def test_section_renderer_safe_markdown_null_byte(self):
        """G6: SectionRenderer._safe_markdown also strips null bytes."""
        from apps_research.outputs.section_renderer import SectionRenderer

        result = SectionRenderer._safe_markdown("clean\x00dirty")
        assert "\x00" not in result

    def test_render_json_is_deterministic(self):
        """G7: render_json produces same output for same model (sort_keys=True)."""
        from apps_research.outputs.research_renderer import ResearchRenderer

        mock_report = MagicMock()
        mock_report.model_dump.return_value = {"z_field": "last", "a_field": "first"}
        renderer = ResearchRenderer()
        out1 = renderer.render_json(mock_report)
        out2 = renderer.render_json(mock_report)
        assert out1 == out2
        assert out1.index('"a_field"') < out1.index('"z_field"')

    def test_render_html_escapes_heading(self):
        """G6 edge: section_renderer.render_html escapes HTML in heading."""
        from apps_research.outputs.section_renderer import SectionRenderer

        mock_section = MagicMock()
        mock_section.heading = "<script>alert(1)</script>"
        mock_section.body = "Safe body content here for testing."
        mock_section.word_count = 5
        mock_section.is_deterministic = True
        mock_section.claim_type = "fact"
        mock_section.sources = []

        renderer = SectionRenderer()
        html_out = renderer.render_html(mock_section)
        assert "<script>" not in html_out
        assert "&lt;script&gt;" in html_out
