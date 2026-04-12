"""Test VllmGatewayIntegrationTypesAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVllmGatewayIntegrationTypesAdg:
    """Test VllmGatewayIntegrationTypesAdg functionality."""

    def test_vllm_gateway_integration_types_adg_imports(self):
        """Test vllm_gateway_integration_types_adg module imports."""
        from agentic_core import vllm_gateway_integration_types_adg

        assert vllm_gateway_integration_types_adg is not None

    def test_vllm_gateway_integration_types_adg_class(self):
        """Test VllmGatewayIntegrationTypesAdg class exists."""
        from agentic_core import VllmGatewayIntegrationTypesAdg

        assert VllmGatewayIntegrationTypesAdg is not None

    def test_vllm_gateway_integration_types_adg_callable(self):
        """Test vllm_gateway_integration_types_adg functions are callable."""
        from agentic_core import validate_vllm_gateway_integration_types_adg

        assert callable(validate_vllm_gateway_integration_types_adg)
