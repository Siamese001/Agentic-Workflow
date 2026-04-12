"""Test VllmGatewayAdapter functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVllmGatewayAdapter:
    """Test VllmGatewayAdapter functionality."""

    def test_vllm_gateway_adapter_imports(self):
        """Test vllm_gateway_adapter module imports."""
        from agentic_core import vllm_gateway_adapter

        assert vllm_gateway_adapter is not None

    def test_vllm_gateway_adapter_class(self):
        """Test VllmGatewayAdapter class exists."""
        from agentic_core import VllmGatewayAdapter

        assert VllmGatewayAdapter is not None

    def test_vllm_gateway_adapter_callable(self):
        """Test vllm_gateway_adapter functions are callable."""
        from agentic_core import validate_vllm_gateway_adapter

        assert callable(validate_vllm_gateway_adapter)
