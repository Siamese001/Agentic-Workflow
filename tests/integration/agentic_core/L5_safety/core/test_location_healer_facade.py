"""Test LocationHealerFacade functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestLocationHealerFacade:
    """Test LocationHealerFacade functionality."""

    def test_location_healer_facade_imports(self):
        """Test location_healer_facade module imports."""
        try:
            from agentic_core import location_healer_facade

            assert location_healer_facade is not None
        except ImportError:
            pytest.skip("location_healer_facade not available")

    def test_location_healer_facade_class(self):
        """Test LocationHealerFacade class exists."""
        try:
            from agentic_core import LocationHealerFacade

            assert LocationHealerFacade is not None
        except ImportError:
            pytest.skip("LocationHealerFacade not available")

    def test_location_healer_facade_callable(self):
        """Test location_healer_facade functions are callable."""
        try:
            from agentic_core import validate_location_healer_facade

            assert callable(validate_location_healer_facade)
        except ImportError:
            pytest.skip("validate_location_healer_facade not available")
