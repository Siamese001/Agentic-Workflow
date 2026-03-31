"""Test ConfignorePolicy functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestConfignorePolicy:
    """Test ConfignorePolicy functionality."""

    def test_confignore_policy_imports(self):
        """Test confignore_policy module imports."""
        from agentic_core import confignore_policy
        assert confignore_policy is not None

    def test_confignore_policy_class(self):
        """Test ConfignorePolicy class exists."""
        from agentic_core import ConfignorePolicy
        assert ConfignorePolicy is not None

    def test_confignore_policy_callable(self):
        """Test confignore_policy functions are callable."""
        from agentic_core import validate_confignore_policy
        assert callable(validate_confignore_policy)
