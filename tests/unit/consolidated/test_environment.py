"""Test Environment functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestEnvironment:
    """Test Environment functionality."""

    def test_environment_imports(self):
        """Test environment module imports."""
        from agentic_core import environment
        assert environment is not None

    def test_environment_class(self):
        """Test Environment class exists."""
        from agentic_core import Environment
        assert Environment is not None

    def test_environment_callable(self):
        """Test environment functions are callable."""
        from agentic_core import validate_environment
        assert callable(validate_environment)
