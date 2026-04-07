"""Tests for apps_underwriting_ai ingestion module."""



class TestIngestionImportable:
    """Verify ingestion module is importable."""

    def test_ingestion_module_importable(self):
        """Test that apps_underwriting_ai.ingestion can be imported."""
        from apps_underwriting_ai import ingestion
        assert ingestion is not None
