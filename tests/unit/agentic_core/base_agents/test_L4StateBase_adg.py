"""Test L4statebaseAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestL4statebaseAdg:
    """Test L4statebaseAdg functionality."""

    def test_L4StateBase_adg_imports(self):
        """Test L4StateBase_adg module imports."""
        from agentic_core import L4StateBase_adg

        assert L4StateBase_adg is not None

    def test_L4StateBase_adg_class(self):
        """Test L4statebaseAdg class exists."""
        from agentic_core import L4statebaseAdg

        assert L4statebaseAdg is not None

    def test_L4StateBase_adg_callable(self):
        """Test L4StateBase_adg functions are callable."""
        from agentic_core import validate_L4StateBase_adg

        assert callable(validate_L4StateBase_adg)
