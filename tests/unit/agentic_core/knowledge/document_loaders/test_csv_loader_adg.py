"""Test CsvLoaderAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestCsvLoaderAdg:
    """Test CsvLoaderAdg functionality."""

    def test_csv_loader_adg_imports(self):
        """Test csv_loader_adg module imports."""
        from agentic_core import csv_loader_adg

        assert csv_loader_adg is not None

    def test_csv_loader_adg_class(self):
        """Test CsvLoaderAdg class exists."""
        from agentic_core import CsvLoaderAdg

        assert CsvLoaderAdg is not None

    def test_csv_loader_adg_callable(self):
        """Test csv_loader_adg functions are callable."""
        from agentic_core import validate_csv_loader_adg

        assert callable(validate_csv_loader_adg)
