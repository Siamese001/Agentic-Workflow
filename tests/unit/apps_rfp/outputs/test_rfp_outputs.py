"""Test consolidated outputs for apps_rfp."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRfpOutputs:
    """Test apps_rfp output renderers."""

    def test_proposal_renderer_json(self):
        """Test ProposalRenderer JSON output."""
        from apps_rfp.outputs.proposal_renderer import ProposalRenderer

        mock_proposal = MagicMock()
        mock_proposal.model_dump.return_value = {"industry": "Technology", "status": "completed"}
        mock_proposal.industry = "Technology"
        mock_proposal.status = "completed"
        mock_proposal.quality_score = 0.85
        mock_proposal.sections = []

        renderer = ProposalRenderer()
        json_output = renderer.render_json(mock_proposal)
        assert "Technology" in json_output

    def test_proposal_renderer_markdown(self):
        """Test ProposalRenderer Markdown output."""
        from apps_rfp.outputs.proposal_renderer import ProposalRenderer

        mock_proposal = MagicMock()
        mock_proposal.industry = "Technology"
        mock_proposal.status = "completed"
        mock_proposal.quality_score = 0.85
        mock_proposal.sections = []

        renderer = ProposalRenderer()
        markdown = renderer.render_markdown(mock_proposal)
        assert "Technology" in markdown

    def test_section_renderer_json(self):
        """Test SectionRenderer JSON output."""
        from apps_rfp.outputs.section_renderer import SectionRenderer

        mock_section = MagicMock()
        mock_section.model_dump.return_value = {"heading": "Test Section"}

        renderer = SectionRenderer()
        json_output = renderer.render_json(mock_section)
        assert "Test Section" in json_output

    def test_section_renderer_markdown(self):
        """Test SectionRenderer Markdown output."""
        from apps_rfp.outputs.section_renderer import SectionRenderer

        mock_section = MagicMock()
        mock_section.heading = "Test Section"
        mock_section.body = "Test content"
        mock_section.word_count = 100
        mock_section.is_deterministic = True
        mock_section.assumptions = []
        mock_section.evidence = []

        renderer = SectionRenderer()
        markdown = renderer.render_markdown(mock_section)
        assert "Test Section" in markdown

    def test_section_renderer_json_dict_fallback(self):
        """G4: render_json uses .dict() when model_dump is absent (Pydantic v1 compat path)."""
        import json as _json
        from types import SimpleNamespace

        from apps_rfp.outputs.section_renderer import SectionRenderer

        obj = SimpleNamespace()
        obj.dict = lambda: {"heading": "V1Section", "body": "pydantic v1 fallback"}
        # SimpleNamespace has no model_dump → hasattr returns False → else branch taken

        renderer = SectionRenderer()
        json_output = renderer.render_json(obj)

        assert "V1Section" in json_output
        data = _json.loads(json_output)
        assert data["heading"] == "V1Section"

    def test_proposal_renderer_json_dict_fallback(self):
        """G4: ProposalRenderer.render_json uses .dict() when model_dump is absent."""
        import json as _json
        from types import SimpleNamespace

        from apps_rfp.outputs.proposal_renderer import ProposalRenderer

        obj = SimpleNamespace()
        obj.dict = lambda: {"industry": "V1Industry", "status": "v1"}

        renderer = ProposalRenderer()
        json_output = renderer.render_json(obj)

        assert "V1Industry" in json_output
        data = _json.loads(json_output)
        assert data["industry"] == "V1Industry"
