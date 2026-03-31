"""Test MlEndToEndEnvelope functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestMlEndToEndEnvelope:
    """Test MlEndToEndEnvelope functionality."""

    def test_ml_end_to_end_envelope_imports(self):
        """Test ml_end_to_end_envelope module imports."""
        from agentic_core import ml_end_to_end_envelope
        assert ml_end_to_end_envelope is not None

    def test_ml_end_to_end_envelope_class(self):
        """Test MlEndToEndEnvelope class exists."""
        from agentic_core import MlEndToEndEnvelope
        assert MlEndToEndEnvelope is not None

    def test_ml_end_to_end_envelope_callable(self):
        """Test ml_end_to_end_envelope functions are callable."""
        from agentic_core import validate_ml_end_to_end_envelope
        assert callable(validate_ml_end_to_end_envelope)
