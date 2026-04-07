"""Test BriefAssemblerService functionality."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestBriefAssemblerService:
    """Test BriefAssemblerService functionality."""

    def test_init_with_config(self):
        """Test initialization with config."""
        from apps_exec.services.brief_assembler_service import BriefAssemblerService

        config = {"default_persona": "recruiter"}
        service = BriefAssemblerService(config)
        assert service.config == config

    def test_init_without_config(self):
        """Test initialization without config."""
        from apps_exec.services.brief_assembler_service import BriefAssemblerService

        service = BriefAssemblerService()
        assert service.config == {}
        assert service._brief_template is not None

    @patch("apps_exec.services.brief_assembler_service._emit_snapshots_state")
    def test_init_emits_state_snapshot(self, mock_emit):
        """Test that initialization emits state snapshot."""
        from apps_exec.services.brief_assembler_service import BriefAssemblerService

        BriefAssemblerService()
        mock_emit.assert_called_once_with("p0", "brief_assembler", "init")

    def test_assemble_brief(self):
        """Test assembling a brief from content sections."""
        from apps_exec.services.brief_assembler_service import BriefAssemblerService

        service = BriefAssemblerService()
        sections = [
            {"heading": "Introduction", "content": "This is the introduction."},
            {"heading": "Analysis", "content": "This is the analysis."},
        ]

        brief = service.assemble_brief(sections, "recruiter", 600)

        assert "brief_id" in brief
        assert brief["persona_id"] == "recruiter"
        assert brief["word_count"] == 8
        assert brief["target_word_count"] == 600
        assert "Introduction" in brief["sections"]
        assert "Analysis" in brief["sections"]
        assert "# Executive Brief" in brief["content"]

    def test_assemble_brief_empty_sections(self):
        """Test assembling brief with empty sections (edge case)."""
        from apps_exec.services.brief_assembler_service import BriefAssemblerService

        service = BriefAssemblerService()
        brief = service.assemble_brief([], "recruiter", 600)

        assert brief["word_count"] == 0
        assert brief["sections"] == []
        assert brief["complete"] is False

    def test_assemble_brief_section_without_heading(self):
        """Test assembling brief with section missing heading (edge case)."""
        from apps_exec.services.brief_assembler_service import BriefAssemblerService

        service = BriefAssemblerService()
        sections = [{"content": "Content without heading"}]

        brief = service.assemble_brief(sections, "recruiter", 600)

        # When heading is missing, it defaults to "Section"
        assert brief["sections"] == ["Section"] or brief["sections"][0] is None

    def test_assemble_brief_section_without_content(self):
        """Test assembling brief with section missing content (edge case)."""
        from apps_exec.services.brief_assembler_service import BriefAssemblerService

        service = BriefAssemblerService()
        sections = [{"heading": "Test Section"}]

        brief = service.assemble_brief(sections, "recruiter", 600)

        assert brief["word_count"] == 0

    def test_assemble_brief_meets_target(self):
        """Test brief marked complete when meets target word count."""
        from apps_exec.services.brief_assembler_service import BriefAssemblerService

        service = BriefAssemblerService()
        long_content = "word " * 500  # 500 words
        sections = [{"heading": "Section", "content": long_content}]

        brief = service.assemble_brief(sections, "recruiter", 600)

        assert brief["complete"] is True

    def test_assemble_brief_below_target(self):
        """Test brief marked incomplete when below target word count."""
        from apps_exec.services.brief_assembler_service import BriefAssemblerService

        service = BriefAssemblerService()
        short_content = "word " * 10  # 10 words
        sections = [{"heading": "Section", "content": short_content}]

        brief = service.assemble_brief(sections, "recruiter", 600)

        assert brief["complete"] is False

    def test_assemble_brief_default_persona(self):
        """Test assembling brief with default persona."""
        from apps_exec.services.brief_assembler_service import BriefAssemblerService

        service = BriefAssemblerService()
        sections = [{"heading": "Section", "content": "Content"}]

        brief = service.assemble_brief(sections)

        assert brief["persona_id"] == "recruiter"

    def test_get_brief_summary(self):
        """Test getting brief summary."""
        from apps_exec.services.brief_assembler_service import BriefAssemblerService

        service = BriefAssemblerService()
        brief = {
            "brief_id": "brief_123",
            "persona_id": "recruiter",
            "word_count": 500,
            "complete": True,
            "sections": ["Introduction", "Analysis"],
        }

        summary = service.get_brief_summary(brief)

        assert summary["brief_id"] == "brief_123"
        assert summary["persona_id"] == "recruiter"
        assert summary["word_count"] == 500
        assert summary["complete"] is True
        assert summary["sections"] == ["Introduction", "Analysis"]

    def test_get_brief_summary_missing_fields(self):
        """Test getting summary with missing fields (edge case)."""
        from apps_exec.services.brief_assembler_service import BriefAssemblerService

        service = BriefAssemblerService()
        brief = {}

        summary = service.get_brief_summary(brief)

        assert summary["brief_id"] is None
        assert summary["persona_id"] is None
        assert summary["word_count"] is None
        assert summary["sections"] == []
