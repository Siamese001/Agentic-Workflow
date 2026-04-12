"""Test LocationUtilsUtilAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestLocationUtilsUtilAdg:
    """Test LocationUtilsUtilAdg functionality."""

    def test_location_utils_util_adg_imports(self):
        """Test location_utils_util_adg module imports."""
        from agentic_core import location_utils_util_adg

        assert location_utils_util_adg is not None

    def test_location_utils_util_adg_class(self):
        """Test LocationUtilsUtilAdg class exists."""
        from agentic_core import LocationUtilsUtilAdg

        assert LocationUtilsUtilAdg is not None

    def test_location_utils_util_adg_callable(self):
        """Test location_utils_util_adg functions are callable."""
        from agentic_core import validate_location_utils_util_adg

        assert callable(validate_location_utils_util_adg)
