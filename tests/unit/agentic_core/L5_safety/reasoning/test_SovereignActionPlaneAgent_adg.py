"""Test SovereignactionplaneagentAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSovereignactionplaneagentAdg:
    """Test SovereignactionplaneagentAdg functionality."""

    def test_SovereignActionPlaneAgent_adg_imports(self):
        """Test SovereignActionPlaneAgent_adg module imports."""
        from agentic_core import SovereignActionPlaneAgent_adg

        assert SovereignActionPlaneAgent_adg is not None

    def test_SovereignActionPlaneAgent_adg_class(self):
        """Test SovereignactionplaneagentAdg class exists."""
        from agentic_core import SovereignactionplaneagentAdg

        assert SovereignactionplaneagentAdg is not None

    def test_SovereignActionPlaneAgent_adg_callable(self):
        """Test SovereignActionPlaneAgent_adg functions are callable."""
        from agentic_core import validate_SovereignActionPlaneAgent_adg

        assert callable(validate_SovereignActionPlaneAgent_adg)
