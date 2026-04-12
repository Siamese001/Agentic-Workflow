"""Test L1ConfigInitAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestL1ConfigInitAdg:
    """Test L1ConfigInitAdg functionality."""

    def test_l1_config_init_adg_imports(self):
        """Test l1_config_init_adg module imports."""
        from agentic_core import l1_config_init_adg

        assert l1_config_init_adg is not None

    def test_l1_config_init_adg_class(self):
        """Test L1ConfigInitAdg class exists."""
        from agentic_core import L1ConfigInitAdg

        assert L1ConfigInitAdg is not None

    def test_l1_config_init_adg_callable(self):
        """Test l1_config_init_adg functions are callable."""
        from agentic_core import validate_l1_config_init_adg

        assert callable(validate_l1_config_init_adg)
