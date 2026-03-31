"""Test SovereignLlmGatewayHardened functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSovereignLlmGatewayHardened:
    """Test SovereignLlmGatewayHardened functionality."""

    def test_sovereign_llm_gateway_hardened_imports(self):
        """Test sovereign_llm_gateway_hardened module imports."""
        from agentic_core import sovereign_llm_gateway_hardened
        assert sovereign_llm_gateway_hardened is not None

    def test_sovereign_llm_gateway_hardened_class(self):
        """Test SovereignLlmGatewayHardened class exists."""
        from agentic_core import SovereignLlmGatewayHardened
        assert SovereignLlmGatewayHardened is not None

    def test_sovereign_llm_gateway_hardened_callable(self):
        """Test sovereign_llm_gateway_hardened functions are callable."""
        from agentic_core import validate_sovereign_llm_gateway_hardened
        assert callable(validate_sovereign_llm_gateway_hardened)
