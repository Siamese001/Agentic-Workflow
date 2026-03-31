"""Test FixedPropertyTesting functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestFixedPropertyTesting:
    """Test FixedPropertyTesting functionality."""

    def test_fixed_property_imports(self):
        """Test fixed property module imports."""
        from infrastructure import fixed_property
        assert fixed_property is not None

    def test_fixed_property_tester_exists(self):
        """Test fixed property tester class exists."""
        from infrastructure.fixed_property import FixedPropertyTester
        assert FixedPropertyTester is not None

    def test_fixed_property_validate(self):
        """Test fixed property validate function."""
        from infrastructure.fixed_property import validate_properties
        assert callable(validate_properties)
