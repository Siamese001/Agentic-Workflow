"""Test ConfCalibGate functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestConfCalibGate:
    """Test ConfCalibGate functionality."""

    def test_conf_calib_gate_imports(self):
        """Test conf_calib_gate module imports."""
        from agentic_core import conf_calib_gate
        assert conf_calib_gate is not None

    def test_conf_calib_gate_class(self):
        """Test ConfCalibGate class exists."""
        from agentic_core import ConfCalibGate
        assert ConfCalibGate is not None

    def test_conf_calib_gate_callable(self):
        """Test conf_calib_gate functions are callable."""
        from agentic_core import validate_conf_calib_gate
        assert callable(validate_conf_calib_gate)
