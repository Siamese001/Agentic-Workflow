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