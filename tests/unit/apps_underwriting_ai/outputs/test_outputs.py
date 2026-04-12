"""Tests for apps_underwriting_ai outputs module."""


class TestOutputsImportable:
    """Verify outputs module is importable."""

    def test_outputs_module_importable(self):
        """Test that apps_underwriting_ai.outputs can be imported."""
        from apps_underwriting_ai import outputs

        assert outputs is not None
