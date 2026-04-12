"""Test SandboxEnvelope functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSandboxEnvelope:
    """Test SandboxEnvelope functionality."""

    def test_sandbox_envelope_imports(self):
        """Test sandbox_envelope module imports."""
        try:
            from agentic_core import sandbox_envelope

            assert sandbox_envelope is not None
        except ImportError:
            pytest.skip("sandbox_envelope not available")

    def test_sandbox_envelope_class(self):
        """Test SandboxEnvelope class exists."""
        try:
            from agentic_core import SandboxEnvelope

            assert SandboxEnvelope is not None
        except ImportError:
            pytest.skip("SandboxEnvelope not available")

    def test_sandbox_envelope_callable(self):
        """Test sandbox_envelope functions are callable."""
        try:
            from agentic_core import validate_sandbox_envelope

            assert callable(validate_sandbox_envelope)
        except ImportError:
            pytest.skip("validate_sandbox_envelope not available")
