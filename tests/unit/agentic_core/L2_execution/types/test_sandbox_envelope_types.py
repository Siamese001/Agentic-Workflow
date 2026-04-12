"""Test SandboxEnvelopeTypes functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSandboxEnvelopeTypes:
    """Test SandboxEnvelopeTypes functionality."""

    def test_sandbox_envelope_types_imports(self):
        """Test sandbox_envelope_types module imports."""
        from agentic_core import sandbox_envelope_types

        assert sandbox_envelope_types is not None

    def test_sandbox_envelope_types_class(self):
        """Test SandboxEnvelopeTypes class exists."""
        from agentic_core import SandboxEnvelopeTypes

        assert SandboxEnvelopeTypes is not None

    def test_sandbox_envelope_types_callable(self):
        """Test sandbox_envelope_types functions are callable."""
        from agentic_core import validate_sandbox_envelope_types

        assert callable(validate_sandbox_envelope_types)
