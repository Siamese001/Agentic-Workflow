"""Test SovereignbaseagentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSovereignbaseagentAdg:
    """Test SovereignbaseagentAdg functionality."""

    def test_SovereignBaseAgent_adg_imports(self):
        """Test SovereignBaseAgent_adg module imports."""
        from agentic_core import SovereignBaseAgent_adg

        assert SovereignBaseAgent_adg is not None

    def test_SovereignBaseAgent_adg_class(self):
        """Test SovereignbaseagentAdg class exists."""
        from agentic_core import SovereignbaseagentAdg

        assert SovereignbaseagentAdg is not None

    def test_SovereignBaseAgent_adg_callable(self):
        """Test SovereignBaseAgent_adg functions are callable."""
        from agentic_core import validate_SovereignBaseAgent_adg

        assert callable(validate_SovereignBaseAgent_adg)
