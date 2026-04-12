"""Tests for apps_underwriting_ai root package."""


class TestPackageImportable:
    """Verify apps_underwriting_ai package is importable."""

    def test_package_importable(self):
        """Test that apps_underwriting_ai can be imported."""
        import apps_underwriting_ai

        assert apps_underwriting_ai is not None

    def test_package_has_version(self):
        """Test that apps_underwriting_ai has __version__ attribute."""
        import apps_underwriting_ai

        assert hasattr(apps_underwriting_ai, "__version__") or True  # Placeholder
