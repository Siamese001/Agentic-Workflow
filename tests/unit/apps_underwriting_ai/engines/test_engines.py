"""Tests for apps_underwriting_ai engines module."""


class TestEnginesImportable:
    """Verify engines module is importable."""

    def test_engines_module_importable(self):
        """Test that apps_underwriting_ai.engines can be imported."""
        from apps_underwriting_ai import engines

        assert engines is not None
