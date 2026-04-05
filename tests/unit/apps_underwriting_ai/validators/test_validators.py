"""Tests for apps_underwriting_ai validators module."""

import pytest


class TestValidatorsImportable:
    """Verify validators module is importable."""

    def test_validators_module_importable(self):
        """Test that apps_underwriting_ai.validators can be imported."""
        from apps_underwriting_ai import validators
        assert validators is not None
