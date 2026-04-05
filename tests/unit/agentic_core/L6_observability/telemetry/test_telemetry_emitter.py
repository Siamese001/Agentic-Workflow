"""Test TelemetryEmitter functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestTelemetryEmitter:
    """Test TelemetryEmitter functionality."""

    def test_telemetry_emitter_imports(self):
        """Test telemetry_emitter module imports."""
        from agentic_core import telemetry_emitter
        assert telemetry_emitter is not None

    def test_telemetry_emitter_class(self):
        """Test TelemetryEmitter class exists."""
        from agentic_core import TelemetryEmitter
        assert TelemetryEmitter is not None

    def test_telemetry_emitter_callable(self):
        """Test telemetry_emitter functions are callable."""
        from agentic_core import validate_telemetry_emitter
        assert callable(validate_telemetry_emitter)
