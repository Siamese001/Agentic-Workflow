"""Test ReactConfigAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestReactConfigAdg:
    """Test ReactConfigAdg functionality."""

    def test_react_config_adg_imports(self):
        """Test react_config_adg module imports."""
        from agentic_core import react_config_adg

        assert react_config_adg is not None

    def test_react_config_adg_class(self):
        """Test ReactConfigAdg class exists."""
        from agentic_core import ReactConfigAdg

        assert ReactConfigAdg is not None

    def test_react_config_adg_callable(self):
        """Test react_config_adg functions are callable."""
        from agentic_core import validate_react_config_adg

        assert callable(validate_react_config_adg)
