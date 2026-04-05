"""Tests for apps_underwriting_ai config module."""

import pytest


class TestConfigImportable:
    """Verify config module is importable."""

    def test_config_module_importable(self):
        """Test that apps_underwriting_ai.config can be imported."""
        from apps_underwriting_ai import config
        assert config is not None
