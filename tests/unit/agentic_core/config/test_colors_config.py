"""Test ColorsConfig functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestColorsConfig:
    """Test ColorsConfig functionality."""

    def test_colors_config_imports(self):
        """Test colors_config module imports."""
        from agentic_core import colors_config

        assert colors_config is not None

    def test_colors_config_class(self):
        """Test ColorsConfig class exists."""
        from agentic_core import ColorsConfig

        assert ColorsConfig is not None

    def test_colors_config_callable(self):
        """Test colors_config functions are callable."""
        from agentic_core import validate_colors_config

        assert callable(validate_colors_config)
