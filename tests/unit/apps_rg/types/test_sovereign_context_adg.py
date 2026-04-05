"""Test SovereignContextAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSovereignContextAdg:
    """Test SovereignContextAdg functionality."""

    def test_sovereign_context_adg_imports(self):
        """Test sovereign_context_adg module imports."""
        from agentic_core import sovereign_context_adg
        assert sovereign_context_adg is not None

    def test_sovereign_context_adg_class(self):
        """Test SovereignContextAdg class exists."""
        from agentic_core import SovereignContextAdg
        assert SovereignContextAdg is not None

    def test_sovereign_context_adg_callable(self):
        """Test sovereign_context_adg functions are callable."""
        from agentic_core import validate_sovereign_context_adg
        assert callable(validate_sovereign_context_adg)
