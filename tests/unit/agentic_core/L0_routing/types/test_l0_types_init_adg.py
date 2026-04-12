"""Test L0TypesInitAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestL0TypesInitAdg:
    """Test L0TypesInitAdg functionality."""

    def test_l0_types_init_adg_imports(self):
        """Test l0_types_init_adg module imports."""
        from agentic_core import l0_types_init_adg

        assert l0_types_init_adg is not None

    def test_l0_types_init_adg_class(self):
        """Test L0TypesInitAdg class exists."""
        from agentic_core import L0TypesInitAdg

        assert L0TypesInitAdg is not None

    def test_l0_types_init_adg_callable(self):
        """Test l0_types_init_adg functions are callable."""
        from agentic_core import validate_l0_types_init_adg

        assert callable(validate_l0_types_init_adg)
