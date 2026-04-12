"""Test SurgicalLowTier functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSurgicalLowTier:
    """Test SurgicalLowTier functionality."""

    def test_surgical_low_tier_imports(self):
        """Test surgical_low_tier module imports."""
        from agentic_core import surgical_low_tier

        assert surgical_low_tier is not None

    def test_surgical_low_tier_class(self):
        """Test SurgicalLowTier class exists."""
        from agentic_core import SurgicalLowTier

        assert SurgicalLowTier is not None

    def test_surgical_low_tier_callable(self):
        """Test surgical_low_tier functions are callable."""
        from agentic_core import validate_surgical_low_tier

        assert callable(validate_surgical_low_tier)
