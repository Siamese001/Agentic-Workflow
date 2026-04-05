"""Tests for apps_underwriting_ai parsers module."""

import pytest


class TestParsersImportable:
    """Verify parsers module is importable."""

    def test_parsers_module_importable(self):
        """Test that apps_underwriting_ai.parsers can be imported."""
        from apps_underwriting_ai import parsers
        assert parsers is not None
