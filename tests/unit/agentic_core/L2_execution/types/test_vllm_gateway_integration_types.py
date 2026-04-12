"""Test VllmGatewayIntegrationTypes functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVllmGatewayIntegrationTypes:
    """Test VllmGatewayIntegrationTypes functionality."""

    def test_vllm_gateway_integration_types_imports(self):
        """Test vllm_gateway_integration_types module imports."""
        from agentic_core import vllm_gateway_integration_types

        assert vllm_gateway_integration_types is not None

    def test_vllm_gateway_integration_types_class(self):
        """Test VllmGatewayIntegrationTypes class exists."""
        from agentic_core import VllmGatewayIntegrationTypes

        assert VllmGatewayIntegrationTypes is not None

    def test_vllm_gateway_integration_types_callable(self):
        """Test vllm_gateway_integration_types functions are callable."""
        from agentic_core import validate_vllm_gateway_integration_types

        assert callable(validate_vllm_gateway_integration_types)
