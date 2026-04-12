"""Test VllmBackpressureIntegration functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestVllmBackpressureIntegration:
    """Test VllmBackpressureIntegration functionality."""

    def test_vllm_backpressure_integration_imports(self):
        """Test vllm_backpressure_integration module imports."""
        from agentic_core import vllm_backpressure_integration

        assert vllm_backpressure_integration is not None

    def test_vllm_backpressure_integration_class(self):
        """Test VllmBackpressureIntegration class exists."""
        from agentic_core import VllmBackpressureIntegration

        assert VllmBackpressureIntegration is not None

    def test_vllm_backpressure_integration_callable(self):
        """Test vllm_backpressure_integration functions are callable."""
        from agentic_core import validate_vllm_backpressure_integration

        assert callable(validate_vllm_backpressure_integration)
