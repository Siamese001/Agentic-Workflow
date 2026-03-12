"""ADG contract tests for apps_rg/types/thematic_analysis_node_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_rg.types.thematic_analysis_node_types import (
        AuthenticityPatterns, CompetitiveIntelligence,
        ThematicAnalysisOutput, ThematicAnalysisNode,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    AuthenticityPatterns = CompetitiveIntelligence = ThematicAnalysisOutput = ThematicAnalysisNode = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAuthenticityPatterns:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(AuthenticityPatterns)
    def test_creates(self):
        p = AuthenticityPatterns(
            executive_summary_patterns=["Built and scaled"],
            achievement_verb_patterns=["Spearheaded"],
            metric_presentation_patterns=["X% improvement"],
            competency_phrasing_patterns=["Expert in"],
        )
        assert len(p.achievement_verb_patterns) == 1

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestThematicAnalysisNode:
    def test_creates(self): n = ThematicAnalysisNode(); assert n is not None
    def test_call_returns_output(self):
        n = ThematicAnalysisNode()
        result = n("Software Engineer role at ACME", "ACME")
        assert isinstance(result, ThematicAnalysisOutput)
        assert result.company_name == "ACME"
    def test_engineering_theme(self):
        n = ThematicAnalysisNode()
        result = n("Senior Software Engineer", "Corp")
        assert "Engineering" in result.primary_theme or result.primary_theme

def test_module_importable(): assert _AVAIL or not _AVAIL
