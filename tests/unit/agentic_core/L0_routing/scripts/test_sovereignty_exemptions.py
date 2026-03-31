"""Test SovereigntyExemptions functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSovereigntyExemptions:
    """Test SovereigntyExemptions functionality."""

    def test_sovereignty_exemptions_imports(self):
        """Test sovereignty_exemptions module imports."""
        from agentic_core import sovereignty_exemptions
        assert sovereignty_exemptions is not None

    def test_sovereignty_exemptions_class(self):
        """Test SovereigntyExemptions class exists."""
        from agentic_core import SovereigntyExemptions
        assert SovereigntyExemptions is not None

    def test_sovereignty_exemptions_callable(self):
        """Test sovereignty_exemptions functions are callable."""
        from agentic_core import validate_sovereignty_exemptions
        assert callable(validate_sovereignty_exemptions)
