"""Test DataSerializerUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestDataSerializerUtilAdg:
    """Test DataSerializerUtilAdg functionality."""

    def test_data_serializer_util_adg_imports(self):
        """Test data_serializer_util_adg module imports."""
        from agentic_core import data_serializer_util_adg

        assert data_serializer_util_adg is not None

    def test_data_serializer_util_adg_class(self):
        """Test DataSerializerUtilAdg class exists."""
        from agentic_core import DataSerializerUtilAdg

        assert DataSerializerUtilAdg is not None

    def test_data_serializer_util_adg_callable(self):
        """Test data_serializer_util_adg functions are callable."""
        from agentic_core import validate_data_serializer_util_adg

        assert callable(validate_data_serializer_util_adg)
