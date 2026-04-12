"""Test L5safetybaseAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestL5safetybaseAdg:
    """Test L5safetybaseAdg functionality."""

    def test_L5SafetyBase_adg_imports(self):
        """Test L5SafetyBase_adg module imports."""
        from agentic_core import L5SafetyBase_adg

        assert L5SafetyBase_adg is not None

    def test_L5SafetyBase_adg_class(self):
        """Test L5safetybaseAdg class exists."""
        from agentic_core import L5safetybaseAdg

        assert L5safetybaseAdg is not None

    def test_L5SafetyBase_adg_callable(self):
        """Test L5SafetyBase_adg functions are callable."""
        from agentic_core import validate_L5SafetyBase_adg

        assert callable(validate_L5SafetyBase_adg)
