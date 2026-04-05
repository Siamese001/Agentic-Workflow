"""Test TelemetryTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestTelemetryTypesAdg:
    """Test TelemetryTypesAdg functionality."""

    def test_telemetry_types_adg_imports(self):
        """Test telemetry_types_adg module imports."""
        from agentic_core import telemetry_types_adg
        assert telemetry_types_adg is not None

    def test_telemetry_types_adg_class(self):
        """Test TelemetryTypesAdg class exists."""
        from agentic_core import TelemetryTypesAdg
        assert TelemetryTypesAdg is not None

    def test_telemetry_types_adg_callable(self):
        """Test telemetry_types_adg functions are callable."""
        from agentic_core import validate_telemetry_types_adg
        assert callable(validate_telemetry_types_adg)
