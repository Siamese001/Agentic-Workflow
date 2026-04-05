"""Test ConfigLoader functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestConfigLoader:
    """Test ConfigLoader functionality."""

    def test_config_loader_imports(self):
        """Test config_loader module imports."""
        from agentic_core import config_loader
        assert config_loader is not None

    def test_config_loader_class(self):
        """Test ConfigLoader class exists."""
        from agentic_core import ConfigLoader
        assert ConfigLoader is not None

    def test_config_loader_callable(self):
        """Test config_loader functions are callable."""
        from agentic_core import validate_config_loader
        assert callable(validate_config_loader)
