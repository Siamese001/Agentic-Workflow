"""Test L2HealersAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestL2HealersAdg:
    """Test L2HealersAdg functionality."""

    def test_l2_healers_adg_imports(self):
        """Test l2_healers_adg module imports."""
        from agentic_core import l2_healers_adg
        assert l2_healers_adg is not None

    def test_l2_healers_adg_class(self):
        """Test L2HealersAdg class exists."""
        from agentic_core import L2HealersAdg
        assert L2HealersAdg is not None

    def test_l2_healers_adg_callable(self):
        """Test l2_healers_adg functions are callable."""
        from agentic_core import validate_l2_healers_adg
        assert callable(validate_l2_healers_adg)
