"""Test VersionedConfig functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVersionedConfig:
    """Test VersionedConfig functionality."""

    def test_versioned_config_imports(self):
        """Test versioned_config module imports."""
        from agentic_core import versioned_config
        assert versioned_config is not None

    def test_versioned_config_class(self):
        """Test VersionedConfig class exists."""
        from agentic_core import VersionedConfig
        assert VersionedConfig is not None

    def test_versioned_config_callable(self):
        """Test versioned_config functions are callable."""
        from agentic_core import validate_versioned_config
        assert callable(validate_versioned_config)
