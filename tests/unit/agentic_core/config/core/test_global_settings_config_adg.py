"""Test GlobalSettingsConfigAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGlobalSettingsConfigAdg:
    """Test GlobalSettingsConfigAdg functionality."""

    def test_global_settings_config_adg_imports(self):
        """Test global_settings_config_adg module imports."""
        from agentic_core import global_settings_config_adg
        assert global_settings_config_adg is not None

    def test_global_settings_config_adg_class(self):
        """Test GlobalSettingsConfigAdg class exists."""
        from agentic_core import GlobalSettingsConfigAdg
        assert GlobalSettingsConfigAdg is not None

    def test_global_settings_config_adg_callable(self):
        """Test global_settings_config_adg functions are callable."""
        from agentic_core import validate_global_settings_config_adg
        assert callable(validate_global_settings_config_adg)
