"""Test Gateway functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestGateway:
    """Test Gateway functionality."""

    def test_gateway_imports(self):
        """Test gateway module imports."""
        from agentic_core.interfaces import gateway
        assert gateway is not None

    def test_gateway_class(self):
        """Test Gateway class exists."""
        from agentic_core.interfaces.gateway_shim import SovereignLLMGateway
        assert SovereignLLMGateway is not None

    def test_gateway_callable(self):
        """Test gateway exports are accessible."""
        from agentic_core.interfaces.gateway_shim import GenerationRequest
        assert GenerationRequest is not None
