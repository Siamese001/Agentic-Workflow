"""Test ConfigLoaderAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestConfigLoaderAdg:
    """Test ConfigLoaderAdg functionality."""

    def test_config_loader_adg_imports(self):
        """Test config_loader_adg module imports."""
        from agentic_core import config_loader_adg

        assert config_loader_adg is not None

    def test_config_loader_adg_class(self):
        """Test ConfigLoaderAdg class exists."""
        from agentic_core import ConfigLoaderAdg

        assert ConfigLoaderAdg is not None

    def test_config_loader_adg_callable(self):
        """Test config_loader_adg functions are callable."""
        from agentic_core import validate_config_loader_adg

        assert callable(validate_config_loader_adg)
