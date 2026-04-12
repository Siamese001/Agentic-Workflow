"""Test Sovereignbaseagent functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSovereignbaseagent:
    """Test Sovereignbaseagent functionality."""

    def test_SovereignBaseAgent_imports(self):
        """Test SovereignBaseAgent module imports."""
        from agentic_core import SovereignBaseAgent

        assert SovereignBaseAgent is not None

    def test_SovereignBaseAgent_class(self):
        """Test Sovereignbaseagent class exists."""
        from agentic_core import Sovereignbaseagent

        assert Sovereignbaseagent is not None

    def test_SovereignBaseAgent_callable(self):
        """Test SovereignBaseAgent functions are callable."""
        from agentic_core import validate_SovereignBaseAgent

        assert callable(validate_SovereignBaseAgent)
