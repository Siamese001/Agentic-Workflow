"""Test HealthStatusTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestHealthStatusTypesAdg:
    """Test HealthStatusTypesAdg functionality."""

    def test_health_status_types_adg_imports(self):
        """Test health_status_types_adg module imports."""
        from agentic_core import health_status_types_adg

        assert health_status_types_adg is not None

    def test_health_status_types_adg_class(self):
        """Test HealthStatusTypesAdg class exists."""
        from agentic_core import HealthStatusTypesAdg

        assert HealthStatusTypesAdg is not None

    def test_health_status_types_adg_callable(self):
        """Test health_status_types_adg functions are callable."""
        from agentic_core import validate_health_status_types_adg

        assert callable(validate_health_status_types_adg)
