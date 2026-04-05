"""Test BriefRenderer functionality."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBriefRenderer:
    """Test BriefRenderer functionality."""

    def test_render_json(self):
        """Test rendering brief as JSON."""
        from apps_exec.outputs.brief_renderer import BriefRenderer

        mock_result = MagicMock()
        mock_result.model_dump.return_value = {
            "audience": "recruiter",
            "tone": "professional",
            "status": "completed"
        }

        renderer = BriefRenderer()
        json_output = renderer.render_json(mock_result)

        assert "recruiter" in json_output
        assert "professional" in json_output

    def test_render_markdown(self):
        """Test rendering brief as Markdown."""
        from apps_exec.outputs.brief_renderer import BriefRenderer

        mock_result = MagicMock()
        mock_result.audience = "recruiter"
        mock_result.tone = "professional"
        mock_result.status = "completed"
        mock_result.quality_score = 0.85
        mock_result.passed_gate = True
        mock_result.sections = []

        renderer = BriefRenderer()
        markdown = renderer.render_markdown(mock_result)

        assert "# Executive Brief" in markdown
        assert "recruiter" in markdown
        assert "professional" in markdown
        assert "✅ PASSED" in markdown
        assert "85%" in markdown

    def test_render_markdown_failed_gate(self):
        """Test rendering Markdown with failed gate."""
        from apps_exec.outputs.brief_renderer import BriefRenderer

        mock_result = MagicMock()
        mock_result.audience = "recruiter"
        mock_result.tone = "professional"
        mock_result.status = "completed"
        mock_result.quality_score = 0.85
        mock_result.passed_gate = False
        mock_result.sections = []

        renderer = BriefRenderer()
        markdown = renderer.render_markdown(mock_result)

        assert "❌ FAILED" in markdown

    def test_render_markdown_with_sections(self):
        """Test rendering Markdown with sections."""
        from apps_exec.outputs.brief_renderer import BriefRenderer

        mock_section = MagicMock()
        mock_section.heading = "Introduction"
        mock_section.body = "This is the introduction."
        mock_section.why_this_matters = "Important context"
        mock_section.word_count = 5
        mock_section.evidence_anchors = ["evidence1", "evidence2"]

        mock_result = MagicMock()
        mock_result.audience = "recruiter"
        mock_result.tone = "professional"
        mock_result.status = "completed"
        mock_result.quality_score = 0.85
        mock_result.passed_gate = True
        mock_result.sections = [mock_section]

        renderer = BriefRenderer()
        markdown = renderer.render_markdown(mock_result)

        assert "## Sections" in markdown
        assert "### Introduction" in markdown
        assert "Why this matters:" in markdown
