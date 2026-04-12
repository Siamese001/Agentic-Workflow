"""Test TelemetryRecorder functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestTelemetryRecorder:
    """Test TelemetryRecorder functionality."""

    def test_telemetry_recorder_imports(self):
        """Test telemetry_recorder module imports."""
        from agentic_core import telemetry_recorder

        assert telemetry_recorder is not None

    def test_telemetry_recorder_class(self):
        """Test TelemetryRecorder class exists."""
        from agentic_core import TelemetryRecorder

        assert TelemetryRecorder is not None

    def test_telemetry_recorder_callable(self):
        """Test telemetry_recorder functions are callable."""
        from agentic_core import validate_telemetry_recorder

        assert callable(validate_telemetry_recorder)
