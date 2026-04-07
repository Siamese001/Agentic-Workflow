"""Tests for apps_underwriting_ai reasoning module."""



class TestReasoningImportable:
    """Verify reasoning module is importable."""

    def test_reasoning_module_importable(self):
        """Test that apps_underwriting_ai.reasoning can be imported."""
        from apps_underwriting_ai import reasoning
        assert reasoning is not None
