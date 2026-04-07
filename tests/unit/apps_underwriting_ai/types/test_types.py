"""Tests for apps_underwriting_ai types module."""



class TestTypesImportable:
    """Verify types module is importable."""

    def test_types_module_importable(self):
        """Test that apps_underwriting_ai.types can be imported."""
        from apps_underwriting_ai import types
        assert types is not None
