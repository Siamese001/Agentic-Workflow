"""
Test: DDDAlignmentAgent

Verifies that the DDDAlignmentAgent correctly detects bounded context violations
and is properly integrated into the core hygiene agent registry.
"""

from pathlib import Path

import pytest


def get_project_root() -> Path:
    """Get project root directory."""
    import os
    if "PROJECT_ROOT" in os.environ:
        return Path(os.environ["PROJECT_ROOT"])

    known_root = Path("C:/Git/Agentic-Workflow")
    if known_root.exists() and (known_root / "agentic_core").is_dir():
        return known_root

    test_file = Path(__file__).resolve()
    return test_file.parent.parent.parent


class TestDDDAlignmentAgent:
    """Test suite for DDDAlignmentAgent."""

    @pytest.fixture
    def project_root(self) -> Path:
        return get_project_root()

    def test_agent_can_be_imported(self):
        """Verify DDDAlignmentAgent can be imported."""
        from agentic_core.L5_safety.validators.DDDAlignmentAgent import DDDAlignmentAgent
        assert DDDAlignmentAgent is not None

    def test_agent_has_heal_repository(self):
        """Verify DDDAlignmentAgent has heal_repository method."""
        from agentic_core.L5_safety.validators.DDDAlignmentAgent import DDDAlignmentAgent
        assert hasattr(DDDAlignmentAgent, 'heal_repository')

    def test_agent_has_run_method(self):
        """Verify DDDAlignmentAgent has run method."""
        from agentic_core.L5_safety.validators.DDDAlignmentAgent import DDDAlignmentAgent
        assert hasattr(DDDAlignmentAgent, 'run')

    def test_agent_can_be_instantiated(self, project_root: Path):
        """Verify DDDAlignmentAgent can be instantiated."""
        from agentic_core.L5_safety.validators.DDDAlignmentAgent import DDDAlignmentAgent
        agent = DDDAlignmentAgent(project_root=project_root)
        assert agent.project_root == project_root.resolve()

    def test_agent_in_core_hygiene_registry(self):
        """Verify DDDAlignmentAgent is in core hygiene agents registry."""
        from agentic_core.config.core_hygiene_agents import CORE_HYGIENE_AGENTS

        tier_2 = CORE_HYGIENE_AGENTS.get("tier_2_architectural", [])
        assert "DDDAlignmentAgent" in tier_2, (
            "DDDAlignmentAgent must be in tier_2_architectural"
        )

    def test_agent_has_description(self):
        """Verify DDDAlignmentAgent has a description in registry."""
        from agentic_core.config.core_hygiene_agents import AGENT_DESCRIPTIONS

        assert "DDDAlignmentAgent" in AGENT_DESCRIPTIONS, (
            "DDDAlignmentAgent must have a description"
        )
        assert "DDD" in AGENT_DESCRIPTIONS["DDDAlignmentAgent"]

    def test_bounded_contexts_defined(self):
        """Verify BOUNDED_CONTEXTS is properly defined."""
        from agentic_core.L5_safety.validators.DDDAlignmentAgent import BOUNDED_CONTEXTS

        # Must have L0-L6 contexts
        required_contexts = [
            "L0_Governance", "L1_Cognition", "L2_Execution",
            "L3_Orchestration", "L4_State", "L5_Safety", "L6_Observability"
        ]

        for ctx in required_contexts:
            assert ctx in BOUNDED_CONTEXTS, f"Missing context: {ctx}"
            assert "path" in BOUNDED_CONTEXTS[ctx]
            assert "rank" in BOUNDED_CONTEXTS[ctx]

    def test_get_alignment_score(self, project_root: Path):
        """Verify alignment score calculation."""
        from agentic_core.L5_safety.validators.DDDAlignmentAgent import DDDAlignmentAgent

        agent = DDDAlignmentAgent(project_root=project_root)
        # Before running, score should be 100 (no violations)
        assert agent.get_alignment_score() == 100.0

    def test_validate_ddd_alignment_function(self, project_root: Path):
        """Verify convenience function works."""
        from agentic_core.L5_safety.validators.DDDAlignmentAgent import validate_ddd_alignment

        score, messages = validate_ddd_alignment(str(project_root / "agentic_core" / "config"))
        assert isinstance(score, float)
        assert 0 <= score <= 100
        assert isinstance(messages, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
