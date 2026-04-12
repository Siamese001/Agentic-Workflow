"""Test MlWriteEnvelope functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMlWriteEnvelope:
    """Test MlWriteEnvelope functionality."""

    def test_ml_write_envelope_imports(self):
        """Test ml_write_envelope module imports."""
        from agentic_core import ml_write_envelope

        assert ml_write_envelope is not None

    def test_ml_write_envelope_class(self):
        """Test MlWriteEnvelope class exists."""
        from agentic_core import MlWriteEnvelope

        assert MlWriteEnvelope is not None

    def test_ml_write_envelope_callable(self):
        """Test ml_write_envelope functions are callable."""
        from agentic_core import validate_ml_write_envelope

        assert callable(validate_ml_write_envelope)
