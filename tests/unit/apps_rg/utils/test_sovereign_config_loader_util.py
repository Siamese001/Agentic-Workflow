"""Test SovereignConfigLoaderUtil functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSovereignConfigLoaderUtil:
    """Test SovereignConfigLoaderUtil functionality."""

    def test_sovereign_config_loader_util_imports(self):
        """Test sovereign_config_loader_util module imports."""
        from agentic_core import sovereign_config_loader_util
        assert sovereign_config_loader_util is not None

    def test_sovereign_config_loader_util_class(self):
        """Test SovereignConfigLoaderUtil class exists."""
        from agentic_core import SovereignConfigLoaderUtil
        assert SovereignConfigLoaderUtil is not None

    def test_sovereign_config_loader_util_callable(self):
        """Test sovereign_config_loader_util functions are callable."""
        from agentic_core import validate_sovereign_config_loader_util
        assert callable(validate_sovereign_config_loader_util)
