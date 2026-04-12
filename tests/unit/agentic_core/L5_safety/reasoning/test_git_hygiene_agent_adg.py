"""Test GitHygieneAgentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGitHygieneAgentAdg:
    """Test GitHygieneAgentAdg functionality."""

    def test_git_hygiene_agent_adg_imports(self):
        """Test git_hygiene_agent_adg module imports."""
        from agentic_core import git_hygiene_agent_adg

        assert git_hygiene_agent_adg is not None

    def test_git_hygiene_agent_adg_class(self):
        """Test GitHygieneAgentAdg class exists."""
        from agentic_core import GitHygieneAgentAdg

        assert GitHygieneAgentAdg is not None

    def test_git_hygiene_agent_adg_callable(self):
        """Test git_hygiene_agent_adg functions are callable."""
        from agentic_core import validate_git_hygiene_agent_adg

        assert callable(validate_git_hygiene_agent_adg)
