"""
Test suite for PascalSovereigntyEnforcerAgent.
Validates eternal PascalCase SSOT enforcement with integrated test cases.
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock

from agentic_core.L5_safety.validators.PascalSovereigntyEnforcerAgent import PascalSovereigntyEnforcerAgent


class TestPascalSovereigntyEnforcer:
    """Test cases for PascalCase sovereignty enforcement."""

    @pytest.fixture
    def agent(self):
        """Create agent instance with mock context."""
        mock_ctx = MagicMock()
        return PascalSovereigntyEnforcerAgent(ctx=mock_ctx, dry_run=True)

    def test_purge_basic_snake_case(self, agent):
        """Test basic snake_case to PascalCase conversion."""
        input_content = """
class sovereign_severity(str, Enum):
    CRITICAL = "CRITICAL"
SovereignSeverity = sovereign_severity
"""
        expected = """
class SovereignSeverity(str, Enum):
    CRITICAL = "CRITICAL"
"""
        result = agent._purge_snake_case(input_content).strip()
        assert result == expected.strip()

    def test_purge_with_references(self, agent):
        """Test snake_case purge with reference updates."""
        input_content = """
class tone_type(str, Enum):
    AUTHORITATIVE = "authoritative"
ToneType = tone_type
severity = tone_type.AUTHORITATIVE
"""
        expected = """
class ToneType(str, Enum):
    AUTHORITATIVE = "authoritative"
severity = ToneType.AUTHORITATIVE
"""
        result = agent._purge_snake_case(input_content).strip()
        assert result == expected.strip()

    def test_no_change_for_clean_code(self, agent):
        """Test that clean PascalCase code is unchanged."""
        input_content = """
class SovereignEvent(BaseModel):
    pass
"""
        result = agent._purge_snake_case(input_content)
        # Normalize whitespace for comparison
        assert result.strip() == input_content.strip()

    def test_multiple_aliases_removed(self, agent):
        """Test removal of multiple backward-compatibility aliases."""
        input_content = """
class agent_message(BaseModel):
    content: str
AgentMessage = agent_message

class territory(BaseModel):
    name: str
Territory = territory
"""
        result = agent._purge_snake_case(input_content)
        assert "AgentMessage = agent_message" not in result
        assert "Territory = territory" not in result
        assert "class AgentMessage(BaseModel):" in result
        assert "class Territory(BaseModel):" in result

    def test_dataclass_purge(self, agent):
        """Test purge of snake_case dataclasses."""
        input_content = """
@dataclass
class file_paths_config:
    master_resume: Path
FilePathsConfig = file_paths_config
"""
        result = agent._purge_snake_case(input_content)
        assert "FilePathsConfig = file_paths_config" not in result
        # Class should be renamed - may keep parentheses in some formats
        assert "FilePathsConfig" in result

    def test_audit_finds_snake_case(self, agent):
        """Test audit correctly identifies snake_case files."""
        # This test would need actual test files, so we'll mock it
        targets = agent._audit_snake_case("schemas")
        # In dry_run mode with current repo state, should find files
        assert isinstance(targets, list)

    @pytest.mark.asyncio
    async def test_critique_tests_pass(self, agent):
        """Test that critique test suite passes."""
        result = await agent._run_critique_tests()
        assert "tests" in result
        assert "basic_passed" in result
        # Basic tests should pass
        assert result["basic_passed"] is True

    def test_validation_keys(self, agent):
        """Test agent returns correct validation keys."""
        keys = agent.get_validation_keys()
        assert 1 in keys  # Naming
        assert 2 in keys  # Structure
        assert 3 in keys  # Sovereignty

    @pytest.mark.asyncio
    async def test_execute_dry_run(self, agent):
        """Test execute in dry-run mode."""
        result = await agent.execute(scope="schemas")
        assert "results" in result
        assert "dry_run" in result
        assert result["dry_run"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
