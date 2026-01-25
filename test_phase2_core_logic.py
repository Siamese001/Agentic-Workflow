import pytest
from apps_rg.logic_nodes.two_phase_generation_node import (
    TwoPhaseGenerationNode,
    BulletGenerationOutput,
)
from apps_rg.logic_nodes.thematic_analysis_node import (
    ThematicAnalysisOutput,
    AuthenticityPatterns,
    CompetitiveIntelligence,
)
from apps_rg.logic_nodes.resume_section_node import ResumeSectionNode


class TestPhase2CoreLogic:
    @pytest.fixture
    def mock_thematic_output(self):
        return ThematicAnalysisOutput(
            primary_theme="Innovation",
            secondary_themes=["AI", "Scale"],
            authenticity_patterns=AuthenticityPatterns(["Led"], ["Built"], ["%"], ["Expert"]),
            competitive_intelligence=CompetitiveIntelligence([], [], []),
            company_name="TechCorp",
        )

    def test_phase_a_bullet_generation_structure(self, mock_thematic_output):
        """
        Verify Phase A produces structured output with provenance metadata.
        """
        node = TwoPhaseGenerationNode()
        role_data = {"role": "Engineer"}

        output = node.generate_bullets_phase_a(mock_thematic_output, role_data)

        assert isinstance(output, BulletGenerationOutput)
        assert len(output.bullets) == 7
        assert "3V" in output.provenance_counts
        # Verify theme injection
        assert any("AI" in b or "Efficiency" in b for b in output.bullets)

    def test_phase_b_enforcement_integration(self, mock_thematic_output):
        """
        Verify Phase B synthesis triggers the Word Count Enforcer.
        """
        node = TwoPhaseGenerationNode()
        bullet_input = BulletGenerationOutput([], {}, 1.0)

        # We expect the output to satisfy the "resume_overview" constraint (25-33 words)
        # The mock generator produces a short string, so the Enforcer's "Regeneration"
        # (mocked in Phase 1 as += string) should trigger.

        output = node.synthesize_overview_phase_b(
            bullet_input, mock_thematic_output, target_section="resume_overview"
        )

        assert output.word_count >= 25, "Enforcer failed to expand underflow text"
        assert output.validation_result == "VALID"

    def test_resume_section_node_orchestration(self, mock_thematic_output):
        """
        Verify ResumeSectionNode correctly orchestrates the two phases.
        """
        section_node = ResumeSectionNode()
        profile = {"data": "test"}

        result = section_node.generate_experience_section(profile, mock_thematic_output)

        assert "bullets" in result
        assert "overview" in result
        assert result["meta"]["provenance"]["3V"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
